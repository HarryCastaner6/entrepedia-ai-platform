#!/bin/bash

echo "🔍 DEBUGGING VERCEL DEPLOYMENT"
echo "=============================="

URL="https://entrepedia-ai-platform-nxgbwjzen-harry-cs-projects.vercel.app"

echo ""
echo "🌐 Testing different endpoints..."

# Test 1: Root of the app
echo "Testing app root..."
curl -s -w "Status: %{http_code}\n" "$URL/" | head -5
echo ""

# Test 2: Favicon (should work if frontend deployed)
echo "Testing favicon (frontend check)..."
curl -s -w "Status: %{http_code}\n" "$URL/favicon.ico" | head -1
echo ""

# Test 3: API root
echo "Testing API root..."
curl -s -w "Status: %{http_code}\n" "$URL/api" | head -5
echo ""

# Test 4: Health endpoint detailed
echo "Testing health endpoint (verbose)..."
curl -v "$URL/api/health" 2>&1 | head -10
echo ""

# Test 5: Check if it's trying to serve static file
echo "Testing auth endpoint (verbose)..."
curl -v "$URL/api/auth/" 2>&1 | head -10
echo ""

echo "🔧 DIAGNOSIS:"
echo "If you see HTML responses instead of JSON, the Python functions aren't working."
echo "If you see 404 or static file responses, check vercel.json configuration."