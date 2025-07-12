"""
Test script for Bruno AI V3.1 BaseAgent implementation
"""

import asyncio
import logging
import os
from base_agent import BaseAgent
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_base_agent():
    """Test the BaseAgent implementation"""
    
    # Test configuration
    agent_id = "test_agent"
    model_name = "claude-3-5-sonnet-20241022"  # Using Sonnet for testing
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    postgres_url = os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai')
    
    try:
        # Initialize the agent
        logger.info("Initializing BaseAgent...")
        agent = BaseAgent(agent_id, model_name, redis_url, postgres_url)
        logger.info(f"Agent initialized with ID: {agent.agent_id}")
        
        # Test simple query processing
        test_query = "What are some healthy breakfast options under $10?"
        logger.info(f"Testing query: {test_query}")
        
        result = await agent.process_with_optimization(test_query)
        logger.info(f"Query result: {result[:100]}...")
        
        # Test caching by running the same query again
        logger.info("Testing cache hit...")
        cached_result = await agent.process_with_optimization(test_query)
        logger.info(f"Cached result: {cached_result[:100]}...")
        
        # Test context management
        context_data = {
            "user_preferences": {
                "budget": 10,
                "dietary_restrictions": ["vegetarian"],
                "cuisine_preferences": ["Italian", "Mediterranean"]
            }
        }
        
        logger.info("Testing context management...")
        await agent.set_context("test_context", context_data)
        retrieved_context = await agent.get_context("test_context")
        logger.info(f"Retrieved context: {retrieved_context}")
        
        # Test with context
        context_query = "Suggest a dinner recipe based on my preferences"
        result_with_context = await agent.process_with_optimization(context_query, "test_context")
        logger.info(f"Context-aware result: {result_with_context[:100]}...")
        
        logger.info("All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_base_agent())
