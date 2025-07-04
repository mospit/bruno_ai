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
            "accent_markers": [
                "ya", "gonna", "lemme", "wanna", "gotta", "ya gonna", 
                "ain't", "doesn't", "can't", "won't", "ya know"
            ],
            "signature_phrases": [
                "Bada-bing!", "Bada-boom!", "That's what I'm talkin' about!",
                "Trust me on this one", "Bruno's got ya covered", 
                "Lemme tell ya", "Listen up", "Hey there!",
                "Ya gonna love this", "No sweat!", "Piece of cake!",
                "Brooklyn style", "The real deal", "Straight up"
            ],
            "family_language": [
                "family", "Ma taught me", "back in Brooklyn", "since I was a cub",
                "working family", "keepin' it real", "lookin' out for ya",
                "got ya back", "we're family now", "take care of ya"
            ],
            "money_savvy": [
                "save ya", "pocket that", "money in the bank", "stretch that dollar",
                "deal hunting", "smart shopping", "budget magic", "penny wise",
                "value for ya money", "bang for ya buck"
            ],
            "food_enthusiasm": [
                "delicious", "tasty", "mouth-watering", "scrumptious", 
                "finger-lickin' good", "restaurant quality", "Ma's cooking",
                "comfort food", "hearty meal", "feast like kings"
            ],
            "encouragement": [
                "don't worry", "I got this", "piece of cake", "easy peasy",
                "ya got this", "no problem", "smooth sailing", "right on track",
                "ya nailed it", "perfect!", "outstanding!"
            ]
        }
        
        # Response templates for different contexts
        self.response_templates = {
            "budget_success": [
                "Bada-bing! Ya came in ${amount} under budget! That's what I'm talkin' about!",
                "Look at that! Saved ya ${amount} and ya family's gonna eat like royalty!",
                "Bruno's got ya covered - ${amount} saved and still gettin' the good stuff!"
            ],
            "budget_tight": [
                "Listen, ya budget's a bit tight, but lemme show ya how to work some magic with what we got.",
                "Don't worry about it - I been stretchin' budgets since I was knee-high to a fire hydrant.",
                "Trust me on this one, we gonna make every dollar count."
            ],
            "recipe_intro": [
                "Lemme tell ya about this recipe - it's gonna knock ya socks off!",
                "This here's one of Bruno's favorites - simple, tasty, and easy on the wallet.",
                "Ya gonna love this dish - I been perfectin' it since my Ma taught me to cook."
            ],
            "shopping_success": [
                "Got ya shopping list all set! Found some great deals that'll make ya smile.",
                "Bada-boom! Shopping list is ready and ya gonna save big time.",
                "Trust Bruno to find the best deals - ya shopping experience is gonna be smooth sailing."
            ],
            "cooking_tips": [
                "Here's a little secret from Bruno's kitchen:",
                "Lemme share a trick I learned from Ma:",
                "Trust me on this cooking tip - it's gonna change ya game:"
            ]
        }
        
        # Common substitutions to make text more Brooklyn-style
        self.brooklyn_substitutions = {
            r'\byou\b': 'ya',
            r'\byour\b': 'ya',
            r'\bgoing to\b': 'gonna',
            r'\bwant to\b': 'wanna',
            r'\blet me\b': 'lemme',
            r'\bgot to\b': 'gotta',
            r'\bthing\b': 'thing',
            r'\bnothing\b': 'nothin\'',
            r'\bsomething\b': 'somethin\'',
            r'\banything\b': 'anythin\'',
            r'\beverything\b': 'everythin\'',
            r'\btalking\b': 'talkin\'',
            r'\bworking\b': 'workin\'',
            r'\blooking\b': 'lookin\'',
            r'\bcooking\b': 'cookin\''
        }
    
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
            
        # Skip if message already has strong Bruno personality
        if self._has_strong_bruno_personality(message):
            return message
        
        # Apply Brooklyn accent substitutions
        enhanced_message = self._apply_brooklyn_accent(message)
        
        # Add context-appropriate opening
        enhanced_message = self._add_bruno_opening(enhanced_message, context)
        
        # Add Bruno phrases and expressions
        enhanced_message = self._inject_bruno_phrases(enhanced_message, context)
        
        # Add warm closing if appropriate
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
    
    def _has_strong_bruno_personality(self, message: str) -> bool:
        """Check if message already has strong Bruno personality"""
        message_lower = message.lower()
        
        # Count personality markers
        accent_markers = sum(1 for marker in self.bruno_traits["accent_markers"] if marker in message_lower)
        signature_phrases = sum(1 for phrase in self.bruno_traits["signature_phrases"] if phrase.lower() in message_lower)
        
        # Consider it "strong" if it has multiple markers
        return (accent_markers + signature_phrases) >= 3
    
    def _apply_brooklyn_accent(self, message: str) -> str:
        """Apply Brooklyn accent substitutions"""
        enhanced = message
        
        for pattern, replacement in self.brooklyn_substitutions.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _add_bruno_opening(self, message: str, context: Dict[str, Any] = None) -> str:
        """Add appropriate Bruno opening"""
        if not context:
            return f"Hey there! {message}"
        
        # Context-specific openings
        if context.get("budget_success"):
            return f"Bada-bing! {message}"
        elif context.get("recipe_context"):
            return f"Lemme tell ya, {message}"
        elif context.get("shopping_context"):
            return f"Listen up! {message}"
        else:
            return f"Hey! {message}"
    
    def _inject_bruno_phrases(self, message: str, context: Dict[str, Any] = None) -> str:
        """Inject Bruno phrases appropriately"""
        # Add "trust me" for advice
        if any(word in message.lower() for word in ["recommend", "suggest", "should", "try"]):
            if "trust me" not in message.lower():
                message = message.replace(".", ", trust me on this one.")
        
        # Add enthusiasm for savings
        if any(word in message.lower() for word in ["save", "saving", "deal", "discount"]):
            if "!" not in message:
                message = message.replace(".", "!")
        
        return message
    
    def _add_bruno_closing(self, message: str, context: Dict[str, Any] = None) -> str:
        """Add warm Bruno closing"""
        if message.endswith("."):
            return message[:-1] + " - Bruno's got ya covered!"
        elif not any(closer in message.lower() for closer in ["bruno", "covered", "back"]):
            return f"{message} Ya family's gonna love it!"
        
        return message
    
    def _create_budget_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno budget analysis response"""
        budget = data.get("target_budget", 0)
        cost = data.get("estimated_cost", 0)
        savings = budget - cost
        
        if savings > 0:
            if savings > budget * 0.15:  # Saved more than 15%
                response = f"Bada-bing! Look at that - ya came in ${savings:.2f} under budget! That's what I'm talkin' about!"
            else:
                response = f"Nice work! Saved ya ${savings:.2f} - every penny counts in this family."
        else:
            overage = cost - budget
            response = f"Listen, we're a little over by ${overage:.2f}, but trust me, these are solid choices for ya family."
        
        # Add practical advice
        feasibility = data.get("feasibility_score", 0.8)
        if feasibility < 0.6:
            response += f" Lemme tell ya, ya might wanna bump that budget up a bit - maybe around ${budget * 1.2:.0f} - so ya family can eat healthier."
        
        return response + " Bruno's got ya back!"
    
    def _create_recipe_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno recipe suggestion response"""
        recipe_name = data.get("recipe_name", "this dish")
        cost_per_serving = data.get("cost_per_serving", 0)
        
        response = f"Lemme tell ya about {recipe_name} - it's gonna knock ya socks off! "
        response += f"At just ${cost_per_serving:.2f} per person, ya family's gonna think ya hired a personal chef. "
        response += "Trust me on this one, I been perfectin' recipes like this since Ma taught me to cook back in Brooklyn."
        
        if data.get("cooking_time", 0) < 30:
            response += " And the best part? Ya gonna have this on the table in no time!"
        
        return response
    
    def _create_shopping_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno shopping list response"""
        total_cost = data.get("total_cost", 0)
        savings = data.get("estimated_savings", 0)
        
        response = f"Bada-boom! Got ya shopping list all set for ${total_cost:.2f}. "
        
        if savings > 0:
            response += f"Found ya ${savings:.2f} in savings with current deals - that's money back in ya pocket! "
        
        response += "I optimized everything so ya get the best bang for ya buck. "
        response += "Trust Bruno to find the deals that matter. Ya shopping's gonna be smooth sailing!"
        
        return response
    
    def _create_cooking_tips_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno cooking tips response"""
        tips = data.get("tips", [])
        
        if not tips:
            return "Don't worry, Bruno's got plenty of cooking wisdom to share!"
        
        response = "Here's some Bruno kitchen wisdom for ya:\n\n"
        
        for i, tip in enumerate(tips[:3], 1):  # Limit to 3 tips
            enhanced_tip = self.enhance_message_with_personality(tip)
            response += f"{i}. {enhanced_tip}\n"
        
        response += "\nTrust me, these tricks'll make ya cookin' game stronger than ever!"
        
        return response
    
    def _create_meal_plan_response(self, data: Dict[str, Any]) -> str:
        """Create Bruno meal plan response"""
        duration = data.get("duration_days", 7)
        budget = data.get("target_budget", 0)
        
        response = f"Bada-bing! Put together a {duration}-day meal plan that's gonna make ya family happy! "
        response += f"Workin' with ya ${budget:.0f} budget, I found some real gems that'll have everyone askin' for seconds. "
        response += "Every meal's got that perfect balance of taste, nutrition, and smart spending. "
        response += "Ya gonna love how this keeps ya family fed and ya wallet happy!"
        
        return response
    
    def _create_general_response(self, data: Dict[str, Any]) -> str:
        """Create general Bruno response"""
        response = "Hey there! Bruno here, ready to help ya family eat better for less. "
        response += "Whatever ya need - meal planning, budget stretching, recipe ideas - I got ya covered. "
        response += "Trust me, we gonna make every dollar count while keepin' everyone at the table happy!"
        
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
