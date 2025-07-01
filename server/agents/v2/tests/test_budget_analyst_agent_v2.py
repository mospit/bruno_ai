import pytest
import os
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import numpy as np
import sys

# Add the agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from budget_analyst_agent import BudgetAnalystAgentV2
from base_agent import AgentCard

class TestBudgetAnalystAgentV2:
    @pytest.fixture
    def mock_redis(self):
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture
    def agent(self, mock_redis):
        with patch('budget_analyst_agent.redis.from_url', return_value=mock_redis):
            with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
                with patch('budget_analyst_agent.genai.configure'):
                    with patch('budget_analyst_agent.genai.GenerativeModel'):
                        agent = BudgetAnalystAgentV2()
                        agent.redis_client = mock_redis
                        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_card.name == "Budget Analyst Agent"
        assert agent.agent_card.version == "2.0.0"
        assert "predictive_budget_analysis" in [skill["id"] for skill in agent.agent_card.capabilities["skills"]]
        assert agent.metrics["tasks_completed"] == 0
    
    @pytest.mark.asyncio
    async def test_analyze_budget_requirements(self, agent):
        """Test budget analysis functionality"""
        task = {
            "action": "analyze_budget",
            "context": {
                "target_budget": 500.0,
                "family_size": 4,
                "timeframe": "monthly",
                "historical_data": {
                    "budget_history": [450, 480, 520, 490, 510]
                }
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "target_budget" in result
        assert result["target_budget"] == 500.0
        assert "per_person_budget" in result
        assert result["per_person_budget"] == 125.0
        assert "feasibility_score" in result
        assert "usda_comparison" in result
        assert "optimization_opportunities" in result
    
    @pytest.mark.asyncio
    async def test_analyze_spending_patterns(self, agent):
        """Test spending pattern analysis"""
        task = {
            "action": "analyze_spending_patterns",
            "context": {
                "user_history": {
                    "budget_history": [400, 450, 480, 520, 490, 510, 530]
                },
                "current_budget": 500.0,
                "analysis_timeframe": "6_months"
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "spending_statistics" in result
        assert "spending_patterns" in result
        assert "budget_comparison" in result
        assert "seasonal_analysis" in result
        assert "optimization_score" in result
        
        # Check spending statistics
        stats = result["spending_statistics"]
        assert "average_spending" in stats
        assert "median_spending" in stats
        assert "spending_variance" in stats
        assert "trend" in stats
    
    @pytest.mark.asyncio
    async def test_predict_future_spending(self, agent):
        """Test spending prediction functionality"""
        task = {
            "action": "predict_future_spending",
            "context": {
                "historical_data": {
                    "budget_history": [400, 420, 450, 480, 500, 520]
                },
                "prediction_period": 3
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "predictions" in result
        assert "prediction_confidence" in result
        assert "trend_analysis" in result
        assert "recommendations" in result
        
        predictions = result["predictions"]
        assert "base_predictions" in predictions
        assert "seasonal_adjusted" in predictions
        assert "confidence_intervals" in predictions
    
    @pytest.mark.asyncio
    async def test_optimize_budget_allocation(self, agent):
        """Test budget allocation optimization"""
        task = {
            "action": "optimize_budget_allocation",
            "context": {
                "total_budget": 600.0,
                "categories": ["proteins", "vegetables", "grains", "dairy", "fruits"],
                "priorities": {
                    "proteins": 0.3,
                    "vegetables": 0.25,
                    "grains": 0.15,
                    "dairy": 0.15,
                    "fruits": 0.15
                }
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "original_allocation" in result
        assert "optimized_allocation" in result
        assert "value_scores" in result
        assert "optimization_summary" in result
        assert "recommendations" in result
        
        # Check that allocations sum to budget
        total_optimized = sum(result["optimized_allocation"].values())
        assert abs(total_optimized - 600.0) < 1.0  # Allow small rounding differences
    
    @pytest.mark.asyncio
    async def test_insufficient_data_handling(self, agent):
        """Test handling of insufficient historical data"""
        task = {
            "action": "analyze_spending_patterns",
            "context": {
                "user_history": {"budget_history": []},
                "current_budget": 500.0,
                "analysis_timeframe": "3_months"
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "error" in result
        assert "recommendations" in result
        assert "Insufficient historical data" in result["error"]
    
    @pytest.mark.asyncio
    async def test_prediction_insufficient_data(self, agent):
        """Test prediction with insufficient data"""
        task = {
            "action": "predict_future_spending",
            "context": {
                "historical_data": {"budget_history": [400, 450]},  # Only 2 data points
                "prediction_period": 3
            }
        }
        
        result = await agent.execute_task(task)
        
        assert "error" in result
        assert "recommendation" in result
        assert "Insufficient data for prediction" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_action_handling(self, agent):
        """Test handling of unknown actions"""
        task = {
            "action": "unknown_action",
            "context": {}
        }
        
        with pytest.raises(ValueError, match="Unknown action: unknown_action"):
            await agent.execute_task(task)
    
    @pytest.mark.asyncio
    async def test_usda_comparison(self, agent):
        """Test USDA guideline comparison"""
        result = await agent._compare_with_usda_guidelines(budget=800.0, family_size=4)
        
        assert "comparisons" in result
        assert "closest_plan" in result
        assert "budget_category" in result
        
        comparisons = result["comparisons"]
        assert "thrifty" in comparisons
        assert "low_cost" in comparisons
        assert "moderate" in comparisons
        assert "liberal" in comparisons
        
        # Check per-person budget calculation
        per_person = 800.0 / 4  # 200 per person
        for plan, data in comparisons.items():
            assert data["your_budget"] == per_person
    
    @pytest.mark.asyncio 
    async def test_spending_trend_calculation(self, agent):
        """Test spending trend calculation"""
        # Test increasing trend
        increasing_data = [100, 110, 120, 130, 140]
        trend = agent._calculate_spending_trend(increasing_data)
        assert trend > 0
        
        # Test decreasing trend
        decreasing_data = [140, 130, 120, 110, 100]
        trend = agent._calculate_spending_trend(decreasing_data)
        assert trend < 0
        
        # Test flat trend
        flat_data = [100, 100, 100, 100, 100]
        trend = agent._calculate_spending_trend(flat_data)
        assert abs(trend) < 0.01  # Very close to 0
    
    @pytest.mark.asyncio
    async def test_budget_feasibility_scoring(self, agent):
        """Test budget feasibility calculation"""
        # Test high budget (liberal plan)
        high_score = await agent._calculate_budget_feasibility(
            budget=1200.0, family_size=4, spending_analysis={"consistency_score": 0.9}
        )
        assert high_score > 0.9
        
        # Test low budget (below thrifty plan)
        low_score = await agent._calculate_budget_feasibility(
            budget=400.0, family_size=4, spending_analysis={"consistency_score": 0.5}
        )
        assert low_score < 0.5
    
    @pytest.mark.asyncio
    async def test_optimization_opportunities_identification(self, agent):
        """Test identification of optimization opportunities"""
        # High volatility scenario
        high_volatility_analysis = {
            "volatility": 100.0,  # High volatility for 500 budget
            "spending_trend": 0.08  # Increasing trend
        }
        
        opportunities = await agent._identify_optimization_opportunities(
            budget=500.0, spending_analysis=high_volatility_analysis
        )
        
        assert len(opportunities) > 0
        
        # Check for volatility reduction opportunity
        volatility_ops = [op for op in opportunities if op["type"] == "reduce_volatility"]
        assert len(volatility_ops) > 0
        
        # Check for inflation control opportunity
        inflation_ops = [op for op in opportunities if op["type"] == "control_inflation"]
        assert len(inflation_ops) > 0
        
        # Check standard opportunities
        meal_planning_ops = [op for op in opportunities if op["type"] == "meal_planning"]
        assert len(meal_planning_ops) > 0
    
    @pytest.mark.asyncio
    async def test_budget_breakdown_generation(self, agent):
        """Test budget breakdown generation"""
        breakdown = await agent._generate_budget_breakdown(budget=600.0, family_size=4)
        
        # Check all categories are present
        expected_categories = [
            "proteins", "vegetables", "grains_starches", 
            "dairy", "fruits", "pantry_staples", "snacks_treats"
        ]
        
        for category in expected_categories:
            assert category in breakdown
            assert breakdown[category] > 0
        
        # Check total equals budget (within rounding)
        total = sum(breakdown.values())
        assert abs(total - 600.0) < 1.0
        
        # Test single person adjustment
        single_breakdown = await agent._generate_budget_breakdown(budget=200.0, family_size=1)
        assert sum(single_breakdown.values()) <= 200.0 * 1.1  # Allow for adjustments
    
    @pytest.mark.asyncio
    async def test_health_check(self, agent):
        """Test agent health check"""
        health = await agent.health_check()
        
        assert "agent" in health
        assert health["agent"] == "Budget Analyst Agent"
        assert "version" in health
        assert "healthy" in health
        assert "last_activity" in health
        assert "metrics" in health
        assert "redis_connected" in health
    
    @pytest.mark.asyncio
    async def test_task_validation(self, agent):
        """Test task validation"""
        # Valid task
        valid_task = {
            "action": "analyze_budget",
            "context": {"target_budget": 500.0}
        }
        
        validation = await agent.validate_task(valid_task)
        assert validation["valid"] is True
        
        # Invalid task - missing action
        invalid_task = {
            "context": {"target_budget": 500.0}
        }
        
        validation = await agent.validate_task(invalid_task)
        assert validation["valid"] is False
        assert "Missing required field: action" in validation["error"]
        
        # Invalid task - missing context
        invalid_task2 = {
            "action": "analyze_budget"
        }
        
        validation = await agent.validate_task(invalid_task2)
        assert validation["valid"] is False
        assert "Missing required field: context" in validation["error"]

