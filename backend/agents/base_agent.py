"""
Base agent class providing common functionality for all AI agents.
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import anthropic
import openai
import google.generativeai as genai
from backend.utils.config import settings
from backend.utils.logger import agent_logger
from backend.embeddings.vector_store import global_vector_store
from backend.embeddings.embedding_generator import EmbeddingGenerator


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, name: str, system_prompt: str):
        """
        Initialize base agent.

        Args:
            name: Agent name
            system_prompt: System prompt for the agent
        """
        self.name = name
        self.system_prompt = system_prompt
        self.logger = agent_logger
        self.conversation_history = []

        # Initialize vector search components
        self.vector_store = global_vector_store
        self.embedding_generator = EmbeddingGenerator()

        # Initialize AI clients
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_model = None

        # Configure Gemini as primary AI
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')

        if settings.anthropic_api_key and settings.anthropic_api_key != "placeholder_anthropic_key":
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        if settings.openai_api_key and settings.openai_api_key != "placeholder_openai_key":
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)

    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query and return a response.

        Args:
            query: User query
            context: Additional context for the query

        Returns:
            Agent response
        """
        pass

    def chat(self, message: str) -> str:
        """
        Send message to the primary AI (Gemini) and get response.
        Falls back to Claude or OpenAI if Gemini is unavailable.

        Args:
            message: Message to send

        Returns:
            AI response
        """
        # Try Gemini first (primary AI)
        if self.gemini_model:
            return self.chat_with_gemini(message)

        # Fall back to Claude
        elif self.anthropic_client:
            return self.chat_with_claude(message)

        # Fall back to OpenAI
        elif self.openai_client:
            return self.chat_with_openai(message)

        else:
            return "Error: No AI models available"

    def chat_with_gemini(self, message: str) -> str:
        """
        Send message to Gemini and get response.

        Args:
            message: Message to send

        Returns:
            Gemini's response
        """
        try:
            if not self.gemini_model:
                raise ValueError("Gemini model not initialized")

            # Prepare the full prompt with system context
            full_prompt = f"System: {self.system_prompt}\n\nUser: {message}"

            response = self.gemini_model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            return f"Error: {e}"

    def chat_with_claude(self, message: str, model: str = "claude-3-sonnet-20240229") -> str:
        """
        Send message to Claude and get response.

        Args:
            message: Message to send
            model: Claude model to use

        Returns:
            Claude's response
        """
        try:
            if not self.anthropic_client:
                raise ValueError("Anthropic client not initialized")

            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[{"role": "user", "content": message}]
            )

            return response.content[0].text

        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            return f"Error: {e}"

    def chat_with_openai(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Send message to OpenAI and get response.

        Args:
            message: Message to send
            model: OpenAI model to use

        Returns:
            OpenAI's response
        """
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized")

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]

            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return f"Error: {e}"

    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })

        # Keep only last 10 messages to avoid context overflow
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    def get_conversation_context(self) -> str:
        """Get conversation history as context string."""
        context = ""
        for msg in self.conversation_history:
            context += f"{msg['role']}: {msg['content']}\n"
        return context

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_relevant_context(self, query: str, max_results: int = 5) -> str:
        """
        Retrieve relevant document context for a query using vector search.

        Args:
            query: The user's query
            max_results: Maximum number of documents to retrieve

        Returns:
            Formatted context string from relevant documents
        """
        try:
            # Generate embedding for the query
            query_embeddings = self.embedding_generator.generate_embeddings([query])

            if not query_embeddings or not query_embeddings[0].get('vector'):
                self.logger.warning("Failed to generate query embedding")
                return ""

            # Search for similar documents
            query_vector = query_embeddings[0]['vector']
            search_results = self.vector_store.search(query_vector, k=max_results)

            if not search_results:
                self.logger.info("No relevant documents found")
                return ""

            # Format the context
            context_parts = []
            context_parts.append("=== RELEVANT DOCUMENTS ===")

            for i, result in enumerate(search_results, 1):
                metadata = result.get('metadata', {})
                embedding_data = result.get('embedding', {})

                filename = metadata.get('filename', 'Unknown')
                source = metadata.get('source', 'Unknown')
                text_content = embedding_data.get('text', 'No content available')

                # Limit text length for context
                if len(text_content) > 500:
                    text_content = text_content[:500] + "..."

                context_parts.append(f"\n[Document {i}: {filename} from {source}]")
                context_parts.append(text_content)
                context_parts.append("---")

            context_parts.append("=== END DOCUMENTS ===\n")

            self.logger.info(f"Retrieved context from {len(search_results)} documents")
            return "\n".join(context_parts)

        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            return ""

    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format agent response in standard format.

        Args:
            content: Response content
            metadata: Additional metadata

        Returns:
            Formatted response
        """
        return {
            "agent": self.name,
            "content": content,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        }