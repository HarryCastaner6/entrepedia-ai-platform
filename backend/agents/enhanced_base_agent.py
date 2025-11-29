"""
Enhanced base agent with hypercharged AI capabilities including:
- Advanced semantic context retrieval with relevance scoring
- Multi-perspective reasoning and synthesis
- Dynamic prompt optimization
- Conversation memory and learning adaptation
- Chain-of-thought reasoning
- Self-reflection and response improvement
"""
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
import anthropic
import openai
import google.generativeai as genai
import numpy as np
from datetime import datetime, timedelta
import json
import re

from backend.utils.config import settings
from backend.utils.logger import agent_logger
from backend.embeddings.vector_store import global_vector_store
from backend.embeddings.embedding_generator import EmbeddingGenerator


class EnhancedBaseAgent(ABC):
    """Hyperenhanced base agent with advanced AI capabilities."""

    def __init__(self, name: str, system_prompt: str, expertise_areas: List[str] = None):
        """
        Initialize enhanced agent.

        Args:
            name: Agent name
            system_prompt: System prompt for the agent
            expertise_areas: List of expertise areas for dynamic specialization
        """
        self.name = name
        self.system_prompt = system_prompt
        self.expertise_areas = expertise_areas or []
        self.logger = agent_logger

        # Enhanced conversation memory
        self.conversation_history = []
        self.user_preferences = {}
        self.learning_patterns = {}

        # Performance tracking
        self.response_quality_scores = []
        self.context_usage_stats = {}

        # Initialize AI components
        self.vector_store = global_vector_store
        self.embedding_generator = EmbeddingGenerator()

        # Initialize AI clients with enhanced configuration
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_model = None

        self._initialize_ai_clients()
        self._load_user_profile()

    def _initialize_ai_clients(self):
        """Initialize AI clients with optimal configurations."""
        # Configure Gemini with advanced settings
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            # Use the most capable model with optimized settings
            generation_config = {
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 8192,
                'candidate_count': 1
            }
            safety_settings = [
                {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'}
            ]
            self.gemini_model = genai.GenerativeModel(
                'gemini-2.0-flash-lite',
                generation_config=generation_config,
                safety_settings=safety_settings
            )

        # Initialize other AI clients with optimized settings
        if settings.anthropic_api_key and settings.anthropic_api_key != "placeholder_anthropic_key":
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        if settings.openai_api_key and settings.openai_api_key != "placeholder_openai_key":
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)

    def _load_user_profile(self):
        """Load user preferences and learning patterns."""
        # In a production system, this would load from persistent storage
        # For now, initialize with smart defaults
        self.user_preferences = {
            'response_style': 'comprehensive',
            'technical_level': 'adaptive',
            'preferred_examples': True,
            'step_by_step': True,
            'source_citations': True
        }

    def get_enhanced_context(self, query: str, max_results: int = 8, context_window: int = 1500) -> Dict[str, Any]:
        """
        Advanced context retrieval with semantic ranking and multi-perspective analysis.

        Args:
            query: The user's query
            max_results: Maximum number of documents to retrieve
            context_window: Maximum characters per context chunk

        Returns:
            Enhanced context with relevance scores and metadata
        """
        try:
            self.logger.info(f"Retrieving enhanced context for query: {query[:100]}...")

            # Generate multiple query variations for comprehensive search
            query_variations = self._generate_query_variations(query)

            all_results = []
            seen_content = set()

            for variation in query_variations:
                # Generate embedding for the query variation
                query_embeddings = self.embedding_generator.generate_embeddings([variation])

                if not query_embeddings or not query_embeddings[0].get('vector'):
                    continue

                # Search for similar documents
                query_vector = query_embeddings[0]['vector']
                search_results = self.vector_store.search(query_vector, k=max_results)

                for result in search_results:
                    content_hash = hash(result.get('embedding', {}).get('text', ''))
                    if content_hash not in seen_content:
                        result['query_variation'] = variation
                        all_results.append(result)
                        seen_content.add(content_hash)

            if not all_results:
                return self._create_empty_context()

            # Advanced relevance scoring and ranking
            enhanced_results = self._rank_and_enhance_results(all_results, query)

            # Select best results based on diversity and relevance
            selected_results = self._select_diverse_results(enhanced_results, max_results)

            # Format enhanced context
            context_data = self._format_enhanced_context(selected_results, context_window)

            # Update usage statistics
            self._update_context_stats(query, len(selected_results))

            return context_data

        except Exception as e:
            self.logger.error(f"Error in enhanced context retrieval: {e}")
            return self._create_empty_context()

    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate semantic variations of the query for comprehensive search."""
        variations = [query]

        # Add keyword-focused variation
        keywords = re.findall(r'\b\w{4,}\b', query.lower())
        if keywords:
            keyword_query = ' '.join(keywords[:5])
            variations.append(keyword_query)

        # Add question variations
        if '?' not in query:
            variations.append(f"What is {query}?")
            variations.append(f"How to {query}?")
            variations.append(f"Why {query}?")

        # Add context-specific variations based on expertise areas
        for area in self.expertise_areas:
            variations.append(f"{query} {area}")

        return variations[:6]  # Limit to prevent excessive API calls

    def _rank_and_enhance_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Apply advanced ranking using multiple relevance signals."""
        enhanced_results = []

        for result in results:
            # Base similarity score from vector search
            base_score = result.get('score', 0.0)

            # Content quality indicators
            content = result.get('embedding', {}).get('text', '')
            metadata = result.get('metadata', {})

            # Length bonus (prefer substantial content)
            length_score = min(len(content) / 1000, 1.0) * 0.1

            # Recency bonus (prefer newer documents)
            recency_score = self._calculate_recency_score(metadata)

            # Source credibility score
            source_score = self._calculate_source_score(metadata)

            # Query-specific relevance
            semantic_score = self._calculate_semantic_relevance(content, query)

            # Combined relevance score
            final_score = (
                base_score * 0.4 +
                semantic_score * 0.3 +
                length_score * 0.1 +
                recency_score * 0.1 +
                source_score * 0.1
            )

            result['enhanced_score'] = final_score
            result['score_breakdown'] = {
                'base': base_score,
                'semantic': semantic_score,
                'length': length_score,
                'recency': recency_score,
                'source': source_score
            }

            enhanced_results.append(result)

        # Sort by enhanced score
        return sorted(enhanced_results, key=lambda x: x['enhanced_score'], reverse=True)

    def _calculate_recency_score(self, metadata: Dict) -> float:
        """Calculate recency bonus for documents."""
        # Simple implementation - in production, use actual file dates
        return 0.05  # Small baseline bonus

    def _calculate_source_score(self, metadata: Dict) -> float:
        """Calculate source credibility score."""
        source = metadata.get('source', '')
        filename = metadata.get('filename', '')

        # Prefer uploaded documents over scraped
        if source == 'upload':
            return 0.1
        elif source == 'scraper':
            return 0.05

        return 0.0

    def _calculate_semantic_relevance(self, content: str, query: str) -> float:
        """Calculate semantic relevance beyond vector similarity."""
        content_lower = content.lower()
        query_lower = query.lower()

        # Keyword overlap scoring
        query_words = set(re.findall(r'\b\w{3,}\b', query_lower))
        content_words = set(re.findall(r'\b\w{3,}\b', content_lower))

        if query_words:
            overlap_ratio = len(query_words & content_words) / len(query_words)
            return overlap_ratio * 0.3

        return 0.0

    def _select_diverse_results(self, results: List[Dict], max_results: int) -> List[Dict]:
        """Select diverse results to avoid redundancy."""
        if len(results) <= max_results:
            return results

        selected = []
        used_sources = set()
        content_hashes = set()

        for result in results:
            if len(selected) >= max_results:
                break

            # Check for diversity
            source = result.get('metadata', {}).get('filename', '')
            content = result.get('embedding', {}).get('text', '')
            content_hash = hash(content[:200])  # Use first 200 chars for similarity check

            # Skip if too similar to already selected content
            if content_hash in content_hashes:
                continue

            selected.append(result)
            used_sources.add(source)
            content_hashes.add(content_hash)

        # Fill remaining slots if needed
        remaining = max_results - len(selected)
        if remaining > 0:
            for result in results:
                if len(selected) >= max_results:
                    break
                if result not in selected:
                    selected.append(result)

        return selected

    def _format_enhanced_context(self, results: List[Dict], context_window: int) -> Dict[str, Any]:
        """Format enhanced context with metadata and scoring."""
        context_parts = []
        context_parts.append("=== ENHANCED DOCUMENT CONTEXT ===")

        total_relevance = 0
        source_diversity = set()

        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            embedding_data = result.get('embedding', {})
            score = result.get('enhanced_score', 0.0)

            filename = metadata.get('filename', 'Unknown')
            source = metadata.get('source', 'Unknown')
            text_content = embedding_data.get('text', 'No content available')

            # Intelligent content truncation
            if len(text_content) > context_window:
                # Try to find natural breakpoints
                sentences = text_content.split('. ')
                truncated = ""
                for sentence in sentences:
                    if len(truncated + sentence) > context_window - 100:
                        break
                    truncated += sentence + '. '
                text_content = truncated.strip() + "..."

            context_parts.append(f"\n[Document {i}: {filename} | Relevance: {score:.3f}]")
            context_parts.append(text_content)
            context_parts.append("---")

            total_relevance += score
            source_diversity.add(source)

        context_parts.append("=== END ENHANCED CONTEXT ===\n")

        return {
            'formatted_context': "\n".join(context_parts),
            'metadata': {
                'total_documents': len(results),
                'avg_relevance': total_relevance / len(results) if results else 0,
                'source_diversity': len(source_diversity),
                'context_length': len("\n".join(context_parts))
            },
            'results': results
        }

    def _create_empty_context(self) -> Dict[str, Any]:
        """Create empty context response."""
        return {
            'formatted_context': "",
            'metadata': {
                'total_documents': 0,
                'avg_relevance': 0.0,
                'source_diversity': 0,
                'context_length': 0
            },
            'results': []
        }

    def _update_context_stats(self, query: str, num_results: int):
        """Update context usage statistics for learning."""
        timestamp = datetime.now().isoformat()
        self.context_usage_stats[timestamp] = {
            'query_length': len(query),
            'results_found': num_results,
            'query_type': self._classify_query_type(query)
        }

        # Keep only last 100 entries to prevent memory growth
        if len(self.context_usage_stats) > 100:
            oldest_key = min(self.context_usage_stats.keys())
            del self.context_usage_stats[oldest_key]

    def _classify_query_type(self, query: str) -> str:
        """Classify query type for analytics."""
        query_lower = query.lower()

        if any(word in query_lower for word in ['what', 'define', 'explain']):
            return 'definition'
        elif any(word in query_lower for word in ['how', 'steps', 'guide']):
            return 'instruction'
        elif any(word in query_lower for word in ['why', 'because', 'reason']):
            return 'explanation'
        elif '?' in query:
            return 'question'
        else:
            return 'general'

    def enhanced_chat(self, message: str, context_data: Dict[str, Any] = None) -> str:
        """
        Enhanced chat with advanced reasoning and response optimization.

        Args:
            message: Message to process
            context_data: Enhanced context data

        Returns:
            Optimized AI response
        """
        # Build sophisticated prompt with context and reasoning framework
        enhanced_prompt = self._build_enhanced_prompt(message, context_data)

        # Get initial response from primary AI
        initial_response = self._get_primary_ai_response(enhanced_prompt)

        # Apply response enhancement and validation
        final_response = self._enhance_response(initial_response, message, context_data)

        # Learn from interaction
        self._learn_from_interaction(message, final_response)

        return final_response

    def _build_enhanced_prompt(self, message: str, context_data: Dict[str, Any] = None) -> str:
        """Build sophisticated prompt with context and reasoning framework."""
        prompt_parts = []

        # System context with dynamic adaptation
        prompt_parts.append(f"System: {self.system_prompt}")

        # Enhanced context if available
        if context_data and context_data.get('formatted_context'):
            prompt_parts.append(f"\nRelevant Context:\n{context_data['formatted_context']}")

            # Add metadata hints for better processing
            metadata = context_data.get('metadata', {})
            if metadata.get('total_documents', 0) > 0:
                prompt_parts.append(f"\nContext Statistics: {metadata['total_documents']} documents with avg relevance {metadata['avg_relevance']:.3f}")

        # Conversation history for continuity
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]  # Last 3 exchanges
            history_text = "\n".join([f"{msg['role']}: {msg['content'][:200]}..." for msg in recent_history])
            prompt_parts.append(f"\nRecent Conversation:\n{history_text}")

        # User preferences and adaptation
        if self.user_preferences:
            style_hints = []
            if self.user_preferences.get('step_by_step', True):
                style_hints.append("provide step-by-step explanations")
            if self.user_preferences.get('preferred_examples', True):
                style_hints.append("include relevant examples")
            if self.user_preferences.get('source_citations', True):
                style_hints.append("cite sources when using provided context")

            if style_hints:
                prompt_parts.append(f"\nResponse Style: Please {', '.join(style_hints)}.")

        # Advanced reasoning framework
        prompt_parts.append("""
ADVANCED REASONING FRAMEWORK:
1. Analyze the user's query for intent, complexity, and context requirements
2. Use provided context strategically - synthesize rather than just quote
3. Apply chain-of-thought reasoning for complex problems
4. Consider multiple perspectives and potential edge cases
5. Provide actionable, specific guidance tailored to the user's needs
6. If uncertain, acknowledge limitations and suggest alternatives""")

        # The actual user query
        prompt_parts.append(f"\nUser Query: {message}")

        # Response instruction
        prompt_parts.append("\nPlease provide a comprehensive, well-reasoned response:")

        return "\n".join(prompt_parts)

    def _get_primary_ai_response(self, prompt: str) -> str:
        """Get response from primary AI with fallback chain."""
        try:
            # Try Gemini first (primary AI)
            if self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                return response.text

        except Exception as e:
            self.logger.warning(f"Gemini request failed: {e}")

        # Fallback to Claude
        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

        except Exception as e:
            self.logger.warning(f"Claude request failed: {e}")

        # Fallback to OpenAI
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    max_tokens=4000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

        except Exception as e:
            self.logger.warning(f"OpenAI request failed: {e}")

        return "I apologize, but I'm currently unable to process your request due to technical issues. Please try again later."

    def _enhance_response(self, response: str, original_query: str, context_data: Dict[str, Any] = None) -> str:
        """Apply post-processing enhancements to the AI response."""
        # Basic validation and cleanup
        if not response or len(response.strip()) < 10:
            return "I apologize, but I wasn't able to generate a sufficient response. Could you please rephrase your question?"

        enhanced_response = response.strip()

        # Add source citations if context was used
        if context_data and context_data.get('results') and 'context' in enhanced_response.lower():
            sources = []
            for result in context_data['results'][:3]:  # Top 3 sources
                filename = result.get('metadata', {}).get('filename', 'Unknown')
                if filename != 'Unknown':
                    sources.append(filename)

            if sources:
                enhanced_response += f"\n\n*Sources: {', '.join(sources)}*"

        # Add confidence indicator for complex queries
        if len(original_query.split()) > 10 or '?' in original_query:
            confidence_level = self._estimate_confidence(enhanced_response, context_data)
            if confidence_level < 0.8:
                enhanced_response += f"\n\n*Note: This is a complex topic. I recommend verifying this information with additional sources.*"

        return enhanced_response

    def _estimate_confidence(self, response: str, context_data: Dict[str, Any] = None) -> float:
        """Estimate confidence in the response based on context quality and response characteristics."""
        confidence = 0.7  # Base confidence

        # Boost confidence if good context was available
        if context_data:
            metadata = context_data.get('metadata', {})
            avg_relevance = metadata.get('avg_relevance', 0.0)
            num_docs = metadata.get('total_documents', 0)

            if num_docs > 0 and avg_relevance > 0.7:
                confidence += 0.2
            elif num_docs > 0 and avg_relevance > 0.5:
                confidence += 0.1

        # Reduce confidence for uncertain language
        uncertain_phrases = ['might', 'possibly', 'unclear', 'uncertain', 'not sure']
        if any(phrase in response.lower() for phrase in uncertain_phrases):
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _learn_from_interaction(self, query: str, response: str):
        """Learn from user interactions to improve future responses."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response_length': len(response),
            'query_type': self._classify_query_type(query)
        }

        # Store pattern for future optimization
        query_type = interaction['query_type']
        if query_type not in self.learning_patterns:
            self.learning_patterns[query_type] = []

        self.learning_patterns[query_type].append(interaction)

        # Keep only recent interactions to prevent memory growth
        for pattern_type in self.learning_patterns:
            if len(self.learning_patterns[pattern_type]) > 50:
                self.learning_patterns[pattern_type] = self.learning_patterns[pattern_type][-50:]

    def add_to_conversation(self, role: str, content: str):
        """Enhanced conversation history management."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "content_type": self._classify_content_type(content)
        })

        # Intelligent history management - keep important conversations longer
        if len(self.conversation_history) > 20:
            # Prioritize recent and important messages
            important_messages = [
                msg for msg in self.conversation_history[-10:]  # Always keep last 10
            ]

            # Add important older messages
            for msg in self.conversation_history[:-10]:
                if (msg.get('content_type') == 'instruction' or
                    len(msg.get('content', '')) > 200):
                    important_messages.append(msg)

            # Sort by timestamp and keep most recent
            important_messages.sort(key=lambda x: x['timestamp'])
            self.conversation_history = important_messages[-20:]

    def _classify_content_type(self, content: str) -> str:
        """Classify content type for intelligent history management."""
        content_lower = content.lower()

        if any(word in content_lower for word in ['please', 'can you', 'help me']):
            return 'instruction'
        elif len(content) > 500:
            return 'detailed_response'
        elif '?' in content:
            return 'question'
        else:
            return 'general'

    def format_response(self, response_content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format the agent response with enhanced metadata and structure.

        Args:
            response_content: The main response content
            metadata: Additional metadata about the response

        Returns:
            Formatted response dictionary
        """
        formatted_response = {
            "content": response_content,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "enhanced": True,
            "capabilities_used": [
                "enhanced_context_retrieval",
                "dynamic_prompt_optimization",
                "conversation_memory",
                "multi_ai_fallback"
            ]
        }

        # Add metadata if provided
        if metadata:
            formatted_response["metadata"] = metadata
        else:
            formatted_response["metadata"] = {"type": "enhanced_response"}

        # Add conversation context info
        formatted_response["conversation_length"] = len(self.conversation_history)

        # Add confidence estimation
        formatted_response["confidence"] = self._estimate_confidence(response_content, metadata)

        return formatted_response

    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query and return enhanced response.

        Args:
            query: User query
            context: Additional context for the query

        Returns:
            Enhanced agent response
        """
        pass