import os
import sys
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables explicitly
load_dotenv()

from backend.database.models import Base, User
from backend.utils.config import settings

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin_user():
    # Force use of env var if available, otherwise settings default
    db_url = os.getenv("DATABASE_URL", settings.database_url)
    print(f"Connecting to database: {db_url}")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        username = "testuser"
        email = "test@example.com"
        password = "test123"
        
        # Check if user exists
        user = db.query(User).filter(User.username == username).first()
        
        if user:
            print(f"User {username} already exists. Updating password...")
            user.hashed_password = hash_password(password)
            user.is_active = True
        else:
            print(f"Creating new user {username}...")
            user = User(
                username=username,
                email=email,
                full_name="Test Admin",
                hashed_password=hash_password(password),
                is_active=True
            )
            db.add(user)
        
        db.commit()
        print("✅ Admin user setup complete!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
