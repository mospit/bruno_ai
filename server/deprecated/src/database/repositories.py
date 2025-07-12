"""
Repository pattern implementations for Bruno AI data access
Provides clean data access layer for all database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, text
from loguru import logger

from .models import (
    User, UserProfile, MealPlan, Recipe, BudgetAnalysis, 
    UserInteraction, UserPreference, FoodItem, ShoppingList, LearningModel
)
from .connection import database_manager
from sqlalchemy.orm import sessionmaker

class BaseRepository:
    """Base repository with common operations"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.db_manager = database_manager
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.db_manager.get_session()
    
    async def get_by_id(self, id: int) -> Optional[Any]:
        """Get entity by ID"""
        session = self.get_session()
        try:
            return session.query(self.model_class).filter(self.model_class.id == id).first()
        finally:
            session.close()
    
    async def create(self, **kwargs) -> Any:
        """Create new entity"""
        session = self.get_session()
        try:
            entity = self.model_class(**kwargs)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception as e:
            session.rollback()
            logger.error(f"Create error in {self.model_class.__name__}: {e}")
            raise
        finally:
            session.close()
    
    async def update(self, id: int, **kwargs) -> Optional[Any]:
        """Update entity by ID"""
        session = self.get_session()
        try:
            entity = session.query(self.model_class).filter(self.model_class.id == id).first()
            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                session.commit()
                session.refresh(entity)
            return entity
        except Exception as e:
            session.rollback()
            logger.error(f"Update error in {self.model_class.__name__}: {e}")
            raise
        finally:
            session.close()
    
    async def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        session = self.get_session()
        try:
            entity = session.query(self.model_class).filter(self.model_class.id == id).first()
            if entity:
                session.delete(entity)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Delete error in {self.model_class.__name__}: {e}")
            raise
        finally:
            session.close()

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_user_with_profile(self, user_id: int) -> Optional[User]:
        """Get user with profile data"""
        session = self.get_session()
        try:
            return session.query(User).options(joinedload(User.profile)).filter(User.id == user_id).first()
        finally:
            session.close()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()

class MealPlanRepository(BaseRepository):
    """Repository for meal plan operations"""
    
    def __init__(self):
        super().__init__(MealPlan)
    
    async def get_user_meal_plans(self, user_id: int, limit: int = 10) -> List[MealPlan]:
        """Get user's meal plans ordered by creation date"""
        session = self.get_session()
        try:
            return session.query(MealPlan)\
                .filter(MealPlan.user_id == user_id)\
                .order_by(desc(MealPlan.created_at))\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    async def get_active_meal_plans(self, user_id: int) -> List[MealPlan]:
        """Get user's active meal plans"""
        session = self.get_session()
        try:
            return session.query(MealPlan)\
                .filter(and_(
                    MealPlan.user_id == user_id,
                    MealPlan.status == 'active'
                ))\
                .order_by(desc(MealPlan.created_at))\
                .all()
        finally:
            session.close()
    
    async def get_meal_plan_with_recipes(self, meal_plan_id: int) -> Optional[MealPlan]:
        """Get meal plan with associated recipes"""
        session = self.get_session()
        try:
            return session.query(MealPlan)\
                .options(joinedload(MealPlan.recipes_detail))\
                .filter(MealPlan.id == meal_plan_id)\
                .first()
        finally:
            session.close()
    
    async def get_performance_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get meal plan performance statistics"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stats = session.query(
                func.count(MealPlan.id).label('total_plans'),
                func.avg(MealPlan.user_rating).label('avg_rating'),
                func.avg(MealPlan.completion_rate).label('avg_completion'),
                func.avg(MealPlan.budget_accuracy).label('avg_budget_accuracy')
            ).filter(and_(
                MealPlan.user_id == user_id,
                MealPlan.created_at >= cutoff_date
            )).first()
            
            return {
                'total_plans': stats.total_plans or 0,
                'average_rating': float(stats.avg_rating or 0),
                'average_completion': float(stats.avg_completion or 0),
                'average_budget_accuracy': float(stats.avg_budget_accuracy or 0)
            }
        finally:
            session.close()

class BudgetRepository(BaseRepository):
    """Repository for budget analysis operations"""
    
    def __init__(self):
        super().__init__(BudgetAnalysis)
    
    async def get_user_budget_history(self, user_id: int, months: int = 6) -> List[BudgetAnalysis]:
        """Get user's budget analysis history"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
            
            return session.query(BudgetAnalysis)\
                .filter(and_(
                    BudgetAnalysis.user_id == user_id,
                    BudgetAnalysis.analysis_date >= cutoff_date
                ))\
                .order_by(desc(BudgetAnalysis.analysis_date))\
                .all()
        finally:
            session.close()
    
    async def get_budget_trends(self, user_id: int) -> Dict[str, Any]:
        """Analyze budget trends for user"""
        session = self.get_session()
        try:
            # Get last 12 months of data
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            
            analyses = session.query(BudgetAnalysis)\
                .filter(and_(
                    BudgetAnalysis.user_id == user_id,
                    BudgetAnalysis.analysis_date >= cutoff_date,
                    BudgetAnalysis.actual_spending.isnot(None)
                ))\
                .order_by(BudgetAnalysis.analysis_date)\
                .all()
            
            if not analyses:
                return {'trend': 'insufficient_data'}
            
            # Calculate trends
            spending_amounts = [a.actual_spending for a in analyses]
            target_budgets = [a.target_budget for a in analyses]
            
            avg_spending = sum(spending_amounts) / len(spending_amounts)
            avg_target = sum(target_budgets) / len(target_budgets)
            
            # Calculate variance trend
            variances = [a.variance_percentage for a in analyses if a.variance_percentage is not None]
            avg_variance = sum(variances) / len(variances) if variances else 0
            
            return {
                'average_spending': avg_spending,
                'average_target': avg_target,
                'average_variance_percentage': avg_variance,
                'trend': 'improving' if avg_variance < 5 else 'needs_attention',
                'analysis_count': len(analyses)
            }
        finally:
            session.close()
    
    async def get_spending_by_category(self, user_id: int, months: int = 3) -> Dict[str, float]:
        """Get spending breakdown by category"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
            
            analyses = session.query(BudgetAnalysis)\
                .filter(and_(
                    BudgetAnalysis.user_id == user_id,
                    BudgetAnalysis.analysis_date >= cutoff_date,
                    BudgetAnalysis.category_spending.isnot(None)
                ))\
                .all()
            
            # Aggregate category spending
            category_totals = {}
            for analysis in analyses:
                if analysis.category_spending:
                    for category, amount in analysis.category_spending.items():
                        category_totals[category] = category_totals.get(category, 0) + amount
            
            return category_totals
        finally:
            session.close()

class PreferenceRepository(BaseRepository):
    """Repository for user preference operations"""
    
    def __init__(self):
        super().__init__(UserPreference)
    
    async def get_user_preferences(self, user_id: int, preference_type: str = None) -> List[UserPreference]:
        """Get user preferences, optionally filtered by type"""
        session = self.get_session()
        try:
            query = session.query(UserPreference)\
                .filter(and_(
                    UserPreference.user_id == user_id,
                    UserPreference.is_active == True
                ))
            
            if preference_type:
                query = query.filter(UserPreference.preference_type == preference_type)
            
            return query.order_by(desc(UserPreference.confidence_score)).all()
        finally:
            session.close()
    
    async def upsert_preference(self, user_id: int, preference_type: str, 
                              preference_key: str, preference_value: Any,
                              confidence_score: float = 0.5, 
                              learning_source: str = 'implicit') -> UserPreference:
        """Insert or update user preference"""
        session = self.get_session()
        try:
            # Try to find existing preference
            existing = session.query(UserPreference)\
                .filter(and_(
                    UserPreference.user_id == user_id,
                    UserPreference.preference_type == preference_type,
                    UserPreference.preference_key == preference_key
                ))\
                .first()
            
            if existing:
                # Update existing preference
                existing.preference_value = preference_value
                existing.confidence_score = max(existing.confidence_score, confidence_score)
                existing.times_observed += 1
                existing.last_reinforced = datetime.utcnow()
                if existing.learning_source == 'implicit' and learning_source == 'explicit':
                    existing.learning_source = learning_source
                
                preference = existing
            else:
                # Create new preference
                preference = UserPreference(
                    user_id=user_id,
                    preference_type=preference_type,
                    preference_key=preference_key,
                    preference_value=preference_value,
                    confidence_score=confidence_score,
                    learning_source=learning_source,
                    times_observed=1
                )
                session.add(preference)
            
            session.commit()
            session.refresh(preference)
            return preference
            
        except Exception as e:
            session.rollback()
            logger.error(f"Preference upsert error: {e}")
            raise
        finally:
            session.close()
    
    async def get_strong_preferences(self, user_id: int, min_confidence: float = 0.7) -> Dict[str, Any]:
        """Get high-confidence user preferences grouped by type"""
        session = self.get_session()
        try:
            preferences = session.query(UserPreference)\
                .filter(and_(
                    UserPreference.user_id == user_id,
                    UserPreference.is_active == True,
                    UserPreference.confidence_score >= min_confidence
                ))\
                .order_by(desc(UserPreference.confidence_score))\
                .all()
            
            # Group by preference type
            grouped = {}
            for pref in preferences:
                if pref.preference_type not in grouped:
                    grouped[pref.preference_type] = {}
                grouped[pref.preference_type][pref.preference_key] = {
                    'value': pref.preference_value,
                    'confidence': pref.confidence_score,
                    'times_observed': pref.times_observed,
                    'source': pref.learning_source
                }
            
            return grouped
        finally:
            session.close()

class InteractionRepository(BaseRepository):
    """Repository for user interaction tracking"""
    
    def __init__(self):
        super().__init__(UserInteraction)
    
    async def log_interaction(self, user_id: int, interaction_type: str, 
                            user_message: str, agent_response: str,
                            context_data: Dict = None, response_time: float = None,
                            extracted_preferences: Dict = None) -> UserInteraction:
        """Log a user interaction"""
        session = self.get_session()
        try:
            interaction = UserInteraction(
                user_id=user_id,
                interaction_type=interaction_type,
                user_message=user_message,
                agent_response=agent_response,
                context_data=context_data or {},
                response_time=response_time,
                extracted_preferences=extracted_preferences or {}
            )
            
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            return interaction
            
        except Exception as e:
            session.rollback()
            logger.error(f"Interaction logging error: {e}")
            raise
        finally:
            session.close()
    
    async def get_recent_interactions(self, user_id: int, days: int = 7, limit: int = 50) -> List[UserInteraction]:
        """Get user's recent interactions"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            return session.query(UserInteraction)\
                .filter(and_(
                    UserInteraction.user_id == user_id,
                    UserInteraction.created_at >= cutoff_date
                ))\
                .order_by(desc(UserInteraction.created_at))\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    async def get_interaction_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        session = self.get_session()
        try:
            # Get interaction statistics
            stats = session.query(
                UserInteraction.interaction_type,
                func.count(UserInteraction.id).label('count'),
                func.avg(UserInteraction.response_time).label('avg_response_time'),
                func.avg(UserInteraction.user_satisfaction).label('avg_satisfaction')
            ).filter(UserInteraction.user_id == user_id)\
             .group_by(UserInteraction.interaction_type)\
             .all()
            
            patterns = {}
            for stat in stats:
                patterns[stat.interaction_type] = {
                    'count': stat.count,
                    'avg_response_time': float(stat.avg_response_time or 0),
                    'avg_satisfaction': float(stat.avg_satisfaction or 0)
                }
            
            # Get most common interaction types
            total_interactions = sum(p['count'] for p in patterns.values())
            
            return {
                'interaction_patterns': patterns,
                'total_interactions': total_interactions,
                'most_common_type': max(patterns.keys(), key=lambda k: patterns[k]['count']) if patterns else None
            }
        finally:
            session.close()

class ShoppingListRepository(BaseRepository):
    """Repository for shopping list operations"""
    
    def __init__(self):
        super().__init__(ShoppingList)
    
    async def get_user_shopping_lists(self, user_id: int, limit: int = 20) -> List[ShoppingList]:
        """Get user's shopping lists"""
        session = self.get_session()
        try:
            return session.query(ShoppingList)\
                .filter(ShoppingList.user_id == user_id)\
                .order_by(desc(ShoppingList.created_at))\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    async def get_shopping_performance(self, user_id: int) -> Dict[str, Any]:
        """Get shopping performance metrics"""
        session = self.get_session()
        try:
            completed_lists = session.query(ShoppingList)\
                .filter(and_(
                    ShoppingList.user_id == user_id,
                    ShoppingList.status == 'completed'
                ))\
                .all()
            
            if not completed_lists:
                return {'status': 'insufficient_data'}
            
            # Calculate performance metrics
            budget_accuracies = [sl.budget_accuracy for sl in completed_lists if sl.budget_accuracy is not None]
            completion_rates = [sl.completion_percentage for sl in completed_lists if sl.completion_percentage is not None]
            
            return {
                'total_completed_lists': len(completed_lists),
                'average_budget_accuracy': sum(budget_accuracies) / len(budget_accuracies) if budget_accuracies else 0,
                'average_completion_rate': sum(completion_rates) / len(completion_rates) if completion_rates else 0,
                'total_spent': sum(sl.actual_cost for sl in completed_lists if sl.actual_cost),
                'total_budgeted': sum(sl.total_budget for sl in completed_lists if sl.total_budget)
            }
        finally:
            session.close()

# Global repository instances
user_repository = UserRepository()
meal_plan_repository = MealPlanRepository()
budget_repository = BudgetRepository()
preference_repository = PreferenceRepository()
interaction_repository = InteractionRepository()
shopping_list_repository = ShoppingListRepository()
