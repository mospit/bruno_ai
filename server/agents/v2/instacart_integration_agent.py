"""
Instacart Integration Agent V2.0
Enhanced integration with Instacart API for comprehensive grocery data and ordering
Replaces the Grocery Browser Agent with direct API integration
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from loguru import logger
from .base_agent import BaseAgent, AgentCard, CacheManager

class InstacartIntegrationAgentV2(BaseAgent):
    """Enhanced Instacart Integration Agent with advanced capabilities"""
    
    def __init__(self):
        # Define agent capabilities
        agent_card = AgentCard(
            name="Instacart Integration Agent",
            version="2.0.0",
            description="Bruno's comprehensive Instacart specialist - pricing, products, and ordering",
            capabilities={
                "skills": [
                    {
                        "id": "comprehensive_product_search",
                        "name": "Comprehensive Product Search & Pricing",
                        "description": "Advanced product discovery with real-time pricing and availability",
                        "examples": [
                            "Find organic chicken breast prices across all local stores",
                            "Search for gluten-free pasta options under $3",
                            "Compare produce prices and quality ratings"
                        ],
                        "tags": ["product-search", "real-time-pricing", "comparison"]
                    },
                    {
                        "id": "intelligent_shopping_optimization",
                        "name": "Intelligent Shopping List Optimization",
                        "description": "Smart shopping list creation with store optimization and delivery scheduling",
                        "examples": [
                            "Create optimized shopping list for $75 budget with fastest delivery",
                            "Optimize across multiple stores for best prices and single delivery",
                            "Schedule recurring weekly orders with budget tracking"
                        ],
                        "tags": ["optimization", "scheduling", "multi-store"]
                    },
                    {
                        "id": "real_time_deal_monitoring",
                        "name": "Real-time Deal Monitoring & Alerts",
                        "description": "Continuous monitoring of price changes and promotional offers",
                        "examples": [
                            "Alert when chicken goes on sale below $2.99/lb",
                            "Monitor weekly deals for user's favorite products",
                            "Track seasonal price patterns for budget planning"
                        ],
                        "tags": ["monitoring", "alerts", "deals"]
                    },
                    {
                        "id": "advanced_order_management",
                        "name": "Advanced Order Management",
                        "description": "Complete order lifecycle management with tracking and optimization",
                        "examples": [
                            "Place order with specific delivery window and dietary notes",
                            "Track order status and delivery updates",
                            "Manage recurring orders and subscription modifications"
                        ],
                        "tags": ["order-management", "tracking", "automation"]
                    }
                ]
            },
            api_integrations={
                "instacart_connect_api": {
                    "version": "v1",
                    "endpoints": ["products", "stores", "orders", "pricing"],
                    "rate_limits": "1000 requests/hour",
                    "caching_strategy": "aggressive_with_ttl"
                },
                "instacart_partner_api": {
                    "version": "beta",
                    "enhanced_features": ["real_time_inventory", "bulk_pricing", "delivery_optimization"],
                    "availability": "pending_approval"
                }
            },
            performance_targets={
                "product_search_time": "< 1 second",
                "pricing_accuracy": "> 99%",
                "order_success_rate": "> 98%",
                "cache_hit_ratio": "> 85%"
            }
        )
        
        super().__init__(agent_card)
        
        # Initialize Instacart API client
        self.api_base_url = "https://connect.instacart.com/v1"
        self.api_key = os.getenv('INSTACART_API_KEY')
        self.affiliate_id = os.getenv('INSTACART_AFFILIATE_ID')
        
        # Initialize advanced cache manager
        self.cache_manager = CacheManager(self.redis_client)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(requests_per_hour=1000)
        
        # Product category mappings for optimization
        self.category_mappings = self._load_category_mappings()
        
        logger.info("Instacart Integration Agent V2.0 initialized successfully")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Instacart-specific tasks"""
        action = task.get('action')
        context = task.get('context', {})
        
        # Route to specific capabilities
        if action == "search_products":
            return await self.search_products_optimized(
                query=context.get('query'),
                filters=context.get('filters', {}),
                location=context.get('location')
            )
        
        elif action == "create_shopping_list":
            return await self.create_optimized_shopping_list(
                items=context.get('items', []),
                budget=context.get('budget', 0),
                preferences=context.get('preferences', {})
            )
        
        elif action == "monitor_deals":
            return await self.monitor_deals_and_prices(
                products=context.get('products', []),
                user_id=context.get('user_id')
            )
        
        elif action == "manage_order":
            return await self.manage_order_lifecycle(
                order_data=context.get('order_data', {}),
                action_type=context.get('action_type', 'create')
            )
        
        elif action == "optimize_store_selection":
            return await self.optimize_store_selection(
                items=context.get('items', []),
                location=context.get('location'),
                preferences=context.get('preferences', {})
            )
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def search_products_optimized(self, query: str, filters: Dict = None, location: str = None) -> Dict[str, Any]:
        """Optimized product search with intelligent caching and batching"""
        cache_key = self._generate_cache_key("product_search", query, filters, location)
        
        # Check cache first
        cached_result = await self.cache_manager.get_with_strategy(cache_key, "instacart_products")
        if cached_result:
            logger.info(f"Cache hit for product search: {query}")
            return cached_result
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Optimize API request
        search_params = {
            "query": query,
            "location": location or "default",
            "filters": filters or {},
            "limit": 50,
            "include_pricing": True,
            "include_availability": True,
            "include_promotions": True
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/products/search",
                    params=search_params,
                    headers=self._get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    products = response.json()
                    
                    # Enhanced product enrichment
                    enriched_products = await self._enrich_product_data(products.get("results", []))
                    
                    result = {
                        "products": enriched_products,
                        "total_found": len(enriched_products),
                        "search_query": query,
                        "location": location,
                        "cached": False,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Cache with appropriate TTL
                    await self.cache_manager.set_with_strategy(cache_key, result, "instacart_products")
                    
                    return result
                else:
                    return await self._handle_api_error(response)
                    
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return await self._handle_exception(e, "product_search")
    
    async def create_optimized_shopping_list(self, items: List[Dict], budget: float, preferences: Dict = None) -> Dict[str, Any]:
        """Create optimized shopping list with multi-store coordination"""
        
        # Step 1: Find best prices across all available stores
        logger.info(f"Optimizing shopping list for {len(items)} items with ${budget} budget")
        
        store_prices = await self._compare_prices_across_stores(items)
        
        # Step 2: Optimize store selection for cost vs convenience
        optimization_result = await self._optimize_store_selection_internal(store_prices, budget, preferences)
        
        # Step 3: Create shopping lists per store
        shopping_lists = await self._create_store_shopping_lists(optimization_result)
        
        # Step 4: Generate Instacart shopping experience
        instacart_experience = await self._generate_shopping_experience(shopping_lists, budget)
        
        return {
            "success": True,
            "shopping_lists": shopping_lists,
            "total_cost": instacart_experience["total_cost"],
            "estimated_savings": instacart_experience["savings"],
            "delivery_options": instacart_experience["delivery_options"],
            "instacart_urls": instacart_experience["urls"],
            "optimization_details": {
                "stores_considered": len(store_prices),
                "cost_optimization": optimization_result["cost_savings"],
                "convenience_score": optimization_result["convenience_score"],
                "delivery_optimization": optimization_result["delivery_details"]
            },
            "budget_status": {
                "target_budget": budget,
                "actual_cost": instacart_experience["total_cost"],
                "under_budget": instacart_experience["total_cost"] <= budget,
                "savings_amount": max(0, budget - instacart_experience["total_cost"])
            }
        }
    
    async def monitor_deals_and_prices(self, products: List[str], user_id: str) -> Dict[str, Any]:
        """Advanced deal monitoring with predictive analytics"""
        monitoring_setup = {
            "products": products,
            "user_id": user_id,
            "monitoring_started": datetime.now().isoformat(),
            "price_thresholds": await self._calculate_price_thresholds(products),
            "deal_predictions": await self._predict_upcoming_deals(products)
        }
        
        # Set up real-time monitoring
        await self._setup_price_monitoring(monitoring_setup)
        
        # Immediate deal analysis
        current_deals = await self._analyze_current_deals(products)
        
        return {
            "monitoring_active": True,
            "current_deals": current_deals,
            "predicted_deals": monitoring_setup["deal_predictions"],
            "savings_opportunities": await self._identify_savings_opportunities(products),
            "monitoring_id": f"monitor_{user_id}_{int(datetime.now().timestamp())}",
            "alert_preferences": {
                "price_drop_threshold": 15,  # 15% price drop
                "deal_categories": ["produce", "meat", "dairy"],
                "notification_frequency": "daily"
            }
        }
    
    async def manage_order_lifecycle(self, order_data: Dict, action_type: str = "create") -> Dict[str, Any]:
        """Complete order lifecycle management"""
        
        if action_type == "create":
            return await self._create_instacart_order(order_data)
        elif action_type == "track":
            return await self._track_order_status(order_data.get('order_id'))
        elif action_type == "modify":
            return await self._modify_order(order_data)
        elif action_type == "cancel":
            return await self._cancel_order(order_data.get('order_id'))
        else:
            raise ValueError(f"Unknown order action: {action_type}")
    
    async def optimize_store_selection(self, items: List[Dict], location: str, preferences: Dict) -> Dict[str, Any]:
        """Advanced store selection optimization"""
        
        # Get store availability and pricing
        stores_data = await self._get_stores_in_location(location)
        
        # Calculate optimization scores
        optimization_factors = {
            "cost": preferences.get("cost_weight", 0.4),
            "convenience": preferences.get("convenience_weight", 0.3),
            "delivery_speed": preferences.get("speed_weight", 0.2),
            "quality": preferences.get("quality_weight", 0.1)
        }
        
        store_scores = {}
        for store in stores_data:
            store_id = store["id"]
            
            # Calculate individual scores
            cost_score = await self._calculate_cost_score(store, items)
            convenience_score = await self._calculate_convenience_score(store, location)
            delivery_score = await self._calculate_delivery_score(store)
            quality_score = await self._calculate_quality_score(store)
            
            # Weighted total score
            total_score = (
                cost_score * optimization_factors["cost"] +
                convenience_score * optimization_factors["convenience"] +
                delivery_score * optimization_factors["delivery_speed"] +
                quality_score * optimization_factors["quality"]
            )
            
            store_scores[store_id] = {
                "store": store,
                "total_score": total_score,
                "individual_scores": {
                    "cost": cost_score,
                    "convenience": convenience_score,
                    "delivery": delivery_score,
                    "quality": quality_score
                }
            }
        
        # Select optimal stores
        sorted_stores = sorted(store_scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
        
        return {
            "recommended_stores": sorted_stores[:3],  # Top 3 stores
            "optimization_factors": optimization_factors,
            "total_stores_analyzed": len(stores_data)
        }
    
    # Helper methods
    
    def _generate_cache_key(self, operation: str, *args) -> str:
        """Generate cache key from operation and arguments"""
        key_data = f"{operation}:{':'.join(str(arg) for arg in args if arg is not None)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Instacart API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Bruno-AI/2.0",
            "X-Affiliate-ID": self.affiliate_id
        }
    
    async def _enrich_product_data(self, products: List[Dict]) -> List[Dict]:
        """Enrich product data with additional insights and optimizations"""
        enriched = []
        
        for product in products:
            try:
                enriched_product = {
                    **product,
                    "price_history": await self._get_price_history(product.get("id")),
                    "alternatives": await self._find_alternatives(product),
                    "nutrition_score": await self._calculate_nutrition_score(product),
                    "value_rating": await self._calculate_value_rating(product),
                    "availability_forecast": await self._forecast_availability(product.get("id")),
                    "substitution_options": await self._find_substitutions(product),
                    "seasonality_info": await self._get_seasonality_info(product)
                }
                enriched.append(enriched_product)
            except Exception as e:
                logger.warning(f"Failed to enrich product {product.get('name', 'unknown')}: {e}")
                enriched.append(product)  # Add original product if enrichment fails
        
        return enriched
    
    async def _compare_prices_across_stores(self, items: List[Dict]) -> Dict[str, Any]:
        """Compare prices across multiple stores"""
        # Implementation for multi-store price comparison
        # This would integrate with Instacart's store comparison API
        
        stores_pricing = {}
        
        for item in items:
            item_name = item.get('name', '')
            
            # Search across multiple stores
            store_results = await self._search_item_across_stores(item_name)
            
            for store_result in store_results:
                store_id = store_result["store_id"]
                if store_id not in stores_pricing:
                    stores_pricing[store_id] = {
                        "store_info": store_result["store_info"],
                        "items": [],
                        "total_cost": 0,
                        "cost_score": 0,
                        "convenience_score": 0,
                        "delivery_score": 0,
                        "quality_score": 0
                    }
                
                stores_pricing[store_id]["items"].append({
                    "item": item_name,
                    "price": store_result["price"],
                    "availability": store_result["availability"],
                    "quality_rating": store_result.get("quality_rating", 0)
                })
                
                stores_pricing[store_id]["total_cost"] += store_result["price"]
        
        return stores_pricing
    
    async def _search_item_across_stores(self, item_name: str) -> List[Dict]:
        """Search for item across multiple stores"""
        # Mock implementation - in real scenario, this would call Instacart's multi-store API
        return [
            {
                "store_id": "store_1",
                "store_info": {"name": "Whole Foods", "distance": 2.3},
                "price": 12.99,
                "availability": True,
                "quality_rating": 4.5
            },
            {
                "store_id": "store_2", 
                "store_info": {"name": "Kroger", "distance": 1.8},
                "price": 10.99,
                "availability": True,
                "quality_rating": 4.2
            }
        ]
    
    def _load_category_mappings(self) -> Dict[str, List[str]]:
        """Load product category mappings for optimization"""
        return {
            "produce": ["fruits", "vegetables", "herbs"],
            "meat": ["beef", "chicken", "pork", "seafood"],
            "dairy": ["milk", "cheese", "yogurt", "butter"],
            "pantry": ["rice", "pasta", "canned_goods", "spices"],
            "frozen": ["frozen_vegetables", "frozen_meals", "ice_cream"],
            "bakery": ["bread", "pastries", "cakes"]
        }
    
    async def _handle_api_error(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API errors gracefully"""
        error_message = f"Instacart API error: {response.status_code}"
        try:
            error_data = response.json()
            error_message += f" - {error_data.get('message', 'Unknown error')}"
        except:
            pass
        
        logger.error(error_message)
        
        return {
            "success": False,
            "error": error_message,
            "fallback_available": True,
            "fallback_message": "Using cached pricing data and estimated availability"
        }
    
    async def _handle_exception(self, exception: Exception, operation: str) -> Dict[str, Any]:
        """Handle exceptions with fallback mechanisms"""
        logger.error(f"Exception in {operation}: {str(exception)}")
        
        return {
            "success": False,
            "error": str(exception),
            "operation": operation,
            "fallback_available": True,
            "recommendations": [
                "Try again in a few minutes",
                "Check internet connection",
                "Use cached data if available"
            ]
        }

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, requests_per_hour: int):
        self.requests_per_hour = requests_per_hour
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make API call"""
        now = datetime.now()
        
        # Remove requests older than 1 hour
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(hours=1)]
        
        # Check if we're within rate limit
        if len(self.requests) >= self.requests_per_hour:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = (oldest_request + timedelta(hours=1) - now).total_seconds()
            
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)
