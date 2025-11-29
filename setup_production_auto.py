"""
Automated setup script for Supabase production environment.
"""
import psycopg2

# Database credentials
db_url = "postgresql://postgres:Glory2GodAlways2023!@db.apmwojsfejoiugiohipm.supabase.co:5432/postgres"
supabase_url = "https://apmwojsfejoiugiohipm.supabase.co"

def setup_database():
    """Initialize database schema."""
    print(f"Setting up Supabase database...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Enable pgvector extension
        print("✓ Enabling pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Create document_vectors table
        print("✓ Creating document_vectors table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_vectors (
                id bigserial PRIMARY KEY,
                content text,
                metadata jsonb,
                embedding vector(1536),
                created_at timestamptz DEFAULT now()
            );
        """)
        
        # 3. Create index for faster search
        print("✓ Creating vector index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS document_vectors_embedding_idx 
            ON document_vectors 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        print("\n✅ Database setup complete!")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def setup_storage():
    """Initialize storage buckets."""
    print("\nSetting up Supabase Storage...")
    try:
        from supabase import create_client
        
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFwbXdvanNmZWpvaXVnaW9oaXBtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0Mzc2MDEsImV4cCI6MjA4MDAxMzYwMX0.aJdRDnyKgLNyyvAxPBH-HRDA6yL1zk7p5EFaF4ju5AM"
        
        supabase = create_client(supabase_url, supabase_key)
        
        # List buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if "courses" not in bucket_names:
            print("✓ Creating 'courses' bucket...")
            supabase.storage.create_bucket("courses", options={"public": True})
        else:
            print("✓ 'courses' bucket already exists.")
            
        print("\n✅ Storage setup complete!")
        return True
    except Exception as e:
        print(f"❌ Storage setup failed: {e}")
        print("Note: You may need to create the 'courses' bucket manually in Supabase dashboard.")
        return False

if __name__ == "__main__":
    print("=== Entrepedia Production Setup ===\n")
    
    if setup_database():
        setup_storage()
        print("\n" + "="*40)
        print("🎉 All systems ready for production!")
        print("="*40)
