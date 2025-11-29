#!/usr/bin/env python3
"""
Create a simple admin user using direct bcrypt.
"""
import bcrypt
import sqlite3
from datetime import datetime

def create_simple_admin():
    """Create admin with working bcrypt hash."""
    # Simple admin credentials
    username = 'admin'
    email = 'admin@entrepedia.ai'
    password = 'admin123'
    full_name = 'Platform Administrator'

    # Create bcrypt hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Connect to database
    conn = sqlite3.connect('data/entrepedia.db')
    cursor = conn.cursor()

    try:
        # Check if admin already exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("❌ Admin user already exists!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            return

        # Insert admin user
        cursor.execute("""
            INSERT INTO users (username, email, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 1, ?, ?)
        """, (username, email, full_name, hashed_password.decode('utf-8'), datetime.now(), datetime.now()))

        conn.commit()

        print("✅ Admin user created successfully!")
        print("\n" + "="*50)
        print("🔑 ADMIN CREDENTIALS")
        print("="*50)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Full Name: {full_name}")
        print("="*50)
        print("\n💡 You can now login to the platform at:")
        print("   Frontend: http://localhost:3001/login")
        print("   API Docs: http://localhost:8000/docs")
        print("\n🔗 Direct links:")
        print("   • Login Page: http://localhost:3001/login")
        print("   • Dashboard: http://localhost:3001/dashboard (after login)")

    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    create_simple_admin()