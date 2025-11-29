#!/usr/bin/env python3
"""
Create an admin user for the Entrepedia AI Platform.
"""
import sys
import os
sys.path.append('/Users/harrycastaner/entrepedia-ai-platform')

from backend.database.database import get_db_context
from backend.database.models import User
from backend.utils.security import hash_password
from backend.utils.logger import app_logger

def create_admin_user():
    """Create an admin user account."""
    admin_credentials = {
        'username': 'admin',
        'email': 'admin@entrepedia.ai',
        'password': 'admin123',
        'full_name': 'Platform Administrator'
    }

    try:
        with get_db_context() as db:
            # Check if admin already exists
            existing_admin = db.query(User).filter(User.username == admin_credentials['username']).first()
            if existing_admin:
                print("❌ Admin user already exists!")
                print(f"Username: {admin_credentials['username']}")
                print(f"Email: {admin_credentials['email']}")
                return

            # Check if email already exists
            existing_email = db.query(User).filter(User.email == admin_credentials['email']).first()
            if existing_email:
                print("❌ Admin email already registered!")
                return

            # Create admin user (use simple hash for admin creation)
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            # Use direct bcrypt with short password
            password = admin_credentials['password'][:8]  # Ensure short password
            hashed_pwd = pwd_context.hash(password)
            admin_user = User(
                username=admin_credentials['username'],
                email=admin_credentials['email'],
                full_name=admin_credentials['full_name'],
                hashed_password=hashed_pwd,
                is_active=True,
                is_superuser=True  # Mark as superuser/admin
            )

            db.add(admin_user)
            db.commit()

            print("✅ Admin user created successfully!")
            print("\n" + "="*50)
            print("🔑 ADMIN CREDENTIALS")
            print("="*50)
            print(f"Username: {admin_credentials['username']}")
            print(f"Email: {admin_credentials['email']}")
            print(f"Password: {password}")  # Show the actual password used
            print(f"Full Name: {admin_credentials['full_name']}")
            print("="*50)
            print("\n💡 You can now login to the platform at:")
            print("   Frontend: http://localhost:3001")
            print("   API Docs: http://localhost:8000/docs")

    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()