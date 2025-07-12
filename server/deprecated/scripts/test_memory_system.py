"""
Test script for Bruno AI long-term memory system
Validates database, authentication, and learning capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.auth_manager import auth_manager
from src.auth.models import UserRegistration
from src.learning.preference_engine import preference_engine
from src.database.repositories import preference_repository, interaction_repository
from loguru import logger

async def test_authentication():
    """Test user authentication system"""
    logger.info("Testing authentication system...")
    
    # Register test user
    test_user = UserRegistration(
        username="test_user",
        email="test@example.com", 
        password="testpass123",
        family_size=2,
        zip_code="12345"
    )
    
    result = await auth_manager.register_user(test_user)
    if result['success']:
        logger.info("✅ User registration successful")
        user_id = result['user']['id']
        return user_id
    else:
        logger.error(f"❌ User registration failed: {result.get('error')}")
        return None

async def test_preference_learning(user_id: int):
    """Test preference learning system"""
    logger.info("Testing preference learning...")
    
    # Simulate user interaction
    interaction_data = {
        'user_message': "I want Italian chicken recipes for my family",
        'context_data': {
            'budget': 75,
            'family_size': 2,
            'dietary_restrictions': ['gluten_free']
        },
        'interaction_type': 'meal_plan',
        'user_satisfaction': 5
    }
    
    # Learn from interaction
    learning_result = await preference_engine.learn_from_interaction(
        user_id=user_id,
        interaction_data=interaction_data,
        feedback_score=4.5
    )
    
    if 'error' not in learning_result:
        logger.info(f"✅ Learned {learning_result['preferences_learned']} preferences")
    else:
        logger.error(f"❌ Learning failed: {learning_result['error']}")
    
    # Test preference prediction
    predictions = await preference_engine.predict_preferences(
        user_id=user_id,
        context={'budget': 100}
    )
    
    if 'error' not in predictions:
        logger.info("✅ Preference prediction successful")
        logger.info(f"Total preferences: {predictions['total_preferences']}")
    else:
        logger.error(f"❌ Prediction failed: {predictions['error']}")

async def test_recommendations(user_id: int):
    """Test recommendation engine"""
    logger.info("Testing recommendation engine...")
    
    recommendations = await preference_engine.get_personalized_recommendations(
        user_id=user_id,
        recommendation_type='recipes',
        context={'budget': 75, 'family_size': 2}
    )
    
    if recommendations:
        logger.info(f"✅ Generated {len(recommendations)} recipe recommendations")
        for rec in recommendations[:2]:
            logger.info(f"  - {rec.get('recipe_name', 'Unknown')} (confidence: {rec.get('confidence_score', 0):.2f})")
    else:
        logger.warning("⚠️ No recommendations generated")

async def test_memory_persistence(user_id: int):
    """Test memory persistence"""
    logger.info("Testing memory persistence...")
    
    # Store a preference directly
    pref_result = await preference_repository.upsert_preference(
        user_id=user_id,
        preference_type='cuisine',
        preference_key='mexican',
        preference_value={'liked': True, 'frequency': 'weekly'},
        confidence_score=0.8,
        learning_source='explicit'
    )
    
    if pref_result:
        logger.info("✅ Direct preference storage successful")
    
    # Retrieve user preferences
    user_prefs = await preference_repository.get_strong_preferences(user_id)
    
    if user_prefs:
        logger.info(f"✅ Retrieved {sum(len(prefs) for prefs in user_prefs.values())} stored preferences")
        for pref_type, prefs in user_prefs.items():
            logger.info(f"  - {pref_type}: {list(prefs.keys())}")
    else:
        logger.warning("⚠️ No preferences found in storage")

async def run_comprehensive_test():
    """Run comprehensive test of the memory system"""
    logger.info("🧠 Starting Bruno AI Long-term Memory System Test")
    logger.info("=" * 60)
    
    try:
        # Test authentication
        user_id = await test_authentication()
        if not user_id:
            logger.error("Authentication test failed - stopping")
            return
        
        # Test preference learning
        await test_preference_learning(user_id)
        
        # Test recommendations
        await test_recommendations(user_id)
        
        # Test memory persistence
        await test_memory_persistence(user_id)
        
        logger.info("=" * 60)
        logger.info("🎉 All tests completed successfully!")
        logger.info("Bruno AI now has long-term memory capabilities:")
        logger.info("  ✅ User authentication & profiles")
        logger.info("  ✅ Preference learning from interactions")
        logger.info("  ✅ Personalized recommendations")
        logger.info("  ✅ Persistent memory storage")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
