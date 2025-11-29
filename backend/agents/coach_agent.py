"""
Coach agent for providing personalized learning guidance and motivation.
"""
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent


class CoachAgent(BaseAgent):
    """AI agent focused on coaching and learning guidance."""

    def __init__(self):
        system_prompt = """You are an expert learning coach and mentor. Your role is to:

1. Provide personalized learning guidance based on user goals and progress
2. Create structured learning plans with clear milestones
3. Offer motivation and encouragement
4. Suggest effective study techniques and strategies
5. Help overcome learning obstacles and challenges
6. Adapt teaching styles to different learning preferences
7. Track progress and celebrate achievements

Be supportive, encouraging, and practical. Focus on actionable advice and sustainable learning habits.
Break down complex topics into manageable steps. Always maintain a positive, growth-oriented mindset."""

        super().__init__("Coach", system_prompt)

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process coaching-related queries.

        Args:
            query: User query about learning or motivation
            context: Additional context like user progress, goals

        Returns:
            Coaching response with guidance and action items
        """
        self.logger.info(f"Coach agent processing query: {query[:100]}...")

        # Prepare enhanced prompt with context
        enhanced_query = self._prepare_coaching_prompt(query, context)

        # Get response from primary AI (Gemini preferred for coaching)
        response_content = self.chat(enhanced_query)

        # Add to conversation history
        self.add_to_conversation("user", query)
        self.add_to_conversation("coach", response_content)

        # Extract action items and learning plan if present
        metadata = self._extract_coaching_metadata(response_content)

        return self.format_response(response_content, metadata)

    def create_learning_plan(self, topic: str, user_level: str = "beginner", duration: str = "4 weeks") -> Dict[str, Any]:
        """
        Create a structured learning plan for a specific topic.

        Args:
            topic: Subject to learn
            user_level: Current skill level (beginner, intermediate, advanced)
            duration: Desired timeline

        Returns:
            Detailed learning plan
        """
        prompt = f"""Create a comprehensive {duration} learning plan for: {topic}

User Level: {user_level}
Timeline: {duration}

Please include:
1. Learning objectives and milestones
2. Week-by-week breakdown
3. Recommended study time per day
4. Key concepts to master
5. Practical exercises and projects
6. Assessment methods
7. Resources and materials needed
8. Common challenges and how to overcome them

Format as a structured, actionable plan that's motivating and achievable."""

        response_content = self.chat(prompt)

        metadata = {
            "type": "learning_plan",
            "topic": topic,
            "level": user_level,
            "duration": duration
        }

        return self.format_response(response_content, metadata)

    def provide_motivation(self, challenge: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Provide motivation and encouragement for learning challenges.

        Args:
            challenge: Specific challenge or obstacle
            context: Additional context about the situation

        Returns:
            Motivational response with strategies
        """
        prompt = f"""The user is facing this learning challenge: {challenge}

Context: {context or 'Not provided'}

Please provide:
1. Empathetic acknowledgment of the challenge
2. Practical strategies to overcome it
3. Motivational perspective and encouragement
4. Similar success stories if relevant
5. Specific next steps they can take
6. Long-term mindset advice

Be supportive, realistic, and actionable. Focus on building confidence and resilience."""

        response_content = self.chat(prompt)

        metadata = {
            "type": "motivation",
            "challenge": challenge
        }

        return self.format_response(response_content, metadata)

    def _prepare_coaching_prompt(self, query: str, context: Dict[str, Any] = None) -> str:
        """Prepare enhanced prompt with coaching context."""
        enhanced_prompt = f"User Query: {query}\n\n"

        # Add relevant document context first
        document_context = self.get_relevant_context(query)
        if document_context:
            enhanced_prompt += f"{document_context}\n"

        if context:
            enhanced_prompt += "Additional Context:\n"
            if context.get("user_goals"):
                enhanced_prompt += f"User Goals: {context['user_goals']}\n"
            if context.get("progress"):
                enhanced_prompt += f"Current Progress: {context['progress']}\n"
            if context.get("learning_style"):
                enhanced_prompt += f"Learning Style: {context['learning_style']}\n"
            if context.get("available_time"):
                enhanced_prompt += f"Available Study Time: {context['available_time']}\n"
            enhanced_prompt += "\n"

        # Add conversation context
        conversation_context = self.get_conversation_context()
        if conversation_context:
            enhanced_prompt += f"Recent Conversation:\n{conversation_context}\n"

        enhanced_prompt += "Please provide coaching guidance that is personalized, practical, and encouraging."

        return enhanced_prompt

    def _extract_coaching_metadata(self, response: str) -> Dict[str, Any]:
        """Extract structured metadata from coaching response."""
        metadata = {"type": "coaching_guidance"}

        # Look for action items
        if "action" in response.lower() or "steps" in response.lower():
            metadata["has_action_items"] = True

        # Look for learning plan elements
        if "plan" in response.lower() or "schedule" in response.lower():
            metadata["has_learning_plan"] = True

        # Look for motivational elements
        if any(word in response.lower() for word in ["encourage", "motivat", "achieve", "success"]):
            metadata["is_motivational"] = True

        return metadata