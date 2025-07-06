"""
Bruno Personality Bridge - Ensures consistent personality across all agents
This module provides utilities to maintain Bruno's Brooklyn personality
throughout all agent interactions and communications.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class BrunoPersonalityBridge:
    """
    Ensures Bruno's personality is consistent across all agent communications
    """
    
    def __init__(self):
        # Core personality traits and phrases
        self.bruno_traits = {
            "professional_markers": [
                "based on", "I recommend", "let me understand", "can you tell me", 
                "I want to make sure", "this approach", "here's why", "effective"
            ],
            "signature_phrases": [
                "Let me understand your situation better", "I want to make sure I give you the best recommendation",
                "Based on your needs", "This approach works well because", "Here's what I found",
                "Let's focus on", "I'd recommend", "This will help you achieve",
                "Excellent work", "That's a solid choice", "Here's the strategy"
            ],
            "supportive_language": [
                "your family", "this approach", "for your situation", "I understand",
                "working together", "practical solution", "looking out for you",
                "here to help", "we can work with this", "support your goals"
            ],
            "money_savvy": [
                "save you", "cost effective", "budget optimization", "value",
                "smart spending", "efficient use", "maximize savings", "strategic",
                "return on investment", "practical choice"
            ],
            "food_enthusiasm": [
                "delicious", "flavorful", "nutritious", "satisfying", 
                "restaurant quality", "well-balanced", "appealing",
                "wholesome", "satisfying meal", "excellent choice"
            ],
            "encouragement": [
                "excellent work", "good choice", "that's effective", "well done",
                "you're on track", "solid approach", "making progress", "working well",
                "great result", "perfect!", "outstanding!"
            ]
        }
        
        # Response templates for different contexts
        self.response_templates = {
            "budget_success": [
                "Excellent work! You came in ${amount} under budget while maintaining great nutritional value.",
                "Great result! You saved ${amount} and your family will have delicious, healthy meals.",
                "Perfect execution - ${amount} saved with a strategic approach to meal planning."
            ],
            "budget_tight": [
                "I understand your budget is tight. Let me show you how to maximize value with what we have.",
                "No problem - I can help you create effective solutions within your current budget.",
                "Let's focus on strategic choices that will make every dollar count."
            ],
            "recipe_intro": [
                "Let me tell you about this recipe - it's both delicious and cost-effective.",
                "This is an excellent choice that balances flavor, nutrition, and budget considerations.",
                "You'll really enjoy this dish - it's been optimized for both taste and efficiency."
            ],
            "shopping_success": [
                "Your shopping list is ready! I found several deals that will help you save.",
                "Perfect! Shopping list optimized for both savings and quality.",
                "I've structured your shopping to maximize value and minimize costs."
            ],
            "cooking_tips": [
                "Here's a strategy that works well:",
                "Let me share an effective technique:",
                "This approach will improve your results:"
            ],
            "uncertainty_questions": [
                "I want to make sure I give you the best recommendation. Can you tell me",
                "To provide the most effective solution, I need to understand",
                "Let me get some details so I can optimize this for your situation:"
            ]
        }
        
        # Professional communication enhancements
        self.professional_enhancements = {
            r'\bthis should\b': 'this approach should',
            r'\bI think\b': 'I recommend',
            r'\byou should\b': 'I suggest you',
            r'\btry this\b': 'consider this approach',
            r'\bgood idea\b': 'effective strategy',
            r'\bbad idea\b': 'less optimal approach',
            r'\bcheap\b': 'cost-effective',
            r'\bexpensive\b': 'higher investment'
        }
        
        # Confidence threshold for asking questions
        self.confidence_threshold = 0.8
    
    def should_ask_questions(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Determine if Bruno should ask questions based on confidence level
        
        Args:
            context: Context about the interaction including confidence scores
            
        Returns:
            Dictionary with should_ask_questions boolean and suggested questions
        """
        if not context:
            return {"should_ask": False, "questions": []}
        
        confidence = context.get("confidence_score", 1.0)
        missing_info = context.get("missing_information", [])
        
        result = {
            "should_ask": confidence < self.confidence_threshold,
            "questions": [],
            "confidence_level": confidence
        }
        
        if result["should_ask"]:
            # Generate specific questions based on missing information
            questions = []
            
            if "family_size" in missing_info:
                questions.append("how many people you're planning for?")
            
            if "dietary_restrictions" in missing_info:
                questions.append("if anyone has dietary restrictions or food allergies?")
            
            if "budget_range" in missing_info:
                questions.append("what your target budget range is for this meal plan?")
            
            if "timeframe" in missing_info:
                questions.append("what timeframe you're planning for - is this for a week or specific days?")
            
            if "preferences" in missing_info:
                questions.append("what types of cuisines or foods your family prefers?")
            
            if "cooking_skill" in missing_info:
                questions.append("how comfortable you are with cooking - simple recipes or more complex ones?")
            
            # If no specific missing info but low confidence, ask general clarification
            if not questions:
                questions.append("more details about what you're looking for so I can provide the best recommendations?")
            
            result["questions"] = questions
        
        return result
    
    def enhance_message_with_personality(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Enhance any agent message with Bruno's personality
        
        Args:
            message: Original message from an agent
            context: Context about the interaction (budget, recipe, etc.)
            
        Returns:
            Enhanced message with Bruno's personality
        """
        if not message:
            return message
            
        # Check if we should ask questions first
        question_check = self.should_ask_questions(context)
        if question_check["should_ask"]:
            return self._create_clarification_message(question_check["questions"])
        
        # Skip if message already has strong Bruno personality
        if self._has_strong_bruno_personality(message):
            return message
        
        # Apply professional communication enhancements
        enhanced_message = self._apply_professional_enhancements(message)
        
        # Add context-appropriate opening
        enhanced_message = self._add_bruno_opening(enhanced_message, context)
        
        # Add Bruno phrases and expressions
        enhanced_message = self._inject_bruno_phrases(enhanced_message, context)
        
        # Add supportive closing if appropriate
        enhanced_message = self._add_bruno_closing(enhanced_message, context)
        
        return enhanced_message
    
    def create_bruno_response(self, content_type: str, data: Dict[str, Any]) -> str:
        """
        Create a complete Bruno response for specific content types
        
        Args:
            content_type: Type of response (budget_analysis, recipe_suggestion, etc.)
            data: Data to include in the response
            
        Returns:
            Complete Bruno response with personality
        """
        if content_type == "budget_analysis":
            return self._create_budget_response(data)
        elif content_type == "recipe_suggestion":
            return self._create_recipe_response(data)
        elif content_type == "shopping_list":
            return self._create_shopping_response(data)
        elif content_type == "cooking_tips":
            return self._create_cooking_tips_response(data)
        elif content_type == "meal_plan":
            return self._create_meal_plan_response(data)
        else:
            return self._create_general_response(data)
    
    def validate_personality_consistency(self, message: str) -> Dict[str, Any]:
        """
        Validate that a message maintains Bruno's personality consistency
        
        Args:
            message: Message to validate
            
        Returns:
            Validation results with suggestions
        """
        results = {
            "has_brooklyn_accent": False,
            "has_signature_phrases": False,
            "has_family_warmth": False,
            "personality_score": 0.0,
            "suggestions": []
        }
        
        message_lower = message.lower()
        
        # Check for Brooklyn accent markers
        accent_count = sum(1 for marker in self.bruno_traits["accent_markers"] if marker in message_lower)
        results["has_brooklyn_accent"] = accent_count > 0
        
        # Check for signature phrases
        phrase_count = sum(1 for phrase in self.bruno_traits["signature_phrases"] if phrase.lower() in message_lower)
        results["has_signature_phrases"] = phrase_count > 0
        
        # Check for family warmth
        family_count = sum(1 for phrase in self.bruno_traits["family_language"] if phrase in message_lower)
        results["has_family_warmth"] = family_count > 0
        
        # Calculate personality score
        total_markers = accent_count + phrase_count + family_count
        max_possible = len(self.bruno_traits["accent_markers"]) + len(self.bruno_traits["signature_phrases"]) + len(self.bruno_traits["family_language"])
        results["personality_score"] = min(total_markers / max_possible * 10, 1.0)  # Scale to 0-1
        
        # Generate suggestions
        if not results["has_brooklyn_accent"]:
            results["suggestions"].append("Add Brooklyn accent markers like 'ya', 'gonna', or 'lemme'")
        
        if not results["has_signature_phrases"]:
            results["suggestions"].append("Include Bruno signature phrases like 'Trust me on this one' or 'Bada-bing!'")
        
        if not results["has_family_warmth"]:
            results["suggestions"].append("Add family-oriented language to show Bruno's caring nature")
        
        if results["personality_score"] < 0.3:
            results["suggestions"].append("Message needs more Bruno personality - consider complete rewrite")
        
        return results
    
    def _create_clarification_message(self, questions: List[str]) -> str:
        """Create a message asking for clarification"""
        intro = "I want to make sure I give you the best recommendation. Can you tell me "
        
        if len(questions) == 1:
            return intro + questions[0] + "?"
        elif len(questions) == 2:
            return intro + questions[0] + " and " + questions[1] + "?"
        else:
            question_list = ", ".join(questions[:-1]) + ", and " + questions[-1]
            return intro + question_list + "?"
    
    def _has_strong_bruno_personality(self, message: str) -> bool:
        """Check if message already has strong Bruno personality"""
        message_lower = message.lower()
        
        # Count personality markers
        professional_markers = sum(1 for marker in self.bruno_traits["professional_markers"] if marker in message_lower)
        signature_phrases = sum(1 for phrase in self.bruno_traits["signature_phrases"] if phrase.lower() in message_lower)
        
        # Consider it "strong" if it has multiple markers
        return (professional_markers + signature_phrases) >= 3
    
    def _apply_professional_enhancements(self, message: str) -> str:
        """Apply professional communication enhancements"""
        enhanced = message
        
        for pattern, replacement in self.professional_enhancements.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _add_bruno_opening(self, message: str, context: Dict[str, Any] = None) -> str:
        """Add appropriate Bruno opening"""
        if not context:
            return message
        
        # Context-specific openings
        if context.get("budget_success"):
            return f"Excellent work! {message}"
        elif context.get("recipe_context"):
            return f"Based on your needs, {message}"
        elif context.get("shopping_context"):
            return f"Here's what I found: {message}"
        else:
            return message
    
    def _inject_bruno_phrases(self, message: str, context: Dict[str, Any] = None) -> str:
        """Inject Bruno phrases appropriately"""
        # Add professional reasoning for recommendations
        if any(word in message.lower() for word in ["recommend", "suggest", "should", "try"]):
            if "because" not in message.lower() and "this approach" not in message.lower():
                message = message.replace(".", " because this approach works well for your situation.")
        
        # Add strategic language for savings
        if any(word in message.lower() for word in ["save", "saving", "deal", "discount"]):
            if "strategic" not in message.lower():
                message = message.replace("save", "strategically save")
        
        return message
    
    def _add_bruno_closing(self, message: str, context: Dict[str, Any] = None) -> str:
        """Add supportive Bruno closing"""
        if message.endswith(".") and not any(closer in message.lower() for closer in ["help", "support", "work"]):
            return message[:-1] + ". I'm here to help you achieve the best results."
        elif not any(closer in message.lower() for closer in ["help", "support", "achieve"]):
            return f"{message} This will help you achieve your goals effectively."
        
        return message
    
    def _create_budget_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno budget analysis response"""
        budget = data.get("target_budget", 0)
        cost = data.get("estimated_cost", 0)
        savings = budget - cost
        
        if savings > 0:
            if savings > budget * 0.15:  # Saved more than 15%
                response = f"Excellent work! You came in ${savings:.2f} under budget while maintaining great nutritional value. This strategic approach is clearly working well."
            else:
                response = f"Good result! You saved ${savings:.2f} - every dollar counts when planning effectively."
        else:
            overage = cost - budget
            response = f"We're slightly over budget by ${overage:.2f}, but these are solid choices that provide good value for your family."
        
        # Add practical advice
        feasibility = data.get("feasibility_score", 0.8)
        if feasibility < 0.6:
            response += f" I'd recommend considering a budget around ${budget * 1.2:.0f} to give you more flexibility for healthier options."
        
        return response + " I'm here to help you achieve the best results."
    
    def _create_recipe_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno recipe suggestion response"""
        recipe_name = data.get("recipe_name", "this dish")
        cost_per_serving = data.get("cost_per_serving", 0)
        
        response = f"Let me tell you about {recipe_name} - it's both delicious and cost-effective. "
        response += f"At ${cost_per_serving:.2f} per person, your family will enjoy restaurant-quality meals at home. "
        response += "This recipe has been optimized for both flavor and budget efficiency."
        
        if data.get("cooking_time", 0) < 30:
            response += " The best part is that you can have this prepared quickly and efficiently."
        
        return response
    
    def _create_shopping_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno shopping list response"""
        total_cost = data.get("total_cost", 0)
        savings = data.get("estimated_savings", 0)
        
        response = f"Your shopping list is ready for ${total_cost:.2f}. "
        
        if savings > 0:
            response += f"I found ${savings:.2f} in savings with current deals - that's effective budget optimization! "
        
        response += "I've structured everything to maximize value while maintaining quality. "
        response += "This strategic approach will help you achieve your shopping goals efficiently."
        
        return response
    
    def _create_cooking_tips_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno cooking tips response"""
        tips = data.get("tips", [])
        
        if not tips:
            return "I have several effective cooking strategies to share with you!"
        
        response = "Here are some practical cooking strategies:\n\n"
        
        for i, tip in enumerate(tips[:3], 1):  # Limit to 3 tips
            enhanced_tip = self.enhance_message_with_personality(tip)
            response += f"{i}. {enhanced_tip}\n"
        
        response += "\nThese techniques will help you improve your cooking efficiency and results."
        
        return response
    
    def _create_meal_plan_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno meal plan response"""
        duration = data.get("duration_days", 7)
        budget = data.get("target_budget", 0)
        
        response = f"I've created a comprehensive {duration}-day meal plan that will work well for your family. "
        response += f"Working within your ${budget:.0f} budget, I found excellent options that balance nutrition, flavor, and cost. "
        response += "Each meal has been optimized for the right balance of taste, nutrition, and strategic spending. "
        response += "This approach will keep your family well-fed while maintaining budget efficiency."
        
        return response
    
    def _create_general_response(self, data: Dict[str, Any]) -> str:
        """Create general Bruno response"""
        response = "Hello! I'm here to help you create effective meal planning strategies that work with your budget and lifestyle. "
        response += "Whether you need meal planning, budget optimization, or recipe recommendations, I can provide solutions. "
        response += "My approach focuses on making every dollar count while ensuring your family enjoys nutritious, delicious meals."
        
        return response

# Global instance for easy access
bruno_personality = BrunoPersonalityBridge()

def enhance_agent_response(response: str, context: Dict[str, Any] = None) -> str:
    """
    Quick function to enhance any agent response with Bruno's personality
    
    Args:
        response: Original agent response
        context: Context information
        
    Returns:
        Enhanced response with Bruno's personality
    """
    return bruno_personality.enhance_message_with_personality(response, context)

def create_bruno_message(content_type: str, data: Dict[str, Any]) -> str:
    """
    Quick function to create a Bruno message for specific content
    
    Args:
        content_type: Type of content (budget_analysis, recipe_suggestion, etc.)
        data: Data for the message
        
    Returns:
        Complete Bruno message
    """
    return bruno_personality.create_bruno_response(content_type, data)

def validate_bruno_personality(message: str) -> Dict[str, Any]:
    """
    Quick function to validate Bruno personality in a message
    
    Args:
        message: Message to validate
        
    Returns:
        Validation results
    """
    return bruno_personality.validate_personality_consistency(message)
