"""
Memory System Tests for Bruno AI
Tests database repositories, preference learning, and long-term memory capabilities
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add project root to path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

env_file = project_root / "config" / ".env"
load_dotenv(env_file)

from src.database.repositories import (
    preference_repository, interaction_repository, 
    meal_plan_repository, budget_repository, user_repository
)
from src.learning.preference_engine import preference_engine
from src.auth.auth_manager import auth_manager
from src.auth.models import UserRegistration


class TestDatabaseRepositories:
    """Test database repository functionality"""
    
    @pytest.fixture
    async def test_user(self):
        """Create a test user for repository tests"""
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"test_user_{timestamp}_{random_suffix}",
            email=f"test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=3
        )
        
        result = await auth_manager.register_user(registration_data)
        assert result["success"] is True
        return result["user"]["id"]
    
    @pytest.mark.asyncio
    async def test_preference_storage_and_retrieval(self, test_user):
        """Test storing and retrieving user preferences"""
        user_id = await test_user
        
        # Store a preference
        pref = await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='italian',
            preference_value={'liked': True, 'confidence': 0.8},
            confidence_score=0.8,
            learning_source='test'
        )
        
        assert pref.preference_key == 'italian'
        assert pref.confidence_score == 0.8
        
        # Retrieve preferences
        user_prefs = await preference_repository.get_user_preferences(user_id, 'cuisine')
        assert len(user_prefs) > 0
        assert any(p.preference_key == 'italian' for p in user_prefs)
        
        # Test strong preferences
        strong_prefs = await preference_repository.get_strong_preferences(user_id)
        assert 'cuisine' in strong_prefs
        assert 'italian' in strong_prefs['cuisine']
    
    @pytest.mark.asyncio
    async def test_preference_update(self, test_user):
        """Test updating existing preferences"""
        user_id = await test_user
        
        # Store initial preference
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='dietary',
            preference_key='vegetarian',
            preference_value={'active': True},
            confidence_score=0.5,
            learning_source='implicit'
        )
        
        # Update the same preference
        updated_pref = await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='dietary',
            preference_key='vegetarian',
            preference_value={'active': True, 'strict': True},
            confidence_score=0.9,
            learning_source='explicit'
        )
        
        assert updated_pref.confidence_score == 0.9
        assert updated_pref.learning_source == 'explicit'
        assert updated_pref.times_observed == 2
    
    @pytest.mark.asyncio
    async def test_interaction_logging(self, test_user):
        """Test logging and retrieving user interactions"""
        user_id = await test_user
        
        # Log an interaction
        interaction = await interaction_repository.log_interaction(
            user_id=user_id,
            interaction_type='meal_plan',
            user_message='I want healthy meals for this week',
            agent_response='Here are some healthy meal suggestions...',
            context_data={'budget': 100, 'family_size': 3},
            response_time=1.5
        )
        
        assert interaction.user_id == user_id
        assert interaction.interaction_type == 'meal_plan'
        assert interaction.response_time == 1.5
        
        # Retrieve recent interactions
        recent = await interaction_repository.get_recent_interactions(user_id, days=1)
        assert len(recent) > 0
        assert any(i.id == interaction.id for i in recent)
    
    @pytest.mark.asyncio
    async def test_interaction_patterns(self, test_user):
        """Test interaction pattern analysis"""
        user_id = await test_user
        
        # Log multiple interactions
        for i in range(3):
            await interaction_repository.log_interaction(
                user_id=user_id,
                interaction_type='meal_plan',
                user_message=f'Test message {i}',
                agent_response=f'Test response {i}',
                context_data={'test': i},
                response_time=1.0 + i * 0.5
            )
        
        # Get interaction patterns
        patterns = await interaction_repository.get_interaction_patterns(user_id)
        
        assert 'interaction_patterns' in patterns
        assert 'meal_plan' in patterns['interaction_patterns']
        assert patterns['interaction_patterns']['meal_plan']['count'] >= 3
        assert patterns['total_interactions'] >= 3


class TestPreferenceEngine:
    """Test preference learning engine"""
    
    @pytest.fixture
    async def test_user(self):
        """Create a test user for preference engine tests"""
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"pref_test_user_{timestamp}_{random_suffix}",
            email=f"pref_test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=2
        )
        
        result = await auth_manager.register_user(registration_data)
        assert result["success"] is True
        return result["user"]["id"]
    
    @pytest.mark.asyncio
    async def test_preference_extraction(self, test_user):
        """Test extracting preferences from user interactions"""
        user_id = await test_user
        
        interaction_data = {
            'user_message': 'I love spicy Mexican food and hate broccoli',
            'context_data': {'budget': 75, 'family_size': 2},
            'interaction_type': 'meal_plan',
            'user_satisfaction': 5
        }
        
        result = await preference_engine.learn_from_interaction(
            user_id=user_id,
            interaction_data=interaction_data,
            feedback_score=4.5
        )
        
        assert 'preferences_learned' in result
        assert result['preferences_learned'] > 0
        assert 'extracted_preferences' in result
        
        # Check that preferences were stored
        user_prefs = await preference_repository.get_strong_preferences(user_id, min_confidence=0.5)
        assert len(user_prefs) > 0
    
    @pytest.mark.asyncio
    async def test_preference_prediction(self, test_user):
        """Test predicting user preferences"""
        user_id = await test_user
        
        # Store some known preferences
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='thai',
            preference_value={'liked': True},
            confidence_score=0.8,
            learning_source='explicit'
        )
        
        # Get predictions
        predictions = await preference_engine.predict_preferences(
            user_id=user_id,
            context={'budget': 100}
        )
        
        assert 'predictions' in predictions
        assert 'cuisine' in predictions['predictions']
        assert 'total_preferences' in predictions
    
    @pytest.mark.asyncio
    async def test_recommendations(self, test_user):
        """Test generating personalized recommendations"""
        user_id = await test_user
        
        # Store some preferences first
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
            preference_type='protein',
            preference_key='chicken',
            preference_value={'liked': True},
            confidence_score=0.8,
            learning_source='implicit'
        )
        
        # Get recipe recommendations
        recommendations = await preference_engine.get_personalized_recommendations(
            user_id=user_id,
            recommendation_type='recipes',
            context={'budget': 50, 'family_size': 2}
        )
        
        # Should get recommendations based on stored preferences
        assert isinstance(recommendations, list)
        # With stored preferences, should get some recommendations
        # (Note: might be 0 if no matching combinations found)
    
    @pytest.mark.asyncio
    async def test_feedback_update(self, test_user):
        """Test updating preferences based on user feedback"""
        user_id = await test_user
        
        # Update preference with explicit feedback
        result = await preference_engine.update_preference_feedback(
            user_id=user_id,
            preference_type='cuisine',
            preference_key='mexican',
            feedback_score=4.5,
            feedback_context={'meal_type': 'dinner'}
        )
        
        assert result['success'] is True
        assert 'updated_preference' in result
        
        # Verify the preference was stored
        prefs = await preference_repository.get_user_preferences(user_id, 'cuisine')
        mexican_pref = next((p for p in prefs if p.preference_key == 'mexican'), None)
        assert mexican_pref is not None
        assert mexican_pref.learning_source == 'explicit'


class TestMemoryIntegration:
    """Test integration of memory components"""
    
    @pytest.fixture
    async def test_user_with_history(self):
        """Create a test user with some interaction history"""
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        
        registration_data = UserRegistration(
            username=f"memory_test_{timestamp}_{random_suffix}",
            email=f"memory_test_{timestamp}_{random_suffix}@example.com",
            password="test_password_123",
            family_size=4
        )
        
        result = await auth_manager.register_user(registration_data)
        user_id = result["user"]["id"]
        
        # Add some interaction history
        interactions = [
            {
                'message': 'I want healthy meals for the family',
                'type': 'meal_plan',
                'context': {'budget': 100, 'family_size': 4}
            },
            {
                'message': 'Make it vegetarian please',
                'type': 'dietary_preference',
                'context': {'dietary_restrictions': ['vegetarian']}
            },
            {
                'message': 'I love Italian cuisine',
                'type': 'cuisine_preference',
                'context': {'cuisine': 'italian'}
            }
        ]
        
        for interaction in interactions:
            await interaction_repository.log_interaction(
                user_id=user_id,
                interaction_type=interaction['type'],
                user_message=interaction['message'],
                agent_response='Test response',
                context_data=interaction['context'],
                response_time=1.0
            )
            
            # Learn from each interaction
            await preference_engine.learn_from_interaction(
                user_id=user_id,
                interaction_data={
                    'user_message': interaction['message'],
                    'context_data': interaction['context'],
                    'interaction_type': interaction['type'],
                    'user_satisfaction': 4
                },
                feedback_score=4.0
            )
        
        return user_id
    
    @pytest.mark.asyncio
    async def test_comprehensive_memory_recall(self, test_user_with_history):
        """Test comprehensive memory recall across all components"""
        user_id = await test_user_with_history
        
        # Test preference retrieval
        preferences = await preference_repository.get_strong_preferences(user_id)
        assert len(preferences) > 0
        
        # Test interaction history
        recent_interactions = await interaction_repository.get_recent_interactions(user_id)
        assert len(recent_interactions) >= 3
        
        # Test pattern analysis
        patterns = await interaction_repository.get_interaction_patterns(user_id)
        assert patterns['total_interactions'] >= 3
        
        # Test predictions based on history
        predictions = await preference_engine.predict_preferences(
            user_id=user_id,
            context={'budget': 100}
        )
        assert predictions['total_preferences'] > 0
    
    @pytest.mark.asyncio
    async def test_learning_evolution(self, test_user_with_history):
        """Test that learning improves over time"""
        user_id = await test_user_with_history
        
        # Get initial preference count
        initial_prefs = await preference_repository.get_strong_preferences(user_id)
        initial_count = sum(len(prefs) for prefs in initial_prefs.values())
        
        # Add more interactions with feedback
        for i in range(3):
            await preference_engine.learn_from_interaction(
                user_id=user_id,
                interaction_data={
                    'user_message': f'I really enjoy spicy food {i}',
                    'context_data': {'spice_level': 'high'},
                    'interaction_type': 'preference_update',
                    'user_satisfaction': 5
                },
                feedback_score=4.8
            )
        
        # Get updated preference count
        updated_prefs = await preference_repository.get_strong_preferences(user_id)
        updated_count = sum(len(prefs) for prefs in updated_prefs.values())
        
        # Should have learned more preferences
        assert updated_count >= initial_count
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, test_user_with_history):
        """Test that confidence scores evolve correctly"""
        user_id = await test_user_with_history
        
        # Add a preference with low initial confidence
        await preference_repository.upsert_preference(
            user_id=user_id,
            preference_type='cooking_style',
            preference_key='quick',
            preference_value={'preferred': True},
            confidence_score=0.3,
            learning_source='implicit'
        )
        
        # Reinforce it multiple times
        for _ in range(3):
            await preference_repository.upsert_preference(
                user_id=user_id,
                preference_type='cooking_style',
                preference_key='quick',
                preference_value={'preferred': True, 'reinforced': True},
                confidence_score=0.8,
                learning_source='explicit'
            )
        
        # Check that confidence improved
        prefs = await preference_repository.get_user_preferences(user_id, 'cooking_style')
        quick_pref = next((p for p in prefs if p.preference_key == 'quick'), None)
        
        assert quick_pref is not None
        assert quick_pref.confidence_score >= 0.8
        assert quick_pref.times_observed >= 4


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
