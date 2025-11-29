#!/usr/bin/env python3
"""
Comprehensive system audit and testing script for Entrepedia AI Platform.
Tests all endpoints, identifies issues, and reports system health.
"""
import requests
import json
import sys
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

class SystemAuditor:
    def __init__(self):
        self.results = []
        self.token = None
        
    def log_result(self, category: str, test: str, status: str, details: str = ""):
        """Log test result."""
        self.results.append({
            "category": category,
            "test": test,
            "status": status,
            "details": details
        })
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} [{category}] {test}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_health(self):
        """Test health endpoint."""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result("CORE", "Health Check", "PASS", 
                              f"App: {data.get('app')}, Env: {data.get('environment')}")
            else:
                self.log_result("CORE", "Health Check", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("CORE", "Health Check", "FAIL", str(e))
    
    def test_auth(self):
        """Test authentication endpoints."""
        # Test login
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": "testuser", "password": "test123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_result("AUTH", "Login", "PASS", "Token received")
            else:
                self.log_result("AUTH", "Login", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AUTH", "Login", "FAIL", str(e))
        
        # Test register
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "newpass123",
                    "full_name": "New User"
                }
            )
            if response.status_code == 200:
                self.log_result("AUTH", "Register", "PASS")
            elif response.status_code == 400:
                self.log_result("AUTH", "Register", "WARN", 
                              "User may already exist (expected)")
            else:
                self.log_result("AUTH", "Register", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AUTH", "Register", "FAIL", str(e))
        
        # Test /me endpoint
        try:
            response = requests.get(f"{BASE_URL}/auth/me")
            if response.status_code == 200:
                self.log_result("AUTH", "Get User Info", "PASS")
            else:
                self.log_result("AUTH", "Get User Info", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AUTH", "Get User Info", "FAIL", str(e))
    
    def test_documents(self):
        """Test document endpoints."""
        # Create a test file
        test_content = "This is a comprehensive system test document for the Entrepedia AI Platform."
        
        # Test upload
        try:
            files = {"file": ("audit_test.txt", test_content, "text/plain")}
            data = {"create_embeddings": "true"}
            response = requests.post(
                f"{BASE_URL}/documents/upload",
                files=files,
                data=data
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    embeddings_status = "with embeddings" if result.get("embeddings_created") else "without embeddings"
                    self.log_result("DOCUMENTS", "Upload", "PASS", embeddings_status)
                else:
                    self.log_result("DOCUMENTS", "Upload", "FAIL", 
                                  result.get("error", "Unknown error"))
            else:
                self.log_result("DOCUMENTS", "Upload", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("DOCUMENTS", "Upload", "FAIL", str(e))
        
        # Test list documents
        try:
            response = requests.get(f"{BASE_URL}/documents/list")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("documents", []))
                self.log_result("DOCUMENTS", "List Documents", "PASS", 
                              f"Found {count} documents")
            else:
                self.log_result("DOCUMENTS", "List Documents", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("DOCUMENTS", "List Documents", "FAIL", str(e))
    
    def test_query(self):
        """Test query endpoints."""
        # Test search
        try:
            response = requests.post(
                f"{BASE_URL}/query/search",
                json={"query": "system test", "top_k": 5}
            )
            if response.status_code == 200:
                data = response.json()
                count = data.get("total_found", 0)
                self.log_result("QUERY", "Vector Search", "PASS", 
                              f"Found {count} results")
            else:
                self.log_result("QUERY", "Vector Search", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("QUERY", "Vector Search", "FAIL", str(e))
        
        # Test ask (may fail without API keys)
        try:
            response = requests.post(
                f"{BASE_URL}/query/ask",
                json={
                    "query": "What is this platform about?",
                    "agent_type": "coach",
                    "include_knowledge_base": True
                }
            )
            if response.status_code == 200:
                self.log_result("QUERY", "Ask (LLM)", "PASS")
            elif response.status_code == 401:
                self.log_result("QUERY", "Ask (LLM)", "WARN", 
                              "API keys not configured (expected)")
            elif response.status_code == 500:
                # Check if it's an API key issue
                error_detail = response.json().get("detail", "")
                if "API" in error_detail or "key" in error_detail.lower():
                    self.log_result("QUERY", "Ask (LLM)", "WARN", 
                                  "API keys not configured (expected)")
                else:
                    self.log_result("QUERY", "Ask (LLM)", "FAIL", 
                                  f"Status: {response.status_code}, Detail: {error_detail}")
            else:
                self.log_result("QUERY", "Ask (LLM)", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            error_str = str(e)
            if "API" in error_str or "key" in error_str.lower():
                self.log_result("QUERY", "Ask (LLM)", "WARN", 
                              "API keys not configured (expected)")
            else:
                self.log_result("QUERY", "Ask (LLM)", "FAIL", error_str)

    
    def test_integrations(self):
        """Test integration endpoints."""
        try:
            response = requests.get(f"{BASE_URL}/integrations/status")
            if response.status_code == 200:
                data = response.json()
                self.log_result("INTEGRATIONS", "Status Check", "PASS", 
                              f"Integrations: {len(data.get('integrations', {}))}")
            else:
                self.log_result("INTEGRATIONS", "Status Check", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("INTEGRATIONS", "Status Check", "FAIL", str(e))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("AUDIT SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n" + "="*60)
            print("FAILED TESTS:")
            print("="*60)
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"❌ [{r['category']}] {r['test']}")
                    if r["details"]:
                        print(f"   {r['details']}")
        
        return failed == 0

def main():
    print("="*60)
    print("ENTREPEDIA AI PLATFORM - SYSTEM AUDIT")
    print("="*60)
    print()
    
    auditor = SystemAuditor()
    
    print("Testing Core Endpoints...")
    auditor.test_health()
    
    print("\nTesting Authentication...")
    auditor.test_auth()
    
    print("\nTesting Document Management...")
    auditor.test_documents()
    
    print("\nTesting Query System...")
    auditor.test_query()
    
    print("\nTesting Integrations...")
    auditor.test_integrations()
    
    success = auditor.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
