#!/usr/bin/env python3
"""
Test script to demonstrate Bruno's comprehensive personality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.v2.bruno_comprehensive_personality import bruno_comprehensive, create_comprehensive_response

def test_comprehensive_personality():
    """Test the comprehensive personality with various scenarios"""
    
    print("=== Bruno AI Comprehensive Personality Test ===\n")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Budget-focused user",
            "message": "I need to save money on groceries",
            "data": {"budget": 50, "family_size": 3}
        },
        {
            "name": "Health-conscious user", 
            "message": "I want healthy meals for my family",
            "data": {"family_size": 4, "dietary_restrictions": ["vegetarian"]}
        },
        {
            "name": "Cooking enthusiast",
            "message": "I love cooking and want delicious recipes",
            "data": {"budget": 100, "family_size": 2}
        },
        {
            "name": "Multi-context user",
            "message": "I need budget-friendly healthy recipes that taste great",
            "data": {"budget": 75, "family_size": 4}
        }
    ]
    
    for scenario in scenarios:
        print(f"🐻 {scenario['name'].upper()}:")
        print(f"Message: \"{scenario['message']}\"")
        print("-" * 60)
        
        # Test greeting
        greeting = create_comprehensive_response(
            content_type="greeting",
            data=scenario["data"],
            message=scenario["message"]
        )
        print(f"Greeting Response:\n{greeting}\n")
        
        # Test budget analysis
        budget_data = {**scenario["data"], "total_cost": 68.50, "savings": 6.50}
        budget_response = create_comprehensive_response(
            content_type="budget_analysis",
            data=budget_data,
            message=scenario["message"]
        )
        print(f"Budget Analysis:\n{budget_response}\n")
        
        # Test meal planning
        meal_data = {**scenario["data"], "recipes_created": 5}
        meal_response = create_comprehensive_response(
            content_type="meal_planning",
            data=meal_data,
            message=scenario["message"]
        )
        print(f"Meal Planning:\n{meal_response}\n")
        
        print("=" * 80)
        print()

def test_context_detection():
    """Test context detection capabilities"""
    
    print("=== Context Detection Test ===\n")
    
    test_messages = [
        "I need to save money on my grocery budget",
        "I want healthy, nutritious meals for my family",
        "I love cooking and want delicious recipes",
        "I need affordable healthy recipes that taste amazing",
        "Help me plan meals"
    ]
    
    for message in test_messages:
        contexts = bruno_comprehensive.detect_primary_context(message)
        print(f"Message: \"{message}\"")
        print(f"Detected contexts: {contexts}")
        print("-" * 40)

def test_message_enhancement():
    """Test message enhancement with comprehensive personality"""
    
    print("\n=== Message Enhancement Test ===\n")
    
    test_messages = [
        "I recommend this recipe for your family.",
        "You can save money by buying in bulk.",
        "This meal plan will help you eat healthier.",
        "Let's create a shopping list for you.",
        "This approach should work well for your budget."
    ]
    
    for message in test_messages:
        enhanced = bruno_comprehensive.enhance_message_comprehensively(
            message, 
            contexts=["budget", "health", "food"]
        )
        print(f"Original: {message}")
        print(f"Enhanced: {enhanced}")
        print("-" * 60)

if __name__ == "__main__":
    test_comprehensive_personality()
    test_context_detection()
    test_message_enhancement()
