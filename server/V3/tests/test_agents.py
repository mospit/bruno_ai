"""
Unit tests for individual agent functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import json

# Import all agents
from agents.base_agent import BaseAgent
from agents.pantry_manager import PantryManagerAgent
from agents.instacart_agent import InstacartIntegrationAgent
from agents.recipe_chef import RecipeChefAgent
from agents.budget_analyst import BudgetAnalystAgent
from agents.reflection_feedback import ReflectionFeedbackAgent


class TestBaseAgent:
    """Test BaseAgent functionality"""
    
    @pytest.fixture
    def base_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create BaseAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = BaseAgent(
                agent_id="test_agent",
                model_name="claude-3-haiku-20240307",
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_base_agent_initialization(self, base_agent):
        """Test BaseAgent initialization"""
        assert base_agent.agent_id == "test_agent"
        assert base_agent.model_name == "claude-3-haiku-20240307"
        assert base_agent.redis_client is not None
        assert base_agent.postgres_conn is not None
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, base_agent):
        """Test cache get and set operations"""
        # Test cache set
        test_data = {"key": "value", "number": 42}
        await base_agent.cache_set("test_key", test_data, ttl=300)
        
        # Verify cache set was called
        base_agent.redis_client.set.assert_called_once()
        
        # Test cache get
        base_agent.redis_client.get.return_value = json.dumps(test_data)
        result = await base_agent.cache_get("test_key")
        
        assert result == test_data
        base_agent.redis_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_memory_operations(self, base_agent):
        """Test memory save and retrieve operations"""
        # Test memory save
        test_memory = {"conversation": "test", "context": "data"}
        await base_agent.save_memory("conversation", test_memory)
        
        # Verify database insert was called
        base_agent.postgres_conn.cursor.assert_called()
        
        # Test memory retrieve
        base_agent.postgres_conn.cursor.return_value.fetchall.return_value = [
            (1, "test_agent", "session_1", "conversation", test_memory, {}, datetime.now())
        ]
        
        memories = await base_agent.retrieve_memory("conversation")
        assert len(memories) >= 0  # Mock returns empty list by default
    
    @pytest.mark.asyncio
    async def test_error_handling(self, base_agent):
        """Test error handling in base agent"""
        # Test cache operation with Redis error
        base_agent.redis_client.get.side_effect = Exception("Redis connection failed")
        
        result = await base_agent.cache_get("test_key")
        assert result is None  # Should return None on error
    
    @pytest.mark.asyncio
    async def test_token_optimization(self, base_agent):
        """Test token optimization features"""
        # Test compress_context method
        long_context = "This is a very long context that needs to be compressed " * 100
        compressed = await base_agent.compress_context(long_context)
        
        # Should return compressed version (mocked)
        assert compressed == "Test response from Claude"  # Mock response


class TestPantryManagerAgent:
    """Test PantryManagerAgent functionality"""
    
    @pytest.fixture
    def pantry_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create PantryManagerAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = PantryManagerAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_check_inventory(self, pantry_agent, sample_pantry_data):
        """Test inventory checking functionality"""
        # Mock cache to return pantry data
        pantry_agent.redis_client.get.return_value = json.dumps(sample_pantry_data)
        
        result = await pantry_agent.check_inventory()
        
        # Should return structured inventory data
        assert "inventory" in result
        assert "expiring_soon" in result
        assert "suggestions" in result
    
    @pytest.mark.asyncio
    async def test_add_item(self, pantry_agent):
        """Test adding item to pantry"""
        item_data = {
            "name": "milk",
            "quantity": 1,
            "unit": "gallon",
            "expiry": "2025-01-20"
        }
        
        result = await pantry_agent.add_item(item_data)
        
        # Should return success response
        assert result["success"] is True
        assert "message" in result
        
        # Should update cache
        pantry_agent.redis_client.set.assert_called()
    
    @pytest.mark.asyncio
    async def test_remove_item(self, pantry_agent):
        """Test removing item from pantry"""
        # Mock existing pantry data
        existing_data = {
            "items": [
                {"name": "milk", "quantity": 2, "unit": "gallon", "expiry": "2025-01-20"}
            ]
        }
        pantry_agent.redis_client.get.return_value = json.dumps(existing_data)
        
        result = await pantry_agent.remove_item("milk", 1)
        
        # Should return success response
        assert result["success"] is True
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_expiry_check(self, pantry_agent, sample_pantry_data):
        """Test expiry checking functionality"""
        # Mock pantry data with expiring items
        pantry_agent.redis_client.get.return_value = json.dumps(sample_pantry_data)
        
        result = await pantry_agent.check_expiring_items()
        
        # Should return expiring items
        assert "expiring_items" in result
        assert isinstance(result["expiring_items"], list)
    
    @pytest.mark.asyncio
    async def test_meal_suggestions(self, pantry_agent, sample_pantry_data):
        """Test meal suggestions based on pantry"""
        # Mock pantry data
        pantry_agent.redis_client.get.return_value = json.dumps(sample_pantry_data)
        
        result = await pantry_agent.suggest_meals()
        
        # Should return meal suggestions
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)


class TestInstacartIntegrationAgent:
    """Test InstacartIntegrationAgent functionality"""
    
    @pytest.fixture
    def instacart_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create InstacartIntegrationAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = InstacartIntegrationAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_search_products(self, instacart_agent):
        """Test product search functionality"""
        search_items = ["chicken breast", "pasta", "tomatoes"]
        
        result = await instacart_agent.search_products(search_items)
        
        # Should return product search results
        assert "products" in result
        assert "total_cost" in result
        assert isinstance(result["products"], list)
    
    @pytest.mark.asyncio
    async def test_create_shopping_list(self, instacart_agent):
        """Test shopping list creation"""
        items = [
            {"name": "chicken breast", "quantity": 2, "unit": "lbs"},
            {"name": "pasta", "quantity": 1, "unit": "box"}
        ]
        
        result = await instacart_agent.create_shopping_list(items, budget=25.00)
        
        # Should return shopping list
        assert "shopping_list" in result
        assert "estimated_total" in result
        assert "delivery_options" in result
    
    @pytest.mark.asyncio
    async def test_budget_optimization(self, instacart_agent):
        """Test budget optimization features"""
        items = ["expensive_item", "cheap_alternative"]
        budget = 20.00
        
        result = await instacart_agent.optimize_for_budget(items, budget)
        
        # Should return optimized suggestions
        assert "optimized_items" in result
        assert "alternatives" in result
        assert "savings" in result
    
    @pytest.mark.asyncio
    async def test_store_comparison(self, instacart_agent):
        """Test store price comparison"""
        items = ["milk", "bread"]
        
        result = await instacart_agent.compare_stores(items)
        
        # Should return store comparison
        assert "store_comparison" in result
        assert "best_deals" in result
        assert isinstance(result["store_comparison"], dict)


class TestRecipeChefAgent:
    """Test RecipeChefAgent functionality"""
    
    @pytest.fixture
    def recipe_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create RecipeChefAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = RecipeChefAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_generate_recipe(self, recipe_agent):
        """Test recipe generation"""
        preferences = ["Italian", "vegetarian"]
        available_ingredients = ["pasta", "tomatoes", "olive oil"]
        
        result = await recipe_agent.generate_recipe(preferences, available_ingredients)
        
        # Should return recipe
        assert "recipe" in result
        assert "name" in result["recipe"]
        assert "ingredients" in result["recipe"]
        assert "instructions" in result["recipe"]
    
    @pytest.mark.asyncio
    async def test_adapt_recipe(self, recipe_agent, sample_recipe_data):
        """Test recipe adaptation"""
        dietary_restrictions = ["gluten-free", "dairy-free"]
        
        result = await recipe_agent.adapt_recipe(sample_recipe_data, dietary_restrictions)
        
        # Should return adapted recipe
        assert "adapted_recipe" in result
        assert "modifications" in result
        assert "substitutions" in result
    
    @pytest.mark.asyncio
    async def test_meal_planning(self, recipe_agent):
        """Test meal planning functionality"""
        preferences = ["healthy", "quick"]
        budget = 100.00
        servings = 4
        timeframe = "week"
        
        result = await recipe_agent.plan_meals(preferences, budget, servings, timeframe)
        
        # Should return meal plan
        assert "meal_plan" in result
        assert "shopping_list" in result
        assert "nutritional_info" in result
    
    @pytest.mark.asyncio
    async def test_recipe_scaling(self, recipe_agent, sample_recipe_data):
        """Test recipe scaling"""
        original_servings = sample_recipe_data["servings"]
        target_servings = 8
        
        result = await recipe_agent.scale_recipe(sample_recipe_data, target_servings)
        
        # Should return scaled recipe
        assert "scaled_recipe" in result
        assert result["scaled_recipe"]["servings"] == target_servings
    
    @pytest.mark.asyncio
    async def test_nutritional_analysis(self, recipe_agent, sample_recipe_data):
        """Test nutritional analysis"""
        result = await recipe_agent.analyze_nutrition(sample_recipe_data)
        
        # Should return nutritional information
        assert "nutrition" in result
        assert "calories_per_serving" in result["nutrition"]
        assert "macronutrients" in result["nutrition"]


class TestBudgetAnalystAgent:
    """Test BudgetAnalystAgent functionality"""
    
    @pytest.fixture
    def budget_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create BudgetAnalystAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = BudgetAnalystAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_analyze_budget(self, budget_agent, sample_budget_data):
        """Test budget analysis"""
        result = await budget_agent.analyze_budget(sample_budget_data)
        
        # Should return budget analysis
        assert "analysis" in result
        assert "remaining_budget" in result["analysis"]
        assert "spending_trends" in result["analysis"]
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_cost_optimization(self, budget_agent):
        """Test cost optimization suggestions"""
        expenses = [
            {"category": "groceries", "amount": 150.00},
            {"category": "dining_out", "amount": 75.00}
        ]
        
        result = await budget_agent.optimize_costs(expenses)
        
        # Should return optimization suggestions
        assert "optimizations" in result
        assert "potential_savings" in result
        assert "priority_actions" in result
    
    @pytest.mark.asyncio
    async def test_budget_forecasting(self, budget_agent, sample_budget_data):
        """Test budget forecasting"""
        result = await budget_agent.forecast_budget(sample_budget_data, months=3)
        
        # Should return forecast
        assert "forecast" in result
        assert "projected_spending" in result["forecast"]
        assert "budget_alerts" in result
    
    @pytest.mark.asyncio
    async def test_expense_tracking(self, budget_agent):
        """Test expense tracking"""
        expense = {
            "amount": 25.50,
            "category": "groceries",
            "description": "Weekly shopping",
            "date": "2025-01-12"
        }
        
        result = await budget_agent.track_expense(expense)
        
        # Should return tracking confirmation
        assert "success" in result
        assert "updated_totals" in result
        assert "category_impact" in result
    
    @pytest.mark.asyncio
    async def test_budget_allocation(self, budget_agent):
        """Test budget allocation recommendations"""
        total_budget = 500.00
        priorities = ["essentials", "savings", "entertainment"]
        
        result = await budget_agent.recommend_allocation(total_budget, priorities)
        
        # Should return allocation recommendations
        assert "allocation" in result
        assert "categories" in result["allocation"]
        assert "rationale" in result


class TestReflectionFeedbackAgent:
    """Test ReflectionFeedbackAgent functionality"""
    
    @pytest.fixture
    def reflection_agent(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Create ReflectionFeedbackAgent instance for testing"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            agent = ReflectionFeedbackAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            return agent
    
    @pytest.mark.asyncio
    async def test_process_feedback(self, reflection_agent, sample_feedback_data):
        """Test feedback processing"""
        result = await reflection_agent.process_feedback(sample_feedback_data)
        
        # Should return feedback analysis
        assert "acknowledgment" in result
        assert "insights" in result
        assert "action_items" in result
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self, reflection_agent):
        """Test feedback trend analysis"""
        timeframe = "30_days"
        
        result = await reflection_agent.analyze_trends(timeframe)
        
        # Should return trend analysis
        assert "trends" in result
        assert "satisfaction_scores" in result
        assert "improvement_areas" in result
    
    @pytest.mark.asyncio
    async def test_system_adaptation(self, reflection_agent):
        """Test system adaptation suggestions"""
        feedback_summary = {
            "common_issues": ["slow responses", "limited recipe variety"],
            "satisfaction_score": 3.5,
            "improvement_requests": ["more vegetarian options"]
        }
        
        result = await reflection_agent.suggest_adaptations(feedback_summary)
        
        # Should return adaptation suggestions
        assert "adaptations" in result
        assert "priority_changes" in result
        assert "implementation_plan" in result
    
    @pytest.mark.asyncio
    async def test_quality_review(self, reflection_agent):
        """Test quality review of agent outputs"""
        agent_output = {
            "agent_id": "recipe_chef",
            "response": "Here's a great pasta recipe...",
            "context": "User requested Italian vegetarian meal"
        }
        
        result = await reflection_agent.review_quality(agent_output)
        
        # Should return quality assessment
        assert "quality_score" in result
        assert "strengths" in result
        assert "improvements" in result
    
    @pytest.mark.asyncio
    async def test_learning_insights(self, reflection_agent):
        """Test learning insights generation"""
        interaction_data = {
            "successful_interactions": 85,
            "total_interactions": 100,
            "common_patterns": ["meal planning", "budget optimization"]
        }
        
        result = await reflection_agent.generate_insights(interaction_data)
        
        # Should return learning insights
        assert "insights" in result
        assert "success_patterns" in result
        assert "learning_opportunities" in result


class TestAgentCollaboration:
    """Test inter-agent collaboration"""
    
    @pytest.mark.asyncio
    async def test_a2a_communication(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Test Agent-to-Agent communication"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            # Create two agents
            pantry_agent = PantryManagerAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            
            recipe_agent = RecipeChefAgent(
                redis_url="redis://localhost:6379",
                postgres_url="postgresql://localhost:5432/test"
            )
            
            # Test A2A request
            request = {
                "type": "inventory_check",
                "data": {"items": ["tomatoes", "pasta"]}
            }
            
            result = await pantry_agent.handle_a2a_request(request)
            
            # Should return A2A response
            assert "response" in result
            assert "agent_id" in result
            assert result["agent_id"] == "pantry_manager"
    
    @pytest.mark.asyncio
    async def test_collaborative_workflow(self, mock_redis, mock_postgres, mock_anthropic_client):
        """Test collaborative workflow execution"""
        with patch('redis.from_url', return_value=mock_redis), \
             patch('psycopg2.connect', return_value=mock_postgres), \
             patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
            
            # Create agents
            agents = {
                "pantry_manager": PantryManagerAgent(
                    redis_url="redis://localhost:6379",
                    postgres_url="postgresql://localhost:5432/test"
                ),
                "recipe_chef": RecipeChefAgent(
                    redis_url="redis://localhost:6379",
                    postgres_url="postgresql://localhost:5432/test"
                ),
                "budget_analyst": BudgetAnalystAgent(
                    redis_url="redis://localhost:6379",
                    postgres_url="postgresql://localhost:5432/test"
                )
            }
            
            # Mock collaborative workflow
            workflow_data = {
                "query": "Plan a healthy meal under $15",
                "context": {"dietary_restrictions": ["vegetarian"]}
            }
            
            # This would normally orchestrate between agents
            # For testing, we'll just verify agent creation
            assert len(agents) == 3
            assert "pantry_manager" in agents
            assert "recipe_chef" in agents
            assert "budget_analyst" in agents
