"""
Generate semantic embeddings using various AI models.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from backend.utils.config import settings
from backend.utils.logger import app_logger

# Optional dependencies
try:
    from backend.utils.cache import cache_manager
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class EmbeddingGenerator:
    """Generate embeddings using multiple AI providers."""

    def __init__(self):
        """Initialize embedding generator."""
        self.logger = app_logger
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)

        # Initialize clients based on available API keys and modules
        if OPENAI_AVAILABLE and settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)

        if ANTHROPIC_AVAILABLE and settings.anthropic_api_key and settings.anthropic_api_key != "placeholder_anthropic_key":
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate_embeddings(
        self,
        texts: List[str],
        model: str = "gemini",
        chunk_size: int = 512
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            model: Model to use ('gemini', 'openai')
            chunk_size: Maximum characters per chunk

        Returns:
            List of embedding dictionaries with text and vector
        """
        self.logger.info(f"Generating embeddings for {len(texts)} texts using {model}")

        # Chunk texts if they're too long
        chunked_texts = []
        for text in texts:
            chunks = self._chunk_text(text, chunk_size)
            chunked_texts.extend(chunks)

        # Check cache for each chunk
        cached_embeddings = []
        texts_to_generate = []
        for chunk in chunked_texts:
            cached = cache_manager.get_embedding(chunk)
            if cached is not None:
                cached_embeddings.append({"text": chunk, "vector": cached})
            else:
                texts_to_generate.append(chunk)
        
        # Generate embeddings for uncached texts
        generated = []
        if model == "gemini" and GEMINI_AVAILABLE:
            generated = self._generate_gemini_embeddings(texts_to_generate)
        elif model == "openai" and self.openai_client:
            generated = self._generate_openai_embeddings(texts_to_generate)
        else:
            # Fallback to Gemini if available, otherwise error
            if GEMINI_AVAILABLE:
                generated = self._generate_gemini_embeddings(texts_to_generate)
            else:
                self.logger.error(f"Model {model} not available or not configured")
                return []
        
        # Store generated embeddings in cache
        for emb in generated:
            cache_manager.set_embedding(emb["text"], emb["vector"])
        
        # Combine cached and newly generated embeddings
        embeddings = cached_embeddings + generated

        self.logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    def _generate_gemini_embeddings(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Generate embeddings using Google Gemini."""
        embeddings = []
        try:
            # Process in batches
            batch_size = 20
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Gemini embedding call
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=batch,
                    task_type="retrieval_document",
                    title="Embedding of list of strings"
                )
                
                for j, vector in enumerate(result['embedding']):
                    embeddings.append({
                        'text': batch[j],
                        'vector': vector,
                        'model': 'models/embedding-001',
                        'dimensions': len(vector)
                    })
                    
        except Exception as e:
            self.logger.error(f"Gemini embedding generation failed: {e}")
            
        return embeddings

    def _generate_openai_embeddings(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Generate embeddings using OpenAI API."""
        embeddings = []

        try:
            # Process in batches to avoid API limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch
                )

                for j, embedding_data in enumerate(response.data):
                    embeddings.append({
                        'text': batch[j],
                        'vector': embedding_data.embedding,
                        'model': 'text-embedding-ada-002',
                        'dimensions': len(embedding_data.embedding)
                    })

        except Exception as e:
            self.logger.error(f"OpenAI embedding generation failed: {e}")

        return embeddings

    def _generate_sentence_transformer_embeddings(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Deprecated: SentenceTransformer removed for Vercel optimization."""
        self.logger.warning("SentenceTransformer is disabled for Vercel deployment")
        return []

    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """
        Split text into smaller chunks for embedding.

        Args:
            text: Input text to chunk
            max_length: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = text.split('. ')
        current_chunk = ""

        for sentence in sentences:
            # If adding this sentence would exceed the limit
            if len(current_chunk) + len(sentence) + 2 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
                else:
                    # Sentence itself is too long, force split
                    chunks.extend(self._force_split_text(sentence, max_length))
            else:
                current_chunk += sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return [chunk for chunk in chunks if chunk.strip()]

    def _force_split_text(self, text: str, max_length: int) -> List[str]:
        """Force split text that's too long even for a single chunk."""
        chunks = []
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i + max_length])
        return chunks

    def compute_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vector1: First embedding vector
            vector2: Second embedding vector

        Returns:
            Cosine similarity score
        """
        v1 = np.array(vector1)
        v2 = np.array(vector2)

        # Compute cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)