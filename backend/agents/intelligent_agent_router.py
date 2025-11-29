"""
Intelligent Agent Router with dynamic agent selection, multi-agent collaboration,
and response fusion capabilities.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import json
import re

from backend.agents.hyperenhanced_strategist import HyperenhancedStrategist
from backend.agents.hyperenhanced_coach import HyperenhancedCoach
from backend.utils.logger import agent_logger


class IntelligentAgentRouter:
    """
    Advanced router that intelligently selects, coordinates, and fuses responses
    from multiple specialized AI agents.
    """

    def __init__(self):
        """Initialize the intelligent agent router."""
        self.logger = agent_logger

        # Initialize specialized agents
        self.agents = {
            'strategist': HyperenhancedStrategist(),
            'coach': HyperenhancedCoach()
        }

        # Agent capability matrix
        self.agent_capabilities = {
            'strategist': {
                'primary': ['strategic_planning', 'business_strategy', 'competitive_analysis', 'innovation_strategy'],
                'secondary': ['goal_setting', 'decision_making', 'risk_assessment', 'market_analysis'],
                'complexity_preference': 'high',
                'response_style': 'analytical'
            },
            'coach': {
                'primary': ['learning_guidance', 'skill_development', 'motivation', 'personalized_instruction'],
                'secondary': ['goal_setting', 'habit_formation', 'performance_improvement', 'feedback'],
                'complexity_preference': 'adaptive',
                'response_style': 'supportive'
            }
        }

        # Response fusion strategies
        self.fusion_strategies = ['collaborative', 'consensus', 'best_fit', 'comprehensive']

        # Query classification patterns
        self.query_patterns = {
            'strategic': [
                r'\b(strategy|strategic|plan|planning|business|competitive|market|innovation)\b',
                r'\b(analyze|assessment|framework|roadmap|vision)\b',
                r'\b(growth|expansion|optimization|transformation)\b'
            ],
            'learning': [
                r'\b(learn|learning|study|teach|understand|master|skill)\b',
                r'\b(how to|guide|tutorial|instruction|practice|improve)\b',
                r'\b(beginner|intermediate|advanced|level|progress)\b'
            ],
            'coaching': [
                r'\b(coach|coaching|mentor|guidance|help|support|advice)\b',
                r'\b(motivation|confidence|challenge|struggle|stuck)\b',
                r'\b(habit|routine|goal|objective|development)\b'
            ],
            'problem_solving': [
                r'\b(problem|issue|challenge|solution|solve|fix|resolve)\b',
                r'\b(difficult|complex|complicated|unclear|confused)\b'
            ]
        }

    def route_query(self, query: str, context: Dict[str, Any] = None,
                   user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Intelligently route query to appropriate agent(s) and return optimized response.

        Args:
            query: User query
            context: Additional context
            user_preferences: User preferences for routing and response style

        Returns:
            Optimized response with routing metadata
        """
        self.logger.info(f"Routing query: {query[:100]}...")

        # Analyze query characteristics
        query_analysis = self._analyze_query(query, context)

        # Determine optimal routing strategy
        routing_decision = self._make_routing_decision(query_analysis, user_preferences)

        # Execute routing strategy
        if routing_decision['strategy'] == 'single_agent':
            response = self._single_agent_response(query, routing_decision, context)
        elif routing_decision['strategy'] == 'multi_agent_collaborative':
            response = self._multi_agent_collaborative(query, routing_decision, context)
        elif routing_decision['strategy'] == 'multi_agent_consensus':
            response = self._multi_agent_consensus(query, routing_decision, context)
        else:  # comprehensive
            response = self._comprehensive_multi_agent(query, routing_decision, context)

        # Enhance with routing metadata
        response['routing_metadata'] = {
            'strategy_used': routing_decision['strategy'],
            'agents_involved': routing_decision['agents'],
            'confidence_scores': routing_decision['confidence_scores'],
            'query_analysis': query_analysis
        }

        return response

    def _analyze_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive query analysis for intelligent routing.

        Returns detailed analysis of query characteristics.
        """
        analysis = {}

        # Intent classification
        analysis['intents'] = self._classify_query_intents(query)

        # Complexity assessment
        analysis['complexity'] = self._assess_query_complexity(query)

        # Domain detection
        analysis['domains'] = self._detect_domains(query)

        # Urgency indicators
        analysis['urgency'] = self._assess_urgency(query)

        # Response preference hints
        analysis['response_preferences'] = self._infer_response_preferences(query)

        # Agent affinity scoring
        analysis['agent_affinities'] = self._calculate_agent_affinities(query, analysis)

        return analysis

    def _classify_query_intents(self, query: str) -> Dict[str, float]:
        """Classify query intents with confidence scores."""
        intents = {}

        for intent_type, patterns in self.query_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, query.lower()))
                score += matches * 0.3

            # Normalize and cap score
            intents[intent_type] = min(score, 1.0)

        # Ensure at least one intent has reasonable score
        if all(score < 0.1 for score in intents.values()):
            intents['general'] = 0.5

        return intents

    def _assess_query_complexity(self, query: str) -> Dict[str, Any]:
        """Assess various dimensions of query complexity."""
        words = query.split()
        sentences = query.split('.')

        complexity = {
            'lexical': min(len(words) / 20, 1.0),
            'syntactic': min(len(sentences) / 5, 1.0),
            'semantic': self._assess_semantic_complexity(query),
            'overall': 0.0
        }

        # Calculate overall complexity
        complexity['overall'] = (
            complexity['lexical'] * 0.3 +
            complexity['syntactic'] * 0.2 +
            complexity['semantic'] * 0.5
        )

        return complexity

    def _assess_semantic_complexity(self, query: str) -> float:
        """Assess semantic complexity based on abstract concepts and relationships."""
        complex_indicators = [
            'relationship', 'analyze', 'compare', 'evaluate', 'synthesize',
            'optimize', 'framework', 'methodology', 'paradigm', 'integrate'
        ]

        score = sum(1 for indicator in complex_indicators if indicator in query.lower())
        return min(score / len(complex_indicators), 1.0)

    def _detect_domains(self, query: str) -> List[str]:
        """Detect relevant domains and subject areas."""
        domains = []

        domain_keywords = {
            'business': ['business', 'company', 'startup', 'enterprise', 'commercial'],
            'technology': ['technology', 'software', 'AI', 'programming', 'digital'],
            'education': ['education', 'learning', 'teaching', 'academic', 'study'],
            'personal_development': ['personal', 'development', 'growth', 'improvement', 'self'],
            'leadership': ['leadership', 'management', 'team', 'organization', 'culture'],
            'marketing': ['marketing', 'brand', 'customer', 'market', 'promotion'],
            'finance': ['finance', 'money', 'investment', 'budget', 'financial']
        }

        query_lower = query.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains.append(domain)

        return domains if domains else ['general']

    def _assess_urgency(self, query: str) -> str:
        """Assess urgency level of the query."""
        urgency_indicators = {
            'high': ['urgent', 'immediately', 'asap', 'emergency', 'critical', 'deadline'],
            'medium': ['soon', 'quickly', 'priority', 'important', 'needed'],
            'low': ['eventually', 'when possible', 'future', 'someday', 'planning']
        }

        query_lower = query.lower()

        for level, indicators in urgency_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return level

        return 'medium'  # Default

    def _infer_response_preferences(self, query: str) -> Dict[str, bool]:
        """Infer preferred response characteristics from query."""
        preferences = {
            'detailed': any(word in query.lower() for word in ['detailed', 'comprehensive', 'thorough', 'deep']),
            'concise': any(word in query.lower() for word in ['brief', 'quick', 'short', 'summary']),
            'actionable': any(word in query.lower() for word in ['action', 'steps', 'how to', 'practical']),
            'examples': any(word in query.lower() for word in ['example', 'case study', 'instance', 'sample']),
            'analytical': any(word in query.lower() for word in ['analyze', 'data', 'metrics', 'evaluation'])
        }

        return preferences

    def _calculate_agent_affinities(self, query: str, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate affinity scores for each agent based on query analysis."""
        affinities = {}

        for agent_name, capabilities in self.agent_capabilities.items():
            score = 0.0

            # Primary capability match
            for capability in capabilities['primary']:
                if any(word in capability for word in query.lower().split()):
                    score += 0.4

            # Secondary capability match
            for capability in capabilities['secondary']:
                if any(word in capability for word in query.lower().split()):
                    score += 0.2

            # Intent alignment
            intents = analysis.get('intents', {})
            if agent_name == 'strategist' and intents.get('strategic', 0) > 0.3:
                score += intents['strategic'] * 0.5
            elif agent_name == 'coach' and (intents.get('learning', 0) > 0.3 or intents.get('coaching', 0) > 0.3):
                score += max(intents.get('learning', 0), intents.get('coaching', 0)) * 0.5

            # Complexity preference alignment
            complexity = analysis.get('complexity', {}).get('overall', 0.5)
            if capabilities['complexity_preference'] == 'high' and complexity > 0.7:
                score += 0.2
            elif capabilities['complexity_preference'] == 'adaptive':
                score += 0.1

            affinities[agent_name] = min(score, 1.0)

        return affinities

    def _make_routing_decision(self, analysis: Dict[str, Any],
                             user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make intelligent routing decision based on analysis and preferences.

        Returns routing strategy and agent selection.
        """
        affinities = analysis.get('agent_affinities', {})
        complexity = analysis.get('complexity', {}).get('overall', 0.5)
        intents = analysis.get('intents', {})

        # Determine if multi-agent approach is beneficial
        top_agents = sorted(affinities.items(), key=lambda x: x[1], reverse=True)

        decision = {
            'strategy': 'single_agent',
            'agents': [top_agents[0][0]] if top_agents else ['coach'],
            'confidence_scores': affinities,
            'reasoning': []
        }

        # Multi-agent decision logic
        if len(top_agents) >= 2:
            top_score = top_agents[0][1]
            second_score = top_agents[1][1]

            # If scores are close, consider collaboration
            if abs(top_score - second_score) < 0.3 and top_score > 0.4:
                if complexity > 0.6:
                    decision['strategy'] = 'comprehensive'
                    decision['agents'] = [agent for agent, score in top_agents[:2]]
                    decision['reasoning'].append('Complex query benefits from multiple perspectives')
                else:
                    decision['strategy'] = 'multi_agent_collaborative'
                    decision['agents'] = [agent for agent, score in top_agents[:2]]
                    decision['reasoning'].append('Similar agent capabilities, collaboration valuable')

            # If query has multiple strong intents
            elif sum(1 for score in intents.values() if score > 0.4) >= 2:
                decision['strategy'] = 'multi_agent_consensus'
                decision['agents'] = [agent for agent, score in top_agents[:2] if score > 0.3]
                decision['reasoning'].append('Multiple strong intents detected')

        # Single agent for clear cases
        if decision['strategy'] == 'single_agent' and top_agents:
            if top_agents[0][1] > 0.7:
                decision['reasoning'].append(f'Strong match for {top_agents[0][0]}')
            else:
                decision['reasoning'].append('Best available match')

        # User preference overrides
        if user_preferences:
            preferred_style = user_preferences.get('response_style', '')
            if preferred_style == 'comprehensive' and decision['strategy'] == 'single_agent':
                decision['strategy'] = 'comprehensive'
                decision['agents'] = list(self.agents.keys())
                decision['reasoning'].append('User prefers comprehensive responses')

        return decision

    def _single_agent_response(self, query: str, routing_decision: Dict[str, Any],
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get response from single best-matched agent."""
        agent_name = routing_decision['agents'][0]
        agent = self.agents[agent_name]

        self.logger.info(f"Single agent response from {agent_name}")

        result = agent.process_query(query, context)
        result['response_strategy'] = 'single_agent'
        result['primary_agent'] = agent_name

        return result

    def _multi_agent_collaborative(self, query: str, routing_decision: Dict[str, Any],
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get collaborative response from multiple agents."""
        agents_to_use = routing_decision['agents']

        self.logger.info(f"Multi-agent collaboration: {agents_to_use}")

        # Get responses from each agent
        agent_responses = {}
        for agent_name in agents_to_use:
            agent = self.agents[agent_name]
            response = agent.process_query(query, context)
            agent_responses[agent_name] = response

        # Collaborate and synthesize
        synthesized_response = self._synthesize_collaborative_response(
            query, agent_responses, routing_decision
        )

        return synthesized_response

    def _multi_agent_consensus(self, query: str, routing_decision: Dict[str, Any],
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get consensus response from multiple agents."""
        agents_to_use = routing_decision['agents']

        self.logger.info(f"Multi-agent consensus: {agents_to_use}")

        # Get responses from each agent
        agent_responses = {}
        for agent_name in agents_to_use:
            agent = self.agents[agent_name]
            response = agent.process_query(query, context)
            agent_responses[agent_name] = response

        # Build consensus
        consensus_response = self._build_consensus_response(
            query, agent_responses, routing_decision
        )

        return consensus_response

    def _comprehensive_multi_agent(self, query: str, routing_decision: Dict[str, Any],
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive response utilizing all relevant agents."""
        agents_to_use = routing_decision['agents']

        self.logger.info(f"Comprehensive multi-agent response: {agents_to_use}")

        # Get specialized responses
        agent_responses = {}
        for agent_name in agents_to_use:
            agent = self.agents[agent_name]
            # Customize query for each agent's specialization
            specialized_query = self._customize_query_for_agent(query, agent_name)
            response = agent.process_query(specialized_query, context)
            agent_responses[agent_name] = response

        # Create comprehensive synthesis
        comprehensive_response = self._create_comprehensive_synthesis(
            query, agent_responses, routing_decision
        )

        return comprehensive_response

    def _customize_query_for_agent(self, query: str, agent_name: str) -> str:
        """Customize query to leverage specific agent strengths."""
        if agent_name == 'strategist':
            return f"From a strategic planning perspective: {query}"
        elif agent_name == 'coach':
            return f"From a learning and development perspective: {query}"
        else:
            return query

    def _synthesize_collaborative_response(self, query: str, agent_responses: Dict[str, Dict],
                                         routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize collaborative response from multiple agents."""
        # Extract content from each agent
        contents = []
        all_metadata = {}

        for agent_name, response in agent_responses.items():
            contents.append(f"**{agent_name.title()} Perspective:**\n{response['content']}")
            # Merge metadata
            all_metadata.update(response.get('metadata', {}))

        # Create collaborative synthesis
        synthesized_content = f"""**Collaborative Response:**

{chr(10).join(contents)}

**Synthesis:**
Based on multiple expert perspectives, here's an integrated response that combines strategic and coaching insights for your query about: "{query}"

This collaborative approach ensures you get both the analytical depth and practical guidance needed for comprehensive understanding and effective action."""

        return {
            'content': synthesized_content,
            'response_strategy': 'multi_agent_collaborative',
            'agents_used': list(agent_responses.keys()),
            'metadata': {
                **all_metadata,
                'collaboration_type': 'synthesized',
                'agent_count': len(agent_responses)
            }
        }

    def _build_consensus_response(self, query: str, agent_responses: Dict[str, Dict],
                                routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus response from multiple agent perspectives."""
        # Find common themes and recommendations
        all_contents = [response['content'] for response in agent_responses.values()]

        # Simple consensus building (in production, this would be more sophisticated)
        consensus_prompt = f"""
        Build a consensus response from these expert perspectives on: "{query}"

        Perspectives:
        {chr(10).join([f"{i+1}. {content[:500]}..." for i, content in enumerate(all_contents)])}

        Create a unified response that:
        • Identifies common themes and agreements
        • Resolves any conflicting recommendations intelligently
        • Provides the most balanced and comprehensive guidance
        • Maintains the strengths of each perspective
        """

        # Use the strategist for synthesis (could be improved with a dedicated synthesis agent)
        strategist = self.agents['strategist']
        consensus_result = strategist.enhanced_chat(consensus_prompt)

        # Merge metadata from all agents
        all_metadata = {}
        for response in agent_responses.values():
            all_metadata.update(response.get('metadata', {}))

        return {
            'content': consensus_result,
            'response_strategy': 'multi_agent_consensus',
            'agents_used': list(agent_responses.keys()),
            'metadata': {
                **all_metadata,
                'consensus_method': 'intelligent_synthesis',
                'agent_count': len(agent_responses)
            }
        }

    def _create_comprehensive_synthesis(self, query: str, agent_responses: Dict[str, Dict],
                                      routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive synthesis utilizing all agent capabilities."""
        # Extract and organize responses by expertise area
        strategic_content = agent_responses.get('strategist', {}).get('content', '')
        coaching_content = agent_responses.get('coach', {}).get('content', '')

        comprehensive_synthesis = f"""**Comprehensive Expert Analysis**

**Strategic Perspective:**
{strategic_content}

**Learning & Development Perspective:**
{coaching_content}

**Integrated Recommendations:**
Based on both strategic planning and learning development expertise, here's your comprehensive action plan:

1. **Strategic Foundation**: Apply the strategic insights to establish clear direction and competitive advantage
2. **Learning Integration**: Use the coaching guidance to develop capabilities and drive implementation
3. **Synergistic Approach**: Combine strategic thinking with practical skill development for maximum impact

This comprehensive response leverages multiple expert perspectives to provide you with both the strategic clarity and practical guidance needed for success."""

        # Merge all metadata
        all_metadata = {}
        for response in agent_responses.values():
            all_metadata.update(response.get('metadata', {}))

        return {
            'content': comprehensive_synthesis,
            'response_strategy': 'comprehensive',
            'agents_used': list(agent_responses.keys()),
            'metadata': {
                **all_metadata,
                'synthesis_type': 'comprehensive',
                'integration_level': 'high',
                'agent_count': len(agent_responses)
            }
        }