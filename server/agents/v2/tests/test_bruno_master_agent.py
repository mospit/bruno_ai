import pytest
import os
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import sys

# Add the agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bruno_master_agent import BrunoMasterAgentV2
from base_agent import AgentCard, AgentMessage

class TestBrunoMasterAgentV2:
    @pytest.fixture
    def mock_redis(self):
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture
    def agent(self, mock_redis):
        with patch('bruno_master_agent.redis.from_url', return_value=mock_redis):
            with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
                with patch('bruno_master_agent.genai.configure'):
                    with patch('bruno_master_agent.genai.GenerativeModel'):
                        agent = BrunoMasterAgentV2()
                        agent.redis_client = mock_redis
                        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_card.name == "Bruno Master Agent"
        assert agent.agent_card.version == "2.0.0"
        assert "intelligent_meal_orchestration" in [skill["id"] for skill in agent.agent_card.capabilities["skills"]]
        assert len(agent.specialized_agents) == 5
        assert "instacart_integration_agent" in agent.specialized_agents
        assert agent.user_preferences == {}
    
    @pytest.mark.asyncio
    async def test_meal_planning_orchestration(self, agent):
        """Test comprehensive meal planning orchestration"""
        task = {
            "action": "plan_meals",
            "message": "Plan meals for $75 this week for family of 4",
            "context": {
                "user_id": "test_user",
                "budget": 75.0,
                "family_size": 4,
                "timeframe": "week",
                "location": {"zip_code": "12345"}
            }
        }
        
        # Mock agent delegations
        mock_budget_result = {
            "target_budget": 75.0,
            "feasibility_score": 0.85,
            "optimization_score": 0.8,
            "recommendations": {"proteins": 18.75, "vegetables": 15.0}
        }
        
        mock_nutrition_result = {
            "daily_requirements": {"calories": 2000, "protein": 150},
            "family_requirements": {"total_calories": 8000, "total_protein": 600}
        }
        
        mock_instacart_result = {
            "current_deals": [
                {"product": "chicken breast", "discount": 0.20},
                {"product": "ground beef", "discount": 0.15}
            ]
        }
        
        mock_recipe_result = {
            "recipes": [
                {"name": "Grilled Chicken", "cost": 12.50, "servings": 4},
                {"name": "Beef Stir Fry", "cost": 15.00, "servings": 4}
            ],
            "nutrition_score": 0.85
        }
        
        mock_shopping_result = {
            "total_cost": 72.50,
            "estimated_savings": 5.50,
            "cost_efficiency": 0.9,
            "items": [
                {"name": "Chicken Breast", "price": 12.99, "quantity": 2}
            ]
        }
        
        with patch.object(agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.side_effect = [
                mock_budget_result,
                mock_nutrition_result,
                mock_instacart_result,
                mock_recipe_result,
                mock_shopping_result
            ]
            
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.side_effect = [
                    json.dumps({
                        "budget": 75.0,
                        "family_size": 4,
                        "intent": "meal_planning",
                        "timeframe": "week"
                    }),
                    "Hi! I'm Bruno and I'm excited to help you plan amazing meals for your family of 4 with your $75 budget!"
                ]
                
                with patch.object(agent, '_get_user_history') as mock_history:
                    mock_history.return_value = {"budget_history": [70, 75, 80]}
                    
                    result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert "bruno_response" in result
        assert "meal_plan" in result
        assert "shopping_experience" in result
        assert "coordination_details" in result
        
        # Check coordination details
        coordination = result["coordination_details"]
        assert coordination["parallel_execution"] is True
        assert len(coordination["agents_used"]) == 4
        assert "optimization_score" in coordination
    
    @pytest.mark.asyncio
    async def test_budget_coaching(self, agent):
        """Test personalized budget coaching"""
        task = {
            "action": "budget_coaching",
            "message": "Why am I overspending on groceries?",
            "context": {
                "user_id": "test_user",
                "current_budget": 100.0
            }
        }
        
        mock_budget_analysis = {
            "spending_statistics": {"average_spending": 120.0},
            "overspending_categories": ["proteins", "snacks"],
            "optimization_score": 0.7
        }
        
        mock_market_trends = {
            "seasonal_deals": ["winter vegetables", "root vegetables"],
            "price_trends": {"proteins": "increasing", "vegetables": "stable"}
        }
        
        with patch.object(agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.side_effect = [mock_budget_analysis, mock_market_trends]
            
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.side_effect = [
                    json.dumps({
                        "original_message": "Why am I overspending on groceries?",
                        "intent": "budget_coaching",
                        "budget": 100.0
                    }),
                    "I see you're spending about $20 more than your budget. Let me help you identify where those extra costs are coming from!"
                ]
                
                with patch.object(agent, '_get_user_history') as mock_history:
                    mock_history.return_value = {"budget_history": [110, 125, 115]}
                    
                    result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert "bruno_coaching" in result
        assert "budget_insights" in result
        assert "market_opportunities" in result
        assert "actionable_tips" in result
    
    @pytest.mark.asyncio
    async def test_real_time_adaptation(self, agent):
        """Test real-time meal plan adaptation"""
        task = {
            "action": "adapt_meal_plan",
            "message": "Update my meal plan, chicken prices went up",
            "context": {
                "current_meal_plan": {
                    "recipes": [
                        {"name": "Chicken Stir Fry", "ingredients": [{"name": "chicken breast"}]}
                    ]
                },
                "adaptation_reason": "price_increase",
                "budget": 75.0,
                "location": {"zip_code": "12345"}
            }
        }
        
        mock_current_pricing = {
            "products": [
                {"name": "chicken breast", "price": 8.99, "availability": True, "price_change": 0.25}
            ]
        }
        
        mock_adaptations_needed = {
            "changes_required": True,
            "affected_recipes": ["Chicken Stir Fry"],
            "suggested_substitutions": [{"from": "chicken breast", "to": "ground turkey"}]
        }
        
        mock_adapted_recipes = {
            "recipes": [
                {"name": "Turkey Stir Fry", "ingredients": [{"name": "ground turkey"}]}
            ]
        }
        
        mock_updated_shopping = {
            "total_cost": 68.50,
            "estimated_savings": 6.50
        }
        
        with patch.object(agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.side_effect = [mock_current_pricing, mock_adapted_recipes, mock_updated_shopping]
            
            with patch.object(agent, '_identify_needed_adaptations') as mock_adaptations:
                mock_adaptations.return_value = mock_adaptations_needed
                
                with patch.object(agent, 'call_gemini') as mock_gemini:
                    mock_gemini.side_effect = [
                        json.dumps({
                            "adaptation_reason": "price_increase",
                            "current_meal_plan": task["context"]["current_meal_plan"]
                        }),
                        "I noticed chicken prices went up, so I've updated your meal plan with ground turkey instead - you'll save $6.50!"
                    ]
                    
                    result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert result["adaptations_made"] is True
        assert "bruno_response" in result
        assert "updated_meal_plan" in result
        assert "updated_shopping" in result
        assert "adaptation_details" in result
    
    @pytest.mark.asyncio
    async def test_no_adaptation_needed(self, agent):
        """Test when no adaptation is needed"""
        task = {
            "action": "adapt_meal_plan",
            "message": "Check if my meal plan is still good",
            "context": {
                "current_meal_plan": {
                    "recipes": [{"name": "Pasta Primavera"}]
                }
            }
        }
        
        mock_adaptations_needed = {
            "changes_required": False,
            "reason": "prices_stable"
        }
        
        with patch.object(agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.return_value = {"products": []}
            
            with patch.object(agent, '_identify_needed_adaptations') as mock_adaptations:
                mock_adaptations.return_value = mock_adaptations_needed
                
                with patch.object(agent, 'call_gemini') as mock_gemini:
                    mock_gemini.side_effect = [
                        json.dumps({"intent": "check_meal_plan"}),
                        "Great news! Your current meal plan is still optimal and within budget."
                    ]
                    
                    result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert result["adaptations_made"] is False
        assert result["status"] == "meal_plan_still_optimal"
    
    @pytest.mark.asyncio
    async def test_instacart_shopping_experience(self, agent):
        """Test Instacart shopping experience creation"""
        task = {
            "action": "create_shopping_list",
            "message": "Create shopping list for pasta dinner",
            "context": {
                "items": ["pasta", "tomato sauce", "parmesan cheese"],
                "budget": 25.0,
                "location": {"zip_code": "12345"}
            }
        }
        
        mock_shopping_result = {
            "total_cost": 22.50,
            "estimated_savings": 2.50,
            "items": [
                {"name": "Pasta", "price": 1.99, "brand": "Barilla"},
                {"name": "Tomato Sauce", "price": 2.49, "brand": "Rao's"},
                {"name": "Parmesan Cheese", "price": 5.99, "brand": "Kraft"}
            ]
        }
        
        with patch.object(agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.return_value = mock_shopping_result
            
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.side_effect = [
                    json.dumps({
                        "items": ["pasta", "tomato sauce", "parmesan cheese"],
                        "budget": 25.0,
                        "intent": "shopping_list"
                    }),
                    "Perfect! I found everything for your pasta dinner for just $22.50 - you'll save $2.50!"
                ]
                
                result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert "bruno_response" in result
        assert "shopping_experience" in result
        assert result["instacart_ready"] is True
    
    @pytest.mark.asyncio
    async def test_general_bruno_interaction(self, agent):
        """Test general Bruno conversation"""
        task = {
            "message": "Hi Bruno, how are you today?",
            "context": {}
        }
        
        with patch.object(agent, 'call_gemini') as mock_gemini:
            mock_gemini.side_effect = [
                json.dumps({
                    "original_message": "Hi Bruno, how are you today?",
                    "intent": "greeting"
                }),
                "Hi there! I'm doing great and ready to help you with all your meal planning needs! What can I help you with today?"
            ]
            
            result = await agent.execute_task(task)
        
        assert result["success"] is True
        assert "bruno_response" in result
        assert result["interaction_type"] == "general_conversation"
    
    @pytest.mark.asyncio
    async def test_agent_delegation_success(self, agent):
        """Test successful agent delegation"""
        task = {"action": "test_action", "context": {"test": "data"}}
        
        mock_result = {"success": True, "result": {"test": "response"}}
        
        with patch.object(agent, 'send_message_to_agent') as mock_send:
            mock_send.return_value = mock_result
            
            result = await agent._delegate_to_agent("test_agent", task)
            
            assert result == {"test": "response"}
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_delegation_failure(self, agent):
        """Test agent delegation failure handling"""
        task = {"action": "test_action", "context": {"test": "data"}}
        
        with patch.object(agent, 'send_message_to_agent') as mock_send:
            mock_send.side_effect = Exception("Connection failed")
            
            result = await agent._delegate_to_agent("test_agent", task)
            
            assert "error" in result
            assert result["agent"] == "test_agent"
            assert "Connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_user_request_analysis(self, agent):
        """Test user request analysis"""
        message = "Plan meals for $100 this week for family of 4 with no dairy"
        context = {"user_id": "test_user"}
        
        mock_gemini_response = json.dumps({
            "budget": 100.0,
            "family_size": 4,
            "dietary_restrictions": ["no_dairy"],
            "timeframe": "week",
            "intent": "meal_planning"
        })
        
        with patch.object(agent, 'call_gemini') as mock_gemini:
            mock_gemini.return_value = mock_gemini_response
            
            result = await agent._analyze_user_request(message, context)
            
            assert result["budget"] == 100.0
            assert result["family_size"] == 4
            assert "no_dairy" in result["dietary_restrictions"]
            assert result["timeframe"] == "week"
            assert result["original_message"] == message
    
    @pytest.mark.asyncio
    async def test_user_request_analysis_json_fallback(self, agent):
        """Test user request analysis with JSON parsing failure"""
        message = "Plan meals for $50"
        context = {"budget": 50.0, "family_size": 2}
        
        with patch.object(agent, 'call_gemini') as mock_gemini:
            mock_gemini.return_value = "Invalid JSON response"
            
            result = await agent._analyze_user_request(message, context)
            
            assert result["original_message"] == message
            assert result["budget"] == 50.0
            assert result["family_size"] == 2
            assert result["intent"] == "general_meal_planning"
    
    @pytest.mark.asyncio
    async def test_bruno_response_generation(self, agent):
        """Test Bruno response generation"""
        request_analysis = {
            "original_message": "Plan meals for $75",
            "budget": 75.0,
            "family_size": 4
        }
        
        budget_analysis = {"feasibility_score": 0.85}
        nutrition_analysis = {"balanced": True}
        recipe_result = {"recipes": [{"name": "Chicken Stir Fry"}]}
        shopping_result = {"total_cost": 72.50, "estimated_savings": 2.50}
        instacart_result = {"current_deals": [{"product": "chicken", "discount": 0.20}]}
        
        mock_response = "I've created a fantastic meal plan for your family of 4 that comes in at $72.50, saving you $2.50!"
        
        with patch.object(agent, 'call_gemini') as mock_gemini:
            mock_gemini.return_value = mock_response
            
            result = await agent._generate_bruno_response(
                request_analysis, budget_analysis, nutrition_analysis, 
                recipe_result, shopping_result, instacart_result
            )
            
            assert result == mock_response
            mock_gemini.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_learning_from_interaction(self, agent):
        """Test learning from user interaction"""
        request_analysis = {
            "user_id": "test_user",
            "budget": 75.0,
            "family_size": 4,
            "dietary_restrictions": ["vegetarian"]
        }
        
        results = {
            "budget_analysis": {"accuracy_score": 0.9},
            "shopping_result": {"optimization_score": 0.85}
        }
        
        with patch.object(agent, 'cache_result') as mock_cache:
            await agent._learn_from_interaction(request_analysis, results)
            
            assert "test_user" in agent.user_preferences
            assert len(agent.user_preferences["test_user"]["interactions"]) == 1
            
            interaction = agent.user_preferences["test_user"]["interactions"][0]
            assert interaction["user_preferences"]["budget_range"] == 75.0
            assert interaction["user_preferences"]["family_size"] == 4
            assert "vegetarian" in interaction["user_preferences"]["dietary_restrictions"]
            
            mock_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_history_retrieval(self, agent):
        """Test user history retrieval"""
        user_id = "test_user"
        
        # Test with cached data
        mock_cached_history = {
            "frequently_bought": ["pasta", "sauce"],
            "budget_history": [80, 75, 85]
        }
        
        with patch.object(agent, 'get_cached_result') as mock_cache:
            mock_cache.return_value = mock_cached_history
            
            result = await agent._get_user_history(user_id)
            
            assert result == mock_cached_history
            mock_cache.assert_called_once_with(f"user_history_{user_id}")
    
    @pytest.mark.asyncio
    async def test_user_history_no_user_id(self, agent):
        """Test user history retrieval without user ID"""
        result = await agent._get_user_history(None)
        
        assert result["frequently_bought"] == []
        assert result["budget_history"] == []
    
    @pytest.mark.asyncio
    async def test_common_products_extraction(self, agent):
        """Test common products extraction based on dietary restrictions"""
        # Test base products
        result = await agent._extract_common_products([])
        assert "chicken" in result
        assert "ground_turkey" in result
        assert "pasta" in result
        
        # Test vegetarian restrictions
        result = await agent._extract_common_products(["vegetarian"])
        assert "chicken" not in result
        assert "ground_turkey" not in result
        assert "tofu" in result
        assert "beans" in result
        
        # Test gluten-free restrictions
        result = await agent._extract_common_products(["gluten_free"])
        assert "pasta" not in result
        assert "quinoa" in result
    
    def test_products_from_meal_plan_extraction(self, agent):
        """Test extracting products from meal plan"""
        meal_plan = {
            "recipes": [
                {
                    "name": "Pasta Primavera",
                    "ingredients": [
                        {"name": "pasta"},
                        {"name": "bell peppers"},
                        {"name": "onions"}
                    ]
                },
                {
                    "name": "Grilled Chicken",
                    "ingredients": [
                        {"name": "chicken breast"},
                        {"name": "olive oil"}
                    ]
                }
            ]
        }
        
        result = agent._extract_products_from_meal_plan(meal_plan)
        
        assert "pasta" in result
        assert "bell peppers" in result
        assert "chicken breast" in result
        assert len(result) == 5
    
    @pytest.mark.asyncio
    async def test_optimization_score_calculation(self, agent):
        """Test optimization score calculation"""
        budget_analysis = {"optimization_score": 0.8}
        recipe_result = {"nutrition_score": 0.85}
        shopping_result = {"cost_efficiency": 0.9}
        
        result = await agent._calculate_optimization_score(budget_analysis, recipe_result, shopping_result)
        
        expected = (0.8 + 0.85 + 0.9) / 3
        assert abs(result - expected) < 0.01
    
    @pytest.mark.asyncio
    async def test_actionable_tips_generation(self, agent):
        """Test actionable tips generation"""
        budget_analysis = {
            "overspending_categories": ["proteins", "snacks"]
        }
        market_trends = {
            "seasonal_deals": ["winter vegetables", "root vegetables"]
        }
        
        result = await agent._generate_actionable_tips(budget_analysis, market_trends)
        
        assert len(result) <= 5
        assert any("proteins" in tip for tip in result)
        assert any("winter vegetables" in tip for tip in result)
        assert any("store brands" in tip for tip in result)
    
    def test_processing_time_calculation(self, agent):
        """Test processing time calculation"""
        result = agent._calculate_total_processing_time()
        assert isinstance(result, float)
        assert result > 0
