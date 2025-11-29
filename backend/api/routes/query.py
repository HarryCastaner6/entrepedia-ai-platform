"""
Query routes for AI agent interactions and knowledge base search.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from backend.agents.hyperenhanced_coach import HyperenhancedCoach
from backend.agents.hyperenhanced_strategist import HyperenhancedStrategist
from backend.agents.intelligent_agent_router import IntelligentAgentRouter
from backend.embeddings.embedding_generator import EmbeddingGenerator
from backend.embeddings.vector_store import VectorStore, global_vector_store
from backend.utils.logger import app_logger


router = APIRouter()

# Initialize hyperenhanced services
intelligent_router = IntelligentAgentRouter()
coach_agent = HyperenhancedCoach()
strategist_agent = HyperenhancedStrategist()
embedding_generator = EmbeddingGenerator()
vector_store = global_vector_store


# Enhanced Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    agent_type: Optional[str] = Field("auto", description="Type of agent to use (auto, coach, strategist, or multi)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences for response style")
    routing_strategy: Optional[str] = Field("intelligent", description="Routing strategy (intelligent, single, collaborative)")

class EnhancedQueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    routing_strategy: str = Field("intelligent", description="Auto-route with intelligent agent selection")
    response_style: Optional[str] = Field("balanced", description="Response style preference")
    complexity_preference: Optional[str] = Field("adaptive", description="Complexity handling preference")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum results to return")
    threshold: float = Field(0.7, description="Minimum similarity threshold")


class LearningPlanRequest(BaseModel):
    topic: str = Field(..., description="Subject to learn")
    level: str = Field("beginner", description="Current skill level")
    duration: str = Field("4 weeks", description="Desired timeline")


class GamePlanRequest(BaseModel):
    objective: str = Field(..., description="Learning objective")
    deadline: str = Field(..., description="Target completion date")
    resources: Optional[Dict[str, Any]] = Field(None, description="Available resources")


@router.post("/ask")
async def ask_agent(request: QueryRequest) -> Dict[str, Any]:
    """
    Ask an AI agent a question with hyperenhanced capabilities and intelligent routing.
    """
    try:
        app_logger.info(f"Processing hyperenhanced query: {request.query[:100]}...")

        # Use intelligent routing for auto and multi agent types
        if request.agent_type.lower() in ["auto", "multi", "intelligent"]:
            response = intelligent_router.route_query(
                query=request.query,
                context=request.context,
                user_preferences=request.user_preferences
            )
            return {
                "success": True,
                "response": response,
                "routing_used": "intelligent",
                "hyperenhanced": True
            }

        # Direct agent routing for specific requests
        elif request.agent_type.lower() == "coach":
            response = coach_agent.process_query(request.query, request.context)
        elif request.agent_type.lower() == "strategist":
            response = strategist_agent.process_query(request.query, request.context)
        else:
            # Default to intelligent routing for unknown types
            app_logger.warning(f"Unknown agent type '{request.agent_type}', using intelligent routing")
            response = intelligent_router.route_query(
                query=request.query,
                context=request.context,
                user_preferences=request.user_preferences
            )

        return {
            "success": True,
            "response": response,
            "agent_used": request.agent_type,
            "hyperenhanced": True
        }

    except Exception as e:
        app_logger.error(f"Hyperenhanced query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/hyperenhanced")
async def hyperenhanced_query(request: EnhancedQueryRequest) -> Dict[str, Any]:
    """
    Process query with full hyperenhanced capabilities including intelligent routing,
    multi-agent collaboration, and advanced context synthesis.
    """
    try:
        app_logger.info(f"Processing hyperenhanced query: {request.query[:100]}...")

        # Prepare user preferences from request
        user_preferences = {
            'response_style': request.response_style,
            'complexity_preference': request.complexity_preference
        }

        # Use intelligent router with full capabilities
        response = intelligent_router.route_query(
            query=request.query,
            context=request.context,
            user_preferences=user_preferences
        )

        return {
            "success": True,
            "response": response,
            "hyperenhanced": True,
            "routing_strategy": request.routing_strategy,
            "capabilities_used": [
                "intelligent_routing",
                "multi_agent_collaboration",
                "enhanced_context_retrieval",
                "dynamic_prompt_optimization",
                "conversation_memory",
                "response_synthesis"
            ]
        }

    except Exception as e:
        app_logger.error(f"Hyperenhanced query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Hyperenhanced processing failed: {str(e)}"
        )


@router.post("/search")
async def search_knowledge_base(request: KnowledgeSearchRequest) -> Dict[str, Any]:
    """
    Search the knowledge base for relevant information.
    """
    try:
        app_logger.info(f"Searching knowledge base: {request.query[:100]}...")

        # Generate embedding for search query
        query_embeddings = embedding_generator.generate_embeddings([request.query])
        if not query_embeddings:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")

        # Search vector store
        search_results = vector_store.search(
            query_embeddings[0]['vector'],
            k=request.limit
        )

        # Filter by threshold
        filtered_results = [
            result for result in search_results
            if result['score'] >= request.threshold
        ]

        return {
            "success": True,
            "query": request.query,
            "results": filtered_results,
            "total_found": len(search_results),
            "after_filtering": len(filtered_results)
        }

    except Exception as e:
        app_logger.error(f"Knowledge base search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/learning-plan")
async def create_learning_plan(request: LearningPlanRequest) -> Dict[str, Any]:
    """
    Create a personalized learning plan.
    """
    try:
        app_logger.info(f"Creating learning plan for: {request.topic}")

        response = coach_agent.create_learning_plan(
            topic=request.topic,
            user_level=request.level,
            duration=request.duration
        )

        return {
            "success": True,
            "learning_plan": response,
            "topic": request.topic,
            "level": request.level,
            "duration": request.duration
        }

    except Exception as e:
        app_logger.error(f"Learning plan creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Learning plan creation failed: {str(e)}"
        )


@router.post("/game-plan")
async def create_game_plan(request: GamePlanRequest) -> Dict[str, Any]:
    """
    Create a tactical game plan for achieving an objective.
    """
    try:
        app_logger.info(f"Creating game plan for: {request.objective}")

        response = strategist_agent.create_game_plan(
            objective=request.objective,
            deadline=request.deadline,
            resources=request.resources
        )

        return {
            "success": True,
            "game_plan": response,
            "objective": request.objective,
            "deadline": request.deadline
        }

    except Exception as e:
        app_logger.error(f"Game plan creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Game plan creation failed: {str(e)}"
        )


@router.post("/master-strategy")
async def create_master_strategy(
    goals: List[str],
    constraints: Optional[Dict[str, Any]] = None,
    timeline: str = "6 months"
) -> Dict[str, Any]:
    """
    Create a comprehensive master learning strategy.
    """
    try:
        app_logger.info(f"Creating master strategy for {len(goals)} goals")

        response = strategist_agent.create_master_strategy(
            goals=goals,
            constraints=constraints,
            timeline=timeline
        )

        return {
            "success": True,
            "master_strategy": response,
            "goals_count": len(goals),
            "timeline": timeline
        }

    except Exception as e:
        app_logger.error(f"Master strategy creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Master strategy creation failed: {str(e)}"
        )


@router.get("/agents")
async def list_available_agents() -> Dict[str, Any]:
    """
    List available AI agents and their capabilities.
    """
    return {
        "success": True,
        "agents": {
            "coach": {
                "name": "Coach Agent",
                "description": "Provides personalized learning guidance, motivation, and study plans",
                "capabilities": [
                    "Learning plan creation",
                    "Motivation and encouragement",
                    "Study technique recommendations",
                    "Progress tracking guidance"
                ]
            },
            "strategist": {
                "name": "Strategist Agent",
                "description": "Creates comprehensive learning strategies and game plans",
                "capabilities": [
                    "Master strategy development",
                    "Learning path optimization",
                    "Tactical game plans",
                    "Resource allocation planning"
                ]
            }
        }
    }