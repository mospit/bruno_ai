#!/usr/bin/env python3
"""
Test script to demonstrate Bruno's personality variants
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.v2.bruno_personality_variants import bruno_variants, create_personality_response

def test_personality_variants():
    """Test all personality variants with sample responses"""
    
    print("=== Bruno AI Personality Variants Test ===\n")
    
    # Test data
    test_data = {
        "user_name": "Marcus",
        "budget": 75,
        "total_cost": 72.50,
        "savings": 2.50,
        "recipe_name": "Chicken Stir-Fry"
    }
    
    # Test each personality variant
    personalities = bruno_variants.list_available_variants()
    
    for personality in personalities:
        print(f"🐻 {personality.upper().replace('_', ' ')} PERSONALITY:")
        print(f"Description: {bruno_variants.get_variant_description(personality)}")
        print("-" * 60)
        
        # Test greeting
        greeting = create_personality_response(
            personality=personality,
            content_type="greeting",
            data=test_data
        )
        print(f"Greeting: {greeting}\n")
        
        # Test budget analysis
        budget_response = create_personality_response(
            personality=personality,
            content_type="budget_analysis",
            data=test_data
        )
        print(f"Budget Analysis: {budget_response}\n")
        
        # Test shopping response
        shopping_response = create_personality_response(
            personality=personality,
            content_type="shopping_list",
            data=test_data
        )
        print(f"Shopping List: {shopping_response}\n")
        
        print("=" * 80)
        print()

def test_message_enhancement():
    """Test message enhancement with different personalities"""
    
    print("=== Message Enhancement Test ===\n")
    
    test_messages = [
        "I recommend this recipe for your family.",
        "You can save money by buying in bulk.",
        "This meal plan will help you eat healthier.",
        "Let's create a shopping list for you."
    ]
    
    personalities = bruno_variants.list_available_variants()
    
    for message in test_messages:
        print(f"Original: {message}")
        print("-" * 40)
        
        for personality in personalities:
            enhanced = bruno_variants.enhance_message_with_variant(
                message, personality, {"budget_context": True}
            )
            print(f"{personality.title().replace('_', ' ')}: {enhanced}")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_personality_variants()
    test_message_enhancement()
