"""
Bruno AI V2.0 Optimized Agent Architecture
Enhanced multi-agent system with streamlined coordination and Instacart integration
"""

from .base_agent import BaseAgent, AgentCard, AgentMessage
from .bruno_master_agent import BrunoMasterAgentV2
from .instacart_integration_agent import InstacartIntegrationAgentV2
from .budget_analyst_agent import BudgetAnalystAgentV2
from .a2a_gateway import BrunoA2AGatewayV2

__version__ = "2.0.0"
__all__ = [
    "BaseAgent",
    "AgentCard", 
    "AgentMessage",
    "BrunoMasterAgentV2",
    "InstacartIntegrationAgentV2",
    "BudgetAnalystAgentV2",
    "BrunoA2AGatewayV2"
]
