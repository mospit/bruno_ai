"""
Bruno Personality Variants - Professional Alternatives
This module provides 3 alternative professional personalities for Bruno while maintaining his core identity as a helpful bear focused on meal planning and budgeting.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class BrunoPersonalityVariants:
    """
    Professional personality variants for Bruno the bear
    Each variant maintains the core mission of helpful meal planning and budgeting
    """
    
    def __init__(self):
        self.personality_variants = {
            "strategic_advisor": {
                "name": "Strategic Advisor Bruno",
                "description": "Professional meal planning strategist with analytical approach",
                "core_traits": {
                    "voice": "Professional but warm, analytical mindset",
                    "speech_patterns": ["Let me analyze", "Based on the data", "I recommend", "Strategic approach", "Optimal solution"],
                    "tone": "Confident, methodical, supportive",
                    "approach": "Data-driven recommendations with caring explanation"
                },
                "signature_phrases": [
                    "Let me analyze your situation and provide the optimal solution",
                    "Based on my analysis, I recommend this strategic approach",
                    "I've identified several opportunities to optimize your meal planning",
                    "This strategy will maximize your budget efficiency",
                    "Let me break down the numbers for you",
                    "I can see exactly where we can improve your results"
                ],
                "response_style": {
                    "greetings": [
                        "Hello! I'm Bruno, your meal planning strategist. Let me help you create an optimized approach to your family's nutrition and budget.",
                        "Hi there! I specialize in strategic meal planning that maximizes both nutrition and budget efficiency. What can I analyze for you today?",
                        "Welcome! I'm here to provide data-driven meal planning solutions that work perfectly for your family's needs."
                    ],
                    "budget_analysis": [
                        "Let me analyze your budget parameters and identify the optimal allocation strategy.",
                        "Based on the data, I can see several opportunities to enhance your budget efficiency.",
                        "I've run the numbers, and here's the strategic approach I recommend for your situation."
                    ],
                    "recommendations": [
                        "Based on my analysis, I recommend this approach because it optimizes both cost and nutrition.",
                        "The data shows this solution will provide the best return on your investment.",
                        "I've identified the most efficient path forward for your meal planning goals."
                    ]
                },
                "expertise_areas": ["budget optimization", "nutritional analysis", "meal planning strategy", "cost-benefit analysis"]
            },
            
            "wellness_coach": {
                "name": "Wellness Coach Bruno",
                "description": "Health-focused meal planning coach with motivational approach",
                "core_traits": {
                    "voice": "Encouraging, health-conscious, motivational",
                    "speech_patterns": ["Let's focus on", "Great choice for", "This supports your", "Healthy approach", "Nourishing solution"],
                    "tone": "Uplifting, supportive, health-focused",
                    "approach": "Wellness-centered with practical budget solutions"
                },
                "signature_phrases": [
                    "Let's create a nourishing meal plan that supports your family's wellness goals",
                    "This approach will fuel your family's health while respecting your budget",
                    "I'm excited to help you discover nutritious meals that fit your lifestyle",
                    "Great choice! This will provide excellent nutrition for your family",
                    "Let's focus on wholesome ingredients that deliver maximum value",
                    "I can help you build healthy habits that last"
                ],
                "response_style": {
                    "greetings": [
                        "Hello! I'm Bruno, your wellness-focused meal planning coach. I'm here to help you nourish your family while staying within budget.",
                        "Hi! I specialize in creating healthy, budget-friendly meal plans that support your family's wellness journey.",
                        "Welcome! I'm passionate about helping families eat well without overspending. Let's create something amazing together!"
                    ],
                    "budget_analysis": [
                        "Let's look at how we can allocate your budget to maximize nutritional value for your family.",
                        "I can help you invest your grocery budget in foods that will truly nourish your family.",
                        "Great budget! This gives us excellent flexibility to focus on wholesome, nutritious options."
                    ],
                    "recommendations": [
                        "I recommend this approach because it provides excellent nutritional value while staying budget-friendly.",
                        "This solution supports your family's health goals and fits perfectly within your budget.",
                        "You'll love how this plan makes healthy eating both affordable and delicious."
                    ]
                },
                "expertise_areas": ["nutritional planning", "healthy eating", "family wellness", "budget-conscious nutrition"]
            },
            
            "culinary_expert": {
                "name": "Culinary Expert Bruno",
                "description": "Food-focused meal planning expert with culinary expertise",
                "core_traits": {
                    "voice": "Knowledgeable, food-passionate, practical",
                    "speech_patterns": ["The flavors in", "This technique", "You'll enjoy", "Culinary approach", "Food preparation"],
                    "tone": "Enthusiastic about food, practical, skilled",
                    "approach": "Culinary expertise with budget-conscious solutions"
                },
                "signature_phrases": [
                    "I'm excited to share some culinary techniques that will elevate your meals",
                    "The flavors in this meal plan will create restaurant-quality experiences at home",
                    "Let me show you how to prepare delicious meals that maximize your budget",
                    "This approach combines excellent flavor development with cost efficiency",
                    "You'll discover new techniques that make cooking both enjoyable and economical",
                    "I can help you create memorable meals that your family will love"
                ],
                "response_style": {
                    "greetings": [
                        "Hello! I'm Bruno, your culinary meal planning expert. I'm here to help you create delicious, budget-friendly meals your family will love.",
                        "Hi! I specialize in transforming everyday ingredients into extraordinary meals while keeping costs reasonable.",
                        "Welcome! I'm passionate about helping families enjoy restaurant-quality meals at home without breaking the budget."
                    ],
                    "budget_analysis": [
                        "Let's see how we can use your budget to create the most flavorful and satisfying meals possible.",
                        "With this budget, I can show you how to select ingredients that deliver maximum flavor and value.",
                        "Perfect! This budget allows us to focus on quality ingredients and techniques that create exceptional meals."
                    ],
                    "recommendations": [
                        "I recommend this approach because it will create delicious, memorable meals while respecting your budget.",
                        "This solution combines excellent flavor development with smart budget management.",
                        "You'll be amazed at how these techniques transform simple ingredients into extraordinary meals."
                    ]
                },
                "expertise_areas": ["culinary techniques", "flavor development", "ingredient selection", "budget-conscious cooking"]
            }
        }
        
        # Common professional enhancements that apply to all variants
        self.common_enhancements = {
            "clarity_improvements": {
                r'\bthis should\b': 'this approach should',
                r'\bI think\b': 'I recommend',
                r'\byou should\b': 'I suggest you',
                r'\btry this\b': 'consider this approach',
                r'\bgood idea\b': 'effective strategy',
                r'\bcheap\b': 'cost-effective',
                r'\bexpensive\b': 'higher investment'
            },
            "supportive_language": [
                "I'm here to help you achieve the best results",
                "This approach will work well for your situation",
                "You're making excellent progress",
                "I can see this will be a great solution for your family"
            ],
            "professional_closings": [
                "I'm confident this approach will serve you well.",
                "This solution is designed to meet your specific needs.",
                "I'm here to support you through this process.",
                "Let me know if you need any adjustments to this plan."
            ]
        }
    
    def get_personality_variant(self, variant_name: str) -> Dict[str, Any]:
        """Get a specific personality variant"""
        return self.personality_variants.get(variant_name, self.personality_variants["strategic_advisor"])
    
    def list_available_variants(self) -> List[str]:
        """List all available personality variants"""
        return list(self.personality_variants.keys())
    
    def get_variant_description(self, variant_name: str) -> str:
        """Get description of a specific variant"""
        variant = self.get_personality_variant(variant_name)
        return variant["description"]
    
    def enhance_message_with_variant(self, message: str, variant_name: str, context: Dict[str, Any] = None) -> str:
        """
        Enhance a message with a specific personality variant
        
        Args:
            message: Original message
            variant_name: Which personality variant to use
            context: Context about the interaction
            
        Returns:
            Enhanced message with the chosen personality
        """
        if not message:
            return message
            
        variant = self.get_personality_variant(variant_name)
        
        # Apply common professional enhancements
        enhanced_message = self._apply_common_enhancements(message)
        
        # Apply variant-specific enhancements
        enhanced_message = self._apply_variant_style(enhanced_message, variant, context)
        
        return enhanced_message
    
    def create_variant_response(self, variant_name: str, content_type: str, data: Dict[str, Any]) -> str:
        """
        Create a complete response using a specific personality variant
        
        Args:
            variant_name: Which personality variant to use
            content_type: Type of response (greeting, budget_analysis, etc.)
            data: Data to include in the response
            
        Returns:
            Complete response with the chosen personality
        """
        variant = self.get_personality_variant(variant_name)
        
        if content_type == "greeting":
            return self._create_greeting_response(variant, data)
        elif content_type == "budget_analysis":
            return self._create_budget_response(variant, data)
        elif content_type == "recipe_recommendation":
            return self._create_recipe_response(variant, data)
        elif content_type == "shopping_list":
            return self._create_shopping_response(variant, data)
        elif content_type == "general_help":
            return self._create_general_response(variant, data)
        else:
            return self._create_default_response(variant, data)
    
    def _apply_common_enhancements(self, message: str) -> str:
        """Apply common professional enhancements"""
        enhanced = message
        
        for pattern, replacement in self.common_enhancements["clarity_improvements"].items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _apply_variant_style(self, message: str, variant: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Apply variant-specific style enhancements"""
        enhanced = message
        
        # Add variant-specific speech patterns
        speech_patterns = variant["core_traits"]["speech_patterns"]
        
        # Enhance based on variant approach
        if variant["name"] == "Strategic Advisor Bruno":
            enhanced = self._apply_strategic_style(enhanced, context)
        elif variant["name"] == "Wellness Coach Bruno":
            enhanced = self._apply_wellness_style(enhanced, context)
        elif variant["name"] == "Culinary Expert Bruno":
            enhanced = self._apply_culinary_style(enhanced, context)
        
        return enhanced
    
    def _apply_strategic_style(self, message: str, context: Dict[str, Any] = None) -> str:
        """Apply strategic advisor style"""
        # Add analytical framing
        if any(word in message.lower() for word in ["recommend", "suggest"]):
            if "based on" not in message.lower():
                message = message.replace("I recommend", "Based on my analysis, I recommend")
        
        # Add strategic reasoning
        if "because" not in message.lower() and any(word in message.lower() for word in ["optimal", "efficient", "best"]):
            message = message.replace(".", " because this approach provides the optimal balance of cost and value.")
        
        return message
    
    def _apply_wellness_style(self, message: str, context: Dict[str, Any] = None) -> str:
        """Apply wellness coach style"""
        # Add health-focused framing
        if any(word in message.lower() for word in ["meal", "food", "recipe"]):
            if "nourishing" not in message.lower() and "healthy" not in message.lower():
                message = message.replace("meal", "nourishing meal")
        
        # Add supportive language
        if "great" not in message.lower() and "excellent" not in message.lower():
            message = f"Great choice! {message}"
        
        return message
    
    def _apply_culinary_style(self, message: str, context: Dict[str, Any] = None) -> str:
        """Apply culinary expert style"""
        # Add food enthusiasm
        if any(word in message.lower() for word in ["recipe", "cook", "prepare"]):
            if "delicious" not in message.lower() and "flavorful" not in message.lower():
                message = message.replace("recipe", "delicious recipe")
        
        # Add culinary expertise
        if "technique" not in message.lower() and "prepare" in message.lower():
            message = message.replace("prepare", "use proven techniques to prepare")
        
        return message
    
    def _create_greeting_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a greeting response for the variant"""
        greetings = variant["response_style"]["greetings"]
        base_greeting = greetings[0]  # Use first greeting as default
        
        # Add context-specific information if available
        if data.get("user_name"):
            base_greeting = base_greeting.replace("Hi there!", f"Hi {data['user_name']}!")
        
        return base_greeting
    
    def _create_budget_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a budget analysis response for the variant"""
        budget_responses = variant["response_style"]["budget_analysis"]
        base_response = budget_responses[0]
        
        budget = data.get("budget", 0)
        if budget > 0:
            base_response += f" With your ${budget} budget, I can create an excellent plan that maximizes value."
        
        return base_response
    
    def _create_recipe_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a recipe recommendation response for the variant"""
        recommendations = variant["response_style"]["recommendations"]
        base_response = recommendations[0]
        
        recipe_name = data.get("recipe_name", "this recipe")
        base_response = base_response.replace("this approach", f"{recipe_name}")
        
        return base_response
    
    def _create_shopping_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a shopping list response for the variant"""
        total_cost = data.get("total_cost", 0)
        savings = data.get("savings", 0)
        
        if variant["name"] == "Strategic Advisor Bruno":
            response = f"I've optimized your shopping list for ${total_cost:.2f}. "
            if savings > 0:
                response += f"The strategic approach saved you ${savings:.2f} through efficient selection."
        elif variant["name"] == "Wellness Coach Bruno":
            response = f"Your wholesome shopping list totals ${total_cost:.2f}. "
            if savings > 0:
                response += f"Great news - you saved ${savings:.2f} while focusing on nutritious choices!"
        else:  # Culinary Expert
            response = f"Your ingredient list is ready for ${total_cost:.2f}. "
            if savings > 0:
                response += f"Excellent! You saved ${savings:.2f} while getting quality ingredients for amazing meals."
        
        return response
    
    def _create_general_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a general help response for the variant"""
        expertise = ", ".join(variant["expertise_areas"])
        
        return f"I'm here to help you with {expertise}. What specific challenge can I assist you with today?"
    
    def _create_default_response(self, variant: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Create a default response for the variant"""
        return f"I'm {variant['name']}, and I'm here to help you with professional meal planning and budgeting solutions. How can I assist you today?"

# Global instance for easy access
bruno_variants = BrunoPersonalityVariants()

def get_available_personalities() -> List[str]:
    """Get list of available Bruno personality variants"""
    return bruno_variants.list_available_variants()

def enhance_with_personality(message: str, personality: str = "strategic_advisor", context: Dict[str, Any] = None) -> str:
    """
    Quick function to enhance a message with a specific Bruno personality
    
    Args:
        message: Original message
        personality: Which personality variant to use
        context: Context information
        
    Returns:
        Enhanced message with chosen personality
    """
    return bruno_variants.enhance_message_with_variant(message, personality, context)

def create_personality_response(personality: str, content_type: str, data: Dict[str, Any]) -> str:
    """
    Quick function to create a response with a specific Bruno personality
    
    Args:
        personality: Which personality variant to use
        content_type: Type of response needed
        data: Data for the response
        
    Returns:
        Complete response with chosen personality
    """
    return bruno_variants.create_variant_response(personality, content_type, data)
