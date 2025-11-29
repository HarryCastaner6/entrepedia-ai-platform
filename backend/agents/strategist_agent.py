"""
Strategist agent for creating comprehensive learning strategies and game plans.
"""
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent


class StrategistAgent(BaseAgent):
    """AI agent focused on strategic planning and comprehensive learning strategies."""

    def __init__(self):
        system_prompt = """You are a strategic learning architect and educational planner. Your role is to:

1. Analyze complex learning objectives and break them into strategic components
2. Create comprehensive, multi-phase learning strategies
3. Design optimal learning paths considering prerequisites and dependencies
4. Develop resource allocation plans and timelines
5. Identify potential risks and mitigation strategies
6. Create measurable milestones and success metrics
7. Adapt strategies based on progress and changing requirements
8. Integrate multiple learning modalities and approaches

Think systematically and strategically. Consider the big picture while maintaining attention to critical details.
Focus on creating scalable, efficient, and effective learning strategies that maximize outcomes."""

        super().__init__("Strategist", system_prompt)

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process strategic planning queries.

        Args:
            query: User query about strategy or planning
            context: Additional context like available resources, constraints

        Returns:
            Strategic response with comprehensive plans
        """
        self.logger.info(f"Strategist agent processing query: {query[:100]}...")

        # Prepare enhanced prompt with strategic context
        enhanced_query = self._prepare_strategic_prompt(query, context)

        # Get response from primary AI (Gemini preferred for strategic thinking)
        response_content = self.chat(enhanced_query)

        # Add to conversation history
        self.add_to_conversation("user", query)
        self.add_to_conversation("strategist", response_content)

        # Extract strategic metadata
        metadata = self._extract_strategic_metadata(response_content, query)

        return self.format_response(response_content, metadata)

    def create_master_strategy(
        self,
        goals: List[str],
        constraints: Dict[str, Any] = None,
        timeline: str = "6 months"
    ) -> Dict[str, Any]:
        """
        Create a comprehensive master learning strategy.

        Args:
            goals: List of learning goals
            constraints: Resource/time constraints
            timeline: Overall timeline

        Returns:
            Comprehensive strategic plan
        """
        prompt = f"""Create a comprehensive master learning strategy:

GOALS:
{chr(10).join(f'- {goal}' for goal in goals)}

TIMELINE: {timeline}

CONSTRAINTS:
{self._format_constraints(constraints)}

Please provide:

1. STRATEGIC ANALYSIS
   - Goal interdependencies
   - Critical path identification
   - Resource requirements assessment
   - Risk analysis

2. PHASED APPROACH
   - Phase breakdown with objectives
   - Prerequisites and dependencies
   - Timeline allocation
   - Success criteria

3. RESOURCE STRATEGY
   - Learning materials and tools
   - Time allocation framework
   - Skill development priorities
   - Support system requirements

4. EXECUTION FRAMEWORK
   - Daily/weekly routines
   - Progress tracking methods
   - Milestone checkpoints
   - Adaptation mechanisms

5. CONTINGENCY PLANNING
   - Alternative pathways
   - Risk mitigation strategies
   - Pivot points and decision criteria
   - Recovery protocols

Format as a comprehensive strategic document with actionable components."""

        response_content = self.chat(prompt)

        metadata = {
            "type": "master_strategy",
            "goals": goals,
            "timeline": timeline,
            "scope": "comprehensive"
        }

        return self.format_response(response_content, metadata)

    def analyze_learning_path(self, subject: str, current_level: str, target_level: str) -> Dict[str, Any]:
        """
        Analyze and optimize learning path for a subject.

        Args:
            subject: Subject to analyze
            current_level: Current proficiency level
            target_level: Desired proficiency level

        Returns:
            Optimized learning path analysis
        """
        prompt = f"""Analyze the optimal learning path:

SUBJECT: {subject}
CURRENT LEVEL: {current_level}
TARGET LEVEL: {target_level}

Please provide:

1. GAP ANALYSIS
   - Skill gaps to bridge
   - Knowledge prerequisites
   - Competency requirements
   - Complexity assessment

2. OPTIMAL PATH DESIGN
   - Sequential learning stages
   - Parallel learning opportunities
   - Critical decision points
   - Efficiency optimizations

3. RESOURCE MAPPING
   - Best learning resources for each stage
   - Alternative resource options
   - Quality vs. time trade-offs
   - Cost-benefit analysis

4. MILESTONE STRATEGY
   - Incremental achievements
   - Validation checkpoints
   - Portfolio building opportunities
   - Skill demonstration methods

5. ACCELERATION OPPORTUNITIES
   - Fast-track options
   - Immersive experiences
   - Mentorship integration
   - Real-world application

Provide a data-driven, efficient learning path strategy."""

        response_content = self.chat(prompt)

        metadata = {
            "type": "learning_path_analysis",
            "subject": subject,
            "current_level": current_level,
            "target_level": target_level
        }

        return self.format_response(response_content, metadata)

    def create_game_plan(self, objective: str, deadline: str, resources: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a tactical game plan for achieving a specific objective.

        Args:
            objective: Specific learning objective
            deadline: Target completion date
            resources: Available resources

        Returns:
            Detailed tactical game plan
        """
        prompt = f"""Create a tactical game plan:

OBJECTIVE: {objective}
DEADLINE: {deadline}
AVAILABLE RESOURCES: {self._format_resources(resources)}

Provide a detailed game plan including:

1. TACTICAL BREAKDOWN
   - Sprint objectives (weekly/bi-weekly)
   - Daily action items
   - Priority rankings
   - Time boxing strategies

2. EXECUTION TACTICS
   - Study techniques for maximum retention
   - Practice methodologies
   - Review and reinforcement cycles
   - Progress validation methods

3. MOMENTUM MANAGEMENT
   - Quick wins for motivation
   - Challenging stretch goals
   - Energy management strategies
   - Burnout prevention

4. MONITORING & ADJUSTMENT
   - Progress tracking mechanisms
   - Performance indicators
   - Pivot triggers
   - Course correction protocols

5. FINAL PREPARATION
   - Consolidation strategies
   - Assessment preparation
   - Confidence building
   - Success validation

Create a practical, executable plan optimized for the given timeline."""

        response_content = self.chat(prompt)

        metadata = {
            "type": "tactical_game_plan",
            "objective": objective,
            "deadline": deadline,
            "urgency": "high" if "urgent" in objective.lower() else "normal"
        }

        return self.format_response(response_content, metadata)

    def _prepare_strategic_prompt(self, query: str, context: Dict[str, Any] = None) -> str:
        """Prepare enhanced prompt with strategic context."""
        enhanced_prompt = f"Strategic Query: {query}\n\n"

        # Add relevant document context first for maximum relevance
        document_context = self.get_relevant_context(query)
        if document_context:
            enhanced_prompt += f"{document_context}\n"

        if context:
            enhanced_prompt += "Strategic Context:\n"
            for key, value in context.items():
                enhanced_prompt += f"{key.replace('_', ' ').title()}: {value}\n"
            enhanced_prompt += "\n"

        # Add conversation context for strategic continuity
        conversation_context = self.get_conversation_context()
        if conversation_context:
            enhanced_prompt += f"Previous Strategic Discussion:\n{conversation_context}\n"

        enhanced_prompt += """Please provide strategic analysis that is:
- Comprehensive and systematic
- Actionable with clear steps
- Optimized for efficiency and outcomes
- Adaptable to changing circumstances
- Measurable with clear success criteria"""

        return enhanced_prompt

    def _extract_strategic_metadata(self, response: str, query: str) -> Dict[str, Any]:
        """Extract strategic metadata from response."""
        metadata = {"type": "strategic_guidance"}

        # Detect strategy type
        if "master" in query.lower() or "comprehensive" in query.lower():
            metadata["strategy_scope"] = "comprehensive"
        elif "game plan" in query.lower() or "tactical" in query.lower():
            metadata["strategy_scope"] = "tactical"
        else:
            metadata["strategy_scope"] = "focused"

        # Detect planning elements
        planning_keywords = ["phase", "milestone", "timeline", "deadline", "schedule"]
        if any(keyword in response.lower() for keyword in planning_keywords):
            metadata["has_timeline"] = True

        # Detect resource considerations
        resource_keywords = ["resource", "material", "tool", "budget", "time"]
        if any(keyword in response.lower() for keyword in resource_keywords):
            metadata["considers_resources"] = True

        # Detect risk analysis
        risk_keywords = ["risk", "challenge", "obstacle", "contingency", "backup"]
        if any(keyword in response.lower() for keyword in risk_keywords):
            metadata["includes_risk_analysis"] = True

        return metadata

    def _format_constraints(self, constraints: Dict[str, Any] = None) -> str:
        """Format constraints for prompt."""
        if not constraints:
            return "No specific constraints provided"

        formatted = []
        for key, value in constraints.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted)

    def _format_resources(self, resources: Dict[str, Any] = None) -> str:
        """Format resources for prompt."""
        if not resources:
            return "Standard learning resources assumed"

        formatted = []
        for key, value in resources.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted)