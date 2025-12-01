#!/usr/bin/env python3
"""
Script to set up admin user in Supabase for Vercel deployment.
Run this locally to ensure admin user exists in production database.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.utils.security import hash_password
from backend.database.models import Base, User

def setup_admin_user():
    """Create admin user in Supabase database."""

    # Use the production database URL
    database_url = "postgresql://postgres:Glory2GodAlways2023!@db.apmwojsfejoiugiohipm.supabase.co:5432/postgres"

    print(f"Connecting to database...")

    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=2,
        )

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Database connection successful")

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")

        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with SessionLocal() as db:
            # Check if admin user exists
            admin_email = "admin@entrepedia.ai"
            admin_user = db.query(User).filter(User.email == admin_email).first()

            if admin_user:
                print(f"✅ Admin user already exists: {admin_user.username} ({admin_user.email})")
                # Update password to ensure it matches
                admin_user.hashed_password = hash_password("admin123")
                admin_user.is_active = True
                action = "updated"
            else:
                # Create new admin user
                admin_user = User(
                    username="admin",
                    email=admin_email,
                    full_name="Admin User",
                    hashed_password=hash_password("admin123"),
                    is_active=True
                )
                db.add(admin_user)
                action = "created"

            db.commit()
            print(f"✅ Admin user {action} successfully!")
            print(f"   Username: admin")
            print(f"   Email: {admin_email}")
            print(f"   Password: admin123")

            # List all users for verification
            all_users = db.query(User).all()
            print(f"\n📊 Total users in database: {len(all_users)}")
            for user in all_users:
                status = "✅ Active" if user.is_active else "❌ Inactive"
                print(f"   - {user.username} ({user.email}) {status}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Setting up admin user in Supabase...")
    setup_admin_user()
    print("\n🎉 Setup complete! You can now login on Vercel with:")
    print("   Email: admin@entrepedia.ai")
    print("   Password: admin123")