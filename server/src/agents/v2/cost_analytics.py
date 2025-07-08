"""
Cost Analytics Service for Bruno AI
Monitors usage patterns and provides cost optimization insights
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import redis
from loguru import logger


class CostCategory(Enum):
    """Cost categories for tracking"""
    MODEL_USAGE = "model_usage"
    BATCH_PROCESSING = "batch_processing"
    CONTEXT_CACHING = "context_caching"
    API_CALLS = "api_calls"


@dataclass
class CostEvent:
    """Individual cost tracking event"""
    timestamp: datetime
    category: CostCategory
    model_type: str
    task_type: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    user_id: Optional[str] = None
    agent_name: Optional[str] = None
    was_cached: bool = False
    was_batched: bool = False


class CostAnalytics:
    """Cost analytics and optimization service"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        
        # Cost tracking configuration
        self.tracking_enabled = True
        self.retention_days = 30
        
        # Model pricing (per 1M tokens)
        self.model_pricing = {
            "gemini-2.5-flash-lite-preview-06-17": {
                "input": 0.10,
                "output": 0.40
            },
            "gemini-2.5-flash": {
                "input": 0.30,
                "output": 2.50
            },
            "gemini-2.5-pro": {
                "input": 1.25,
                "output": 10.00
            }
        }
        
        # Aggregated metrics
        self.daily_metrics = {}
        self.weekly_metrics = {}
        self.monthly_metrics = {}
        
        logger.info("CostAnalytics service initialized")
    
    async def track_cost_event(self, event: CostEvent):
        """Track a cost event"""
        if not self.tracking_enabled:
            return
        
        # Calculate estimated cost
        pricing = self.model_pricing.get(event.model_type, self.model_pricing["gemini-2.5-flash"])
        input_cost = (event.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (event.output_tokens / 1_000_000) * pricing["output"]
        event.estimated_cost = input_cost + output_cost
        
        # Apply batch processing discount (50% off)
        if event.was_batched:
            event.estimated_cost *= 0.5
        
        # Store event
        event_key = f"cost_event:{event.timestamp.isoformat()}:{id(event)}"
        await asyncio.to_thread(
            self.redis_client.setex,
            event_key,
            86400 * self.retention_days,  # TTL in seconds
            json.dumps(asdict(event), default=str)
        )
        
        # Update aggregated metrics
        await self._update_aggregated_metrics(event)
        
        logger.debug(f"Tracked cost event: ${event.estimated_cost:.4f} for {event.task_type}")
    
    async def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get cost summary for the specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        events = await self._get_events_in_range(start_date, end_date)
        
        if not events:
            return {"message": "No cost data available for the specified period"}
        
        # Calculate totals
        total_cost = sum(event.estimated_cost for event in events)
        total_events = len(events)
        
        # Model usage breakdown
        model_usage = {}
        for event in events:
            if event.model_type not in model_usage:
                model_usage[event.model_type] = {
                    "count": 0,
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            model_usage[event.model_type]["count"] += 1
            model_usage[event.model_type]["cost"] += event.estimated_cost
            model_usage[event.model_type]["input_tokens"] += event.input_tokens
            model_usage[event.model_type]["output_tokens"] += event.output_tokens
        
        # Task type breakdown
        task_breakdown = {}
        for event in events:
            if event.task_type not in task_breakdown:
                task_breakdown[event.task_type] = {
                    "count": 0,
                    "cost": 0.0,
                    "avg_cost": 0.0
                }
            task_breakdown[event.task_type]["count"] += 1
            task_breakdown[event.task_type]["cost"] += event.estimated_cost
        
        # Calculate averages
        for task_type in task_breakdown:
            task_breakdown[task_type]["avg_cost"] = (
                task_breakdown[task_type]["cost"] / task_breakdown[task_type]["count"]
            )
        
        # Optimization metrics
        cached_events = sum(1 for event in events if event.was_cached)
        batched_events = sum(1 for event in events if event.was_batched)
        
        cache_hit_rate = (cached_events / total_events) * 100 if total_events > 0 else 0
        batch_rate = (batched_events / total_events) * 100 if total_events > 0 else 0
        
        # Estimate savings
        estimated_savings_cache = cached_events * 0.15  # Approximate savings per cached request
        estimated_savings_batch = sum(
            event.estimated_cost for event in events if event.was_batched
        )  # Already discounted in tracking
        
        return {
            "period": f"{days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_cost": f"${total_cost:.2f}",
                "total_events": total_events,
                "average_cost_per_event": f"${(total_cost / total_events):.4f}" if total_events > 0 else "$0.00"
            },
            "model_usage": {
                model: {
                    "count": data["count"],
                    "cost": f"${data['cost']:.2f}",
                    "percentage": f"{(data['cost'] / total_cost * 100):.1f}%" if total_cost > 0 else "0%",
                    "tokens": f"{data['input_tokens']:,} in / {data['output_tokens']:,} out"
                }
                for model, data in model_usage.items()
            },
            "task_breakdown": {
                task: {
                    "count": data["count"],
                    "total_cost": f"${data['cost']:.2f}",
                    "avg_cost": f"${data['avg_cost']:.4f}"
                }
                for task, data in sorted(task_breakdown.items(), key=lambda x: x[1]["cost"], reverse=True)[:10]
            },
            "optimization_metrics": {
                "cache_hit_rate": f"{cache_hit_rate:.1f}%",
                "batch_processing_rate": f"{batch_rate:.1f}%",
                "estimated_savings": {
                    "from_caching": f"${estimated_savings_cache:.2f}",
                    "from_batching": f"${estimated_savings_batch:.2f}",
                    "total": f"${estimated_savings_cache + estimated_savings_batch:.2f}"
                }
            }
        }
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        events = await self._get_events_in_range(
            datetime.now() - timedelta(days=7),
            datetime.now()
        )
        
        recommendations = []
        
        if not events:
            return [{"type": "info", "message": "No data available for recommendations"}]
        
        # Analyze model usage patterns
        model_costs = {}
        task_model_usage = {}
        
        for event in events:
            if event.model_type not in model_costs:
                model_costs[event.model_type] = 0
            model_costs[event.model_type] += event.estimated_cost
            
            if event.task_type not in task_model_usage:
                task_model_usage[event.task_type] = {}
            if event.model_type not in task_model_usage[event.task_type]:
                task_model_usage[event.task_type][event.model_type] = 0
            task_model_usage[event.task_type][event.model_type] += 1
        
        # Recommendation 1: Model optimization
        total_cost = sum(model_costs.values())
        if "gemini-2.5-flash" in model_costs and "gemini-2.5-flash-lite-preview-06-17" in model_costs:
            flash_percentage = (model_costs["gemini-2.5-flash"] / total_cost) * 100
            if flash_percentage > 60:
                recommendations.append({
                    "type": "model_optimization",
                    "priority": "high",
                    "title": "Consider using Flash Lite for simple tasks",
                    "description": f"{flash_percentage:.1f}% of costs from Flash model. Could save ~70% on simple tasks with Flash Lite.",
                    "potential_savings": f"${model_costs['gemini-2.5-flash'] * 0.7 * 0.3:.2f}/week",
                    "action": "Review task complexity routing in ModelRouter"
                })
        
        # Recommendation 2: Batch processing
        non_batched_count = sum(1 for event in events if not event.was_batched)
        batchable_tasks = ["weekly_meal_planning", "bulk_recipe_generation", "budget_analysis"]
        batchable_events = [
            event for event in events 
            if event.task_type in batchable_tasks and not event.was_batched
        ]
        
        if len(batchable_events) > 5:
            potential_savings = sum(event.estimated_cost * 0.5 for event in batchable_events)
            recommendations.append({
                "type": "batch_processing",
                "priority": "medium",
                "title": "Enable batch processing for more tasks",
                "description": f"{len(batchable_events)} tasks could benefit from batch processing",
                "potential_savings": f"${potential_savings:.2f}/week",
                "action": "Submit eligible tasks to BatchProcessor"
            })
        
        # Recommendation 3: Context caching
        cache_miss_rate = sum(1 for event in events if not event.was_cached) / len(events) * 100
        if cache_miss_rate > 70:
            recommendations.append({
                "type": "context_caching",
                "priority": "medium",
                "title": "Improve context caching",
                "description": f"Cache miss rate is {cache_miss_rate:.1f}%. Better caching could reduce costs.",
                "potential_savings": f"${len(events) * 0.15 * (cache_miss_rate / 100):.2f}/week",
                "action": "Review caching strategy and TTL settings"
            })
        
        # Recommendation 4: Usage patterns
        peak_hours = {}
        for event in events:
            hour = event.timestamp.hour
            if hour not in peak_hours:
                peak_hours[hour] = 0
            peak_hours[hour] += 1
        
        if peak_hours:
            peak_hour = max(peak_hours, key=peak_hours.get)
            peak_usage = peak_hours[peak_hour]
            if peak_usage > len(events) * 0.3:  # More than 30% in one hour
                recommendations.append({
                    "type": "usage_patterns",
                    "priority": "low",
                    "title": "Consider load balancing",
                    "description": f"Peak usage at {peak_hour}:00 ({peak_usage} requests). Consider spreading load.",
                    "action": "Implement request queuing or encourage off-peak usage"
                })
        
        return recommendations
    
    async def _get_events_in_range(self, start_date: datetime, end_date: datetime) -> List[CostEvent]:
        """Get cost events within a date range"""
        # This is a simplified implementation
        # In production, you'd want more efficient querying
        events = []
        
        try:
            # Scan for cost events (simplified - in production use a time-series database)
            keys = await asyncio.to_thread(self.redis_client.keys, "cost_event:*")
            
            for key in keys:
                try:
                    event_data = await asyncio.to_thread(self.redis_client.get, key)
                    if event_data:
                        event_dict = json.loads(event_data)
                        event_timestamp = datetime.fromisoformat(event_dict["timestamp"])
                        
                        if start_date <= event_timestamp <= end_date:
                            # Convert back to CostEvent object
                            event = CostEvent(
                                timestamp=event_timestamp,
                                category=CostCategory(event_dict["category"]),
                                model_type=event_dict["model_type"],
                                task_type=event_dict["task_type"],
                                input_tokens=event_dict["input_tokens"],
                                output_tokens=event_dict["output_tokens"],
                                estimated_cost=event_dict["estimated_cost"],
                                user_id=event_dict.get("user_id"),
                                agent_name=event_dict.get("agent_name"),
                                was_cached=event_dict.get("was_cached", False),
                                was_batched=event_dict.get("was_batched", False)
                            )
                            events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse cost event {key}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to retrieve cost events: {e}")
        
        return events
    
    async def _update_aggregated_metrics(self, event: CostEvent):
        """Update aggregated metrics"""
        date_str = event.timestamp.date().isoformat()
        
        # Update daily metrics
        daily_key = f"daily_metrics:{date_str}"
        daily_data = await asyncio.to_thread(self.redis_client.get, daily_key)
        
        if daily_data:
            daily_metrics = json.loads(daily_data)
        else:
            daily_metrics = {
                "total_cost": 0.0,
                "total_events": 0,
                "model_breakdown": {},
                "task_breakdown": {}
            }
        
        # Update metrics
        daily_metrics["total_cost"] += event.estimated_cost
        daily_metrics["total_events"] += 1
        
        if event.model_type not in daily_metrics["model_breakdown"]:
            daily_metrics["model_breakdown"][event.model_type] = 0
        daily_metrics["model_breakdown"][event.model_type] += event.estimated_cost
        
        if event.task_type not in daily_metrics["task_breakdown"]:
            daily_metrics["task_breakdown"][event.task_type] = 0
        daily_metrics["task_breakdown"][event.task_type] += event.estimated_cost
        
        # Save updated metrics
        await asyncio.to_thread(
            self.redis_client.setex,
            daily_key,
            86400 * self.retention_days,
            json.dumps(daily_metrics)
        )
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get current pricing information"""
        return {
            "models": self.model_pricing,
            "optimization_strategies": {
                "model_selection": "Use Flash Lite for simple tasks (70% cost savings)",
                "batch_processing": "Process non-urgent tasks in batches (50% cost savings)",
                "context_caching": "Cache user context and preferences (reduces redundant calls)",
                "task_routing": "Smart routing based on complexity and urgency"
            },
            "best_practices": [
                "Use the simplest model that meets your requirements",
                "Batch non-urgent requests when possible",
                "Cache frequently accessed data",
                "Monitor usage patterns and adjust accordingly",
                "Consider request timing for better resource utilization"
            ]
        }


# Global cost analytics instance
cost_analytics = CostAnalytics()
