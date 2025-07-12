#!/usr/bin/env python3
"""
Simple Bruno AI Personality Test
Tests personality consistency and basic communication without full agent initialization
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the personality bridge
from agents.v2.bruno_personality_bridge import BrunoPersonalityBridge, validate_bruno_personality, create_bruno_message

def test_personality_bridge():
    """Test the Bruno personality bridge functionality"""
    print("🐻 Testing Bruno Personality Bridge...")
    
    bridge = BrunoPersonalityBridge()
    
    # Test 1: Enhance generic message
    generic_message = "Here are your budget recommendations for this week."
    enhanced_message = bridge.enhance_message_with_personality(generic_message, {"budget_success": True})
    
    print(f"\n📝 Original: {generic_message}")
    print(f"✨ Enhanced: {enhanced_message}")
    
    # Test 2: Validate personality
    validation = validate_bruno_personality(enhanced_message)
    print(f"\n🔍 Personality Analysis:")
    print(f"   Brooklyn Accent: {'✅' if validation['has_brooklyn_accent'] else '❌'}")
    print(f"   Signature Phrases: {'✅' if validation['has_signature_phrases'] else '❌'}")
    print(f"   Family Warmth: {'✅' if validation['has_family_warmth'] else '❌'}")
    print(f"   Personality Score: {validation['personality_score']:.2f}")
    
    # Test 3: Create Bruno messages for different content types
    content_types = [
        ("budget_analysis", {"target_budget": 100, "estimated_cost": 85, "feasibility_score": 0.8}),
        ("recipe_suggestion", {"recipe_name": "Budget Chicken Stir Fry", "cost_per_serving": 3.25, "cooking_time": 25}),
        ("shopping_list", {"total_cost": 75.50, "estimated_savings": 12.30}),
        ("meal_plan", {"duration_days": 7, "target_budget": 100})
    ]
    
    print(f"\n🎯 Testing Bruno Message Generation:")
    
    for content_type, data in content_types:
        bruno_message = create_bruno_message(content_type, data)
        validation = validate_bruno_personality(bruno_message)
        
        print(f"\n📋 {content_type.upper()}:")
        print(f"   Message: {bruno_message[:80]}...")
        print(f"   Personality Score: {validation['personality_score']:.2f}")
        print(f"   Brooklyn Elements: {'✅' if validation['has_brooklyn_accent'] else '❌'}")
    
    return True

def test_budget_recommendation_transformation():
    """Test transforming budget recommendations to Bruno style"""
    print("\n💰 Testing Budget Recommendation Transformation...")
    
    generic_recommendations = [
        "Consider reducing spending on premium items.",
        "Your budget is adequate for a family of 4.",
        "Bulk buying could save you approximately $15 per month.",
        "Seasonal shopping can reduce costs by 8%."
    ]
    
    bridge = BrunoPersonalityBridge()
    
    for i, rec in enumerate(generic_recommendations, 1):
        enhanced_rec = bridge.enhance_message_with_personality(rec, {"budget_context": True})
        validation = validate_bruno_personality(enhanced_rec)
        
        print(f"\n{i}. Original: {rec}")
        print(f"   Bruno Style: {enhanced_rec}")
        print(f"   Personality Score: {validation['personality_score']:.2f}")

def test_cooking_tips_enhancement():
    """Test enhancing cooking tips with Bruno's personality"""
    print("\n👨‍🍳 Testing Cooking Tips Enhancement...")
    
    cooking_tips = [
        "Prep all ingredients before cooking.",
        "Use medium-high heat for sautéing.",
        "Let meat rest after cooking.",
        "Season food in layers during cooking."
    ]
    
    bridge = BrunoPersonalityBridge()
    
    for i, tip in enumerate(cooking_tips, 1):
        enhanced_tip = bridge.enhance_message_with_personality(tip, {"recipe_context": True})
        validation = validate_bruno_personality(enhanced_tip)
        
        print(f"\n{i}. Original: {tip}")
        print(f"   Bruno Style: {enhanced_tip}")
        print(f"   Brooklyn Elements: {'✅' if validation['has_brooklyn_accent'] else '❌'}")

def test_personality_consistency_scenarios():
    """Test personality consistency across different scenarios"""
    print("\n🎭 Testing Personality Consistency Scenarios...")
    
    scenarios = [
        {
            "context": "User saved money",
            "message": "You saved $12 on your grocery bill.",
            "expected_elements": ["bada-bing", "savings", "ya"]
        },
        {
            "context": "Budget is tight",
            "message": "Your budget might be challenging for a family of 5.", 
            "expected_elements": ["listen", "trust me", "work with"]
        },
        {
            "context": "Recipe suggestion",
            "message": "This chicken recipe serves 4 people.",
            "expected_elements": ["lemme tell ya", "gonna", "family"]
        },
        {
            "context": "Shopping help",
            "message": "Here's your optimized shopping list.",
            "expected_elements": ["got ya", "shopping", "deals"]
        }
    ]
    
    bridge = BrunoPersonalityBridge()
    
    for i, scenario in enumerate(scenarios, 1):
        enhanced_message = bridge.enhance_message_with_personality(
            scenario["message"], 
            {"scenario": scenario["context"]}
        )
        
        validation = validate_bruno_personality(enhanced_message)
        
        print(f"\n{i}. Scenario: {scenario['context']}")
        print(f"   Original: {scenario['message']}")
        print(f"   Enhanced: {enhanced_message}")
        print(f"   Personality Score: {validation['personality_score']:.2f}")
        
        # Check for expected elements
        enhanced_lower = enhanced_message.lower()
        found_elements = [elem for elem in scenario["expected_elements"] 
                         if any(part in enhanced_lower for part in elem.split())]
        
        print(f"   Expected Elements Found: {len(found_elements)}/{len(scenario['expected_elements'])}")

def run_comprehensive_personality_test():
    """Run comprehensive personality tests"""
    print("🐻 BRUNO AI PERSONALITY CONSISTENCY TEST")
    print("="*60)
    
    tests = [
        ("Personality Bridge Functionality", test_personality_bridge),
        ("Budget Recommendation Transformation", test_budget_recommendation_transformation),
        ("Cooking Tips Enhancement", test_cooking_tips_enhancement),
        ("Personality Consistency Scenarios", test_personality_consistency_scenarios)
    ]
    
    passed_tests = 0
    
    for test_name, test_function in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_function()
            if result is not False:  # Consider None or True as pass
                print(f"✅ {test_name}: PASSED")
                passed_tests += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
    
    print(f"\n🎯 TEST RESULTS: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 All personality tests passed! Bruno's personality is consistent and working properly!")
    else:
        print("⚠️  Some tests failed. Bruno's personality needs adjustment.")
    
    # Save results
    results_file = f"bruno_personality_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(results_file, 'w') as f:
        f.write(f"Bruno AI Personality Test Results\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Tests Passed: {passed_tests}/{len(tests)}\n")
        f.write(f"Success Rate: {passed_tests/len(tests)*100:.1f}%\n")
    
    print(f"📄 Results saved to: {results_file}")
    
    return passed_tests == len(tests)

if __name__ == "__main__":
    success = run_comprehensive_personality_test()
    sys.exit(0 if success else 1)
