import asyncio
import random
from datetime import datetime
from server.src.agents.v2.base_agent import BaseAgent, AgentCard
from server.src.agents.v2.cost_analytics import cost_analytics, CostEvent, CostCategory
from server.src.agents.v2.batch_processor import batch_processor, BatchPriority

# Initialize a sample agent card
agent_card = AgentCard(
    name="Test Agent",
    version="1.0.0",
    description="Agent for testing purposes",
    capabilities={},
    service_endpoint="",
    supported_protocols=["JSON-RPC 2.0"],
    authentication_required=False
)

# Create test agent
class TestAgent(BaseAgent):
    async def execute_task(self, task):
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return {"success": True, "processed_at": datetime.now().isoformat()}

# Instantiate test agent
agent = TestAgent(agent_card)

# Define test workloads
workloads = [
    {"action": "plan_meal", "complexity": "complex", "tokens": {"input": 500, "output": 800}},
    {"action": "update_pantry", "complexity": "simple", "tokens": {"input": 100, "output": 200}},
    {"action": "budget_analysis", "complexity": "moderate", "tokens": {"input": 300, "output": 400}}
]

async def run_tests():
    for workload in workloads:
        task = {
            "action": workload["action"],
            "context": {},
            "user_id": "test_user",
            "tokens": workload["tokens"]
        }

        # Use different methods based on complexity for the illustration
        if workload["complexity"] == "simple":
            prompt = "Simulate simple task with minimal processing"
        elif workload["complexity"] == "moderate":
            prompt = "Simulate moderate task with standard processing"
        else:
            prompt = "Simulate complex task with extensive processing"

        result = await agent.call_smart_model(prompt, task_type=workload["action"], context=task)
        
        # Track cost event
        event = CostEvent(
            timestamp=datetime.now(),
            category=CostCategory.MODEL_USAGE,
            model_type=agent.model_router.get_model_for_task(workload["action"]).name,
            task_type=workload["action"],
            input_tokens=workload["tokens"]["input"],
            output_tokens=workload["tokens"]["output"],
            estimated_cost=0.0,
            user_id=task["user_id"],
            agent_name=agent_card.name,
            was_cached=False,
            was_batched=False
        )
        await cost_analytics.track_cost_event(event)

        print(f"Task: {workload['action']}, Result: {result}, Estimated Cost: ${event.estimated_cost:.4f}")

# Execute the test suite
asyncio.run(run_tests())
