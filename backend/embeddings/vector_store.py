"""
Vector database interface supporting FAISS, Pinecone, and Weaviate.
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pickle
from pathlib import Path
from backend.utils.config import settings
from backend.utils.logger import app_logger

# Optional vector database dependencies
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


DEFAULT_VECTOR_DB_PATH = Path("data/vector_db")

class VectorStore:
    """Unified interface for vector databases."""

    def __init__(self, store_type: str = None):
        """
        Initialize vector store.

        Args:
            store_type: Type of vector store ('faiss', 'pinecone', 'weaviate')
        """
        self.store_type = store_type or settings.vector_db_type
        self.logger = app_logger

        if self.store_type == "faiss":
            self.store = FAISSVectorStore()
            # Auto-load existing index
            if DEFAULT_VECTOR_DB_PATH.exists():
                self.store.load(str(DEFAULT_VECTOR_DB_PATH))
        elif self.store_type == "pinecone":
            self.store = PineconeVectorStore()
        elif self.store_type == "weaviate":
            self.store = WeaviateVectorStore()
        elif self.store_type == "supabase":
            self.store = SupabaseVectorStore()
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")

    def add_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]] = None) -> bool:
        """
        Add embeddings to the vector store.

        Args:
            embeddings: List of embedding dictionaries
            metadata: Optional metadata for each embedding

        Returns:
            True if successful
        """
        success = self.store.add_embeddings(embeddings, metadata)
        
        # Auto-save for local FAISS store
        if success and self.store_type == "faiss":
            self.store.save(str(DEFAULT_VECTOR_DB_PATH))
            
        return success

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.

        Args:
            query_vector: Query embedding vector
            k: Number of results to return

        Returns:
            List of similar embeddings with scores
        """
        return self.store.search(query_vector, k)

    def delete(self, ids: List[str]) -> bool:
        """
        Delete embeddings by IDs.

        Args:
            ids: List of embedding IDs to delete

        Returns:
            True if successful
        """
        return self.store.delete(ids)

    def save(self, path: str) -> bool:
        """
        Save the vector store to disk.

        Args:
            path: Path to save the store

        Returns:
            True if successful
        """
        return self.store.save(path)

    def load(self, path: str) -> bool:
        """
        Load the vector store from disk.

        Args:
            path: Path to load the store from

        Returns:
            True if successful
        """
        return self.store.load(path)


class FAISSVectorStore:
    """FAISS-based vector store implementation."""

    def __init__(self):
        """Initialize FAISS store."""
        self.index = None
        self.embeddings = []
        self.metadata = []
        self.dimension = None
        self.deleted_indices = set()  # Track deleted indices
        self.logger = app_logger
        self.logger.info(f"FAISSVectorStore initialized. Instance ID: {id(self)}")

    def add_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]] = None) -> bool:
        """Add embeddings to FAISS index."""
        try:
            if not embeddings:
                return False

            # Extract vectors
            vectors = []
            for emb in embeddings:
                if 'vector' in emb:
                    vectors.append(emb['vector'])
                else:
                    self.logger.error("Embedding missing 'vector' field")
                    return False

            vectors = np.array(vectors, dtype=np.float32)
            self.logger.info(f"Adding {len(vectors)} vectors to FAISS. Shape: {vectors.shape}")

            # Initialize index if needed
            if self.index is None:
                self.dimension = vectors.shape[1]
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                self.logger.info(f"Created new FAISS index with dimension {self.dimension}")

            # Normalize vectors for cosine similarity
            faiss.normalize_L2(vectors)

            # Add to index
            self.index.add(vectors)
            self.logger.info(f"Added vectors to index. Total vectors: {self.index.ntotal}")

            # Store embeddings and metadata
            self.embeddings.extend(embeddings)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{}] * len(embeddings))

            self.logger.info(f"Added {len(embeddings)} embeddings to FAISS index")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add embeddings to FAISS: {e}")
            return False

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search FAISS index."""
        try:
            if self.index is None:
                self.logger.warning("FAISS index is None during search")
                return []
            
            self.logger.info(f"Searching FAISS index. Total vectors: {self.index.ntotal}")

            # Normalize query vector
            query = np.array([query_vector], dtype=np.float32)
            self.logger.info(f"Query vector shape: {query.shape}")
            
            faiss.normalize_L2(query)
            self.logger.info("Query vector normalized")

            # Search
            self.logger.info(f"Executing search with k={k}")
            scores, indices = self.index.search(query, k)
            self.logger.info(f"Search complete. Found {len(indices[0])} results")

            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and idx not in self.deleted_indices:  # Valid result and not deleted
                    results.append({
                        'id': int(idx),  # Convert numpy int to python int
                        'score': float(score),
                        'embedding': self.embeddings[idx],
                        'metadata': self.metadata[idx] if idx < len(self.metadata) else {}
                    })

            self.logger.info(f"Returning {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"FAISS search failed: {e}", exc_info=True)
            return []

    def delete(self, ids: List[str]) -> bool:
        """Delete embeddings by marking indices as deleted."""
        try:
            deleted_count = 0
            for id_str in ids:
                try:
                    idx = int(id_str)
                    if 0 <= idx < len(self.embeddings):
                        self.deleted_indices.add(idx)
                        deleted_count += 1
                except ValueError:
                    self.logger.warning(f"Invalid ID format: {id_str}")
                    continue

            self.logger.info(f"Marked {deleted_count} embeddings as deleted")

            # If too many items are deleted, consider rebuilding the index
            if len(self.deleted_indices) > len(self.embeddings) * 0.3:
                self.logger.warning(f"Many items deleted ({len(self.deleted_indices)}/{len(self.embeddings)}). Consider rebuilding index for better performance.")

            return deleted_count > 0
        except Exception as e:
            self.logger.error(f"Failed to delete embeddings: {e}")
            return False

    def save(self, path: str) -> bool:
        """Save FAISS index and metadata."""
        try:
            save_path = Path(path)
            save_path.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            if self.index:
                faiss.write_index(self.index, str(save_path / "faiss.index"))

            # Save metadata
            with open(save_path / "embeddings.pkl", "wb") as f:
                pickle.dump(self.embeddings, f)

            with open(save_path / "metadata.pkl", "wb") as f:
                pickle.dump(self.metadata, f)

            # Save deleted indices
            with open(save_path / "deleted_indices.pkl", "wb") as f:
                pickle.dump(self.deleted_indices, f)

            self.logger.info(f"Saved FAISS store to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save FAISS store: {e}")
            return False

    def load(self, path: str) -> bool:
        """Load FAISS index and metadata."""
        try:
            load_path = Path(path)

            # Load FAISS index
            index_file = load_path / "faiss.index"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))

            # Load metadata
            embeddings_file = load_path / "embeddings.pkl"
            if embeddings_file.exists():
                with open(embeddings_file, "rb") as f:
                    self.embeddings = pickle.load(f)

            metadata_file = load_path / "metadata.pkl"
            if metadata_file.exists():
                with open(metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)

            # Load deleted indices
            deleted_file = load_path / "deleted_indices.pkl"
            if deleted_file.exists():
                with open(deleted_file, "rb") as f:
                    self.deleted_indices = pickle.load(f)
            else:
                self.deleted_indices = set()

            self.logger.info(f"Loaded FAISS store from {path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load FAISS store: {e}")
            return False


# Singleton instance
global_vector_store = VectorStore()


class PineconeVectorStore:
    """Pinecone-based vector store implementation."""

    def __init__(self):
        """Initialize Pinecone store."""
        self.logger = app_logger
        self.index = None

        try:
            if settings.pinecone_api_key:
                import pinecone
                pinecone.init(
                    api_key=settings.pinecone_api_key,
                    environment=settings.pinecone_environment
                )
                # Initialize index here based on your Pinecone setup
                self.logger.info("Pinecone initialized")
            else:
                self.logger.warning("Pinecone API key not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")

    def add_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]] = None) -> bool:
        """Add embeddings to Pinecone."""
        # Implementation would depend on your Pinecone setup
        self.logger.info("Pinecone add_embeddings - implement based on your setup")
        return False

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone index."""
        self.logger.info("Pinecone search - implement based on your setup")
        return []

    def delete(self, ids: List[str]) -> bool:
        """Delete from Pinecone."""
        return False

    def save(self, path: str) -> bool:
        """Pinecone is cloud-based, no local save needed."""
        return True

    def load(self, path: str) -> bool:
        """Pinecone is cloud-based, no local load needed."""
        return True


class WeaviateVectorStore:
    """Weaviate-based vector store implementation."""

    def __init__(self):
        """Initialize Weaviate store."""
        self.logger = app_logger
        self.client = None

        try:
            if settings.weaviate_url:
                import weaviate
                self.client = weaviate.Client(url=settings.weaviate_url)
                self.logger.info("Weaviate initialized")
            else:
                self.logger.warning("Weaviate URL not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize Weaviate: {e}")

    def add_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]] = None) -> bool:
        """Add embeddings to Weaviate."""
        # Implementation would depend on your Weaviate schema
        self.logger.info("Weaviate add_embeddings - implement based on your schema")
        return False

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search Weaviate."""
        self.logger.info("Weaviate search - implement based on your schema")
        return []

    def delete(self, ids: List[str]) -> bool:
        """Delete from Weaviate."""
        return False

    def save(self, path: str) -> bool:
        """Weaviate persists automatically."""
        return True

    def load(self, path: str) -> bool:
        """Weaviate loads automatically."""
        return True


class SupabaseVectorStore:
    """Supabase (PostgreSQL + pgvector) vector store implementation."""

    def __init__(self):
        """Initialize Supabase store."""
        self.logger = app_logger
        self.conn_string = settings.database_url
        
        # Ensure we have a connection string
        if not self.conn_string:
            self.logger.error("Database URL not configured for SupabaseVectorStore")
            return

        # Initialize pgvector extension and table if needed
        # This is best done in a migration, but we'll try to ensure it exists here or log a warning
        self._check_setup()

    def _get_conn(self):
        import psycopg2
        return psycopg2.connect(self.conn_string)

    def _check_setup(self):
        """Check if pgvector extension and table exist."""
        try:
            with self._get_conn() as conn:
                with conn.cursor() as cur:
                    # Check extension
                    cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
                    if not cur.fetchone():
                        self.logger.warning("pgvector extension not found. Please run setup_supabase.py")
                    
                    # Check table
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'document_vectors'
                        )
                    """)
                    if not cur.fetchone()[0]:
                         self.logger.warning("document_vectors table not found. Please run setup_supabase.py")
        except Exception as e:
            self.logger.error(f"Failed to check Supabase setup: {e}")

    def add_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]] = None) -> bool:
        """Add embeddings to Supabase."""
        if not embeddings:
            return False

        try:
            import json
            from pgvector.psycopg2 import register_vector
            
            with self._get_conn() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    for i, emb in enumerate(embeddings):
                        vector = emb['vector']
                        meta = metadata[i] if metadata and i < len(metadata) else {}
                        
                        # Insert
                        cur.execute("""
                            INSERT INTO document_vectors (content, embedding, metadata)
                            VALUES (%s, %s, %s)
                        """, (emb.get('text', ''), vector, json.dumps(meta)))
                conn.commit()
            
            self.logger.info(f"Added {len(embeddings)} embeddings to Supabase")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add embeddings to Supabase: {e}")
            return False

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search Supabase using pgvector cosine similarity."""
        try:
            from pgvector.psycopg2 import register_vector
            
            results = []
            with self._get_conn() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    # Cosine distance operator is <=>
                    # We want 1 - distance for similarity
                    cur.execute("""
                        SELECT id, content, metadata, 1 - (embedding <=> %s) as similarity
                        FROM document_vectors
                        ORDER BY embedding <=> %s
                        LIMIT %s
                    """, (query_vector, query_vector, k))
                    
                    rows = cur.fetchall()
                    for row in rows:
                        results.append({
                            'id': row[0],
                            'text': row[1],
                            'metadata': row[2],
                            'score': float(row[3]),
                            'embedding': {} # Don't return full vector to save bandwidth
                        })
            
            return results

        except Exception as e:
            self.logger.error(f"Supabase search failed: {e}")
            return []

    def delete(self, ids: List[str]) -> bool:
        """Delete from Supabase."""
        try:
            with self._get_conn() as conn:
                with conn.cursor() as cur:
                    # Assuming ids are integers for this table
                    # If ids are filenames or other metadata, we'd need a different query
                    # For now, let's assume we delete by metadata->>'filename' if id is not int
                    
                    for id_str in ids:
                        if id_str.isdigit():
                            cur.execute("DELETE FROM document_vectors WHERE id = %s", (int(id_str),))
                        else:
                            # Try deleting by filename in metadata
                            cur.execute("DELETE FROM document_vectors WHERE metadata->>'filename' = %s", (id_str,))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Supabase delete failed: {e}")
            return False

    def save(self, path: str) -> bool:
        """Supabase persists automatically."""
        return True

    def load(self, path: str) -> bool:
        """Supabase loads automatically."""
        return True