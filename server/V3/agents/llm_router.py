"""
LLM Router System for Bruno AI V3.2
Dynamic LLM selection based on agent roles and task complexity
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"

@dataclass
class LLMConfig:
    """Configuration for each LLM provider"""
    provider: LLMProvider
    model: str
    cost_per_token: float
    avg_latency: float
    api_key_env: str
    max_tokens: int = 4000
    temperature: float = 0.7

@dataclass
class RoutingMetrics:
    """Metrics for LLM routing decisions"""
    provider_used: str
    model_used: str
    cost_estimate: float
    latency_estimate: float
    fallback_used: bool
    timestamp: datetime

class LLMRouter:
    """
    Intelligent LLM router that selects optimal provider based on agent role and task complexity
    """
    
    def __init__(self):
        self.logger = logging.getLogger("bruno.llm_router")
        self.routing_metrics = []
        
        # Define LLM configurations based on V3.2 specifications
        self.llm_configs = {
            # Gemini 2.5 Flash - Fast and cost-effective for simple tasks
            'gemini_flash': LLMConfig(
                provider=LLMProvider.GOOGLE,
                model="gemini-2.5-flash",
                cost_per_token=0.00015,  # $0.15 per 1M tokens
                avg_latency=0.3,  # 300ms average
                api_key_env="GOOGLE_API_KEY",
                max_tokens=8000
            ),
            
            # Claude 4 Sonnet - Strong reasoning and creative tasks
            'claude_sonnet': LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-5-sonnet-20241022",
                cost_per_token=0.003,  # $3 per 1M tokens
                avg_latency=1.5,  # 1.5s average
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=200000
            ),
            
            # GPT-4o - Versatile for financial analysis and complex reasoning
            'gpt4o': LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o",
                cost_per_token=0.005,  # $5 per 1M tokens
                avg_latency=2.0,  # 2s average
                api_key_env="OPENAI_API_KEY",
                max_tokens=128000
            ),
            
            # Claude Haiku - Fallback for fast, simple tasks
            'claude_haiku': LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-5-haiku-20241022",
                cost_per_token=0.0008,  # $0.8 per 1M tokens
                avg_latency=0.5,  # 500ms average
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=200000
            )
        }
        
        # Agent-to-LLM mapping based on V3.2 specifications
        self.agent_llm_mapping = {
            'pantry_manager': 'gemini_flash',
            'instacart_integration': 'gemini_flash',
            'recipe_chef': 'claude_sonnet',
            'budget_analyst': 'gpt4o',
            'reflection_feedback': 'claude_sonnet'
        }
        
        # Fallback hierarchy
        self.fallback_hierarchy = {
            'gemini_flash': 'claude_haiku',
            'claude_sonnet': 'claude_haiku',
            'gpt4o': 'claude_sonnet',
            'claude_haiku': None  # Last resort
        }
        
        self.logger.info("LLM Router initialized with multi-provider support")
    
    def select_llm_for_agent(self, agent_id: str, task_complexity: str = "medium") -> Tuple[str, LLMConfig]:
        """
        Select optimal LLM for an agent based on its role and task complexity
        
        Args:
            agent_id: The agent identifier
            task_complexity: Task complexity level (simple, medium, complex)
            
        Returns:
            Tuple of (model_string, LLMConfig)
        """
        # Get primary LLM for this agent
        primary_llm = self.agent_llm_mapping.get(agent_id, 'claude_haiku')
        
        # Adjust based on task complexity
        if task_complexity == "simple" and primary_llm == 'claude_sonnet':
            # Use faster model for simple tasks
            primary_llm = 'claude_haiku'
        elif task_complexity == "complex" and primary_llm == 'gemini_flash':
            # Use more powerful model for complex tasks
            primary_llm = 'claude_sonnet'
        
        config = self.llm_configs[primary_llm]
        
        # Check if API key is available
        if not self._check_api_key_availability(config):
            self.logger.warning(f"API key not available for {primary_llm}, using fallback")
            return self._get_fallback_llm(primary_llm)
        
        # Format model string for PydanticAI
        model_string = self._format_model_string(config)
        
        # Track routing decision
        self._track_routing_decision(agent_id, config, fallback_used=False)
        
        self.logger.info(f"Selected {model_string} for agent {agent_id} (complexity: {task_complexity})")
        return model_string, config
    
    def _format_model_string(self, config: LLMConfig) -> str:
        """Format model string for PydanticAI usage"""
        if config.provider == LLMProvider.ANTHROPIC:
            return f"anthropic:{config.model}"
        elif config.provider == LLMProvider.OPENAI:
            return f"openai:{config.model}"
        elif config.provider == LLMProvider.GOOGLE:
            return f"google:{config.model}"
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    def _check_api_key_availability(self, config: LLMConfig) -> bool:
        """Check if API key is available for the provider"""
        return bool(os.getenv(config.api_key_env))
    
    def _get_fallback_llm(self, primary_llm: str) -> Tuple[str, LLMConfig]:
        """Get fallback LLM if primary is unavailable"""
        fallback_llm = self.fallback_hierarchy.get(primary_llm)
        
        if fallback_llm is None:
            raise RuntimeError("No fallback LLM available")
        
        config = self.llm_configs[fallback_llm]
        
        # Check fallback availability
        if not self._check_api_key_availability(config):
            # Try the next fallback
            return self._get_fallback_llm(fallback_llm)
        
        model_string = self._format_model_string(config)
        
        # Track fallback usage
        self._track_routing_decision("fallback", config, fallback_used=True)
        
        self.logger.warning(f"Using fallback LLM: {model_string}")
        return model_string, config
    
    def _track_routing_decision(self, agent_id: str, config: LLMConfig, fallback_used: bool = False):
        """Track routing decision metrics"""
        metrics = RoutingMetrics(
            provider_used=config.provider.value,
            model_used=config.model,
            cost_estimate=config.cost_per_token,
            latency_estimate=config.avg_latency,
            fallback_used=fallback_used,
            timestamp=datetime.now()
        )
        
        self.routing_metrics.append(metrics)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.routing_metrics) > 1000:
            self.routing_metrics = self.routing_metrics[-1000:]
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_metrics:
            return {"message": "No routing metrics available"}
        
        total_requests = len(self.routing_metrics)
        fallback_count = sum(1 for m in self.routing_metrics if m.fallback_used)
        
        provider_usage = {}
        for metric in self.routing_metrics:
            provider = metric.provider_used
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        avg_cost = sum(m.cost_estimate for m in self.routing_metrics) / total_requests
        avg_latency = sum(m.latency_estimate for m in self.routing_metrics) / total_requests
        
        return {
            "total_requests": total_requests,
            "fallback_usage_rate": fallback_count / total_requests,
            "provider_distribution": provider_usage,
            "average_cost_per_token": avg_cost,
            "average_latency_seconds": avg_latency,
            "last_updated": datetime.now().isoformat()
        }
    
    def estimate_cost(self, agent_id: str, estimated_tokens: int) -> float:
        """Estimate cost for a request"""
        _, config = self.select_llm_for_agent(agent_id)
        return config.cost_per_token * estimated_tokens
    
    def get_optimal_provider_for_task(self, task_type: str, estimated_tokens: int, 
                                     priority: str = "balanced") -> Tuple[str, LLMConfig]:
        """
        Get optimal provider for a specific task type
        
        Args:
            task_type: Type of task (fast, reasoning, financial, creative)
            estimated_tokens: Estimated token count
            priority: Priority (speed, cost, quality, balanced)
            
        Returns:
            Tuple of (model_string, LLMConfig)
        """
        if task_type == "fast" or priority == "speed":
            return self._format_model_string(self.llm_configs['gemini_flash']), self.llm_configs['gemini_flash']
        elif task_type == "financial":
            return self._format_model_string(self.llm_configs['gpt4o']), self.llm_configs['gpt4o']
        elif task_type == "reasoning" or task_type == "creative":
            return self._format_model_string(self.llm_configs['claude_sonnet']), self.llm_configs['claude_sonnet']
        elif priority == "cost":
            # Choose cheapest option
            cheapest = min(self.llm_configs.values(), key=lambda x: x.cost_per_token)
            return self._format_model_string(cheapest), cheapest
        else:
            # Balanced approach - use Claude Haiku as default
            return self._format_model_string(self.llm_configs['claude_haiku']), self.llm_configs['claude_haiku']


# Global router instance
_router_instance = None

def get_llm_router() -> LLMRouter:
    """Get global LLM router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance

def llm_router(agent_id: str, task_complexity: str = "medium") -> str:
    """
    Main router function for selecting LLM based on agent role
    
    Args:
        agent_id: The agent identifier
        task_complexity: Task complexity level
        
    Returns:
        Model string for PydanticAI
    """
    router = get_llm_router()
    model_string, _ = router.select_llm_for_agent(agent_id, task_complexity)
    return model_string
