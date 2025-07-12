"""
Cost Optimization API Endpoints
Provides monitoring and control for cost optimization features
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from ..agents.v2.model_router import model_router
from ..agents.v2.batch_processor import batch_processor
from ..agents.v2.cost_analytics import cost_analytics, CostEvent, CostCategory

router = APIRouter(prefix="/api/v1/cost-optimization", tags=["Cost Optimization"])


@router.get("/summary")
async def get_cost_summary(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90)
) -> Dict[str, Any]:
    """Get cost summary and optimization metrics"""
    try:
        summary = await cost_analytics.get_cost_summary(days)
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost summary: {str(e)}")


@router.get("/recommendations")
async def get_optimization_recommendations() -> Dict[str, Any]:
    """Get cost optimization recommendations"""
    try:
        recommendations = await cost_analytics.get_optimization_recommendations()
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/model-metrics")
async def get_model_metrics() -> Dict[str, Any]:
    """Get model router performance metrics"""
    try:
        metrics = model_router.get_cost_metrics()
        return {
            "success": True,
            "model_routing": metrics,
            "routing_rules": {
                "simple_tasks": [
                    "pantry_update", "inventory_check", "simple_query", 
                    "basic_math", "data_validation", "status_check"
                ],
                "moderate_tasks": [
                    "product_search", "price_comparison", "shopping_list_creation",
                    "basic_meal_planning", "ingredient_substitution", "dietary_analysis"
                ],
                "complex_tasks": [
                    "advanced_meal_planning", "budget_optimization", "multi_store_optimization",
                    "complex_dietary_planning", "nutritional_analysis", "recipe_generation"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model metrics: {str(e)}")


@router.get("/batch-metrics")
async def get_batch_metrics() -> Dict[str, Any]:
    """Get batch processing performance metrics"""
    try:
        metrics = batch_processor.get_cost_metrics()
        return {
            "success": True,
            "batch_processing": metrics,
            "eligible_tasks": list(batch_processor.batch_eligible_tasks.keys()),
            "configuration": {
                "max_batch_size": batch_processor.batch_config["max_batch_size"],
                "processing_interval": f"{batch_processor.batch_config['processing_interval_seconds']}s",
                "batch_timeout": f"{batch_processor.batch_config['batch_timeout_seconds']}s"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch metrics: {str(e)}")


@router.post("/batch/submit")
async def submit_batch_task(
    task_type: str,
    payload: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Submit a task for batch processing"""
    try:
        result = await batch_processor.submit_task(task_type, payload, user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "task_submission": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit batch task: {str(e)}")


@router.get("/batch/status/{task_id}")
async def get_batch_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a batch task"""
    try:
        status = await batch_processor.get_task_status(task_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "success": True,
            "task_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.get("/pricing")
async def get_pricing_info() -> Dict[str, Any]:
    """Get current pricing information and optimization strategies"""
    try:
        pricing_info = cost_analytics.get_pricing_info()
        return {
            "success": True,
            "pricing": pricing_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pricing info: {str(e)}")


@router.post("/track-cost")
async def track_cost_event(
    model_type: str,
    task_type: str,
    input_tokens: int,
    output_tokens: int,
    user_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    was_cached: bool = False,
    was_batched: bool = False
) -> Dict[str, Any]:
    """Track a cost event for analytics"""
    try:
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.MODEL_USAGE,
            model_type=model_type,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=0.0,  # Will be calculated
            user_id=user_id,
            agent_name=agent_name,
            was_cached=was_cached,
            was_batched=was_batched
        )
        
        await cost_analytics.track_cost_event(event)
        
        return {
            "success": True,
            "message": "Cost event tracked successfully",
            "estimated_cost": f"${event.estimated_cost:.4f}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track cost event: {str(e)}")


@router.get("/dashboard")
async def get_optimization_dashboard() -> Dict[str, Any]:
    """Get comprehensive cost optimization dashboard data"""
    try:
        # Gather all metrics concurrently
        summary_task = cost_analytics.get_cost_summary(7)
        recommendations_task = cost_analytics.get_optimization_recommendations()
        model_metrics = model_router.get_cost_metrics()
        batch_metrics = batch_processor.get_cost_metrics()
        pricing_info = cost_analytics.get_pricing_info()
        
        # Wait for async operations
        summary, recommendations = await asyncio.gather(
            summary_task, recommendations_task
        )
        
        return {
            "success": True,
            "dashboard": {
                "cost_summary": summary,
                "recommendations": recommendations,
                "model_optimization": model_metrics,
                "batch_processing": batch_metrics,
                "pricing_info": pricing_info,
                "optimization_status": {
                    "model_routing_active": True,
                    "batch_processing_active": batch_processor._processing,
                    "cost_tracking_active": cost_analytics.tracking_enabled,
                    "context_caching_active": True
                }
            },
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.post("/configuration/model-routing")
async def update_model_routing(
    task_type: str,
    complexity: str  # "simple", "moderate", "complex"
) -> Dict[str, Any]:
    """Update model routing configuration"""
    try:
        from ..agents.v2.model_router import TaskComplexity
        
        complexity_map = {
            "simple": TaskComplexity.SIMPLE,
            "moderate": TaskComplexity.MODERATE,
            "complex": TaskComplexity.COMPLEX
        }
        
        if complexity not in complexity_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid complexity. Must be one of: {list(complexity_map.keys())}"
            )
        
        model_router.register_custom_routing(task_type, complexity_map[complexity])
        
        return {
            "success": True,
            "message": f"Updated routing for {task_type} to {complexity}",
            "configuration": {
                "task_type": task_type,
                "complexity": complexity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update model routing: {str(e)}")


@router.get("/health")
async def get_optimization_health() -> Dict[str, Any]:
    """Get health status of optimization services"""
    try:
        return {
            "success": True,
            "health": {
                "model_router": "healthy",
                "batch_processor": "healthy" if batch_processor._processing else "stopped",
                "cost_analytics": "healthy" if cost_analytics.tracking_enabled else "disabled",
                "redis_connection": "healthy" if cost_analytics.redis_client else "unavailable"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "health": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }
