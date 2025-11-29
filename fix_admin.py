#!/usr/bin/env python3
"""
Fix admin user with proper bcrypt hash.
"""
import bcrypt
import sqlite3

def fix_admin():
    """Update admin user with proper bcrypt hash."""
    username = 'admin'
    password = 'admin123'

    # Create proper bcrypt hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Connect to database
    conn = sqlite3.connect('data/entrepedia.db')
    cursor = conn.cursor()

    try:
        # Update admin user password
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE username = ?",
            (hashed_password.decode('utf-8'), username)
        )

        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Admin password updated successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Hash: {hashed_password.decode('utf-8')[:50]}...")
        else:
            print("❌ Admin user not found!")

    except Exception as e:
        print(f"❌ Failed to update admin password: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_admin()