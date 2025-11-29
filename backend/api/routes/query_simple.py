"""
Simplified query routes for AI agent interactions.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.agents.simple_agents import SimpleCoachAgent, SimpleStrategistAgent
from backend.utils.logger import app_logger


router = APIRouter()

# Initialize agents
coach_agent = SimpleCoachAgent()
strategist_agent = SimpleStrategistAgent()


# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    agent_type: Optional[str] = Field("coach", description="Type of agent to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    include_knowledge_base: bool = Field(True, description="Search knowledge base")


class LearningPlanRequest(BaseModel):
    topic: str = Field(..., description="Subject to learn")
    level: str = Field("beginner", description="Current skill level")
    duration: str = Field("4 weeks", description="Desired timeline")


@router.post("/ask")
async def ask_agent(request: QueryRequest) -> Dict[str, Any]:
    """Ask an AI agent a question."""
    try:
        app_logger.info(f"Processing query: {request.query[:100]}...")

        # Route to appropriate agent
        if request.agent_type.lower() == "coach":
            response = coach_agent.process_query(request.query, request.context)
        elif request.agent_type.lower() == "strategist":
            response = strategist_agent.process_query(request.query, request.context)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown agent type: {request.agent_type}. Available: coach, strategist"
            )

        return {
            "success": True,
            "response": response,
            "knowledge_base_results": 0,  # Disabled in demo
            "agent_used": request.agent_type,
            "note": "Demo version - full AI integration available with API keys"
        }

    except Exception as e:
        app_logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/search")
async def search_knowledge_base(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search the knowledge base (demo version)."""
    app_logger.info(f"Demo: Knowledge base search for: {query[:100]}...")

    return {
        "success": True,
        "query": query,
        "results": [],
        "total_found": 0,
        "after_filtering": 0,
        "note": "Demo version - knowledge base search requires embeddings setup"
    }


@router.post("/learning-plan")
async def create_learning_plan(request: LearningPlanRequest) -> Dict[str, Any]:
    """Create a personalized learning plan."""
    try:
        app_logger.info(f"Creating learning plan for: {request.topic}")

        # Generate learning plan response
        plan_query = f"Create a {request.duration} learning plan for {request.topic} at {request.level} level"
        response = coach_agent.process_query(plan_query)

        return {
            "success": True,
            "learning_plan": response,
            "topic": request.topic,
            "level": request.level,
            "duration": request.duration,
            "note": "Enhanced AI planning available with API keys"
        }

    except Exception as e:
        app_logger.error(f"Learning plan creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Learning plan creation failed: {str(e)}"
        )


@router.post("/game-plan")
async def create_game_plan(
    objective: str,
    deadline: str,
    resources: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a tactical game plan for achieving an objective."""
    try:
        app_logger.info(f"Creating game plan for: {objective}")

        # Generate game plan response
        plan_query = f"Create a strategic game plan to achieve: {objective} by {deadline}"
        response = strategist_agent.process_query(plan_query)

        return {
            "success": True,
            "game_plan": response,
            "objective": objective,
            "deadline": deadline,
            "note": "Advanced strategic planning available with full AI integration"
        }

    except Exception as e:
        app_logger.error(f"Game plan creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Game plan creation failed: {str(e)}"
        )


@router.get("/agents")
async def list_available_agents() -> Dict[str, Any]:
    """List available AI agents and their capabilities."""
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
                ],
                "status": "Demo mode - basic responses available"
            },
            "strategist": {
                "name": "Strategist Agent",
                "description": "Creates comprehensive learning strategies and game plans",
                "capabilities": [
                    "Master strategy development",
                    "Learning path optimization",
                    "Tactical game plans",
                    "Resource allocation planning"
                ],
                "status": "Demo mode - strategic frameworks available"
            }
        },
        "note": "Full AI capabilities available with Anthropic/OpenAI API keys"
    }