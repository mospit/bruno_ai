#!/usr/bin/env python3
"""
Mock Bruno AI Server for Integration Testing
Provides a simple mock server that responds to agent requests
"""

import json
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

app = FastAPI(title="Mock Bruno AI Gateway", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    action: str
    context: Dict[str, Any]
    message: Optional[str] = ""
    priority: str = "normal"
    timeout: int = 30

# Mock responses based on message content
def generate_mock_response(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock response based on message content"""
    message_lower = message.lower()
    
    # Budget setting response
    if "budget" in message_lower and "$" in message:
        import re
        budget_match = re.search(r'\$(\d+)', message)
        budget = budget_match.group(1) if budget_match else "80"
        
        return {
            "response": f"Perfect! I'll help you plan delicious meals within your ${budget} budget. Let me find the best deals for you! 🐻",
            "timestamp": datetime.now().isoformat(),
            "budget_info": {"budget": budget, "currency": "USD"},
            "actions": {
                "set_budget": budget
            },
            "agent_used": "bruno_master_agent"
        }
    
    # Recipe requests
    elif "recipe" in message_lower or "cook" in message_lower:
        return {
            "response": "Here's a great recipe for you! 🍳\n\n**Bruno's Budget Chicken Stir-Fry**\n- Prep time: 15 minutes\n- Serves: 4 people\n- Cost: $12.80\n\nIngredients:\n• 1 lb chicken breast\n• 2 cups mixed vegetables\n• 2 tbsp soy sauce\n• 1 tbsp oil\n\nReady to add ingredients to your cart?",
            "timestamp": datetime.now().isoformat(),
            "shopping_list": [
                {"name": "Chicken breast", "price": 8.99, "quantity": 1, "unit": "lb"},
                {"name": "Mixed vegetables", "price": 3.49, "quantity": 1, "unit": "bag"},
                {"name": "Soy sauce", "price": 2.99, "quantity": 1, "unit": "bottle"}
            ],
            "total_cost": 15.47,
            "agent_used": "recipe_chef_agent"
        }
    
    # Shopping/Instacart requests
    elif "instacart" in message_lower or "shop" in message_lower or "cart" in message_lower:
        return {
            "response": "Great! I've added everything to your shopping list. 🛒\n\n**Shopping List Ready:**\n• 4 items\n• Total: $21.96\n• Store: Whole Foods\n• Delivery: 2 hours\n\nYour Instacart cart is ready for checkout!",
            "timestamp": datetime.now().isoformat(),
            "shopping_list": [
                {"name": "Chicken breast", "price": 8.99, "quantity": 2, "unit": "lbs"},
                {"name": "Sweet potatoes", "price": 3.49, "quantity": 1, "unit": "bag"},
                {"name": "Broccoli", "price": 2.99, "quantity": 1, "unit": "bunch"},
                {"name": "Rice", "price": 6.49, "quantity": 1, "unit": "bag"}
            ],
            "total_cost": 21.96,
            "actions": {
                "create_instacart_cart": True
            },
            "agent_used": "instacart_integration_agent"
        }
    
    # Meal planning requests
    elif "plan" in message_lower or "meal" in message_lower:
        return {
            "response": "I've created a fantastic meal plan for you! 🗓️\n\n**This Week's Meals:**\n• Monday: Chicken Stir-Fry ($12.80)\n• Tuesday: Pasta Primavera ($10.50)\n• Wednesday: Taco Night ($14.25)\n• Thursday: Salmon & Veggies ($16.99)\n• Friday: Pizza Night ($13.75)\n\n**Total: $68.29** (under your $80 budget!)\n\nShall I add all ingredients to your cart?",
            "timestamp": datetime.now().isoformat(),
            "budget_info": {"spent": 68.29, "remaining": 11.71, "budget": 80},
            "meal_plan": {
                "meals": 5,
                "total_cost": 68.29,
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "agent_used": "bruno_master_agent"
        }
    
    # Dietary restrictions
    elif "vegetarian" in message_lower or "vegan" in message_lower or "gluten" in message_lower:
        return {
            "response": "I understand your dietary preferences! 🌱\n\nI'll make sure to suggest vegetarian and gluten-free options that fit your needs. Here are some great meal ideas:\n\n• Quinoa Buddha Bowl ($8.99)\n• Lentil Curry ($7.50)\n• Stuffed Bell Peppers ($9.25)\n\nAll recipes are vegetarian and gluten-free!",
            "timestamp": datetime.now().isoformat(),
            "dietary_info": {
                "restrictions": ["vegetarian", "gluten-free"],
                "options_found": 3
            },
            "agent_used": "nutrition_guide_agent"
        }
    
    # Default greeting/general response
    else:
        return {
            "response": "Hi! I'm Bruno, your friendly AI meal planning assistant! 🐻\n\nI can help you with:\n• Setting your weekly budget\n• Planning delicious meals\n• Creating shopping lists\n• Finding great recipes\n• Ordering through Instacart\n\nWhat would you like to do first?",
            "timestamp": datetime.now().isoformat(),
            "agent_used": "bruno_master_agent"
        }

@app.get("/gateway/health")
async def gateway_health():
    """Gateway health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "redis_connected": False,
        "mode": "mock"
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": [
            {
                "name": "bruno_master_agent",
                "status": "healthy",
                "url": "http://localhost:8080"
            },
            {
                "name": "instacart_integration_agent", 
                "status": "healthy",
                "url": "http://localhost:8081"
            },
            {
                "name": "recipe_chef_agent",
                "status": "healthy", 
                "url": "http://localhost:8083"
            }
        ],
        "total_count": 3,
        "healthy_count": 3
    }

@app.post("/agents/{agent_name}/task")
async def create_task(agent_name: str, task_data: TaskRequest):
    """Create a task for a specific agent"""
    
    # Simulate processing time
    time.sleep(0.5)
    
    message = task_data.message or task_data.context.get('message', '')
    context = task_data.context
    
    response = generate_mock_response(message, context)
    
    # Add some metadata
    response.update({
        "request_id": f"req_{int(time.time())}",
        "processing_time_ms": 500,
        "agent_name": agent_name
    })
    
    return response

@app.get("/agents/{agent_name}/health")
async def check_agent_health(agent_name: str):
    """Check health of a specific agent"""
    return {
        "status": "healthy",
        "agent": agent_name,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🐻 Starting Mock Bruno AI Server for Testing...")
    print("Gateway running on: http://localhost:3000")
    print("Use Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info"
    )
