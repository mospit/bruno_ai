"""
Smart Model Router for Cost Optimization
Routes tasks to appropriate Gemini models based on complexity and requirements
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
import google.generativeai as genai
from loguru import logger


class TaskComplexity(Enum):
    """Task complexity levels for model selection"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ModelType(Enum):
    """Available Gemini models"""
    FLASH_LITE = "gemini-2.0-flash-lite"
    FLASH = "gemini-1.5-flash"
    PRO = "gemini-1.5-pro"


class ModelRouter:
    """Smart model selection for cost optimization"""
    
    def __init__(self):
        # Initialize Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize models
        self.models = {
            ModelType.FLASH_LITE: genai.GenerativeModel('gemini-2.0-flash-lite'),
            ModelType.FLASH: genai.GenerativeModel('gemini-1.5-flash'),
            ModelType.PRO: genai.GenerativeModel('gemini-1.5-pro')
        }
        
        # Task complexity routing rules
        self.task_routing = {
            # Simple tasks - use Flash Lite (70% cost savings)
            "pantry_update": TaskComplexity.SIMPLE,
            "inventory_check": TaskComplexity.SIMPLE,
            "simple_query": TaskComplexity.SIMPLE,
            "basic_math": TaskComplexity.SIMPLE,
            "data_validation": TaskComplexity.SIMPLE,
            "status_check": TaskComplexity.SIMPLE,
            "simple_formatting": TaskComplexity.SIMPLE,
            
            # Moderate tasks - use Flash
            "product_search": TaskComplexity.MODERATE,
            "price_comparison": TaskComplexity.MODERATE,
            "shopping_list_creation": TaskComplexity.MODERATE,
            "basic_meal_planning": TaskComplexity.MODERATE,
            "ingredient_substitution": TaskComplexity.MODERATE,
            "dietary_analysis": TaskComplexity.MODERATE,
            
            # Complex tasks - use Flash or Pro
            "advanced_meal_planning": TaskComplexity.COMPLEX,
            "budget_optimization": TaskComplexity.COMPLEX,
            "multi_store_optimization": TaskComplexity.COMPLEX,
            "complex_dietary_planning": TaskComplexity.COMPLEX,
            "nutritional_analysis": TaskComplexity.COMPLEX,
            "recipe_generation": TaskComplexity.COMPLEX,
        }
        
        # Model selection based on complexity
        self.complexity_to_model = {
            TaskComplexity.SIMPLE: ModelType.FLASH_LITE,
            TaskComplexity.MODERATE: ModelType.FLASH,
            TaskComplexity.COMPLEX: ModelType.FLASH  # Use Flash for most complex tasks
        }
        
        # Cost tracking
        self.cost_tracker = {
            "total_requests": 0,
            "flash_lite_requests": 0,
            "flash_requests": 0,
            "pro_requests": 0,
            "estimated_cost_saved": 0.0
        }
        
        logger.info("ModelRouter initialized with smart cost optimization")
    
    def get_model_for_task(self, task_type: str, context: Optional[Dict[str, Any]] = None) -> genai.GenerativeModel:
        """Get the appropriate model for a given task"""
        
        # Determine task complexity
        complexity = self._determine_complexity(task_type, context)
        
        # Select model based on complexity
        model_type = self.complexity_to_model[complexity]
        
        # Update cost tracking
        self._update_cost_tracking(model_type)
        
        logger.info(f"Selected {model_type.value} for task '{task_type}' (complexity: {complexity.value})")
        
        return self.models[model_type]
    
    def _determine_complexity(self, task_type: str, context: Optional[Dict[str, Any]] = None) -> TaskComplexity:
        """Determine task complexity based on type and context"""
        
        # Check predefined routing rules
        if task_type in self.task_routing:
            base_complexity = self.task_routing[task_type]
        else:
            # Default to moderate for unknown tasks
            base_complexity = TaskComplexity.MODERATE
            logger.warning(f"Unknown task type '{task_type}', defaulting to moderate complexity")
        
        # Context-based complexity adjustments
        if context:
            # Upgrade complexity for large datasets
            if self._has_large_context(context):
                if base_complexity == TaskComplexity.SIMPLE:
                    base_complexity = TaskComplexity.MODERATE
                elif base_complexity == TaskComplexity.MODERATE:
                    base_complexity = TaskComplexity.COMPLEX
            
            # Upgrade for multi-step operations
            if self._is_multi_step_operation(context):
                if base_complexity == TaskComplexity.SIMPLE:
                    base_complexity = TaskComplexity.MODERATE
        
        return base_complexity
    
    def _has_large_context(self, context: Dict[str, Any]) -> bool:
        """Check if context suggests large data processing"""
        large_context_indicators = [
            len(context.get('items', [])) > 20,
            len(context.get('products', [])) > 50,
            context.get('budget_analysis_required', False),
            context.get('multi_store_comparison', False)
        ]
        return any(large_context_indicators)
    
    def _is_multi_step_operation(self, context: Dict[str, Any]) -> bool:
        """Check if operation requires multiple steps"""
        multi_step_indicators = [
            context.get('requires_planning', False),
            context.get('optimization_required', False),
            len(context.get('steps', [])) > 1,
            context.get('chain_operations', False)
        ]
        return any(multi_step_indicators)
    
    def _update_cost_tracking(self, model_type: ModelType):
        """Update cost tracking metrics"""
        self.cost_tracker["total_requests"] += 1
        
        if model_type == ModelType.FLASH_LITE:
            self.cost_tracker["flash_lite_requests"] += 1
            # Estimate cost savings compared to using Flash
            self.cost_tracker["estimated_cost_saved"] += 0.20  # Approximate savings per request
        elif model_type == ModelType.FLASH:
            self.cost_tracker["flash_requests"] += 1
        elif model_type == ModelType.PRO:
            self.cost_tracker["pro_requests"] += 1
    
    def get_cost_metrics(self) -> Dict[str, Any]:
        """Get cost optimization metrics"""
        total = self.cost_tracker["total_requests"]
        if total == 0:
            return {"message": "No requests processed yet"}
        
        flash_lite_percentage = (self.cost_tracker["flash_lite_requests"] / total) * 100
        flash_percentage = (self.cost_tracker["flash_requests"] / total) * 100
        pro_percentage = (self.cost_tracker["pro_requests"] / total) * 100
        
        return {
            "total_requests": total,
            "model_distribution": {
                "flash_lite": f"{flash_lite_percentage:.1f}%",
                "flash": f"{flash_percentage:.1f}%",
                "pro": f"{pro_percentage:.1f}%"
            },
            "estimated_cost_saved": f"${self.cost_tracker['estimated_cost_saved']:.2f}",
            "optimization_effectiveness": f"{flash_lite_percentage:.1f}% of requests using cost-optimized model"
        }
    
    def register_custom_routing(self, task_type: str, complexity: TaskComplexity):
        """Register custom routing rule for specific task type"""
        self.task_routing[task_type] = complexity
        logger.info(f"Registered custom routing: {task_type} -> {complexity.value}")


# Global router instance
model_router = ModelRouter()
