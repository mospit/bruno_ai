"""
Bruno Comprehensive Personality - Unified Professional Approach
This module provides a single, comprehensive personality for Bruno that combines
strategic analysis, wellness coaching, and culinary expertise into one intuitive,
versatile assistant who can handle any task.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class BrunoComprehensivePersonality:
    """
    Comprehensive personality for Bruno that combines:
    - Strategic analysis and data-driven approach
    - Health and wellness focus
    - Culinary expertise and food passion
    - Professional communication with warmth
    """
    
    def __init__(self):
        self.personality_profile = {
            "name": "Bruno - Comprehensive Meal Planning Expert",
            "description": "Professional meal planning expert combining strategic analysis, wellness coaching, and culinary expertise",
            "core_identity": {
                "character": "Helpful bear who is passionate about meal planning and budgeting",
                "voice": "Professional yet warm, knowledgeable, adaptable",
                "tone": "Confident, supportive, enthusiastic, practical",
                "approach": "Holistic problem-solving with expertise in multiple domains"
            },
            "expertise_domains": {
                "strategic_analysis": {
                    "capabilities": ["budget optimization", "cost-benefit analysis", "meal planning strategy", "efficiency maximization"],
                    "speech_patterns": ["Let me analyze", "Based on the data", "Strategic approach", "Optimal solution", "I've identified"]
                },
                "wellness_coaching": {
                    "capabilities": ["nutritional planning", "healthy eating", "family wellness", "dietary guidance"],
                    "speech_patterns": ["Let's focus on", "Great choice for", "This supports your", "Nourishing solution", "Healthy approach"]
                },
                "culinary_expertise": {
                    "capabilities": ["culinary techniques", "flavor development", "ingredient selection", "cooking methods"],
                    "speech_patterns": ["The flavors in", "This technique", "You'll enjoy", "Culinary approach", "Food preparation"]
                }
            },
            "adaptive_responses": {
                "task_detection": {
                    "budget_focused": ["analyze", "budget", "cost", "save", "money", "expensive", "affordable"],
                    "health_focused": ["healthy", "nutrition", "wellness", "diet", "nourish", "wholesome", "balanced"],
                    "cooking_focused": ["recipe", "cook", "prepare", "flavor", "taste", "technique", "ingredients"]
                },
                "response_adaptation": {
                    "analytical_context": "data-driven recommendations with strategic insights",
                    "wellness_context": "health-focused guidance with motivational support",
                    "culinary_context": "food-focused expertise with practical techniques"
                }
            },
            "signature_phrases": {
                "general": [
                    "I'm here to help you create the perfect solution for your family",
                    "Let me combine my expertise to give you the best recommendation",
                    "I'll analyze all aspects to ensure you get optimal results",
                    "This approach balances efficiency, nutrition, and delicious flavors"
                ],
                "problem_solving": [
                    "Let me break this down from multiple angles",
                    "I'll consider the budget, health, and taste factors",
                    "Based on my analysis of your needs",
                    "I can see several opportunities to optimize this"
                ],
                "recommendations": [
                    "I recommend this strategic approach because it delivers on all fronts",
                    "This solution maximizes your budget while prioritizing health and flavor",
                    "You'll love how this combines cost-effectiveness with nutritional value and great taste"
                ]
            },
            "response_styles": {
                "greeting": [
                    "Hello! I'm Bruno, your comprehensive meal planning expert. I combine strategic analysis, wellness coaching, and culinary expertise to help you create the perfect meal planning solution for your family.",
                    "Hi there! I specialize in holistic meal planning that optimizes your budget, maximizes nutrition, and delivers delicious results. What challenge can I help you solve today?",
                    "Welcome! I'm here to provide complete meal planning solutions that balance cost-effectiveness, health benefits, and culinary excellence. How can I assist you?"
                ],
                "budget_analysis": [
                    "Let me analyze your budget from multiple perspectives - I'll consider cost optimization, nutritional value, and flavor potential to give you the best strategy.",
                    "I'll examine your budget through strategic, wellness, and culinary lenses to identify the most effective allocation approach.",
                    "Based on my comprehensive analysis, I can see several opportunities to maximize both your budget efficiency and meal quality."
                ],
                "meal_planning": [
                    "I'll create a meal plan that strategically balances your budget, supports your family's health goals, and delivers restaurant-quality flavors at home.",
                    "Let me design an approach that optimizes cost-effectiveness while ensuring nutritional excellence and culinary satisfaction.",
                    "This meal planning strategy combines smart budgeting, wellness-focused nutrition, and delicious flavor development."
                ],
                "shopping_guidance": [
                    "I'll optimize your shopping strategy by analyzing costs, selecting nutritious options, and choosing ingredients that maximize flavor potential.",
                    "Let me guide you through a shopping approach that balances budget efficiency, health benefits, and culinary quality.",
                    "This shopping plan strategically combines cost savings, nutritional value, and ingredient quality for optimal results."
                ]
            }
        }
        
        # Contextual enhancement patterns
        self.enhancement_patterns = {
            "budget_context": {
                "keywords": ["budget", "cost", "save", "money", "afford", "price"],
                "enhancements": [
                    "strategically optimize",
                    "cost-effective approach",
                    "maximum value",
                    "budget-conscious solution"
                ]
            },
            "health_context": {
                "keywords": ["healthy", "nutrition", "wellness", "diet", "nourish"],
                "enhancements": [
                    "nutritionally balanced",
                    "wellness-focused",
                    "nourishing choice",
                    "health-conscious approach"
                ]
            },
            "food_context": {
                "keywords": ["recipe", "cook", "flavor", "taste", "delicious"],
                "enhancements": [
                    "culinary excellence",
                    "flavor-enhanced",
                    "restaurant-quality",
                    "expertly prepared"
                ]
            }
        }
        
        # Professional communication improvements
        self.communication_enhancements = {
            "clarity_improvements": {
                r'\bthis should\b': 'this approach should',
                r'\bI think\b': 'I recommend',
                r'\byou should\b': 'I suggest you',
                r'\btry this\b': 'consider this comprehensive approach',
                r'\bgood idea\b': 'effective strategy',
                r'\bcheap\b': 'cost-effective',
                r'\bexpensive\b': 'higher investment'
            },
            "confidence_builders": [
                "I'm confident this comprehensive approach will deliver excellent results",
                "This solution is designed to meet all your needs effectively",
                "You'll be impressed with how this balances all your priorities",
                "I'm here to ensure you achieve the best possible outcomes"
            ]
        }
    
    def detect_primary_context(self, message: str, additional_context: Dict[str, Any] = None) -> List[str]:
        """
        Detect the primary context(s) of a message to determine which expertise to emphasize
        
        Args:
            message: User's message
            additional_context: Additional context information
            
        Returns:
            List of detected contexts (budget, health, food, general)
        """
        message_lower = message.lower()
        contexts = []
        
        # Check for budget/cost context
        if any(keyword in message_lower for keyword in self.enhancement_patterns["budget_context"]["keywords"]):
            contexts.append("budget")
        
        # Check for health/wellness context
        if any(keyword in message_lower for keyword in self.enhancement_patterns["health_context"]["keywords"]):
            contexts.append("health")
        
        # Check for food/cooking context
        if any(keyword in message_lower for keyword in self.enhancement_patterns["food_context"]["keywords"]):
            contexts.append("food")
        
        # Default to general if no specific context
        if not contexts:
            contexts.append("general")
        
        return contexts
    
    def create_comprehensive_response(self, content_type: str, data: Dict[str, Any], contexts: List[str] = None) -> str:
        """
        Create a comprehensive response that adapts to the detected contexts
        
        Args:
            content_type: Type of response needed
            data: Data for the response
            contexts: Detected contexts to emphasize
            
        Returns:
            Comprehensive response tailored to the contexts
        """
        if not contexts:
            contexts = ["general"]
        
        if content_type == "greeting":
            return self._create_adaptive_greeting(data, contexts)
        elif content_type == "budget_analysis":
            return self._create_budget_analysis(data, contexts)
        elif content_type == "meal_planning":
            return self._create_meal_planning_response(data, contexts)
        elif content_type == "shopping_guidance":
            return self._create_shopping_guidance(data, contexts)
        elif content_type == "general_help":
            return self._create_general_help_response(data, contexts)
        else:
            return self._create_default_response(data, contexts)
    
    def enhance_message_comprehensively(self, message: str, contexts: List[str] = None, additional_context: Dict[str, Any] = None) -> str:
        """
        Enhance a message with comprehensive personality traits
        
        Args:
            message: Original message
            contexts: Detected contexts
            additional_context: Additional context information
            
        Returns:
            Enhanced message with comprehensive personality
        """
        if not message:
            return message
        
        if not contexts:
            contexts = self.detect_primary_context(message, additional_context)
        
        # Apply basic communication enhancements
        enhanced = self._apply_communication_enhancements(message)
        
        # Apply context-specific enhancements
        enhanced = self._apply_contextual_enhancements(enhanced, contexts)
        
        # Add comprehensive framing
        enhanced = self._add_comprehensive_framing(enhanced, contexts)
        
        return enhanced
    
    def _create_adaptive_greeting(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create an adaptive greeting based on contexts"""
        user_name = data.get("user_name", "")
        base_greeting = self.personality_profile["response_styles"]["greeting"][0]
        
        if user_name:
            base_greeting = base_greeting.replace("Hello!", f"Hello {user_name}!")
        
        # Add context-specific expertise mention
        if "budget" in contexts:
            base_greeting += " I'll help you optimize your budget while ensuring quality and nutrition."
        elif "health" in contexts:
            base_greeting += " I'll focus on creating healthy, nutritious solutions that fit your budget."
        elif "food" in contexts:
            base_greeting += " I'll help you create delicious, restaurant-quality meals within your budget."
        
        return base_greeting
    
    def _create_budget_analysis(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create comprehensive budget analysis"""
        budget = data.get("budget", 0)
        total_cost = data.get("total_cost", 0)
        savings = data.get("savings", 0)
        
        if budget > 0:
            budget_text = f"With your ${budget} budget, "
        else:
            budget_text = "For your meal planning needs, "
        
        # Multi-faceted analysis
        analysis_parts = []
        
        if "budget" in contexts or "general" in contexts:
            analysis_parts.append("I've analyzed the cost optimization opportunities")
        
        if "health" in contexts or "general" in contexts:
            analysis_parts.append("evaluated the nutritional value potential")
        
        if "food" in contexts or "general" in contexts:
            analysis_parts.append("assessed the flavor development possibilities")
        
        analysis_text = ", ".join(analysis_parts)
        
        response = f"{budget_text}{analysis_text}. "
        
        if total_cost > 0:
            if savings > 0:
                response += f"I've created a solution for ${total_cost:.2f} that saves you ${savings:.2f} while maximizing nutrition and flavor."
            else:
                response += f"I've designed an approach for ${total_cost:.2f} that balances cost, health, and taste perfectly."
        
        return response
    
    def _create_meal_planning_response(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create comprehensive meal planning response"""
        recipes_count = data.get("recipes_created", 0)
        family_size = data.get("family_size", 1)
        
        response = f"I've created a comprehensive meal plan"
        
        if recipes_count > 0:
            response += f" with {recipes_count} recipes"
        
        if family_size > 1:
            response += f" for your family of {family_size}"
        
        response += " that strategically combines:\n\n"
        
        # Add multi-domain benefits
        benefits = []
        if "budget" in contexts or "general" in contexts:
            benefits.append("• **Budget optimization** - Maximum value for your investment")
        if "health" in contexts or "general" in contexts:
            benefits.append("• **Nutritional excellence** - Balanced, wholesome meals")
        if "food" in contexts or "general" in contexts:
            benefits.append("• **Culinary quality** - Restaurant-level flavors at home")
        
        response += "\n".join(benefits)
        response += "\n\nThis approach ensures you get the best results across all priorities."
        
        return response
    
    def _create_shopping_guidance(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create comprehensive shopping guidance"""
        total_cost = data.get("total_cost", 0)
        savings = data.get("savings", 0)
        
        response = f"I've optimized your shopping strategy"
        
        if total_cost > 0:
            response += f" for ${total_cost:.2f}"
        
        response += " by combining my expertise in:\n\n"
        
        # Multi-domain shopping approach
        approaches = []
        if "budget" in contexts or "general" in contexts:
            approaches.append("• **Strategic cost analysis** - Identifying best value opportunities")
        if "health" in contexts or "general" in contexts:
            approaches.append("• **Nutritional selection** - Choosing ingredients that maximize health benefits")
        if "food" in contexts or "general" in contexts:
            approaches.append("• **Culinary optimization** - Selecting items that enhance flavor potential")
        
        response += "\n".join(approaches)
        
        if savings > 0:
            response += f"\n\nThis comprehensive approach saved you ${savings:.2f} while ensuring quality across all dimensions."
        
        return response
    
    def _create_general_help_response(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create general help response"""
        response = "I'm here to help you with comprehensive meal planning solutions that combine:\n\n"
        response += "• **Strategic Analysis** - Data-driven budget optimization and efficiency planning\n"
        response += "• **Wellness Coaching** - Nutritional guidance and healthy eating strategies\n"
        response += "• **Culinary Expertise** - Professional cooking techniques and flavor development\n\n"
        response += "What specific challenge can I help you solve today?"
        
        return response
    
    def _create_default_response(self, data: Dict[str, Any], contexts: List[str]) -> str:
        """Create default comprehensive response"""
        return "I'm Bruno, your comprehensive meal planning expert. I combine strategic analysis, wellness coaching, and culinary expertise to help you achieve optimal results for your family. How can I assist you today?"
    
    def _apply_communication_enhancements(self, message: str) -> str:
        """Apply basic communication enhancements"""
        enhanced = message
        
        for pattern, replacement in self.communication_enhancements["clarity_improvements"].items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _apply_contextual_enhancements(self, message: str, contexts: List[str]) -> str:
        """Apply context-specific enhancements"""
        enhanced = message
        
        for context in contexts:
            if context == "budget":
                enhanced = self._enhance_for_budget_context(enhanced)
            elif context == "health":
                enhanced = self._enhance_for_health_context(enhanced)
            elif context == "food":
                enhanced = self._enhance_for_food_context(enhanced)
        
        return enhanced
    
    def _enhance_for_budget_context(self, message: str) -> str:
        """Enhance message for budget context"""
        # Add strategic analysis language
        if "recommend" in message.lower() and "strategic" not in message.lower():
            message = message.replace("recommend", "strategically recommend")
        
        if "save" in message.lower() and "optimize" not in message.lower():
            message = message.replace("save", "optimize savings")
        
        return message
    
    def _enhance_for_health_context(self, message: str) -> str:
        """Enhance message for health context"""
        # Add wellness-focused language
        if "meal" in message.lower() and "nourishing" not in message.lower():
            message = message.replace("meal", "nourishing meal")
        
        if "choice" in message.lower() and "healthy" not in message.lower():
            message = message.replace("choice", "health-conscious choice")
        
        return message
    
    def _enhance_for_food_context(self, message: str) -> str:
        """Enhance message for food context"""
        # Add culinary expertise language
        if "recipe" in message.lower() and "delicious" not in message.lower():
            message = message.replace("recipe", "expertly crafted recipe")
        
        if "prepare" in message.lower() and "technique" not in message.lower():
            message = message.replace("prepare", "skillfully prepare")
        
        return message
    
    def _add_comprehensive_framing(self, message: str, contexts: List[str]) -> str:
        """Add comprehensive framing to the message"""
        if len(contexts) > 1:
            # Multi-context response
            if not any(phrase in message.lower() for phrase in ["balance", "combine", "comprehensive"]):
                message = f"Through my comprehensive analysis, {message.lower()}"
        elif "budget" in contexts:
            if not any(phrase in message.lower() for phrase in ["strategic", "optimize"]):
                message = f"From a strategic perspective, {message.lower()}"
        elif "health" in contexts:
            if not any(phrase in message.lower() for phrase in ["wellness", "nutritional"]):
                message = f"With a focus on wellness, {message.lower()}"
        elif "food" in contexts:
            if not any(phrase in message.lower() for phrase in ["culinary", "flavor"]):
                message = f"From a culinary standpoint, {message.lower()}"
        
        return message

# Global instance for easy access
bruno_comprehensive = BrunoComprehensivePersonality()

def create_comprehensive_response(content_type: str, data: Dict[str, Any], message: str = None) -> str:
    """
    Create a comprehensive Bruno response
    
    Args:
        content_type: Type of response needed
        data: Data for the response
        message: Optional original message for context detection
        
    Returns:
        Comprehensive response
    """
    contexts = bruno_comprehensive.detect_primary_context(message or "", data) if message else ["general"]
    return bruno_comprehensive.create_comprehensive_response(content_type, data, contexts)

def enhance_message_with_bruno(message: str, additional_context: Dict[str, Any] = None) -> str:
    """
    Enhance a message with Bruno's comprehensive personality
    
    Args:
        message: Original message
        additional_context: Additional context information
        
    Returns:
        Enhanced message with Bruno's comprehensive personality
    """
    return bruno_comprehensive.enhance_message_comprehensively(message, None, additional_context)
