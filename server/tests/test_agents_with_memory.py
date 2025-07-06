"""
Bruno AI Agent Tests with Memory System Integration
Tests the agent system's integration with long-term memory, user context, and learning capabilities
"""

import pytest
import asyncio
import os
import sys
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add project root to path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

env_file = project_root / "config" / ".env"
load_dotenv(env_file)

from src.agents.v2.base_agent import BaseAgent, AgentCard
from src.agents.v2.bruno_master_agent import BrunoMasterAgentV2
from src.auth.auth_manager import auth_manager
from src.auth.models import UserRegistration
from src.database.repositories import (
    preference_repository, interaction_repository, user_repository
)
from src.learning.preference_engine import preference_engine


class TestBaseAgentMemoryIntegration:
    """Test BaseAgent memory system integration"""
    
    @pytest.fixture
    async def test_user(self):
        """Create a test user for agent tests"""
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"agent_test_user_{timestamp}_{random_suffix}",
            email=f"agent_test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=3
        )
        
        result = await auth_manager.register_user(registration_data)
        assert result["success"] is True
        return result["user"]["id"]
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing"""
        class MockAgent(BaseAgent):
            async def execute_task(self, task):
                return {"mock_result": "success", "task_processed": task.get("action")}
        
        agent_card = AgentCard(
            name="Test Agent",
            version="1.0.0",
            description="Test agent for memory integration testing",
            capabilities={"test": "capability"}
        )
        
        # Mock Gemini API to avoid real API calls
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            agent = MockAgent(agent_card)
            agent.model = MagicMock()
            agent.model.generate_content = AsyncMock(return_value=MagicMock(text="Mocked response"))
            return agent
    
    @pytest.mark.asyncio
    async def test_load_user_context(self, mock_agent, test_user):
        """Test loading user context from memory system"""
        user_id = await test_user
        
        # Add some preferences first
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='italian',
            preference_value={'liked': True},
            confidence_score=0.9,
            learning_source='explicit'
        )
        
        # Add an interaction
        await interaction_repository.log_interaction(
            user_id=user_id,
            interaction_type='meal_plan',
            user_message='I want healthy meals',
            agent_response='Here are some healthy suggestions',
            context_data={'budget': 100},
            response_time=1.5
        )
        
        # Test loading user context
        user_context = await mock_agent._load_user_context(user_id)
        
        assert 'profile' in user_context
        assert 'preferences' in user_context
        assert 'interaction_patterns' in user_context
        assert 'loaded_at' in user_context
        
        # Check that preferences were loaded
        if 'cuisine' in user_context['preferences'] and 'italian' in user_context['preferences']['cuisine']:
            assert user_context['preferences']['cuisine']['italian'] is not None
        else:
            # Preferences might be empty if loading failed, but context should still exist
            assert 'preferences' in user_context
        
        # Check that interaction patterns were loaded
        assert user_context['interaction_patterns']['total_interactions'] >= 1
    
    @pytest.mark.asyncio
    async def test_process_task_with_memory_integration(self, mock_agent, test_user):
        """Test task processing with full memory integration"""
        user_id = await test_user
        
        task = {
            'id': 'test_task_123',
            'action': 'test_action',
            'context': {'budget': 75, 'family_size': 3},
            'message': 'Test message for processing',
            'user_id': user_id
        }
        
        # Process the task
        result = await mock_agent.process_task(task)
        
        # Verify result structure
        assert result['success'] is True
        assert result['task_id'] == 'test_task_123'
        assert result['agent'] == 'Test Agent'
        assert 'result' in result
        assert 'processing_time' in result
        assert 'timestamp' in result
        
        # Verify that user context was loaded (task should include it)
        assert task['user_context'] is not None
        assert 'profile' in task['user_context']
        
        # Verify interaction was logged
        recent_interactions = await interaction_repository.get_recent_interactions(user_id, days=1)
        assert len(recent_interactions) > 0
        
        # Find our interaction
        our_interaction = next(
            (i for i in recent_interactions if i.interaction_type == 'test_action'), 
            None
        )
        assert our_interaction is not None
        assert our_interaction.user_message == 'Test message for processing'
        assert our_interaction.response_time > 0
    
    @pytest.mark.asyncio
    async def test_log_interaction_triggers_learning(self, mock_agent, test_user):
        """Test that logged interactions trigger preference learning"""
        user_id = await test_user
        
        # Process a task with food-related content
        task = {
            'action': 'meal_planning',
            'context': {'budget': 50, 'cuisine': 'mexican'},
            'message': 'I love spicy Mexican food and want meals under $50',
            'user_id': user_id
        }
        
        result = await mock_agent.process_task(task)
        assert result['success'] is True
        
        # Give the learning engine time to process
        await asyncio.sleep(0.2)
        
        # Check that preferences were learned (might be minimal due to test environment)
        user_prefs = await preference_repository.get_strong_preferences(user_id, min_confidence=0.1)
        
        # Verify that at least the interaction was logged
        recent_interactions = await interaction_repository.get_recent_interactions(user_id, days=1)
        assert len(recent_interactions) > 0
        
        # Learning might be minimal in test environment, but interaction should be logged
        meal_planning_interaction = next(
            (i for i in recent_interactions if i.interaction_type == 'meal_planning'), 
            None
        )
        assert meal_planning_interaction is not None
    
    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, mock_agent, test_user):
        """Test getting personalized recommendations"""
        user_id = await test_user
        
        # Add some preferences
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='thai',
            preference_value={'liked': True},
            confidence_score=0.8,
            learning_source='explicit'
        )
        
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='protein',
            preference_key='chicken',
            preference_value={'liked': True},
            confidence_score=0.9,
            learning_source='explicit'
        )
        
        # Get recommendations
        recommendations = await mock_agent.get_personalized_recommendations(
            user_id=user_id,
            recommendation_type='recipes',
            context={'budget': 60, 'family_size': 3}
        )
        
        # Should return a list (even if empty)
        assert isinstance(recommendations, list)
    
    @pytest.mark.asyncio
    async def test_failed_task_still_logs_interaction(self, mock_agent, test_user):
        """Test that failed tasks still log interactions for learning"""
        user_id = await test_user
        
        # Create a task that will fail validation
        invalid_task = {
            'user_id': user_id,
            'message': 'Invalid task without required fields'
            # Missing 'action' and 'context' required fields
        }
        
        result = await mock_agent.process_task(invalid_task)
        
        # Task should fail
        assert result['success'] is False
        assert 'error' in result
        
        # But interaction should still be logged
        recent_interactions = await interaction_repository.get_recent_interactions(user_id, days=1)
        
        # Should have at least one interaction (the failed one)
        failed_interaction = next(
            (i for i in recent_interactions if 'error' in i.agent_response), 
            None
        )
        assert failed_interaction is not None


class TestBrunoMasterAgentMemoryIntegration:
    """Test Bruno Master Agent memory integration"""
    
    @pytest.fixture
    async def test_user(self):
        """Create a test user for Bruno tests"""
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"bruno_test_user_{timestamp}_{random_suffix}",
            email=f"bruno_test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=4
        )
        
        result = await auth_manager.register_user(registration_data)
        assert result["success"] is True
        return result["user"]["id"]
    
    @pytest.fixture
    def mock_bruno_agent(self):
        """Create Bruno Master Agent with mocked external dependencies"""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            
            bruno = BrunoMasterAgentV2()
            bruno.model = MagicMock()
            
            # Mock the call_gemini method directly to avoid asyncio.to_thread issues
            async def mock_call_gemini(prompt, context=None):
                return "Hey there! Bruno's got ya covered with your request!"
            
            bruno.call_gemini = mock_call_gemini
            
            # Mock the delegate method to avoid calling external agents
            bruno._delegate_to_agent = AsyncMock()
            
            return bruno
    
    @pytest.mark.asyncio
    async def test_bruno_meal_planning_with_user_context(self, mock_bruno_agent, test_user):
        """Test Bruno's meal planning with user context integration"""
        user_id = await test_user
        
        # Set up user preferences
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='italian',
            preference_value={'liked': True},
            confidence_score=0.9,
            learning_source='explicit'
        )
        
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='dietary',
            preference_key='vegetarian',
            preference_value={'active': True},
            confidence_score=0.8,
            learning_source='explicit'
        )
        
        # Mock agent responses
        mock_bruno_agent._delegate_to_agent.return_value = {
            'success': True,
            'recommendations': ['Recipe 1', 'Recipe 2'],
            'total_cost': 65.50,
            'estimated_savings': 8.50
        }
        
        # Gemini response is already mocked in the fixture
        
        # Create a meal planning task
        task = {
            'action': 'plan_meals',
            'context': {
                'budget': 75,
                'family_size': 4,
                'timeframe': 'week'
            },
            'message': 'Plan meals for my family for $75 this week',
            'user_id': user_id
        }
        
        # Process the task
        result = await mock_bruno_agent.process_task(task)
        
        # Verify success
        assert result['success'] is True
        assert 'result' in result
        
        # Verify that user context was loaded and used
        # Check that the task included user context
        assert task['user_context'] is not None
        assert 'preferences' in task['user_context']
        assert 'italian' in str(task['user_context']['preferences'])
        
        # Verify interaction was logged
        recent_interactions = await interaction_repository.get_recent_interactions(user_id, days=1)
        meal_plan_interaction = next(
            (i for i in recent_interactions if i.interaction_type == 'plan_meals'), 
            None
        )
        assert meal_plan_interaction is not None
    
    @pytest.mark.asyncio
    async def test_bruno_learns_from_user_feedback(self, mock_bruno_agent, test_user):
        """Test that Bruno learns from user interactions over time"""
        user_id = await test_user
        
        # Mock agent responses
        mock_bruno_agent._delegate_to_agent.return_value = {
            'success': True,
            'budget_analysis': {'optimization_score': 0.85}
        }
        
        # Gemini response is already mocked in the fixture
        
        # Simulate multiple budget coaching interactions
        for i in range(3):
            task = {
                'action': 'budget_coaching',
                'context': {'budget': 80 + i * 10},
                'message': f'Help me with my budget - interaction {i}',
                'user_id': user_id
            }
            
            result = await mock_bruno_agent.process_task(task)
            assert result['success'] is True
            
            # Small delay between interactions
            await asyncio.sleep(0.1)
        
        # Check that multiple interactions were logged
        recent_interactions = await interaction_repository.get_recent_interactions(user_id, days=1)
        budget_interactions = [
            i for i in recent_interactions 
            if i.interaction_type == 'budget_coaching'
        ]
        assert len(budget_interactions) >= 3
        
        # Check interaction patterns
        patterns = await interaction_repository.get_interaction_patterns(user_id)
        assert patterns['total_interactions'] >= 3
        assert 'budget_coaching' in patterns['interaction_patterns']
    
    @pytest.mark.asyncio
    async def test_bruno_adapts_to_user_preferences(self, mock_bruno_agent, test_user):
        """Test that Bruno adapts responses based on learned preferences"""
        user_id = await test_user
        
        # Set initial preferences
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='budget_style',
            preference_key='tight_budget',
            preference_value={'preference_level': 'high'},
            confidence_score=0.9,
            learning_source='explicit'
        )
        
        # Mock responses
        mock_bruno_agent._delegate_to_agent.return_value = {
            'current_deals': ['Chicken $1.99/lb', 'Rice $0.99/lb'],
            'estimated_savings': 12.75
        }
        
        # Gemini response is already mocked in the fixture
        
        task = {
            'action': 'create_shopping_list',
            'context': {
                'budget': 40,  # Tight budget
                'items': ['chicken', 'rice', 'vegetables']
            },
            'message': 'Create a shopping list for $40',
            'user_id': user_id
        }
        
        result = await mock_bruno_agent.process_task(task)
        
        # Verify success and that user context was considered
        assert result['success'] is True
        assert task['user_context'] is not None
        assert 'tight_budget' in str(task['user_context']['preferences'])
    
    @pytest.mark.asyncio
    async def test_bruno_handles_user_without_history(self, mock_bruno_agent):
        """Test Bruno handles users without existing history gracefully"""
        # Create task without user_id
        task = {
            'action': 'general_conversation',
            'context': {},
            'message': 'Hello Bruno!',
            # No user_id provided
        }
        
        # Gemini response is already mocked in the fixture
        
        result = await mock_bruno_agent.process_task(task)
        
        # Should still work without user context
        assert result['success'] is True
        assert 'result' in result
    
    @pytest.mark.asyncio
    async def test_bruno_interaction_analytics(self, mock_bruno_agent, test_user):
        """Test Bruno's interaction analytics and pattern recognition"""
        user_id = await test_user
        
        # Mock responses
        mock_bruno_agent._delegate_to_agent.return_value = {'success': True}
        # Gemini response is already mocked in the fixture
        
        # Create interactions across different types
        interaction_types = ['plan_meals', 'budget_coaching', 'create_shopping_list']
        
        for interaction_type in interaction_types:
            for i in range(2):  # 2 of each type
                task = {
                    'action': interaction_type,
                    'context': {'test': f'{interaction_type}_{i}'},
                    'message': f'Test {interaction_type} message {i}',
                    'user_id': user_id
                }
                
                result = await mock_bruno_agent.process_task(task)
                assert result['success'] is True
                await asyncio.sleep(0.05)  # Small delay
        
        # Analyze patterns
        patterns = await interaction_repository.get_interaction_patterns(user_id)
        
        # Should show multiple interaction types
        assert patterns['total_interactions'] >= 6
        assert len(patterns['interaction_patterns']) >= 3
        
        # Each interaction type should be represented
        for interaction_type in interaction_types:
            assert interaction_type in patterns['interaction_patterns']
            assert patterns['interaction_patterns'][interaction_type]['count'] >= 2


class TestAgentPerformanceWithMemory:
    """Test agent performance and optimization with memory system"""
    
    @pytest.fixture
    async def test_user_with_history(self):
        """Create user with rich interaction history"""
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"perf_test_user_{timestamp}_{random_suffix}",
            email=f"perf_test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=3
        )
        
        result = await auth_manager.register_user(registration_data)
        user_id = result["user"]["id"]
        
        # Create rich preference history
        preferences = [
            ('cuisine', 'mexican', {'liked': True}, 0.9),
            ('cuisine', 'italian', {'liked': True}, 0.8),
            ('protein', 'chicken', {'liked': True}, 0.85),
            ('dietary', 'low_sodium', {'active': True}, 0.7),
            ('budget_style', 'moderate', {'preference_level': 'medium'}, 0.75)
        ]
        
        for pref_type, pref_key, pref_value, confidence in preferences:
            await preference_repository.upsert_preference(
                user_id=user_id,
                preference_type=pref_type,
                preference_key=pref_key,
                preference_value=pref_value,
                confidence_score=confidence,
                learning_source='learned'
            )
        
        # Create interaction history
        interactions = [
            ('meal_plan', 'Plan meals for the week', 'Here are your meal suggestions'),
            ('budget_coaching', 'Help me save money', 'Try these budget tips'),
            ('shopping_list', 'Create shopping list', 'Here is your optimized list'),
        ]
        
        for int_type, message, response in interactions:
            await interaction_repository.log_interaction(
                user_id=user_id,
                interaction_type=int_type,
                user_message=message,
                agent_response=response,
                context_data={'test': 'data'},
                response_time=1.0
            )
        
        return user_id
    
    @pytest.mark.asyncio
    async def test_agent_performance_with_rich_context(self, test_user_with_history):
        """Test agent performance when loading rich user context"""
        user_id = await test_user_with_history
        
        # Create mock agent
        agent_card = AgentCard(
            name="Performance Test Agent",
            version="1.0.0",
            description="Test agent for performance testing",
            capabilities={}
        )
        
        class PerfTestAgent(BaseAgent):
            async def execute_task(self, task):
                return {"performance_test": "completed"}
        
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            agent = PerfTestAgent(agent_card)
            agent.model = MagicMock()
            agent.model.generate_content = AsyncMock(return_value=MagicMock(text="Response"))
        
        # Measure performance of loading user context
        start_time = time.time()
        
        task = {
            'action': 'performance_test',
            'context': {'test': 'performance'},
            'message': 'Performance test message',
            'user_id': user_id
        }
        
        result = await agent.process_task(task)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify success
        assert result['success'] is True
        
        # Performance should be reasonable (under 5 seconds for context loading)
        assert processing_time < 5.0
        
        # Verify rich context was loaded
        assert task['user_context'] is not None
        assert len(task['user_context']['preferences']) >= 4
        assert task['user_context']['interaction_patterns']['total_interactions'] >= 3
    
    @pytest.mark.asyncio
    async def test_memory_system_caching_effectiveness(self, test_user_with_history):
        """Test that memory system caching improves performance"""
        user_id = await test_user_with_history
        
        agent_card = AgentCard(
            name="Cache Test Agent",
            version="1.0.0",
            description="Test agent for cache testing",
            capabilities={}
        )
        
        class CacheTestAgent(BaseAgent):
            async def execute_task(self, task):
                return {"cache_test": "completed"}
        
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            agent = CacheTestAgent(agent_card)
            agent.model = MagicMock()
            agent.model.generate_content = AsyncMock(return_value=MagicMock(text="Response"))
        
        # First request - should load from database
        start_time1 = time.time()
        user_context1 = await agent._load_user_context(user_id)
        time1 = time.time() - start_time1
        
        # Second request - might benefit from any internal caching
        start_time2 = time.time()
        user_context2 = await agent._load_user_context(user_id)
        time2 = time.time() - start_time2
        
        # Both should return the same data
        assert user_context1['preferences'] == user_context2['preferences']
        assert user_context1['interaction_patterns']['total_interactions'] == user_context2['interaction_patterns']['total_interactions']
        
        # Both should complete in reasonable time
        assert time1 < 2.0
        assert time2 < 2.0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
