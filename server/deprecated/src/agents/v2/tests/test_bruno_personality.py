import pytest
import json
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bruno_master_agent import BrunoMasterAgentV2

class TestBrunoPersonality:
    
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
    async def test_grocery_budget_advice(self, agent):
        """Test Bruno's advice for grocery budgeting in his characteristic style"""
        task = {
            "action": "plan_meals",
            "message": "Help me shop for groceries on a budget",
            "context": {"budget": 50.0}
        }
        
        # Mock the request analysis
        mock_analysis = {
            "budget": 50.0,
            "intent": "meal_planning",
            "original_message": "Help me shop for groceries on a budget"
        }
        
        # Expected Bruno response with characteristic language
        expected_response = "Hey there! Ya ain't gotta spend a fortune to eat like royalty. Here's how ya do it with $50 - I got ya back!"

        with patch.object(agent, '_analyze_user_request') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            with patch.object(agent, '_delegate_to_agent') as mock_delegate:
                mock_delegate.return_value = {"success": True}
                with patch.object(agent, 'call_gemini') as mock_gemini:
                    mock_gemini.return_value = expected_response
                    
                    result = await agent.execute_task(task)
                    
                    assert result["success"] is True
                    assert "bruno_response" in result
                    # Check for Bruno's characteristic language patterns
                    response = result["bruno_response"]
                    assert any(phrase in response for phrase in ["ya", "ain't", "gotta", "I got ya"])

    @pytest.mark.asyncio
    async def test_deal_spotting(self, agent):
        """Test Bruno's spotting of budget deals and his quick-witted insights"""
        task = {
            "message": "Spot me the best grocery deals",
            "context": {}
        }
        
        mock_analysis = {
            "intent": "general_conversation",
            "original_message": "Spot me the best grocery deals"
        }
        
        expected_deal_response = "Hold up, hold up - I just spotted chicken thighs for $1.99! That's what I'm talkin' about!"

        with patch.object(agent, '_analyze_user_request') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.return_value = expected_deal_response
                result = await agent.execute_task(task)
                
                assert result["success"] is True
                assert "bruno_response" in result
                # Check for Bruno's deal-hunting excitement
                response = result["bruno_response"]
                assert any(phrase in response for phrase in ["Hold up", "spotted", "what I'm talkin' about"])

    @pytest.mark.asyncio
    async def test_budget_warning(self, agent):
        """Test Bruno's warning when user approaches budget limits"""
        task = {
            "message": "Am I over budget?",
            "context": {"budget_used": 95.0, "budget": 100.0}
        }
        
        mock_analysis = {
            "intent": "budget_coaching",
            "original_message": "Am I over budget?",
            "budget": 100.0
        }
        
        expected_warning_response = "Whoa, whoa, whoa! Ya about to go over budget there, pal. Lemme find ya some alternatives before ya wallet starts cryin'."

        with patch.object(agent, '_analyze_user_request') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            with patch.object(agent, '_delegate_to_agent') as mock_delegate:
                mock_delegate.return_value = {"overspending_categories": ["proteins"]}
                with patch.object(agent, 'call_gemini') as mock_gemini:
                    mock_gemini.return_value = expected_warning_response
                    result = await agent.execute_task(task)
                    
                    assert result["success"] is True
                    assert "bruno_coaching" in result
                    # Check for Bruno's protective language
                    response = result["bruno_coaching"]
                    assert any(phrase in response for phrase in ["Whoa", "ya", "pal", "wallet"])

    @pytest.mark.asyncio
    async def test_celebrate_savings(self, agent):
        """Test how Bruno celebrates when the user saves money"""
        task = {
            "message": "I saved $10 on my grocery bill!",
            "context": {"savings": 10.0}
        }
        
        mock_analysis = {
            "intent": "general_conversation",
            "original_message": "I saved $10 on my grocery bill!"
        }
        
        expected_celebration_response = "Bada-bing! Look at that - ya came in $10 under budget! That's what I'm talkin' about! Ya makin' ya old pal Bruno proud!"

        with patch.object(agent, '_analyze_user_request') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.return_value = expected_celebration_response
                result = await agent.execute_task(task)
                
                assert result["success"] is True
                assert "bruno_response" in result
                # Check for Bruno's celebratory language
                response = result["bruno_response"]
                assert any(phrase in response for phrase in ["Bada-bing", "what I'm talkin' about", "Bruno proud"])

    @pytest.mark.asyncio
    async def test_accent_and_language(self, agent):
        """Test how Bruno uses his characteristic New York accent and language style"""
        task = {
            "message": "Hi Bruno!",
            "context": {}
        }
        
        mock_analysis = {
            "intent": "greeting",
            "original_message": "Hi Bruno!"
        }
        
        expected_accent_response = "Hey there! Bruno here, ya friendly neighborhood budget bear from Brooklyn. Listen, I been helpin' families eat good without goin' broke for years. Lemme show ya how it's done."

        with patch.object(agent, '_analyze_user_request') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            with patch.object(agent, 'call_gemini') as mock_gemini:
                mock_gemini.return_value = expected_accent_response
                result = await agent.execute_task(task)
                
                assert result["success"] is True
                assert "bruno_response" in result
                # Check for Bruno's characteristic Brooklyn accent and phrases
                response = result["bruno_response"]
                assert any(phrase in response for phrase in ["ya", "Brooklyn", "lemme", "goin'", "been"])

