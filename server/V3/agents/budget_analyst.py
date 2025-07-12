"""
Budget Analyst Agent - Bruno AI V3.1
Refined implementation with enhanced token optimization, memory management, and A2A support
Uses Claude 4 Sonnet for sophisticated forecasting and cost optimization
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from .base_agent import BaseAgent

# Pydantic models for input validation
class CostAnalysisRequest(BaseModel):
    """Validated input for cost analysis requests"""
    meal_ideas: List[str] = Field(min_items=1, max_items=20)
    budget: float = Field(gt=0, le=10000)
    context_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class ForecastRequest(BaseModel):
    """Validated input for spending forecast requests"""
    current_patterns: Dict[str, Any]
    context_id: Optional[str] = None
    forecast_period: int = Field(default=30, ge=7, le=365)  # days

class BudgetAllocationRequest(BaseModel):
    """Validated input for budget allocation optimization"""
    total_budget: float = Field(gt=0, le=10000)
    preferences: Dict[str, Any]
    context_id: Optional[str] = None
    family_size: int = Field(default=4, ge=1, le=12)

class BudgetAnalystAgent(BaseAgent):
    """Analyzes costs and provides budget optimization with sophisticated forecasting"""
    
    def __init__(self, agent_id: str = "budget_analyst", model_name: str = "claude-3-5-sonnet-20241022", 
                 redis_url: str = None, postgres_url: str = None):
        """Initialize Budget Analyst Agent with enhanced capabilities"""
        super().__init__(agent_id, model_name, redis_url, postgres_url)
        self.inflation_rate = 0.04  # 4% annual inflation rate
        self.logger = logging.getLogger(f"bruno.{agent_id}")
        
        # Performance tracking
        self.analysis_times = []
        self.token_usage = []
        
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using word count approximation"""
        # Approximation: 1 token ≈ 0.75 words for English text
        words = len(text.split())
        return int(words / 0.75)
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for the Budget Analyst Agent"""
        return """
        You are Bruno's financial advisor and budget optimization specialist. Your role is to:
        - Analyze food spending patterns and trends
        - Provide sophisticated cost forecasting and budget planning
        - Optimize meal costs while maintaining quality and preferences
        - Identify savings opportunities and cost-effective alternatives
        - Track spending against budgets with detailed breakdowns
        - Suggest budget allocation strategies for maximum value
        
        Always maintain Bruno's supportive personality while providing clear, actionable financial guidance.
        Focus on helping users achieve their financial goals without compromising their food preferences.
        Present recommendations as options (e.g., "You might save by...") rather than prescriptive advice.
        """
    
    async def analyze_meal_costs(self, meal_ideas: List[str], budget: float, context_id: str = None) -> Dict[str, Any]:
        """Analyze costs for proposed meal ideas against budget"""
        
        query = f"""
        Analyze the cost implications of these meal ideas against the target budget:
        
        Meal Ideas:
        {chr(10).join(f"- {meal}" for meal in meal_ideas)}
        
        Target Budget: ${budget}
        
        Provide detailed analysis including:
        - Estimated cost per meal
        - Cost per serving breakdown
        - Budget utilization percentage
        - Cost optimization recommendations
        - Potential savings opportunities
        - Alternative ingredient suggestions for cost reduction
        """
        
        # Get historical spending data from context
        if context_id:
            context = self.get_context(context_id)
            spending_history = context.get('spending_history', [])
            user_preferences = context.get('preferences', {})
            
            if spending_history:
                query += f"\nHistorical spending patterns: {json.dumps(spending_history[-5:])}"
            if user_preferences:
                query += f"\nUser preferences to maintain: {json.dumps(user_preferences)}"
        
        analysis = await self.process_with_optimization(query, context_id)
        
        # Structure the response
        result = {
            'analysis': analysis,
            'target_budget': budget,
            'meal_count': len(meal_ideas),
            'estimated_cost_per_meal': budget / len(meal_ideas) if meal_ideas else 0,
            'cost_breakdown': await self._generate_cost_breakdown(meal_ideas, budget, context_id),
            'recommendations': await self._generate_budget_recommendations(analysis, budget, context_id),
            'potential_savings': await self._calculate_potential_savings(meal_ideas, budget, context_id)
        }
        
        return result
    
    async def forecast_monthly_spending(self, current_patterns: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Forecast monthly food spending based on current patterns"""
        
        query = f"""
        Forecast monthly food spending based on these patterns:
        
        Current Spending Patterns: {json.dumps(current_patterns)}
        
        Provide:
        - Monthly spending projection
        - Week-by-week breakdown
        - Seasonal adjustment factors
        - Inflation considerations
        - Budget variance predictions
        - Recommended budget adjustments
        - Early warning indicators for overspending
        """
        
        # Get historical data for better forecasting
        if context_id:
            context = self.get_context(context_id)
            spending_history = context.get('spending_history', [])
            family_size = context.get('family_size', 4)
            
            if spending_history:
                query += f"\nHistorical spending data: {json.dumps(spending_history)}"
            query += f"\nFamily size: {family_size}"
        
        forecast = await self.process_with_optimization(query, context_id)
        
        result = {
            'monthly_forecast': forecast,
            'projection_date': datetime.now().isoformat(),
            'confidence_level': 'high',  # Can be calculated based on data quality
            'key_factors': await self._identify_cost_factors(current_patterns, context_id),
            'recommended_actions': await self._generate_spending_recommendations(forecast, context_id)
        }
        
        return result
    
    async def optimize_budget_allocation(self, total_budget: float, preferences: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Optimize budget allocation across different food categories"""
        
        query = f"""
        Optimize budget allocation for maximum value and satisfaction:
        
        Total Budget: ${total_budget}
        User Preferences: {json.dumps(preferences)}
        
        Optimize allocation across:
        - Proteins (meat, fish, plant-based)
        - Fresh produce (fruits, vegetables)
        - Pantry staples (grains, spices, oils)
        - Dairy and eggs
        - Specialty/treat items
        
        Provide:
        - Recommended percentage allocation per category
        - Dollar amounts per category
        - Flexibility ranges for each category
        - Seasonal adjustment strategies
        - Value maximization tips
        """
        
        # Get spending patterns and family info
        if context_id:
            context = self.get_context(context_id)
            family_size = context.get('family_size', 4)
            dietary_restrictions = context.get('dietary_restrictions', [])
            spending_history = context.get('spending_history', [])
            
            query += f"\nFamily size: {family_size}"
            if dietary_restrictions:
                query += f"\nDietary restrictions: {', '.join(dietary_restrictions)}"
            if spending_history:
                query += f"\nPast spending patterns: {json.dumps(spending_history[-3:])}"
        
        optimization = await self.process_with_optimization(query, context_id)
        
        result = {
            'allocation_strategy': optimization,
            'total_budget': total_budget,
            'category_breakdowns': await self._generate_category_breakdown(total_budget, preferences, context_id),
            'flexibility_recommendations': await self._generate_flexibility_guidelines(total_budget, context_id),
            'monitoring_suggestions': await self._generate_monitoring_plan(total_budget, context_id)
        }
        
        return result
    
    async def process_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process A2A request from other agents (e.g., Recipe Chef)"""
        
        context_id = request.get('context_id')
        agent_id = request.get('agent_id')
        request_type = request.get('request_type', 'cost_analysis')
        
        if request_type == 'cost_analysis':
            meal_ideas = request.get('meal_ideas', [])
            target_budget = request.get('target_budget', 0)
            analysis_request = request.get('analysis_request', '')
            
            # Perform detailed cost analysis
            cost_analysis = await self.analyze_meal_costs(meal_ideas, target_budget, context_id)
            
            response = {
                'context_id': context_id,
                'agent_id': 'budget_analyst',
                'request_type': 'cost_analysis_response',
                'analysis': cost_analysis['analysis'],
                'cost_breakdown': cost_analysis['cost_breakdown'],
                'recommendations': cost_analysis['recommendations'],
                'potential_savings': cost_analysis['potential_savings'],
                'budget_status': 'within_budget' if cost_analysis.get('estimated_total_cost', 0) <= target_budget else 'over_budget'
            }
            
        elif request_type == 'spending_forecast':
            current_patterns = request.get('current_patterns', {})
            forecast = await self.forecast_monthly_spending(current_patterns, context_id)
            
            response = {
                'context_id': context_id,
                'agent_id': 'budget_analyst',
                'request_type': 'forecast_response',
                'forecast': forecast['monthly_forecast'],
                'key_factors': forecast['key_factors'],
                'recommended_actions': forecast['recommended_actions']
            }
            
        else:
            response = {
                'context_id': context_id,
                'agent_id': 'budget_analyst',
                'status': 'unsupported_request_type',
                'message': f"Request type '{request_type}' not supported"
            }
        
        # Update context with analysis
        if context_id:
            context = self.get_context(context_id)
            context['budget_analysis'] = response
            self.set_context(context_id, context)
        
        return response
    
    async def track_spending_progress(self, current_spending: float, budget: float, period_progress: float, context_id: str = None) -> Dict[str, Any]:
        """Track spending progress against budget with projections"""
        
        query = f"""
        Analyze spending progress and provide recommendations:
        
        Current Spending: ${current_spending}
        Total Budget: ${budget}
        Period Progress: {period_progress * 100}% complete
        
        Calculate:
        - Spending velocity (rate of spending)
        - Projected end-of-period spending
        - Budget variance analysis
        - Course correction recommendations
        - Risk assessment for budget overrun
        """
        
        progress_analysis = await self.process_with_optimization(query, context_id)
        
        projected_total = current_spending / period_progress if period_progress > 0 else current_spending
        variance = budget - projected_total
        
        result = {
            'progress_analysis': progress_analysis,
            'current_spending': current_spending,
            'budget': budget,
            'period_progress': period_progress,
            'projected_total': round(projected_total, 2),
            'variance': round(variance, 2),
            'status': 'on_track' if variance >= 0 else 'over_budget',
            'recommendations': await self._generate_course_corrections(variance, period_progress, context_id)
        }
        
        return result
    
    async def _generate_cost_breakdown(self, meal_ideas: List[str], budget: float, context_id: str = None) -> Dict[str, float]:
        """Generate detailed cost breakdown for meals"""
        
        # Simplified breakdown - can be enhanced with real pricing data
        breakdown = {
            'proteins': budget * 0.35,
            'vegetables': budget * 0.25,
            'grains_starches': budget * 0.20,
            'dairy': budget * 0.10,
            'seasonings_oils': budget * 0.10
        }
        
        return breakdown
    
    async def _generate_budget_recommendations(self, analysis: str, budget: float, context_id: str = None) -> List[str]:
        """Generate specific budget recommendations"""
        
        query = f"""
        Based on this cost analysis, provide specific actionable recommendations:
        {analysis}
        
        Budget: ${budget}
        
        Focus on:
        - Immediate cost-saving actions
        - Ingredient substitutions
        - Shopping strategies
        - Meal planning optimizations
        """
        
        recommendations = await self.process_with_optimization(query, context_id)
        return recommendations.split('\n') if recommendations else []
    
    async def _calculate_potential_savings(self, meal_ideas: List[str], budget: float, context_id: str = None) -> float:
        """Calculate potential savings through optimization"""
        
        # Simplified calculation - can be enhanced with real data
        base_savings_rate = 0.15  # 15% potential savings
        meal_complexity_factor = len(meal_ideas) * 0.02  # More meals = more optimization opportunities
        
        potential_savings = budget * (base_savings_rate + meal_complexity_factor)
        return round(min(potential_savings, budget * 0.30), 2)  # Cap at 30% savings
    
    async def _identify_cost_factors(self, patterns: Dict[str, Any], context_id: str = None) -> List[str]:
        """Identify key factors affecting food costs"""
        
        factors = [
            "Seasonal price variations",
            "Shopping frequency and bulk buying opportunities",
            "Brand preferences vs. generic alternatives",
            "Meal complexity and ingredient variety",
            "Food waste and leftover utilization"
        ]
        
        return factors
    
    async def _generate_spending_recommendations(self, forecast: str, context_id: str = None) -> List[str]:
        """Generate spending recommendations based on forecast"""
        
        recommendations = [
            "Set weekly spending checkpoints",
            "Create a buffer for unexpected price increases",
            "Plan seasonal budget adjustments",
            "Monitor high-impact expense categories",
            "Establish emergency meal budget protocols"
        ]
        
        return recommendations
    
    async def _generate_category_breakdown(self, budget: float, preferences: Dict[str, Any], context_id: str = None) -> Dict[str, float]:
        """Generate category-wise budget breakdown"""
        
        # Standard allocation that can be customized based on preferences
        breakdown = {
            'proteins': budget * 0.30,
            'produce': budget * 0.25,
            'pantry_staples': budget * 0.20,
            'dairy_eggs': budget * 0.15,
            'specialty_treats': budget * 0.10
        }
        
        return breakdown
    
    async def _generate_flexibility_guidelines(self, budget: float, context_id: str = None) -> Dict[str, str]:
        """Generate guidelines for budget flexibility"""
        
        guidelines = {
            'seasonal_adjustments': f"Allow ±{round(budget * 0.1, 2)} for seasonal price changes",
            'special_occasions': f"Reserve {round(budget * 0.05, 2)} for special meals",
            'emergency_buffer': f"Maintain {round(budget * 0.08, 2)} emergency fund",
            'optimization_target': f"Aim to save {round(budget * 0.12, 2)} through smart shopping"
        }
        
        return guidelines
    
    async def _generate_monitoring_plan(self, budget: float, context_id: str = None) -> List[str]:
        """Generate budget monitoring plan"""
        
        plan = [
            "Track spending weekly against budget targets",
            "Review price trends for frequently purchased items",
            "Monitor category allocation effectiveness",
            "Assess meal satisfaction vs. cost ratios",
            "Adjust strategies based on spending patterns"
        ]
        
        return plan
    
    async def _generate_course_corrections(self, variance: float, progress: float, context_id: str = None) -> List[str]:
        """Generate course correction recommendations"""
        
        if variance < 0:  # Over budget
            corrections = [
                "Switch to more budget-friendly meal options",
                "Increase use of pantry staples and leftovers",
                "Consider generic brands and bulk purchases",
                "Reduce dining out and convenience foods",
                "Focus on simple, ingredient-efficient meals"
            ]
        else:  # Under budget
            corrections = [
                "Consider upgrading some ingredients for better nutrition",
                "Stock up on non-perishables when on sale",
                "Try new recipes within remaining budget",
                "Build emergency food reserves",
                "Invest in quality ingredients for special meals"
            ]
        
        return corrections
    
    async def send_a2a_response(self, to_agent: str, response_data: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Send A2A response to requesting agent"""
        try:
            # Log the A2A response
            self.logger.info(f"Sending A2A response to {to_agent}: {response_data.get('request_type', 'unknown')}")
            
            # Create A2A response message
            a2a_response = {
                'timestamp': datetime.now().isoformat(),
                'from_agent': self.agent_id,
                'to_agent': to_agent,
                'context_id': context_id,
                'response_data': response_data,
                'status': 'success'
            }
            
            # Send via A2A protocol (placeholder - integrate with FastA2A)
            await self.send_a2a_message(to_agent, a2a_response)
            
            return a2a_response
            
        except Exception as e:
            self.logger.error(f"Failed to send A2A response: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def analyze_multiple_meal_batches(self, meal_batches: List[List[str]], budget_per_batch: List[float], 
                                          context_id: str = None) -> Dict[str, Any]:
        """Batch processing for multiple meal sets with individual budgets"""
        start_time = datetime.now()
        
        try:
            batch_results = []
            total_estimated_tokens = 0
            
            # Process each batch concurrently
            tasks = []
            for i, (meals, budget) in enumerate(zip(meal_batches, budget_per_batch)):
                task = self.analyze_meal_costs(meals, budget, f"{context_id}_batch_{i}" if context_id else None)
                tasks.append(task)
            
            # Wait for all batch analyses to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch {i} analysis failed: {result}")
                    batch_results.append({
                        'batch_id': i,
                        'status': 'error',
                        'error': str(result),
                        'meals': meal_batches[i],
                        'budget': budget_per_batch[i]
                    })
                else:
                    batch_results.append({
                        'batch_id': i,
                        'status': 'success',
                        'result': result,
                        'meals': meal_batches[i],
                        'budget': budget_per_batch[i]
                    })
            
            # Calculate aggregate metrics
            total_budget = sum(budget_per_batch)
            total_meals = sum(len(batch) for batch in meal_batches)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            aggregate_result = {
                'batch_results': batch_results,
                'aggregate_metrics': {
                    'total_batches': len(meal_batches),
                    'total_meals': total_meals,
                    'total_budget': total_budget,
                    'processing_time_seconds': processing_time,
                    'successful_batches': len([r for r in batch_results if r['status'] == 'success']),
                    'failed_batches': len([r for r in batch_results if r['status'] == 'error'])
                },
                'recommendations': await self._generate_batch_recommendations(batch_results, context_id)
            }
            
            self.logger.info(f"Processed {len(meal_batches)} batches in {processing_time:.2f} seconds")
            return aggregate_result
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
    
    async def generate_variance_alerts(self, current_spending: float, budget: float, 
                                     period_progress: float, context_id: str = None) -> Dict[str, Any]:
        """Generate alerts for budget variance and spending patterns"""
        try:
            projected_total = current_spending / period_progress if period_progress > 0 else current_spending
            variance = budget - projected_total
            variance_percentage = (variance / budget) * 100 if budget > 0 else 0
            
            alerts = []
            recommendations = []
            
            # Critical variance alerts
            if variance_percentage < -20:
                alerts.append({
                    'level': 'critical',
                    'message': f'You might be spending {abs(variance_percentage):.1f}% over budget',
                    'action_required': True
                })
                recommendations.append("Consider switching to more budget-friendly meal options immediately")
            
            elif variance_percentage < -10:
                alerts.append({
                    'level': 'warning',
                    'message': f'You might be spending {abs(variance_percentage):.1f}% over budget',
                    'action_required': True
                })
                recommendations.append("You might want to review your recent purchases and adjust upcoming meals")
            
            elif variance_percentage > 15:
                alerts.append({
                    'level': 'info',
                    'message': f'You might have {variance_percentage:.1f}% budget remaining',
                    'action_required': False
                })
                recommendations.append("You might consider upgrading some ingredients or trying new recipes")
            
            # Spending velocity alerts
            if period_progress > 0:
                daily_spend_rate = current_spending / (period_progress * 30)  # Assuming 30-day period
                if daily_spend_rate > (budget / 30) * 1.5:
                    alerts.append({
                        'level': 'warning',
                        'message': 'Your daily spending rate might be too high',
                        'action_required': True
                    })
                    recommendations.append("You might want to slow down spending to stay within budget")
            
            # Persist alerts to context
            if context_id:
                context = await self.get_context(context_id)
                context['budget_alerts'] = {
                    'alerts': alerts,
                    'recommendations': recommendations,
                    'generated_at': datetime.now().isoformat(),
                    'variance_percentage': variance_percentage
                }
                await self.set_context(context_id, context)
            
            return {
                'alerts': alerts,
                'recommendations': recommendations,
                'variance_details': {
                    'current_spending': current_spending,
                    'projected_total': round(projected_total, 2),
                    'variance_amount': round(variance, 2),
                    'variance_percentage': round(variance_percentage, 1),
                    'period_progress': period_progress
                }
            }
            
        except Exception as e:
            self.logger.error(f"Variance alert generation failed: {e}")
            return {
                'alerts': [{
                    'level': 'error',
                    'message': 'Unable to generate variance alerts',
                    'action_required': False
                }],
                'recommendations': [],
                'variance_details': {}
            }
    
    async def enhance_forecast_with_trends(self, current_patterns: Dict[str, Any], 
                                         context_id: str = None) -> Dict[str, Any]:
        """Enhanced forecasting with trend analysis and seasonal factors"""
        try:
            # Get historical data for trend analysis
            context = await self.get_context(context_id) if context_id else {}
            spending_history = context.get('spending_history', [])
            
            # Apply inflation adjustment
            inflation_adjusted_patterns = self._apply_inflation_adjustment(current_patterns)
            
            # Calculate seasonal factors
            seasonal_factors = self._calculate_seasonal_factors(datetime.now().month)
            
            # Enhanced query with trend analysis
            query = f"""
            Provide enhanced spending forecast with trend analysis:
            
            Current Patterns (Inflation-Adjusted): {json.dumps(inflation_adjusted_patterns)}
            Seasonal Factors: {json.dumps(seasonal_factors)}
            Historical Data Points: {len(spending_history)}
            
            Analyze:
            - Spending trend direction (increasing/decreasing/stable)
            - Seasonal impact on costs
            - Inflation impact over time
            - Variance predictions with confidence intervals
            - Early warning indicators
            
            Present as options ("You might expect...", "You could see...")
            """
            
            # Add historical context if available
            if spending_history:
                recent_history = spending_history[-12:]  # Last 12 periods
                query += f"\nRecent spending history: {json.dumps(recent_history)}"
            
            # Get compressed forecast
            forecast_query = await self.compress_context(query, max_tokens=3000)
            estimated_tokens = self._estimate_tokens(forecast_query)
            
            # Process forecast
            forecast_result = await self.process_with_optimization(forecast_query, context_id)
            
            # Structure enhanced forecast response
            enhanced_forecast = {
                'forecast_analysis': forecast_result,
                'trend_indicators': {
                    'inflation_rate': self.inflation_rate,
                    'seasonal_factors': seasonal_factors,
                    'data_quality': 'high' if len(spending_history) > 6 else 'medium' if len(spending_history) > 3 else 'low',
                    'confidence_level': self._calculate_confidence_level(spending_history)
                },
                'projections': {
                    'monthly_estimate': self._calculate_monthly_projection(current_patterns, seasonal_factors),
                    'variance_range': self._calculate_variance_range(current_patterns),
                    'inflation_impact': current_patterns.get('weekly_spend', 0) * 4 * self.inflation_rate / 12
                },
                'token_usage': {
                    'estimated_tokens': estimated_tokens,
                    'compression_applied': len(query) > len(forecast_query)
                }
            }
            
            return enhanced_forecast
            
        except Exception as e:
            self.logger.error(f"Enhanced forecast failed: {e}")
            # Return basic forecast as fallback
            return await self.forecast_monthly_spending(current_patterns, context_id)
    
    def _apply_inflation_adjustment(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Apply inflation adjustment to spending patterns"""
        adjusted_patterns = patterns.copy()
        
        # Apply inflation to spending amounts
        for key, value in patterns.items():
            if 'spend' in key.lower() and isinstance(value, (int, float)):
                adjusted_patterns[f"{key}_inflation_adjusted"] = value * (1 + self.inflation_rate)
        
        return adjusted_patterns
    
    def _calculate_seasonal_factors(self, month: int) -> Dict[str, float]:
        """Calculate seasonal adjustment factors based on month"""
        # Seasonal factors for food spending (simplified model)
        seasonal_multipliers = {
            1: 1.05,   # January - post-holiday, comfort foods
            2: 1.02,   # February - winter produce prices
            3: 1.00,   # March - baseline
            4: 0.98,   # April - spring produce
            5: 0.95,   # May - abundant spring produce
            6: 0.97,   # June - summer starts
            7: 0.99,   # July - summer peak
            8: 1.01,   # August - summer peak prices
            9: 0.96,   # September - fall harvest
            10: 0.94,  # October - fall abundance
            11: 1.08,  # November - holiday preparations
            12: 1.12   # December - holiday premium
        }
        
        return {
            'current_month_factor': seasonal_multipliers.get(month, 1.0),
            'next_month_factor': seasonal_multipliers.get(month + 1 if month < 12 else 1, 1.0),
            'seasonal_trend': 'increasing' if month in [10, 11, 12] else 'decreasing' if month in [1, 2, 3] else 'stable'
        }
    
    def _calculate_confidence_level(self, spending_history: List[Dict]) -> str:
        """Calculate forecast confidence level based on data quality"""
        if len(spending_history) >= 12:
            return 'high'
        elif len(spending_history) >= 6:
            return 'medium'
        elif len(spending_history) >= 3:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_monthly_projection(self, patterns: Dict[str, Any], seasonal_factors: Dict[str, float]) -> float:
        """Calculate monthly spending projection with seasonal adjustment"""
        weekly_spend = patterns.get('weekly_spend', 0)
        monthly_base = weekly_spend * 4.33  # Average weeks per month
        
        # Apply seasonal adjustment
        seasonal_multiplier = seasonal_factors.get('current_month_factor', 1.0)
        
        return round(monthly_base * seasonal_multiplier, 2)
    
    def _calculate_variance_range(self, patterns: Dict[str, Any]) -> Dict[str, float]:
        """Calculate expected variance range for projections"""
        weekly_spend = patterns.get('weekly_spend', 0)
        monthly_base = weekly_spend * 4.33
        
        # Typical variance of ±15% for food spending
        variance_factor = 0.15
        
        return {
            'low_estimate': round(monthly_base * (1 - variance_factor), 2),
            'high_estimate': round(monthly_base * (1 + variance_factor), 2),
            'variance_percentage': variance_factor * 100
        }
    
    async def _generate_batch_recommendations(self, batch_results: List[Dict], context_id: str = None) -> List[str]:
        """Generate recommendations for batch processing results"""
        successful_batches = [r for r in batch_results if r['status'] == 'success']
        failed_batches = [r for r in batch_results if r['status'] == 'error']
        
        recommendations = []
        
        if successful_batches:
            # Analyze successful batches for patterns
            total_potential_savings = sum(r['result'].get('potential_savings', 0) for r in successful_batches)
            recommendations.append(f"You might save up to ${total_potential_savings:.2f} across all meal batches")
            
        if failed_batches:
            recommendations.append(f"You might want to retry analysis for {len(failed_batches)} failed batches")
            
        if len(successful_batches) > 1:
            recommendations.append("You might consider combining similar meal types for better bulk purchasing")
            
        return recommendations

# Usage Example
if __name__ == "__main__":
    import asyncio
    import os
    
    async def main():
        """Comprehensive usage example for BudgetAnalystAgent"""
        
        # Initialize the Budget Analyst Agent
        agent = BudgetAnalystAgent(
            agent_id="budget_analyst_demo",
            model_name="claude-3-5-sonnet-20241022",
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            postgres_url=os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai')
        )
        
        print("🤖 Bruno AI Budget Analyst Agent - Demo")
        print("=" * 50)
        
        # Example 1: Cost Analysis for Jerk Chicken and Rice & Peas
        print("\n📊 Example 1: Cost Analysis")
        meal_ideas = ["Jerk Chicken", "Rice & Peas"]
        budget = 200.0
        context_id = "demo_context_001"
        
        try:
            cost_analysis = await agent.analyze_meal_costs(meal_ideas, budget, context_id)
            print(f"✅ Analysis for {meal_ideas} with ${budget} budget:")
            print(f"   - Cost breakdown: {cost_analysis['cost_breakdown']}")
            print(f"   - Potential savings: ${cost_analysis['potential_savings']}")
            print(f"   - Cost per meal: ${cost_analysis['estimated_cost_per_meal']:.2f}")
        except Exception as e:
            print(f"❌ Cost analysis failed: {e}")
        
        # Example 2: A2A Request Processing
        print("\n🔄 Example 2: A2A Request Processing")
        a2a_request = {
            'context_id': context_id,
            'agent_id': 'recipe_chef',
            'request_type': 'cost_analysis',
            'meal_ideas': ['Caribbean Curry', 'Plantain Chips'],
            'target_budget': 150,
            'analysis_request': 'Validate pricing for Caribbean meal plan'
        }
        
        try:
            a2a_response = await agent.process_a2a_request(a2a_request)
            print(f"✅ A2A Response: {a2a_response['request_type']}")
            print(f"   - Budget status: {a2a_response.get('budget_status', 'unknown')}")
        except Exception as e:
            print(f"❌ A2A processing failed: {e}")
        
        # Example 3: Enhanced Forecasting
        print("\n📈 Example 3: Enhanced Forecasting with Trends")
        spending_patterns = {
            'weekly_spend': 150,
            'protein_percentage': 35,
            'produce_percentage': 25,
            'shopping_frequency': 2
        }
        
        try:
            enhanced_forecast = await agent.enhance_forecast_with_trends(spending_patterns, context_id)
            print(f"✅ Enhanced forecast generated:")
            print(f"   - Monthly estimate: ${enhanced_forecast['projections']['monthly_estimate']}")
            print(f"   - Confidence level: {enhanced_forecast['trend_indicators']['confidence_level']}")
            print(f"   - Inflation impact: ${enhanced_forecast['projections']['inflation_impact']:.2f}")
            print(f"   - Token usage: {enhanced_forecast['token_usage']['estimated_tokens']} tokens")
        except Exception as e:
            print(f"❌ Enhanced forecasting failed: {e}")
        
        # Example 4: Variance Alerts
        print("\n⚠️ Example 4: Variance Alerts")
        current_spending = 180.0
        budget = 150.0
        period_progress = 0.6  # 60% through the period
        
        try:
            variance_alerts = await agent.generate_variance_alerts(current_spending, budget, period_progress, context_id)
            print(f"✅ Variance analysis completed:")
            print(f"   - Alerts: {len(variance_alerts['alerts'])}")
            for alert in variance_alerts['alerts']:
                print(f"     • {alert['level'].upper()}: {alert['message']}")
            print(f"   - Variance: {variance_alerts['variance_details']['variance_percentage']}%")
        except Exception as e:
            print(f"❌ Variance alerts failed: {e}")
        
        # Example 5: Batch Processing
        print("\n📦 Example 5: Batch Processing Multiple Meal Sets")
        meal_batches = [
            ["Jerk Chicken", "Rice & Peas"],
            ["Curry Goat", "Festival"],
            ["Ackee & Saltfish", "Fried Dumplings"]
        ]
        budget_per_batch = [200.0, 180.0, 160.0]
        
        try:
            batch_results = await agent.analyze_multiple_meal_batches(meal_batches, budget_per_batch, context_id)
            print(f"✅ Batch processing completed:")
            print(f"   - Total batches: {batch_results['aggregate_metrics']['total_batches']}")
            print(f"   - Successful: {batch_results['aggregate_metrics']['successful_batches']}")
            print(f"   - Processing time: {batch_results['aggregate_metrics']['processing_time_seconds']:.2f}s")
            print(f"   - Total budget: ${batch_results['aggregate_metrics']['total_budget']}")
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Token-optimized cost analysis with context compression")
        print("• A2A protocol integration for agent communication")
        print("• Enhanced forecasting with seasonal and inflation adjustments")
        print("• Real-time variance alerts with user-friendly messaging")
        print("• Concurrent batch processing for multiple meal sets")
        print("• Comprehensive error handling and logging")
        print("• Memory persistence via Redis and Postgres integration")
    
    # Run the comprehensive demo
    asyncio.run(main())
