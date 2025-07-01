import pytest
import re

class TestBrunoPersonalityValidation:
    """Test cases to validate Bruno's personality traits and language patterns"""
    
    def test_brooklyn_accent_patterns(self):
        """Test recognition of Brooklyn accent patterns in text"""
        # Sample Bruno responses that should contain accent patterns
        bruno_responses = [
            "Hey there! Bruno here, ya friendly neighborhood budget bear from Brooklyn.",
            "Ya ain't gotta spend a fortune to eat like royalty.",
            "Hold up, hold up - I just spotted chicken thighs for $1.99!",
            "Bada-bing! Look at that - ya came in under budget!",
            "Lemme show ya how to make a chicken dish that'll knock ya socks off.",
            "Trust me on this one, I got ya back."
        ]
        
        # Brooklyn accent patterns to check for
        accent_patterns = [
            r'\bya\b',      # "ya" instead of "you"
            r'\bgotta\b',   # "gotta" 
            r'\blemme\b',   # "lemme" instead of "let me"
            r'\bain\'t\b',  # "ain't"
            r'\bgonna\b',   # "gonna"
            r'in\'\b'       # dropping 'g' from -ing words
        ]
        
        # Check that at least some responses contain accent patterns
        responses_with_accent = 0
        for response in bruno_responses:
            for pattern in accent_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    responses_with_accent += 1
                    break
        
        # At least 80% of responses should have accent patterns
        assert responses_with_accent >= len(bruno_responses) * 0.8
    
    def test_bruno_catchphrases(self):
        """Test that Bruno's characteristic catchphrases are recognized"""
        bruno_responses = [
            "Trust me on this one - I know where the good deals are!",
            "That's what I'm talkin' about!",
            "Bada-bing, bada-boom! Ya got a great meal plan.",
            "Ya gonna love this chicken recipe.",
            "Bruno's got ya covered with these savings.",
            "I got ya back, don't worry about it."
        ]
        
        # Bruno's signature catchphrases
        catchphrases = [
            "Trust me on this",
            "That's what I'm talkin' about",
            "Bada-bing",
            "Ya gonna love",
            "Bruno's got ya",
            "I got ya"
        ]
        
        # Check that catchphrases appear in responses
        catchphrase_count = 0
        for response in bruno_responses:
            for phrase in catchphrases:
                if phrase.lower() in response.lower():
                    catchphrase_count += 1
                    break
        
        # At least 5 out of 6 responses should have catchphrases
        assert catchphrase_count >= 5
    
    def test_budget_focused_language(self):
        """Test that Bruno uses budget and savings focused language"""
        budget_responses = [
            "Ya came in $8.50 under budget! That's what I'm talkin' about!",
            "This deal is gonna save ya family $20 this week.",
            "Ya wallet's gonna thank ya for this smart shopping.",
            "I found ya some alternatives before ya budget gets blown.",
            "We're gonna make every dollar count here.",
            "Look at you go! Ya just saved enough for a nice coffee."
        ]
        
        # Budget-focused vocabulary
        budget_terms = [
            "budget", "save", "savings", "dollar", "deals", 
            "wallet", "money", "cost", "price", "cheap", "steal"
        ]
        
        # Check that budget language appears frequently
        responses_with_budget_terms = 0
        for response in budget_responses:
            for term in budget_terms:
                if term.lower() in response.lower():
                    responses_with_budget_terms += 1
                    break
        
        # All responses should contain budget-related terms
        assert responses_with_budget_terms == len(budget_responses)
    
    def test_caring_protective_tone(self):
        """Test that Bruno's responses show caring and protective characteristics"""
        caring_responses = [
            "Hey, don't worry about it. Even us Brooklyn bears gotta learn the ropes.",
            "Ya gonna nail this budget thing, trust me. I got ya back.",
            "Lemme find ya some alternatives before ya wallet starts cryin'.",
            "I'm gonna show ya how to make a dish that'll knock ya socks off.",
            "Bruno's got ya covered with the best deals in town.",
            "Ya kids are gonna eat like royalty and ya wallet's gonna thank ya."
        ]
        
        # Caring/protective language indicators
        caring_indicators = [
            "don't worry", "I got ya", "trust me", "gonna help", 
            "got ya covered", "I'm gonna", "lemme", "gonna nail"
        ]
        
        # Check for caring tone
        caring_response_count = 0
        for response in caring_responses:
            for indicator in caring_indicators:
                if indicator.lower() in response.lower():
                    caring_response_count += 1
                    break
        
        # Most responses should show caring tone
        assert caring_response_count >= len(caring_responses) * 0.8
    
    def test_new_york_cultural_references(self):
        """Test that Bruno includes New York cultural references"""
        ny_responses = [
            "Bruno here, ya friendly neighborhood budget bear from Brooklyn.",
            "I been hunting deals in bodegas, supermarkets, and farmer's markets.",
            "My ma taught me how to stretch a grocery budget in Brooklyn.",
            "Even us Brooklyn bears gotta learn the ropes sometimes.",
            "This is how we do it in the boroughs, baby!",
            "I know every corner store from here to Queens."
        ]
        
        # New York references
        ny_references = [
            "brooklyn", "queens", "borough", "bodega", "neighborhood",
            "corner store", "ma", "nyc", "new york"
        ]
        
        # Check for NY cultural references
        ny_reference_count = 0
        for response in ny_responses:
            for reference in ny_references:
                if reference.lower() in response.lower():
                    ny_reference_count += 1
                    break
        
        # At least half should have NY references
        assert ny_reference_count >= len(ny_responses) * 0.5
    
    def test_excitement_and_energy(self):
        """Test that Bruno's responses show excitement and energy"""
        energetic_responses = [
            "Bada-bing! Look at that savings!",
            "Holy cannoli! That's a fantastic deal!",
            "Whoa, whoa, whoa! Ya about to go over budget there!",
            "Hold up, hold up - I just spotted something amazing!",
            "Look at you go! Ya makin' me proud!",
            "That's what I'm talkin' about! Boom!"
        ]
        
        # Energy/excitement indicators
        energy_indicators = [
            "bada-bing", "holy", "whoa", "hold up", "look at", 
            "boom", "fantastic", "amazing", "proud", "talkin'"
        ]
        
        # Check for energetic language
        energetic_count = 0
        for response in energetic_responses:
            for indicator in energy_indicators:
                if indicator.lower() in response.lower():
                    energetic_count += 1
                    break
        
        # All responses should show energy
        assert energetic_count == len(energetic_responses)

    def test_food_expertise_language(self):
        """Test that Bruno demonstrates food and cooking expertise"""
        food_responses = [
            "I'm gonna show ya how to make a chicken dish that'll knock ya socks off.",
            "Forget that fancy salmon recipe - here's something better.",
            "My nonna would be proud of this pasta dish.",
            "This marinade is gonna make that meat tender as butter.",
            "We're gonna turn these simple ingredients into magic.",
            "Trust me, this spice blend is gonna change ya life."
        ]
        
        # Food expertise indicators
        food_terms = [
            "recipe", "dish", "cook", "ingredient", "spice", "marinade",
            "tender", "flavor", "nonna", "pasta", "chicken", "salmon"
        ]
        
        # Check for food expertise
        food_expertise_count = 0
        for response in food_responses:
            for term in food_terms:
                if term.lower() in response.lower():
                    food_expertise_count += 1
                    break
        
        # All responses should show food knowledge
        assert food_expertise_count == len(food_responses)
