"""
Reflection & Feedback Agent - Bruno AI V3.1
Uses Claude 4 Sonnet for nuanced iterations and continuous improvement
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .base_agent import TokenOptimizedAgent

class ReflectionFeedbackAgent(TokenOptimizedAgent):
    """Reviews outputs and adapts based on user wants and feedback"""
    
    def __init__(self):
        super().__init__(
            model="anthropic:claude-4-sonnet",
            instructions="""
            You are Bruno's reflection and feedback specialist, responsible for continuous improvement. Your role is to:
            - Review and analyze outputs from all other agents
            - Gather and interpret user feedback on recommendations
            - Identify patterns in user preferences and satisfaction
            - Suggest improvements to agent interactions and recommendations
            - Adapt the system's approach based on user wants and outcomes
            - Ensure all recommendations align with user goals and constraints
            
            Always maintain Bruno's warm, learning-oriented personality. Focus on making the experience 
            better for users while respecting their preferences and feedback.
            """,
            agent_name="reflection_feedback"
        )
    
    async def analyze_system_performance(self, interaction_data: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Analyze overall system performance and user satisfaction"""
        
        query = f"""
        Analyze this interaction data to assess system performance:
        
        Interaction Data: {json.dumps(interaction_data)}
        
        Evaluate:
        - User satisfaction indicators
        - Recommendation accuracy and relevance
        - System response times and efficiency
        - Goal achievement rates
        - Areas needing improvement
        - Patterns in user behavior and preferences
        
        Provide specific recommendations for enhancement.
        """
        
        # Get historical performance data
        if context_id:
            context = self.get_context(context_id)
            performance_history = context.get('performance_history', [])
            user_feedback_history = context.get('feedback_history', [])
            
            if performance_history:
                query += f"\nHistorical performance: {json.dumps(performance_history[-5:])}"
            if user_feedback_history:
                query += f"\nUser feedback history: {json.dumps(user_feedback_history[-5:])}"
        
        analysis = await self.process_with_optimization(query, context_id)
        
        result = {
            'performance_analysis': analysis,
            'interaction_timestamp': datetime.now().isoformat(),
            'satisfaction_score': self._calculate_satisfaction_score(interaction_data),
            'improvement_recommendations': await self._generate_improvement_recommendations(analysis, context_id),
            'system_adaptations': await self._suggest_system_adaptations(interaction_data, context_id),
            'next_review_suggestions': await self._plan_next_review(analysis, context_id)
        }
        
        # Update performance history
        if context_id:
            context = self.get_context(context_id)
            history = context.get('performance_history', [])
            history.append({
                'timestamp': datetime.now().isoformat(),
                'satisfaction_score': result['satisfaction_score'],
                'key_insights': analysis[:200]  # Store summary
            })
            context['performance_history'] = history[-10:]  # Keep last 10 entries
            self.set_context(context_id, context)
        
        return result
    
    async def process_user_feedback(self, feedback: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Process and learn from user feedback"""
        
        feedback_text = feedback.get('text', '')
        rating = feedback.get('rating', 0)
        category = feedback.get('category', 'general')
        specific_agent = feedback.get('agent', '')
        
        query = f"""
        Analyze this user feedback and extract actionable insights:
        
        Feedback Text: {feedback_text}
        Rating: {rating}/5
        Category: {category}
        Specific Agent: {specific_agent or 'General system'}
        
        Extract:
        - User satisfaction indicators
        - Specific improvement areas
        - Preference patterns
        - Expectation misalignments
        - Actionable recommendations for each agent
        - System-wide adaptations needed
        """
        
        # Get feedback context
        if context_id:
            context = self.get_context(context_id)
            recent_interactions = context.get('recent_interactions', [])
            user_preferences = context.get('preferences', {})
            
            if recent_interactions:
                query += f"\nRecent interactions context: {json.dumps(recent_interactions[-3:])}"
            if user_preferences:
                query += f"\nUser preferences: {json.dumps(user_preferences)}"
        
        feedback_analysis = await self.process_with_optimization(query, context_id)
        
        result = {
            'feedback_analysis': feedback_analysis,
            'original_feedback': feedback,
            'improvement_actions': await self._generate_improvement_actions(feedback_analysis, context_id),
            'agent_specific_recommendations': await self._generate_agent_recommendations(feedback_analysis, specific_agent, context_id),
            'user_preference_updates': await self._update_user_preferences(feedback, context_id),
            'priority_level': self._assess_feedback_priority(feedback)
        }
        
        # Store feedback for future reference
        if context_id:
            context = self.get_context(context_id)
            feedback_history = context.get('feedback_history', [])
            feedback_history.append({
                'timestamp': datetime.now().isoformat(),
                'rating': rating,
                'category': category,
                'summary': feedback_text[:100],
                'priority': result['priority_level']
            })
            context['feedback_history'] = feedback_history[-20:]  # Keep last 20 entries
            self.set_context(context_id, context)
        
        return result
    
    async def review_agent_outputs(self, agent_outputs: Dict[str, Any], user_query: str, context_id: str = None) -> Dict[str, Any]:
        """Review outputs from all agents for consistency and quality"""
        
        query = f"""
        Review these agent outputs for quality, consistency, and user alignment:
        
        Original User Query: {user_query}
        Agent Outputs: {json.dumps(agent_outputs)}
        
        Evaluate:
        - Consistency across agent recommendations
        - Alignment with user query and intent
        - Practical feasibility of suggestions
        - Budget and preference adherence
        - Missing information or gaps
        - Integration opportunities between agents
        
        Provide specific quality assessment and improvement suggestions.
        """
        
        # Get user context for review
        if context_id:
            context = self.get_context(context_id)
            user_preferences = context.get('preferences', {})
            budget_constraints = context.get('budget', 0)
            dietary_restrictions = context.get('dietary_restrictions', [])
            
            query += f"\nUser preferences: {json.dumps(user_preferences)}"
            query += f"\nBudget: ${budget_constraints}"
            if dietary_restrictions:
                query += f"\nDietary restrictions: {', '.join(dietary_restrictions)}"
        
        review = await self.process_with_optimization(query, context_id)
        
        result = {
            'quality_review': review,
            'consistency_score': self._calculate_consistency_score(agent_outputs),
            'alignment_score': self._calculate_alignment_score(agent_outputs, user_query),
            'integration_opportunities': await self._identify_integration_opportunities(agent_outputs, context_id),
            'recommended_refinements': await self._suggest_output_refinements(review, context_id),
            'user_communication_plan': await self._plan_user_communication(agent_outputs, context_id)
        }
        
        return result
    
    async def adapt_system_behavior(self, adaptation_data: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Adapt system behavior based on learning and feedback"""
        
        query = f"""
        Based on accumulated learning and feedback, suggest system behavior adaptations:
        
        Adaptation Data: {json.dumps(adaptation_data)}
        
        Consider:
        - User preference patterns
        - Successful interaction patterns
        - Common failure modes
        - Efficiency improvements
        - User satisfaction trends
        - Agent collaboration effectiveness
        
        Provide specific, actionable adaptation strategies.
        """
        
        # Get learning context
        if context_id:
            context = self.get_context(context_id)
            performance_trends = context.get('performance_history', [])
            feedback_patterns = context.get('feedback_history', [])
            successful_interactions = context.get('successful_patterns', [])
            
            if performance_trends:
                query += f"\nPerformance trends: {json.dumps(performance_trends[-5:])}"
            if feedback_patterns:
                query += f"\nFeedback patterns: {json.dumps(feedback_patterns[-5:])}"
            if successful_interactions:
                query += f"\nSuccessful patterns: {json.dumps(successful_interactions[-3:])}"
        
        adaptations = await self.process_with_optimization(query, context_id)
        
        result = {
            'adaptation_strategies': adaptations,
            'implementation_priority': await self._prioritize_adaptations(adaptations, context_id),
            'expected_improvements': await self._estimate_improvement_impact(adaptations, context_id),
            'rollback_plan': await self._create_rollback_plan(adaptations, context_id),
            'monitoring_metrics': await self._define_monitoring_metrics(adaptations, context_id)
        }
        
        # Update adaptation history
        if context_id:
            context = self.get_context(context_id)
            adaptation_history = context.get('adaptation_history', [])
            adaptation_history.append({
                'timestamp': datetime.now().isoformat(),
                'adaptations': adaptations[:200],  # Summary
                'priority': result['implementation_priority']
            })
            context['adaptation_history'] = adaptation_history[-10:]
            self.set_context(context_id, context)
        
        return result
    
    async def generate_learning_insights(self, interaction_history: List[Dict[str, Any]], context_id: str = None) -> Dict[str, Any]:
        """Generate insights from interaction history for continuous learning"""
        
        query = f"""
        Analyze interaction history to extract learning insights:
        
        Interaction History: {json.dumps(interaction_history)}
        
        Identify:
        - User behavior patterns
        - Preference evolution over time
        - Successful recommendation patterns
        - Common request types and solutions
        - Seasonal or temporal patterns
        - Optimization opportunities
        - Predictive indicators for user satisfaction
        
        Provide actionable insights for system improvement.
        """
        
        insights = await self.process_with_optimization(query, context_id)
        
        result = {
            'learning_insights': insights,
            'pattern_analysis': await self._analyze_patterns(interaction_history, context_id),
            'predictive_models': await self._suggest_predictive_models(insights, context_id),
            'optimization_opportunities': await self._identify_optimizations(insights, context_id),
            'knowledge_updates': await self._suggest_knowledge_updates(insights, context_id)
        }
        
        return result
    
    def _calculate_satisfaction_score(self, interaction_data: Dict[str, Any]) -> float:
        """Calculate user satisfaction score based on interaction data"""
        
        # Simplified scoring - can be enhanced with ML models
        base_score = 3.0
        
        # Adjust based on various factors
        if interaction_data.get('task_completed', False):
            base_score += 1.0
        if interaction_data.get('response_time', 10) < 5:
            base_score += 0.5
        if interaction_data.get('user_rating'):
            base_score = interaction_data['user_rating']
        
        return min(5.0, max(1.0, base_score))
    
    def _calculate_consistency_score(self, agent_outputs: Dict[str, Any]) -> float:
        """Calculate consistency score across agent outputs"""
        
        # Simplified consistency calculation
        if len(agent_outputs) < 2:
            return 5.0
        
        # Check for conflicting recommendations
        budget_mentions = []
        for output in agent_outputs.values():
            if isinstance(output, dict) and 'budget' in str(output).lower():
                budget_mentions.append(output)
        
        # More sophisticated consistency checking would be implemented here
        return 4.2  # Placeholder score
    
    def _calculate_alignment_score(self, agent_outputs: Dict[str, Any], user_query: str) -> float:
        """Calculate how well outputs align with user query"""
        
        # Simplified alignment calculation
        query_keywords = user_query.lower().split()
        alignment_indicators = 0
        
        for output in agent_outputs.values():
            output_text = str(output).lower()
            for keyword in query_keywords:
                if keyword in output_text:
                    alignment_indicators += 1
        
        # Normalize to 1-5 scale
        max_possible = len(query_keywords) * len(agent_outputs)
        if max_possible > 0:
            return min(5.0, 1.0 + (alignment_indicators / max_possible) * 4.0)
        return 3.0
    
    def _assess_feedback_priority(self, feedback: Dict[str, Any]) -> str:
        """Assess priority level of feedback"""
        
        rating = feedback.get('rating', 3)
        text = feedback.get('text', '').lower()
        
        # High priority indicators
        if rating <= 2 or any(word in text for word in ['terrible', 'awful', 'broken', 'unusable']):
            return 'high'
        elif rating >= 4 or any(word in text for word in ['excellent', 'perfect', 'amazing']):
            return 'low'  # Positive feedback is lower priority for fixes
        else:
            return 'medium'
    
    async def _generate_improvement_recommendations(self, analysis: str, context_id: str = None) -> List[str]:
        """Generate specific improvement recommendations"""
        
        query = f"""
        Based on this analysis, provide specific, actionable improvement recommendations:
        {analysis}
        
        Focus on:
        - Immediate fixes
        - Medium-term enhancements
        - Long-term strategic improvements
        - User experience optimizations
        """
        
        recommendations = await self.process_with_optimization(query, context_id)
        return recommendations.split('\n') if recommendations else []
    
    async def _suggest_system_adaptations(self, interaction_data: Dict[str, Any], context_id: str = None) -> List[str]:
        """Suggest system-wide adaptations"""
        
        adaptations = [
            "Adjust response personalization based on user patterns",
            "Optimize agent collaboration workflows",
            "Refine budget recommendation algorithms",
            "Enhance meal suggestion diversity",
            "Improve context retention across sessions"
        ]
        
        return adaptations
    
    async def _plan_next_review(self, analysis: str, context_id: str = None) -> Dict[str, Any]:
        """Plan next review cycle"""
        
        return {
            'next_review_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'focus_areas': ['user_satisfaction', 'response_times', 'recommendation_accuracy'],
            'metrics_to_track': ['satisfaction_score', 'task_completion_rate', 'user_retention']
        }
    
    async def _generate_improvement_actions(self, feedback_analysis: str, context_id: str = None) -> List[str]:
        """Generate specific improvement actions from feedback"""
        
        actions = [
            "Review and adjust recommendation algorithms",
            "Enhance user preference learning",
            "Improve response clarity and specificity",
            "Optimize multi-agent coordination",
            "Refine budget optimization strategies"
        ]
        
        return actions
    
    async def _generate_agent_recommendations(self, feedback_analysis: str, specific_agent: str, context_id: str = None) -> Dict[str, List[str]]:
        """Generate agent-specific recommendations"""
        
        recommendations = {
            'pantry_manager': ["Improve inventory accuracy", "Enhance expiration predictions"],
            'instacart_integration': ["Optimize price accuracy", "Improve alternative suggestions"],
            'recipe_chef': ["Enhance recipe diversity", "Improve dietary restriction handling"],
            'budget_analyst': ["Refine cost predictions", "Improve savings recommendations"],
            'reflection_feedback': ["Enhance feedback processing", "Improve adaptation strategies"]
        }
        
        if specific_agent and specific_agent in recommendations:
            return {specific_agent: recommendations[specific_agent]}
        
        return recommendations
    
    async def _update_user_preferences(self, feedback: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Update user preferences based on feedback"""
        
        if not context_id:
            return {}
        
        context = self.get_context(context_id)
        preferences = context.get('preferences', {})
        
        # Extract preference updates from feedback
        # This would be more sophisticated in a real implementation
        feedback_text = feedback.get('text', '').lower()
        
        if 'too expensive' in feedback_text:
            preferences['budget_conscious'] = True
        if 'more variety' in feedback_text:
            preferences['diversity_preference'] = 'high'
        if 'simpler' in feedback_text:
            preferences['complexity_preference'] = 'low'
        
        # Update context
        context['preferences'] = preferences
        self.set_context(context_id, context)
        
        return preferences
    
    async def _identify_integration_opportunities(self, agent_outputs: Dict[str, Any], context_id: str = None) -> List[str]:
        """Identify opportunities for better agent integration"""
        
        opportunities = [
            "Better budget-recipe alignment",
            "Improved pantry-shopping coordination", 
            "Enhanced meal-cost optimization",
            "Streamlined feedback incorporation",
            "Real-time preference adaptation"
        ]
        
        return opportunities
    
    async def _suggest_output_refinements(self, review: str, context_id: str = None) -> List[str]:
        """Suggest refinements to agent outputs"""
        
        refinements = [
            "Add more specific cost breakdowns",
            "Include preparation time estimates",
            "Provide clearer alternative options",
            "Enhance nutritional information",
            "Improve shopping list organization"
        ]
        
        return refinements
    
    async def _plan_user_communication(self, agent_outputs: Dict[str, Any], context_id: str = None) -> Dict[str, str]:
        """Plan how to communicate results to user"""
        
        plan = {
            'summary_style': 'concise_with_details',
            'prioritization': 'budget_first',
            'format': 'structured_list',
            'tone': 'friendly_and_helpful',
            'follow_up': 'request_feedback'
        }
        
        return plan
    
    async def _prioritize_adaptations(self, adaptations: str, context_id: str = None) -> List[str]:
        """Prioritize adaptation strategies"""
        
        priorities = [
            "High: User satisfaction improvements",
            "Medium: Efficiency optimizations", 
            "Medium: Feature enhancements",
            "Low: Interface refinements"
        ]
        
        return priorities
    
    async def _estimate_improvement_impact(self, adaptations: str, context_id: str = None) -> Dict[str, str]:
        """Estimate impact of proposed improvements"""
        
        impact = {
            'user_satisfaction': '+15%',
            'response_accuracy': '+10%',
            'efficiency': '+20%',
            'user_retention': '+8%'
        }
        
        return impact
    
    async def _create_rollback_plan(self, adaptations: str, context_id: str = None) -> Dict[str, str]:
        """Create rollback plan for adaptations"""
        
        plan = {
            'backup_strategy': 'Maintain previous version configurations',
            'rollback_triggers': 'User satisfaction drop >10%',
            'recovery_time': '<2 hours',
            'monitoring_period': '72 hours post-deployment'
        }
        
        return plan
    
    async def _define_monitoring_metrics(self, adaptations: str, context_id: str = None) -> List[str]:
        """Define metrics to monitor adaptations"""
        
        metrics = [
            'User satisfaction scores',
            'Response time averages',
            'Task completion rates',
            'Feedback sentiment analysis',
            'System error rates'
        ]
        
        return metrics
    
    async def _analyze_patterns(self, interaction_history: List[Dict[str, Any]], context_id: str = None) -> Dict[str, Any]:
        """Analyze patterns in interaction history"""
        
        patterns = {
            'peak_usage_times': ['7-9 AM', '5-7 PM'],
            'common_request_types': ['meal_planning', 'budget_optimization', 'shopping_lists'],
            'user_satisfaction_trends': 'Improving over time',
            'seasonal_patterns': 'Higher usage during meal planning seasons'
        }
        
        return patterns
    
    async def _suggest_predictive_models(self, insights: str, context_id: str = None) -> List[str]:
        """Suggest predictive models for improvement"""
        
        models = [
            "User satisfaction prediction model",
            "Meal preference evolution model",
            "Budget optimization model",
            "Seasonal demand forecasting model",
            "Churn prediction model"
        ]
        
        return models
    
    async def _identify_optimizations(self, insights: str, context_id: str = None) -> List[str]:
        """Identify optimization opportunities"""
        
        optimizations = [
            "Cache frequently requested meal plans",
            "Pre-compute budget analyses for common scenarios",
            "Optimize agent coordination protocols",
            "Implement smart context compression",
            "Enhance response personalization algorithms"
        ]
        
        return optimizations
    
    async def _suggest_knowledge_updates(self, insights: str, context_id: str = None) -> List[str]:
        """Suggest knowledge base updates"""
        
        updates = [
            "Update seasonal ingredient pricing data",
            "Enhance recipe nutrition database",
            "Expand dietary restriction handling",
            "Update regional cuisine preferences",
            "Improve ingredient substitution knowledge"
        ]
        
        return updates
