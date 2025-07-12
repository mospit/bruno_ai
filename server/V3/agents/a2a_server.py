"""
A2A Server Implementation for Bruno AI V3.1
Exposes agents via FastA2A protocol for agent-to-agent communication
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from base_agent import BaseAgent
from dotenv import load_dotenv

# Note: This is a simplified A2A server implementation
# In production, you would use the actual FastA2A library

load_dotenv()

class A2AServer:
    """A2A Server for exposing Bruno AI agents via FastA2A protocol"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("bruno.a2a_server")
        
    async def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent with the A2A server"""
        self.agents[agent_id] = agent
        self.logger.info(f"Agent {agent_id} registered with A2A server")
        
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from the A2A server"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Agent {agent_id} unregistered from A2A server")
            
    async def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A messages"""
        try:
            # Extract message components
            target_agent = message.get('target_agent')
            query = message.get('query')
            context_id = message.get('context_id')
            source_agent = message.get('source_agent')
            
            if not target_agent or not query:
                return {
                    'status': 'error',
                    'message': 'Missing required fields: target_agent, query'
                }
                
            # Check if target agent exists
            if target_agent not in self.agents:
                return {
                    'status': 'error',
                    'message': f'Agent {target_agent} not found'
                }
                
            # Process the query with the target agent
            agent = self.agents[target_agent]
            result = await agent.process_with_optimization(query, context_id)
            
            # Log the interaction
            self.logger.info(f"A2A message from {source_agent} to {target_agent}: {query[:50]}...")
            
            return {
                'status': 'success',
                'result': result,
                'target_agent': target_agent,
                'source_agent': source_agent,
                'context_id': context_id
            }
            
        except Exception as e:
            self.logger.error(f"A2A message handling failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def start_server(self):
        """Start the A2A server"""
        # This is a simplified implementation
        # In production, you would integrate with FastA2A library
        self.logger.info(f"A2A Server starting on port {self.port}")
        
        # For now, just demonstrate the concept
        await self._demo_a2a_communication()
    
    async def _demo_a2a_communication(self):
        """Demonstrate A2A communication between agents"""
        try:
            # Create demo agents
            meal_planner = BaseAgent(
                "meal_planner",
                "claude-3-5-haiku-20241022",
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai')
            )
            
            grocery_assistant = BaseAgent(
                "grocery_assistant", 
                "claude-3-5-haiku-20241022",
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai')
            )
            
            # Register agents
            await self.register_agent("meal_planner", meal_planner)
            await self.register_agent("grocery_assistant", grocery_assistant)
            
            # Demo A2A communication
            self.logger.info("Demonstrating A2A communication...")
            
            # Meal planner asks grocery assistant for budget-friendly ingredients
            a2a_message = {
                'source_agent': 'meal_planner',
                'target_agent': 'grocery_assistant',
                'query': 'What are the most budget-friendly proteins available this week?',
                'context_id': 'demo_context'
            }
            
            response = await self.handle_a2a_message(a2a_message)
            self.logger.info(f"A2A Response: {response}")
            
        except Exception as e:
            self.logger.error(f"Demo A2A communication failed: {e}")

async def main():
    """Main function to run the A2A server"""
    logging.basicConfig(level=logging.INFO)
    
    server = A2AServer(port=8080)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
