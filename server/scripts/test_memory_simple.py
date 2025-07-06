"""
Simple test script for Bruno AI memory system
Tests core functionality without complex authentication
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

env_file = project_root / "config" / ".env"
load_dotenv(env_file)

from src.database.repositories import preference_repository, interaction_repository
from src.learning.preference_engine import preference_engine
from loguru import logger

async def test_preference_storage():
    """Test basic preference storage and retrieval"""
    logger.info("Testing preference storage...")
    
    # Test user ID (using the demo user)
    test_user_id = 1
    
    try:
        # Store a preference
        pref = await preference_repository.upsert_preference(
            user_id=test_user_id,
            preference_type='cuisine',
            preference_key='italian',
            preference_value={'liked': True, 'confidence': 0.8},
            confidence_score=0.8,
            learning_source='test'
        )
        
        logger.info(f"✅ Stored preference: {pref.preference_key}")
        
        # Retrieve preferences
        user_prefs = await preference_repository.get_strong_preferences(test_user_id)
        logger.info(f"✅ Retrieved preferences: {user_prefs}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Preference test failed: {e}")
        return False

async def test_interaction_logging():
    """Test interaction logging"""
    logger.info("Testing interaction logging...")
    
    test_user_id = 1
    
    try:
        # Log an interaction
        interaction = await interaction_repository.log_interaction(
            user_id=test_user_id,
            interaction_type='meal_plan',
            user_message='I want Italian food for dinner',
            agent_response='Here are some Italian recipes...',
            context_data={'budget': 50, 'family_size': 2},
            response_time=1.5
        )
        
        logger.info(f"✅ Logged interaction: {interaction.id}")
        
        # Get recent interactions
        recent = await interaction_repository.get_recent_interactions(test_user_id, days=1)
        logger.info(f"✅ Found {len(recent)} recent interactions")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Interaction test failed: {e}")
        return False

async def test_preference_learning():
    """Test preference learning engine"""
    logger.info("Testing preference learning...")
    
    test_user_id = 1
    
    try:
        # Simulate learning from interaction
        interaction_data = {
            'user_message': 'I love spicy Mexican food',
            'context_data': {'budget': 75, 'family_size': 3},
            'interaction_type': 'meal_plan',
            'user_satisfaction': 5
        }
        
        result = await preference_engine.learn_from_interaction(
            user_id=test_user_id,
            interaction_data=interaction_data,
            feedback_score=4.5
        )
        
        logger.info(f"✅ Learning result: {result}")
        
        # Test predictions
        predictions = await preference_engine.predict_preferences(
            user_id=test_user_id,
            context={'budget': 100}
        )
        
        logger.info(f"✅ Generated predictions for {predictions.get('total_preferences', 0)} preferences")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Learning test failed: {e}")
        return False

async def test_recommendations():
    """Test recommendation generation"""
    logger.info("Testing recommendations...")
    
    test_user_id = 1
    
    try:
        recommendations = await preference_engine.get_personalized_recommendations(
            user_id=test_user_id,
            recommendation_type='recipes',
            context={'budget': 50, 'family_size': 2}
        )
        
        logger.info(f"✅ Generated {len(recommendations)} recipe recommendations")
        
        for rec in recommendations[:2]:
            logger.info(f"  - {rec.get('recipe_name', 'Unknown')} (confidence: {rec.get('confidence_score', 0):.2f})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Recommendation test failed: {e}")
        return False

async def run_simple_memory_test():
    """Run comprehensive memory system test"""
    logger.info("🧠 Starting Bruno AI Memory System Test (Simple)")
    logger.info("=" * 60)
    
    tests = [
        ("Preference Storage", test_preference_storage),
        ("Interaction Logging", test_interaction_logging),
        ("Preference Learning", test_preference_learning),
        ("Recommendations", test_recommendations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            success = await test_func()
            if success:
                passed += 1
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
    
    logger.info("=" * 60)
    logger.info(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All memory system tests PASSED!")
        logger.info("Bruno AI long-term memory is working correctly!")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} tests failed. Memory system needs attention.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_simple_memory_test())
    sys.exit(0 if success else 1)
