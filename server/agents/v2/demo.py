"""
Bruno AI V2.0 Demo Script
Test the optimized multi-agent system
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any
from loguru import logger

class BrunoAIDemo:
    """Demo client for testing Bruno AI V2.0 system"""
    
    def __init__(self):
        self.gateway_url = "http://localhost:3000"
        self.bruno_url = "http://localhost:8080"
        
    async def run_demo(self):
        """Run comprehensive demo of Bruno AI capabilities"""
        logger.info("Starting Bruno AI V2.0 Demo")
        
        # Wait for system to be ready
        await self._wait_for_system()
        
        # Run demo scenarios
        scenarios = [
            self._demo_meal_planning,
            self._demo_budget_coaching,
            self._demo_instacart_shopping,
            self._demo_real_time_adaptation
        ]
        
        for scenario in scenarios:
            try:
                await scenario()
                await asyncio.sleep(2)  # Brief pause between scenarios
            except Exception as e:
                logger.error(f"Scenario failed: {e}")
                continue
        
        logger.info("Bruno AI V2.0 Demo completed!")
    
    async def _wait_for_system(self):
        """Wait for the system to be ready"""
        logger.info("Waiting for Bruno AI system to be ready...")
        
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    # Check gateway health
                    gateway_response = await client.get(f"{self.gateway_url}/gateway/health", timeout=5.0)
                    
                    # Check Bruno agent health
                    bruno_response = await client.get(f"{self.bruno_url}/health", timeout=5.0)
                    
                    if gateway_response.status_code == 200 and bruno_response.status_code == 200:
                        logger.info("System is ready!")
                        return
                        
            except Exception as e:
                logger.debug(f"System not ready yet (attempt {attempt + 1}): {e}")
                await asyncio.sleep(retry_delay)
        
        raise Exception("System failed to become ready within timeout period")
    
    async def _demo_meal_planning(self):
        """Demo comprehensive meal planning workflow"""
        logger.info("🍽️ Demo: Comprehensive Meal Planning")
        
        request_data = {
            "action": "plan_meals",
            "message": "Bruno, plan meals for $75 this week for my family of 4. We need healthy options and my daughter is vegetarian.",
            "context": {
                "budget": 75,
                "family_size": 4,
                "dietary_restrictions": ["vegetarian"],
                "timeframe": "week",
                "location": {"zip": "60601", "city": "Chicago"},
                "user_id": "demo_user"
            }
        }
        
        result = await self._send_request_to_bruno(request_data)
        
        if result.get('success'):
            logger.info("✅ Meal planning successful!")
            logger.info(f"Bruno's response: {result.get('bruno_response', 'No response')[:200]}...")
            
            # Display key results
            meal_plan = result.get('meal_plan', {})
            shopping = result.get('shopping_experience', {})
            
            logger.info(f"📊 Meals created: {len(meal_plan.get('recipes', []))}")
            logger.info(f"💰 Total cost: ${shopping.get('total_cost', 0):.2f}")
            logger.info(f"💸 Estimated savings: ${shopping.get('estimated_savings', 0):.2f}")
            
        else:
            logger.error(f"❌ Meal planning failed: {result.get('error', 'Unknown error')}")
    
    async def _demo_budget_coaching(self):
        """Demo budget coaching capabilities"""
        logger.info("💰 Demo: Budget Coaching")
        
        request_data = {
            "action": "budget_coaching",
            "message": "Bruno, I've been overspending on groceries lately. Can you help me understand why and how to save money?",
            "context": {
                "budget": 80,
                "user_id": "demo_user",
                "current_spending": 95
            }
        }
        
        result = await self._send_request_to_bruno(request_data)
        
        if result.get('success'):
            logger.info("✅ Budget coaching successful!")
            logger.info(f"Bruno's coaching: {result.get('bruno_coaching', 'No coaching')[:200]}...")
            
            # Display insights
            insights = result.get('budget_insights', {})
            tips = result.get('actionable_tips', [])
            
            logger.info(f"📈 Budget insights available: {len(insights)}")
            logger.info(f"💡 Actionable tips: {len(tips)}")
            
        else:
            logger.error(f"❌ Budget coaching failed: {result.get('error', 'Unknown error')}")
    
    async def _demo_instacart_shopping(self):
        """Demo Instacart shopping integration"""
        logger.info("🛒 Demo: Instacart Shopping Integration")
        
        request_data = {
            "action": "create_shopping_list",
            "message": "Bruno, create a shopping list for chicken stir-fry tonight and add it to Instacart",
            "context": {
                "items": [
                    {"name": "chicken breast", "quantity": 1, "unit": "lb"},
                    {"name": "bell peppers", "quantity": 2, "unit": "pieces"},
                    {"name": "onion", "quantity": 1, "unit": "piece"},
                    {"name": "soy sauce", "quantity": 1, "unit": "bottle"},
                    {"name": "rice", "quantity": 1, "unit": "bag"}
                ],
                "budget": 25,
                "location": {"zip": "60601"}
            }
        }
        
        result = await self._send_request_to_bruno(request_data)
        
        if result.get('success'):
            logger.info("✅ Instacart shopping successful!")
            logger.info(f"Bruno's guidance: {result.get('bruno_response', 'No response')[:200]}...")
            
            # Display shopping details
            shopping = result.get('shopping_experience', {})
            
            logger.info(f"🏪 Shopping lists created: {len(shopping.get('shopping_lists', []))}")
            logger.info(f"💰 Total cost: ${shopping.get('total_cost', 0):.2f}")
            logger.info(f"📱 Instacart ready: {shopping.get('instacart_ready', False)}")
            
        else:
            logger.error(f"❌ Instacart shopping failed: {result.get('error', 'Unknown error')}")
    
    async def _demo_real_time_adaptation(self):
        """Demo real-time meal plan adaptation"""
        logger.info("🔄 Demo: Real-time Meal Plan Adaptation")
        
        request_data = {
            "action": "adapt_meal_plan",
            "message": "Bruno, chicken prices went up. Can you update my meal plan with alternatives?",
            "context": {
                "current_meal_plan": {
                    "recipes": [
                        {
                            "name": "Chicken Stir Fry",
                            "ingredients": [
                                {"name": "chicken breast", "quantity": 1, "unit": "lb", "cost": 6.99}
                            ]
                        }
                    ]
                },
                "adaptation_reason": "price_increase",
                "budget": 75,
                "location": {"zip": "60601"}
            }
        }
        
        result = await self._send_request_to_bruno(request_data)
        
        if result.get('success'):
            logger.info("✅ Real-time adaptation successful!")
            logger.info(f"Bruno's explanation: {result.get('bruno_response', 'No response')[:200]}...")
            
            # Display adaptation details
            adaptations_made = result.get('adaptations_made', False)
            logger.info(f"🔧 Adaptations made: {adaptations_made}")
            
            if adaptations_made:
                updated_plan = result.get('updated_meal_plan', {})
                logger.info(f"📋 Updated recipes: {len(updated_plan.get('recipes', []))}")
            
        else:
            logger.error(f"❌ Real-time adaptation failed: {result.get('error', 'Unknown error')}")
    
    async def _send_request_to_bruno(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to Bruno Master Agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bruno_url}/task",
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_system_status(self):
        """Check the status of all system components"""
        logger.info("🔍 Checking system status...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Check gateway
                gateway_response = await client.get(f"{self.gateway_url}/gateway/metrics")
                if gateway_response.status_code == 200:
                    metrics = gateway_response.json()
                    logger.info(f"🌐 Gateway: {metrics.get('gateway_status', 'unknown')}")
                    logger.info(f"🤖 Total agents: {metrics.get('total_agents', 0)}")
                    logger.info(f"✅ Healthy agents: {metrics.get('healthy_agents', 0)}")
                
                # List all agents
                agents_response = await client.get(f"{self.gateway_url}/agents")
                if agents_response.status_code == 200:
                    agents_data = agents_response.json()
                    agents = agents_data.get('agents', [])
                    
                    logger.info("📋 Registered agents:")
                    for agent in agents:
                        name = agent.get('name', 'Unknown')
                        status = agent.get('status', 'Unknown')
                        version = agent.get('version', 'Unknown')
                        logger.info(f"  - {name} (v{version}): {status}")
                
        except Exception as e:
            logger.error(f"Failed to check system status: {e}")

async def main():
    """Main demo function"""
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=''),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    demo = BrunoAIDemo()
    
    print("\n" + "="*60)
    print("🐻 BRUNO AI V2.0 OPTIMIZED SYSTEM DEMO")
    print("="*60)
    
    try:
        # Check system status first
        await demo.check_system_status()
        print("\n" + "-"*60)
        
        # Run the demo
        await demo.run_demo()
        
        print("\n" + "="*60)
        print("🎉 Demo completed successfully!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print("\n" + "="*60)
        print("❌ Demo failed. Make sure the Bruno AI system is running.")
        print("Run: python agents/v2/main.py")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
