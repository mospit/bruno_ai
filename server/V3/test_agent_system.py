#!/usr/bin/env python3
"""
Comprehensive test script for Bruno AI V3.1 agent system
Tests A2A communication, agent functionality, and error handling
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.base_agent import BaseAgent
from agents.a2a_server import A2AServer
from agents.pantry_manager import PantryManagerAgent
from agents.recipe_chef import RecipeChefAgent
from agents.budget_analyst import BudgetAnalystAgent
from agents.reflection_feedback import ReflectionFeedbackAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrunoAITestSuite:
    """Test suite for Bruno AI agent system"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.postgres_url = os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai')
        self.agents = {}
        self.a2a_server = A2AServer(port=8080)
        self.test_context_id = f"test_context_{datetime.now().timestamp()}"
        
    async def initialize_agents(self):
        """Initialize all agents for testing"""
        logger.info("Initializing agents...")
        
        try:
            # Initialize agents
            self.agents['pantry_manager'] = PantryManagerAgent(
                redis_url=self.redis_url,
                postgres_url=self.postgres_url
            )
            
            self.agents['recipe_chef'] = RecipeChefAgent(
                redis_url=self.redis_url,
                postgres_url=self.postgres_url
            )
            
            self.agents['budget_analyst'] = BudgetAnalystAgent(
                redis_url=self.redis_url,
                postgres_url=self.postgres_url
            )
            
            self.agents['reflection_feedback'] = ReflectionFeedbackAgent(
                redis_url=self.redis_url,
                postgres_url=self.postgres_url
            )
            
            # Register agents with A2A server
            for agent_id, agent in self.agents.items():
                await self.a2a_server.register_agent(agent_id, agent)
                
            logger.info(f"Successfully initialized {len(self.agents)} agents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return False
    
    async def test_individual_agent_functionality(self):
        """Test individual agent functionality"""
        logger.info("Testing individual agent functionality...")
        
        tests = []
        
        # Test PantryManagerAgent
        try:
            pantry_agent = self.agents['pantry_manager']
            
            # Test adding items
            add_result = await pantry_agent.add_items([
                {"name": "chicken breast", "quantity": 2, "unit": "lbs", "expiration": "2025-01-20"},
                {"name": "broccoli", "quantity": 1, "unit": "bunch", "expiration": "2025-01-16"},
                {"name": "rice", "quantity": 3, "unit": "cups", "expiration": "2025-06-01"}
            ], self.test_context_id)
            
            tests.append(("PantryManager - Add Items", add_result.get('success', False)))
            
            # Test checking inventory
            inventory_result = await pantry_agent.check_inventory(self.test_context_id)
            tests.append(("PantryManager - Check Inventory", inventory_result.get('success', False)))
            
            logger.info(f"PantryManager tests: {[t[0] for t in tests if t[1]]}")
            
        except Exception as e:
            logger.error(f"PantryManager test failed: {e}")
            tests.append(("PantryManager - Error", False))
        
        # Test RecipeChefAgent
        try:
            recipe_agent = self.agents['recipe_chef']
            
            # Test meal plan creation
            meal_plan_result = await recipe_agent.create_meal_plan(
                "Create a 3-day meal plan for 2 people with a $50 budget",
                self.test_context_id
            )
            
            tests.append(("RecipeChef - Create Meal Plan", meal_plan_result.get('success', False)))
            
            logger.info(f"RecipeChef tests: {[t[0] for t in tests if t[1]]}")
            
        except Exception as e:
            logger.error(f"RecipeChef test failed: {e}")
            tests.append(("RecipeChef - Error", False))
        
        # Test BudgetAnalystAgent
        try:
            budget_agent = self.agents['budget_analyst']
            
            # Test budget analysis
            budget_result = await budget_agent.analyze_budget(
                {"monthly_budget": 400, "current_spending": 120, "days_remaining": 20},
                self.test_context_id
            )
            
            tests.append(("BudgetAnalyst - Analyze Budget", budget_result.get('success', False)))
            
            logger.info(f"BudgetAnalyst tests: {[t[0] for t in tests if t[1]]}")
            
        except Exception as e:
            logger.error(f"BudgetAnalyst test failed: {e}")
            tests.append(("BudgetAnalyst - Error", False))
        
        # Summary
        passed = sum(1 for t in tests if t[1])
        total = len(tests)
        logger.info(f"Individual agent tests: {passed}/{total} passed")
        
        return tests
    
    async def test_a2a_communication(self):
        """Test Agent-to-Agent communication"""
        logger.info("Testing A2A communication...")
        
        tests = []
        
        # Test 1: PantryManager -> RecipeChef
        try:
            a2a_message = {
                'source_agent': 'pantry_manager',
                'target_agent': 'recipe_chef',
                'query': 'Based on current inventory (chicken breast, broccoli, rice), suggest a healthy dinner recipe for 2 people',
                'context_id': self.test_context_id
            }
            
            response = await self.a2a_server.handle_a2a_message(a2a_message)
            tests.append(("A2A: PantryManager -> RecipeChef", response.get('status') == 'success'))
            
            if response.get('status') == 'success':
                logger.info(f"A2A Response: {response.get('result', '')[:100]}...")
            
        except Exception as e:
            logger.error(f"A2A test 1 failed: {e}")
            tests.append(("A2A: PantryManager -> RecipeChef", False))
        
        # Test 2: RecipeChef -> BudgetAnalyst
        try:
            a2a_message = {
                'source_agent': 'recipe_chef',
                'target_agent': 'budget_analyst',
                'query': 'Estimate the cost for ingredients: chicken breast (2 lbs), broccoli (1 bunch), rice (3 cups), olive oil, garlic',
                'context_id': self.test_context_id
            }
            
            response = await self.a2a_server.handle_a2a_message(a2a_message)
            tests.append(("A2A: RecipeChef -> BudgetAnalyst", response.get('status') == 'success'))
            
            if response.get('status') == 'success':
                logger.info(f"A2A Response: {response.get('result', '')[:100]}...")
            
        except Exception as e:
            logger.error(f"A2A test 2 failed: {e}")
            tests.append(("A2A: RecipeChef -> BudgetAnalyst", False))
        
        # Test 3: Multiple agent collaboration
        try:
            # Simulate a complex workflow
            workflow_steps = [
                {
                    'source_agent': 'pantry_manager',
                    'target_agent': 'recipe_chef',
                    'query': 'What can I make with my current ingredients?',
                    'context_id': self.test_context_id
                },
                {
                    'source_agent': 'recipe_chef',
                    'target_agent': 'budget_analyst',
                    'query': 'What would be the cost to shop for missing ingredients for a chicken stir-fry?',
                    'context_id': self.test_context_id
                }
            ]
            
            workflow_success = True
            for step in workflow_steps:
                response = await self.a2a_server.handle_a2a_message(step)
                if response.get('status') != 'success':
                    workflow_success = False
                    break
                    
            tests.append(("A2A: Multi-agent Workflow", workflow_success))
            
        except Exception as e:
            logger.error(f"A2A workflow test failed: {e}")
            tests.append(("A2A: Multi-agent Workflow", False))
        
        # Summary
        passed = sum(1 for t in tests if t[1])
        total = len(tests)
        logger.info(f"A2A communication tests: {passed}/{total} passed")
        
        return tests
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        logger.info("Testing error handling...")
        
        tests = []
        
        # Test 1: Invalid agent target
        try:
            a2a_message = {
                'source_agent': 'pantry_manager',
                'target_agent': 'nonexistent_agent',
                'query': 'This should fail',
                'context_id': self.test_context_id
            }
            
            response = await self.a2a_server.handle_a2a_message(a2a_message)
            tests.append(("Error: Invalid Target Agent", response.get('status') == 'error'))
            
        except Exception as e:
            logger.error(f"Error test 1 failed: {e}")
            tests.append(("Error: Invalid Target Agent", False))
        
        # Test 2: Missing required fields
        try:
            a2a_message = {
                'source_agent': 'pantry_manager',
                # Missing target_agent and query
                'context_id': self.test_context_id
            }
            
            response = await self.a2a_server.handle_a2a_message(a2a_message)
            tests.append(("Error: Missing Fields", response.get('status') == 'error'))
            
        except Exception as e:
            logger.error(f"Error test 2 failed: {e}")
            tests.append(("Error: Missing Fields", False))
        
        # Test 3: Invalid context handling
        try:
            pantry_agent = self.agents['pantry_manager']
            result = await pantry_agent.check_inventory("invalid_context_id")
            # Should handle gracefully and return some response
            tests.append(("Error: Invalid Context", True))
            
        except Exception as e:
            logger.error(f"Error test 3 failed: {e}")
            tests.append(("Error: Invalid Context", False))
        
        # Summary
        passed = sum(1 for t in tests if t[1])
        total = len(tests)
        logger.info(f"Error handling tests: {passed}/{total} passed")
        
        return tests
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        logger.info("Starting Bruno AI V3.1 comprehensive test suite...")
        
        # Initialize agents
        if not await self.initialize_agents():
            logger.error("Failed to initialize agents. Aborting tests.")
            return False
        
        all_tests = []
        
        # Run individual agent tests
        individual_tests = await self.test_individual_agent_functionality()
        all_tests.extend(individual_tests)
        
        # Run A2A communication tests
        a2a_tests = await self.test_a2a_communication()
        all_tests.extend(a2a_tests)
        
        # Run error handling tests
        error_tests = await self.test_error_handling()
        all_tests.extend(error_tests)
        
        # Final summary
        passed = sum(1 for t in all_tests if t[1])
        total = len(all_tests)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("BRUNO AI V3.1 TEST SUITE RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total tests run: {total}")
        logger.info(f"Tests passed: {passed}")
        logger.info(f"Tests failed: {total - passed}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        # Detailed results
        for test_name, result in all_tests:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{status} - {test_name}")
        
        return success_rate >= 80  # Consider 80% success rate as passing

async def main():
    """Main test function"""
    test_suite = BrunoAITestSuite()
    
    try:
        success = await test_suite.run_comprehensive_test()
        
        if success:
            logger.info("🎉 Test suite completed successfully!")
            return 0
        else:
            logger.error("❌ Test suite failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Test suite crashed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
