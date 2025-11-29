"""
Setup script for Supabase production environment.
This script initializes the database schema and storage buckets.
"""
import os
import sys
import psycopg2
from supabase import create_client

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_database(db_url):
    """Initialize database schema."""
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Enable pgvector extension
        print("Enabling pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Create document_vectors table
        print("Creating document_vectors table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_vectors (
                id bigserial PRIMARY KEY,
                content text,
                metadata jsonb,
                embedding vector(1536)
            );
        """)
        
        # 3. Create index for faster search
        print("Creating vector index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS document_vectors_embedding_idx 
            ON document_vectors 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        print("Database setup complete!")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False

def setup_storage(url, key):
    """Initialize storage buckets."""
    print("Connecting to Supabase Storage...")
    try:
        supabase = create_client(url, key)
        
        # List buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if "courses" not in bucket_names:
            print("Creating 'courses' bucket...")
            supabase.storage.create_bucket("courses", options={"public": True})
            print("'courses' bucket created.")
        else:
            print("'courses' bucket already exists.")
            
        return True
    except Exception as e:
        print(f"Storage setup failed: {e}")
        return False

def main():
    print("=== Entrepedia Production Setup ===")
    
    # Get credentials
    db_url = input("Enter your Supabase Database URL (postgresql://...): ").strip()
    if not db_url:
        print("Database URL is required.")
        return

    sb_url = input("Enter your Supabase Project URL (https://...): ").strip()
    sb_key = input("Enter your Supabase Service Role Key: ").strip()
    
    if not sb_url or not sb_key:
        print("Supabase URL and Key are required for storage setup.")
        return

    # Run setup
    if setup_database(db_url):
        setup_storage(sb_url, sb_key)
        print("\nAll systems go! Your Supabase environment is ready.")
        print("Don't forget to set these environment variables in Render/Vercel:")
        print(f"DATABASE_URL={db_url}")
        print(f"SUPABASE_URL={sb_url}")
        print(f"SUPABASE_KEY={sb_key}")
        print("STORAGE_TYPE=supabase")
        print("VECTOR_DB_TYPE=supabase")

if __name__ == "__main__":
    main()
