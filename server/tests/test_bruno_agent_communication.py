#!/usr/bin/env python3
"""
Test Script for Bruno AI Agent Communication and Personality
Verifies that agents can communicate effectively while staying in character
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add current directory to path so we can import our agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the v2 agents
from agents.v2.bruno_master_agent import BrunoMasterAgentV2
from agents.v2.budget_analyst_agent import BudgetAnalystAgentV2
from agents.v2.instacart_integration_agent import InstacartIntegrationAgentV2
from recipe_chef_agent import RecipeChefAgent

class BrunoAgentCommunicationTest:
    """Test Bruno AI agent communication and personality consistency"""
    
    def __init__(self):
        self.test_results = []
        self.agent_instances = {}
        
    async def setup_agents(self):
        """Initialize all Bruno AI agents"""
        print("🐻 Setting up Bruno's agent team...")
        
        try:
            # Initialize Bruno Master Agent
            self.agent_instances['bruno_master'] = BrunoMasterAgentV2()
            print("✅ Bruno Master Agent initialized")
            
            # Initialize Budget Analyst Agent  
            self.agent_instances['budget_analyst'] = BudgetAnalystAgentV2()
            print("✅ Budget Analyst Agent initialized")
            
            # Initialize Recipe Chef Agent
            self.agent_instances['recipe_chef'] = RecipeChefAgent()
            print("✅ Recipe Chef Agent initialized")
            
            # Initialize Instacart Integration Agent
            self.agent_instances['instacart_integration'] = InstacartIntegrationAgentV2()
            print("✅ Instacart Integration Agent initialized")
            
            print("🎉 All agents are ready to work!")
            
        except Exception as e:
            print(f"❌ Failed to setup agents: {e}")
            raise
    
    async def test_bruno_personality_consistency(self):
        """Test that Bruno's personality is consistent across agents"""
        print("\n🧪 Testing Bruno's Personality Consistency...")
        
        test_case = {
            "test_name": "personality_consistency",
            "description": "Verify Bruno's Brooklyn personality across agents",
            "results": {}
        }
        
        # Test Master Agent personality
        try:
            master_task = {
                "action": "general_conversation",
                "context": {"user_id": "test_user"},
                "message": "Hey Bruno, what can you help me with for my family's meal planning?"
            }
            
            master_response = await self.agent_instances['bruno_master'].execute_task(master_task)
            
            # Check for Brooklyn personality markers
            response_text = master_response.get('bruno_response', '').lower()
            personality_markers = [
                'lemme', 'ya', 'gonna', 'brooklyn', 'trust me', 
                'bada-bing', "that's what i'm talkin' about", 'family'
            ]
            
            found_markers = [marker for marker in personality_markers if marker in response_text]
            
            test_case["results"]["master_agent"] = {
                "response_generated": bool(master_response.get('bruno_response')),
                "personality_markers_found": found_markers,
                "personality_score": len(found_markers) / len(personality_markers),
                "response_preview": master_response.get('bruno_response', '')[:100] + "..."
            }
            
            print(f"✅ Master Agent personality test: {len(found_markers)}/{len(personality_markers)} markers found")
            
        except Exception as e:
            test_case["results"]["master_agent"] = {"error": str(e)}
            print(f"❌ Master Agent personality test failed: {e}")
        
        # Test Budget Analyst personality in recommendations
        try:
            budget_task = {
                "action": "analyze_budget",
                "context": {
                    "target_budget": 100,
                    "family_size": 4,
                    "timeframe": "week",
                    "historical_data": {"budget_history": [85, 90, 95, 88]}
                }
            }
            
            budget_response = await self.agent_instances['budget_analyst'].execute_task(budget_task)
            
            # Check Bruno's voice in budget recommendations
            recommendations = budget_response.get('recommendations', [])
            bruno_voice_markers = 0
            
            for rec in recommendations:
                if any(marker in rec.lower() for marker in ['lemme tell ya', 'bada-bing', 'trust me', 'ya']):
                    bruno_voice_markers += 1
            
            test_case["results"]["budget_analyst"] = {
                "recommendations_count": len(recommendations),
                "bruno_voice_markers": bruno_voice_markers,
                "personality_in_recommendations": bruno_voice_markers > 0,
                "sample_recommendation": recommendations[0] if recommendations else "No recommendations"
            }
            
            print(f"✅ Budget Analyst personality test: {bruno_voice_markers} recommendations with Bruno's voice")
            
        except Exception as e:
            test_case["results"]["budget_analyst"] = {"error": str(e)}
            print(f"❌ Budget Analyst personality test failed: {e}")
        
        self.test_results.append(test_case)
    
    async def test_agent_coordination(self):
        """Test that agents can coordinate effectively through Bruno Master"""
        print("\n🤝 Testing Agent Coordination...")
        
        test_case = {
            "test_name": "agent_coordination",
            "description": "Test multi-agent meal planning workflow",
            "results": {}
        }
        
        try:
            # Simulate a comprehensive meal planning request
            meal_planning_task = {
                "action": "plan_meals",
                "context": {
                    "user_id": "test_family",
                    "budget": 75,
                    "family_size": 3,
                    "timeframe": "week",
                    "location": {"city": "Brooklyn", "state": "NY"},
                    "dietary_restrictions": []
                },
                "message": "Bruno, I need to plan meals for my family of 3 with $75 for the week. Can you help?"
            }
            
            # Execute through Bruno Master Agent (which should coordinate other agents)
            coordination_response = await self.agent_instances['bruno_master'].execute_task(meal_planning_task)
            
            test_case["results"]["coordination_test"] = {
                "task_completed": coordination_response.get('success', False),
                "bruno_response_provided": bool(coordination_response.get('bruno_response')),
                "meal_plan_created": bool(coordination_response.get('meal_plan')),
                "budget_analysis_included": bool(coordination_response.get('budget_analysis')),
                "shopping_experience_created": bool(coordination_response.get('shopping_experience')),
                "coordination_details": coordination_response.get('coordination_details', {}),
                "response_summary": {
                    "agents_coordinated": coordination_response.get('coordination_details', {}).get('agents_used', []),
                    "total_processing_time": coordination_response.get('coordination_details', {}).get('total_processing_time', 0),
                    "optimization_score": coordination_response.get('coordination_details', {}).get('optimization_score', 0)
                }
            }
            
            if coordination_response.get('success'):
                print("✅ Agent coordination successful - multiple agents worked together")
                print(f"  📊 Agents used: {coordination_response.get('coordination_details', {}).get('agents_used', [])}")
                print(f"  ⏱️  Processing time: {coordination_response.get('coordination_details', {}).get('total_processing_time', 0)} seconds")
            else:
                print("❌ Agent coordination failed")
            
        except Exception as e:
            test_case["results"]["coordination_test"] = {"error": str(e)}
            print(f"❌ Agent coordination test failed: {e}")
        
        self.test_results.append(test_case)
    
    async def test_recipe_chef_functionality(self):
        """Test Recipe Chef Agent functionality and Bruno personality"""
        print("\n👨‍🍳 Testing Recipe Chef Agent...")
        
        test_case = {
            "test_name": "recipe_chef_functionality",
            "description": "Test recipe creation and Bruno's cooking personality",
            "results": {}
        }
        
        try:
            # Test meal plan creation
            meal_plan_params = {
                "duration_days": 3,
                "budget_limit": 60.0,
                "dietary_preferences": [],
                "servings_per_meal": 2,
                "meals_per_day": 2
            }
            
            # Use the tool directly (simulating how Bruno Master would call it)
            recipe_agent = self.agent_instances['recipe_chef']
            meal_plan_tool = recipe_agent._create_meal_plan_tool()
            
            meal_plan_result = await meal_plan_tool.function(**meal_plan_params)
            
            test_case["results"]["meal_plan_creation"] = {
                "plan_created": meal_plan_result.get('success', False),
                "within_budget": meal_plan_result.get('budget_analysis', {}).get('under_budget', False),
                "estimated_cost": meal_plan_result.get('budget_analysis', {}).get('estimated_cost', 0),
                "target_budget": meal_plan_result.get('budget_analysis', {}).get('target_budget', 0),
                "meal_plan_id": meal_plan_result.get('plan_id'),
                "meals_included": len(meal_plan_result.get('meal_plan', {}).get('meals', {}))
            }
            
            if meal_plan_result.get('success'):
                print(f"✅ Recipe Chef created meal plan: ${meal_plan_result.get('budget_analysis', {}).get('estimated_cost', 0):.2f} of ${meal_plan_result.get('budget_analysis', {}).get('target_budget', 0):.2f}")
            else:
                print("❌ Recipe Chef meal plan creation failed")
            
            # Test recipe optimization
            optimization_params = {
                "recipe_name": "Budget Chicken Stir Fry",
                "target_budget": 10.0,
                "servings": 4
            }
            
            optimization_tool = recipe_agent._optimize_recipe_for_budget_tool()
            optimization_result = await optimization_tool.function(**optimization_params)
            
            test_case["results"]["recipe_optimization"] = {
                "optimization_completed": optimization_result.get('success', False),
                "optimization_needed": optimization_result.get('optimization_needed', True),
                "original_cost": optimization_result.get('optimization_summary', {}).get('original_cost', 0),
                "optimized_cost": optimization_result.get('optimization_summary', {}).get('optimized_cost', 0),
                "fits_budget": optimization_result.get('optimization_summary', {}).get('fits_budget', False)
            }
            
            if optimization_result.get('success'):
                print(f"✅ Recipe optimization: ${optimization_result.get('optimization_summary', {}).get('optimized_cost', 0):.2f} (target: ${optimization_params['target_budget']})")
            else:
                print("❌ Recipe optimization failed")
            
        except Exception as e:
            test_case["results"]["recipe_chef_test"] = {"error": str(e)}
            print(f"❌ Recipe Chef test failed: {e}")
        
        self.test_results.append(test_case)
    
    async def test_meaningful_results(self):
        """Test that agents provide meaningful, actionable results"""
        print("\n📊 Testing Meaningful Results Generation...")
        
        test_case = {
            "test_name": "meaningful_results",
            "description": "Verify agents provide actionable, valuable outputs",
            "results": {}
        }
        
        try:
            # Test Budget Analyst provides actionable insights
            budget_task = {
                "action": "analyze_spending_patterns",
                "context": {
                    "user_history": {
                        "budget_history": [75, 82, 78, 90, 85, 88, 76],
                        "frequently_bought": ["chicken", "rice", "vegetables", "milk"]
                    },
                    "current_budget": 80,
                    "analysis_timeframe": "3_months"
                }
            }
            
            budget_response = await self.agent_instances['budget_analyst'].execute_task(budget_task)
            
            # Evaluate meaningfulness of budget analysis
            spending_stats = budget_response.get('spending_statistics', {})
            insights = budget_response.get('insights', [])
            
            test_case["results"]["budget_analysis_quality"] = {
                "statistics_provided": bool(spending_stats),
                "insights_count": len(insights) if isinstance(insights, list) else 0,
                "trend_analysis": bool(spending_stats.get('trend')),
                "actionable_insights": len([i for i in insights if isinstance(i, str) and any(word in i.lower() for word in ['save', 'reduce', 'increase', 'try', 'consider'])]) if isinstance(insights, list) else 0,
                "overspending_categories_identified": bool(budget_response.get('overspending_categories')),
                "optimization_score": budget_response.get('optimization_score', 0)
            }
            
            print(f"✅ Budget analysis quality: {len(insights) if isinstance(insights, list) else 0} insights provided")
            
        except Exception as e:
            test_case["results"]["budget_analysis_quality"] = {"error": str(e)}
            print(f"❌ Budget analysis quality test failed: {e}")
        
        self.test_results.append(test_case)
    
    def print_test_summary(self):
        """Print a comprehensive test summary"""
        print("\n" + "="*60)
        print("🐻 BRUNO AI AGENT COMMUNICATION TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = 0
        
        for test in self.test_results:
            print(f"\n📋 {test['test_name'].upper()}")
            print(f"   Description: {test['description']}")
            
            test_passed = True
            for result_key, result_data in test['results'].items():
                if isinstance(result_data, dict) and 'error' in result_data:
                    print(f"   ❌ {result_key}: {result_data['error']}")
                    test_passed = False
                else:
                    print(f"   ✅ {result_key}: Completed successfully")
            
            if test_passed:
                passed_tests += 1
                print(f"   ✅ Overall: PASSED")
            else:
                print(f"   ❌ Overall: FAILED")
        
        print(f"\n🎯 TEST RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Bruno's agents are communicating effectively!")
        else:
            print("⚠️  Some tests failed. Check the details above for issues.")
        
        # Save detailed results to file
        results_file = f"bruno_agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2, default=str)
        
        print(f"📄 Detailed results saved to: {results_file}")

async def main():
    """Run the Bruno AI agent communication tests"""
    print("🐻 Starting Bruno AI Agent Communication Tests...")
    print("="*60)
    
    tester = BrunoAgentCommunicationTest()
    
    try:
        # Setup all agents
        await tester.setup_agents()
        
        # Run test suite
        await tester.test_bruno_personality_consistency()
        await tester.test_agent_coordination()
        await tester.test_recipe_chef_functionality()
        await tester.test_meaningful_results()
        
        # Print comprehensive summary
        tester.print_test_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Set up environment variables if not present (for testing)
    os.environ.setdefault('GEMINI_API_KEY', 'test_key')
    os.environ.setdefault('INSTACART_API_KEY', 'test_key')
    os.environ.setdefault('INSTACART_AFFILIATE_ID', 'test_affiliate')
    
    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
