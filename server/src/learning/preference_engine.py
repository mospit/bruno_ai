"""
Preference Learning Engine for Bruno AI
Uses machine learning to understand and predict user preferences from interactions
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from loguru import logger

from ..database.repositories import (
    preference_repository, interaction_repository, 
    meal_plan_repository, user_repository
)

class PreferenceEngine:
    """Engine for learning and predicting user food and meal preferences"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.preference_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Preference categories we track
        self.preference_categories = {
            'cuisine': ['italian', 'mexican', 'chinese', 'american', 'mediterranean', 'indian', 'thai'],
            'dietary': ['vegetarian', 'vegan', 'gluten_free', 'dairy_free', 'low_carb', 'keto'],
            'cooking_style': ['quick', 'gourmet', 'comfort', 'healthy', 'family', 'budget'],
            'meal_type': ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'],
            'protein': ['chicken', 'beef', 'pork', 'fish', 'tofu', 'beans', 'eggs'],
            'cooking_method': ['grilled', 'baked', 'fried', 'steamed', 'roasted', 'raw']
        }
    
    async def learn_from_interaction(self, user_id: int, interaction_data: Dict[str, Any], 
                                   feedback_score: Optional[float] = None) -> Dict[str, Any]:
        """Learn user preferences from a single interaction"""
        
        try:
            # Extract preferences from the interaction
            extracted_preferences = await self._extract_preferences_from_interaction(interaction_data)
            
            # Determine confidence based on feedback and interaction type
            confidence_score = self._calculate_confidence_score(
                interaction_data.get('interaction_type', ''),
                feedback_score,
                interaction_data.get('user_satisfaction')
            )
            
            # Store learned preferences
            learning_results = []
            for pref_type, preferences in extracted_preferences.items():
                for pref_key, pref_value in preferences.items():
                    result = await preference_repository.upsert_preference(
                        user_id=user_id,
                        preference_type=pref_type,
                        preference_key=pref_key,
                        preference_value=pref_value,
                        confidence_score=confidence_score,
                        learning_source='implicit' if feedback_score is None else 'explicit'
                    )
                    learning_results.append(result)
            
            # Update user's preference model
            await self._update_user_preference_model(user_id)
            
            logger.info(f"Learned {len(learning_results)} preferences for user {user_id}")
            
            return {
                'preferences_learned': len(learning_results),
                'confidence_score': confidence_score,
                'extracted_preferences': extracted_preferences
            }
            
        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
            return {'error': str(e)}
    
    async def predict_preferences(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user preferences for a given context"""
        
        try:
            # Get user's existing preferences
            user_preferences = await preference_repository.get_strong_preferences(user_id)
            
            # Analyze interaction patterns
            interaction_patterns = await self._analyze_user_patterns(user_id)
            
            # Generate contextual predictions
            predictions = {}
            
            for category, options in self.preference_categories.items():
                category_prefs = user_preferences.get(category, {})
                
                # Calculate preference scores for each option
                preference_scores = {}
                for option in options:
                    if option in category_prefs:
                        preference_scores[option] = category_prefs[option]['confidence']
                    else:
                        # Predict based on similar preferences
                        predicted_score = await self._predict_preference_score(
                            user_id, category, option, context
                        )
                        preference_scores[option] = predicted_score
                
                # Sort by preference score
                sorted_prefs = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
                predictions[category] = {
                    'top_preferences': sorted_prefs[:3],
                    'confidence': max(preference_scores.values()) if preference_scores else 0.0
                }
            
            return {
                'predictions': predictions,
                'interaction_patterns': interaction_patterns,
                'total_preferences': sum(len(prefs) for prefs in user_preferences.values())
            }
            
        except Exception as e:
            logger.error(f"Error predicting preferences: {e}")
            return {'error': str(e)}
    
    async def get_personalized_recommendations(self, user_id: int, 
                                             recommendation_type: str,
                                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on learned preferences"""
        
        try:
            # Get user preferences and patterns
            preferences = await self.predict_preferences(user_id, context)
            
            if recommendation_type == 'recipes':
                return await self._recommend_recipes(user_id, preferences, context)
            elif recommendation_type == 'cuisines':
                return await self._recommend_cuisines(user_id, preferences, context)
            elif recommendation_type == 'ingredients':
                return await self._recommend_ingredients(user_id, preferences, context)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def update_preference_feedback(self, user_id: int, preference_type: str,
                                       preference_key: str, feedback_score: float,
                                       feedback_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update preference based on explicit user feedback"""
        
        try:
            # Update the preference with explicit feedback
            updated_pref = await preference_repository.upsert_preference(
                user_id=user_id,
                preference_type=preference_type,
                preference_key=preference_key,
                preference_value={'score': feedback_score, 'context': feedback_context},
                confidence_score=min(0.9, feedback_score / 5.0),  # Convert 1-5 score to confidence
                learning_source='explicit'
            )
            
            logger.info(f"Updated preference feedback for user {user_id}: {preference_type}.{preference_key}")
            
            return {
                'success': True,
                'updated_preference': {
                    'type': preference_type,
                    'key': preference_key,
                    'confidence': updated_pref.confidence_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating preference feedback: {e}")
            return {'success': False, 'error': str(e)}
    
    # Private helper methods
    
    async def _extract_preferences_from_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract preferences from interaction data using NLP and pattern matching"""
        
        extracted = {}
        
        user_message = interaction_data.get('user_message', '').lower()
        context_data = interaction_data.get('context_data', {})
        
        # Extract cuisine preferences
        cuisine_prefs = {}
        for cuisine in self.preference_categories['cuisine']:
            if cuisine in user_message:
                cuisine_prefs[cuisine] = {'mentioned': True, 'context': 'user_request'}
        if cuisine_prefs:
            extracted['cuisine'] = cuisine_prefs
        
        # Extract dietary restrictions/preferences
        dietary_prefs = {}
        for dietary in self.preference_categories['dietary']:
            if dietary.replace('_', ' ') in user_message or dietary in user_message:
                dietary_prefs[dietary] = {'mentioned': True, 'context': 'user_request'}
        if dietary_prefs:
            extracted['dietary'] = dietary_prefs
        
        # Extract cooking style preferences
        cooking_style_prefs = {}
        for style in self.preference_categories['cooking_style']:
            if style in user_message:
                cooking_style_prefs[style] = {'mentioned': True, 'context': 'user_request'}
        if cooking_style_prefs:
            extracted['cooking_style'] = cooking_style_prefs
        
        # Extract preferences from context data
        if 'dietary_restrictions' in context_data:
            if 'dietary' not in extracted:
                extracted['dietary'] = {}
            for restriction in context_data['dietary_restrictions']:
                extracted['dietary'][restriction] = {'mentioned': True, 'context': 'profile'}
        
        if 'budget' in context_data:
            budget = context_data['budget']
            if budget < 50:
                extracted['cooking_style'] = extracted.get('cooking_style', {})
                extracted['cooking_style']['budget'] = {'mentioned': True, 'context': 'budget_constraint'}
        
        return extracted
    
    def _calculate_confidence_score(self, interaction_type: str, 
                                  feedback_score: Optional[float],
                                  user_satisfaction: Optional[int]) -> float:
        """Calculate confidence score for learned preferences"""
        
        base_confidence = 0.5
        
        # Adjust based on interaction type
        type_weights = {
            'meal_plan': 0.8,
            'recipe_request': 0.7,
            'general_conversation': 0.3,
            'budget_coaching': 0.5
        }
        
        confidence = base_confidence * type_weights.get(interaction_type, 0.5)
        
        # Adjust based on explicit feedback
        if feedback_score is not None:
            # feedback_score should be 0-1 or 1-5
            normalized_score = feedback_score if feedback_score <= 1 else feedback_score / 5.0
            confidence = min(0.9, confidence + (normalized_score * 0.3))
        
        # Adjust based on user satisfaction
        if user_satisfaction is not None:
            # user_satisfaction should be 1-5
            normalized_satisfaction = user_satisfaction / 5.0
            confidence = min(0.9, confidence + (normalized_satisfaction * 0.2))
        
        return confidence
    
    async def _update_user_preference_model(self, user_id: int):
        """Update the user's overall preference model"""
        
        try:
            # Get recent interactions for pattern analysis
            recent_interactions = await interaction_repository.get_recent_interactions(
                user_id, days=30, limit=100
            )
            
            if len(recent_interactions) < 5:
                return  # Not enough data for meaningful updates
            
            # Analyze patterns in preferences
            preference_patterns = self._analyze_preference_patterns(recent_interactions)
            
            # Update meta-preferences (preferences about preferences)
            for pattern_type, pattern_data in preference_patterns.items():
                await preference_repository.upsert_preference(
                    user_id=user_id,
                    preference_type='meta',
                    preference_key=pattern_type,
                    preference_value=pattern_data,
                    confidence_score=0.6,
                    learning_source='pattern'
                )
                
        except Exception as e:
            logger.error(f"Error updating user preference model: {e}")
    
    def _analyze_preference_patterns(self, interactions: List) -> Dict[str, Any]:
        """Analyze patterns in user interactions to derive meta-preferences"""
        
        patterns = {}
        
        if not interactions:
            return patterns
        
        # Analyze time-based patterns
        interaction_times = [interaction.created_at.hour for interaction in interactions]
        if interaction_times:
            most_common_hour = max(set(interaction_times), key=interaction_times.count)
            patterns['preferred_interaction_time'] = {
                'hour': most_common_hour,
                'pattern': 'morning' if most_common_hour < 12 else 'afternoon' if most_common_hour < 18 else 'evening'
            }
        
        # Analyze interaction type preferences
        interaction_types = [interaction.interaction_type for interaction in interactions]
        if interaction_types:
            most_common_type = max(set(interaction_types), key=interaction_types.count)
            patterns['preferred_interaction_type'] = {
                'type': most_common_type,
                'frequency': interaction_types.count(most_common_type) / len(interaction_types)
            }
        
        # Analyze response satisfaction patterns
        satisfactions = [interaction.user_satisfaction for interaction in interactions 
                        if interaction.user_satisfaction is not None]
        if satisfactions:
            avg_satisfaction = sum(satisfactions) / len(satisfactions)
            patterns['average_satisfaction'] = {
                'score': avg_satisfaction,
                'trend': 'improving' if avg_satisfaction > 3.5 else 'neutral'
            }
        
        return patterns
    
    async def _predict_preference_score(self, user_id: int, category: str, 
                                       option: str, context: Dict[str, Any]) -> float:
        """Predict preference score for an option the user hasn't tried"""
        
        # Get similar preferences
        user_preferences = await preference_repository.get_user_preferences(user_id, category)
        
        if not user_preferences:
            return 0.3  # Neutral score for unknown users
        
        # Simple similarity-based prediction
        similar_scores = []
        for pref in user_preferences:
            if isinstance(pref.preference_value, dict) and 'score' in pref.preference_value:
                similar_scores.append(pref.preference_value['score'])
            else:
                similar_scores.append(pref.confidence_score)
        
        if similar_scores:
            return sum(similar_scores) / len(similar_scores)
        
        return 0.3
    
    async def _analyze_user_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        
        try:
            patterns = await interaction_repository.get_interaction_patterns(user_id)
            return patterns
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    async def _recommend_recipes(self, user_id: int, preferences: Dict[str, Any],
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recipe recommendations based on preferences"""
        
        recommendations = []
        
        # Get top preferences
        top_cuisines = preferences.get('cuisine', {}).get('top_preferences', [])
        top_cooking_styles = preferences.get('cooking_style', {}).get('top_preferences', [])
        top_proteins = preferences.get('protein', {}).get('top_preferences', [])
        
        # Generate recipe suggestions (mock data - in real implementation, 
        # this would query a recipe database)
        for i, (cuisine, score) in enumerate(top_cuisines[:3]):
            for j, (protein, p_score) in enumerate(top_proteins[:2]):
                recommendations.append({
                    'recipe_name': f"{cuisine.title()} {protein.title()} Dish",
                    'cuisine': cuisine,
                    'protein': protein,
                    'confidence_score': (score + p_score) / 2,
                    'estimated_cost': context.get('budget', 100) / 7,  # Per meal
                    'cooking_time': 30 + (i * 10),
                    'reason': f"Based on your preference for {cuisine} cuisine and {protein}"
                })
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return recommendations[:5]
    
    async def _recommend_cuisines(self, user_id: int, preferences: Dict[str, Any],
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cuisine recommendations"""
        
        cuisine_prefs = preferences.get('cuisine', {}).get('top_preferences', [])
        
        recommendations = []
        for cuisine, score in cuisine_prefs:
            recommendations.append({
                'cuisine': cuisine,
                'confidence_score': score,
                'reason': f"You've shown interest in {cuisine} cuisine",
                'suggested_frequency': 'weekly' if score > 0.7 else 'monthly'
            })
        
        return recommendations
    
    async def _recommend_ingredients(self, user_id: int, preferences: Dict[str, Any],
                                   context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ingredient recommendations"""
        
        protein_prefs = preferences.get('protein', {}).get('top_preferences', [])
        
        recommendations = []
        for protein, score in protein_prefs:
            recommendations.append({
                'ingredient': protein,
                'category': 'protein',
                'confidence_score': score,
                'reason': f"Matches your {protein} preferences",
                'estimated_cost_per_serving': 2.50 + (score * 2)  # Mock pricing
            })
        
        return recommendations

# Global preference engine instance
preference_engine = PreferenceEngine()
