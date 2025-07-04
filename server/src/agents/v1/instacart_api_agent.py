"""Instacart API Agent - Integration with Instacart for product data and ordering.

This agent handles all interactions with the Instacart API including product search,
pricing, availability, and order management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json
import aiohttp
from dataclasses import dataclass

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstacartConfig:
    """Configuration for Instacart API."""
    api_key: str
    base_url: str = "https://api.instacart.com/v2"
    timeout: int = 30
    max_retries: int = 3


class InstacartProduct(BaseModel):
    """Model for Instacart product information."""
    product_id: str
    name: str
    brand: str
    description: str
    price: Decimal
    unit_price: Optional[Decimal] = None
    unit: str = "each"
    size: str = ""
    category: str
    subcategory: str = ""
    image_url: Optional[str] = None
    availability: bool = True
    store_id: str
    store_name: str
    nutrition_info: Optional[Dict[str, Any]] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    organic: bool = False
    sale_price: Optional[Decimal] = None
    promotion: Optional[str] = None
    stock_level: str = "in_stock"  # in_stock, low_stock, out_of_stock
    last_updated: datetime = Field(default_factory=datetime.now)


class InstacartStore(BaseModel):
    """Model for Instacart store information."""
    store_id: str
    name: str
    chain: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: Optional[str] = None
    hours: Dict[str, str] = Field(default_factory=dict)
    delivery_available: bool = True
    pickup_available: bool = False
    delivery_fee: Decimal = Field(default=Decimal('5.99'))
    minimum_order: Decimal = Field(default=Decimal('35.00'))
    estimated_delivery_time: str = "1-2 hours"
    rating: Optional[float] = None
    distance_miles: Optional[float] = None


class InstacartCart(BaseModel):
    """Model for Instacart shopping cart."""
    cart_id: str
    store_id: str
    items: List[Dict[str, Any]] = Field(default_factory=list)
    subtotal: Decimal = Field(default=Decimal('0.00'))
    tax: Decimal = Field(default=Decimal('0.00'))
    delivery_fee: Decimal = Field(default=Decimal('5.99'))
    service_fee: Decimal = Field(default=Decimal('2.99'))
    tip: Decimal = Field(default=Decimal('0.00'))
    total: Decimal = Field(default=Decimal('0.00'))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class InstacartOrder(BaseModel):
    """Model for Instacart order information."""
    order_id: str
    cart_id: str
    status: str = "pending"  # pending, confirmed, shopping, delivered, cancelled
    store: InstacartStore
    items: List[Dict[str, Any]]
    delivery_address: Dict[str, str]
    delivery_instructions: Optional[str] = None
    estimated_delivery: datetime
    actual_delivery: Optional[datetime] = None
    shopper_info: Optional[Dict[str, str]] = None
    total_amount: Decimal
    payment_method: str
    created_at: datetime = Field(default_factory=datetime.now)
    tracking_url: Optional[str] = None


class InstacartAPIAgent(LlmAgent):
    """Instacart API Agent for product search, pricing, and order management."""

    def __init__(self, config: InstacartConfig, model: str = "gemini-2.0-flash-exp"):
        self._config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._stores_cache: Dict[str, InstacartStore] = {}
        self._products_cache: Dict[str, InstacartProduct] = {}
        self._carts: Dict[str, InstacartCart] = {}
        self._orders: Dict[str, InstacartOrder] = {}
        
        # Initialize with demo data for development
        self._initialize_demo_data()
        
        # Define tools for the Instacart API agent
        tools = [
            self._search_products_tool(),
            self._get_product_details_tool(),
            self._find_stores_tool(),
            self._get_store_details_tool(),
            self._create_cart_tool(),
            self._add_to_cart_tool(),
            self._update_cart_item_tool(),
            self._remove_from_cart_tool(),
            self._get_cart_tool(),
            self._estimate_delivery_tool(),
            self._place_order_tool(),
            self._track_order_tool(),
            self._get_product_alternatives_tool(),
            self._check_product_availability_tool(),
            self._get_weekly_deals_tool()
        ]

        super().__init__(
            model=model,
            name="instacart_api_agent",
            description="Instacart API integration agent for product search, pricing, and order management",
            instruction="""You are an expert Instacart API integration specialist focused on
            providing accurate, real-time grocery product information and seamless ordering.
            
            Your capabilities include:
            1. Searching for products across multiple stores with real-time pricing
            2. Providing detailed product information including nutrition and availability
            3. Finding nearby stores with delivery and pickup options
            4. Managing shopping carts and calculating accurate totals
            5. Placing orders and tracking delivery status
            6. Finding product alternatives and substitutions
            7. Identifying weekly deals and promotions
            
            Always prioritize:
            - Accurate, up-to-date pricing and availability information
            - Clear communication about delivery fees, minimums, and timing
            - Helpful product alternatives when items are unavailable
            - Transparent cost breakdowns including taxes and fees
            - Reliable order tracking and status updates
            
            When handling requests:
            - Verify product availability before adding to cart
            - Suggest cost-effective alternatives when appropriate
            - Provide clear delivery time estimates
            - Handle API errors gracefully with helpful fallback options
            - Maintain accurate cart totals and order summaries""",
            tools=tools
        )

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _initialize_demo_data(self) -> None:
        """Initialize demo data for development and testing."""
        # Demo stores
        demo_stores = [
            {
                "store_id": "walmart_001",
                "name": "Walmart Supercenter",
                "chain": "Walmart",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "90210",
                "delivery_fee": 7.95,
                "minimum_order": 35.00,
                "estimated_delivery_time": "2-3 hours"
            },
            {
                "store_id": "kroger_001",
                "name": "Kroger",
                "chain": "Kroger",
                "address": "456 Oak Ave",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "90210",
                "delivery_fee": 5.99,
                "minimum_order": 35.00,
                "estimated_delivery_time": "1-2 hours"
            },
            {
                "store_id": "safeway_001",
                "name": "Safeway",
                "chain": "Safeway",
                "address": "789 Pine St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "90210",
                "delivery_fee": 6.99,
                "minimum_order": 30.00,
                "estimated_delivery_time": "1-2 hours"
            }
        ]
        
        for store_data in demo_stores:
            store = InstacartStore(**store_data)
            self._stores_cache[store.store_id] = store
        
        # Demo products
        demo_products = [
            {
                "product_id": "chicken_breast_001",
                "name": "Boneless Skinless Chicken Breast",
                "brand": "Fresh",
                "description": "Fresh boneless skinless chicken breast, family pack",
                "price": 4.99,
                "unit_price": 4.99,
                "unit": "lb",
                "size": "per lb",
                "category": "Meat & Seafood",
                "subcategory": "Chicken",
                "store_id": "walmart_001",
                "store_name": "Walmart Supercenter"
            },
            {
                "product_id": "ground_beef_001",
                "name": "Ground Beef 80/20",
                "brand": "Fresh",
                "description": "Fresh ground beef, 80% lean / 20% fat",
                "price": 5.99,
                "unit_price": 5.99,
                "unit": "lb",
                "size": "per lb",
                "category": "Meat & Seafood",
                "subcategory": "Beef",
                "store_id": "walmart_001",
                "store_name": "Walmart Supercenter"
            },
            {
                "product_id": "bananas_001",
                "name": "Bananas",
                "brand": "Fresh",
                "description": "Fresh bananas, sold by the pound",
                "price": 0.68,
                "unit_price": 0.68,
                "unit": "lb",
                "size": "per lb",
                "category": "Produce",
                "subcategory": "Fruits",
                "store_id": "walmart_001",
                "store_name": "Walmart Supercenter",
                "organic": False
            },
            {
                "product_id": "milk_001",
                "name": "Whole Milk",
                "brand": "Great Value",
                "description": "Great Value Whole Milk, 1 gallon",
                "price": 3.48,
                "unit_price": 3.48,
                "unit": "gallon",
                "size": "1 gallon",
                "category": "Dairy & Eggs",
                "subcategory": "Milk",
                "store_id": "walmart_001",
                "store_name": "Walmart Supercenter"
            },
            {
                "product_id": "bread_001",
                "name": "White Bread",
                "brand": "Wonder",
                "description": "Wonder Classic White Bread, 20 oz loaf",
                "price": 1.28,
                "unit_price": 1.28,
                "unit": "loaf",
                "size": "20 oz",
                "category": "Bakery",
                "subcategory": "Bread",
                "store_id": "walmart_001",
                "store_name": "Walmart Supercenter"
            }
        ]
        
        for product_data in demo_products:
            product = InstacartProduct(**product_data)
            self._products_cache[product.product_id] = product

    async def _make_api_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an API request to Instacart with error handling and retries."""
        if not self._session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._config.timeout)
            )
        
        url = f"{self._config.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self._config.max_retries):
            try:
                async with self._session.request(method, url, headers=headers, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        return {"error": f"API request failed: {response.status}", "details": error_text}
            except asyncio.TimeoutError:
                logger.warning(f"API request timeout, attempt {attempt + 1}")
                if attempt == self._config.max_retries - 1:
                    return {"error": "Request timeout", "details": "API request timed out after retries"}
            except Exception as e:
                logger.error(f"API request error: {e}")
                return {"error": "Request failed", "details": str(e)}
        
        return {"error": "Max retries exceeded", "details": "Failed after multiple attempts"}

    def _search_products_tool(self) -> FunctionTool:
        """Create tool for searching products."""
        async def search_products(
            query: str,
            store_id: Optional[str] = None,
            category: Optional[str] = None,
            max_results: int = 20,
            sort_by: str = "relevance"  # relevance, price_low, price_high, rating
        ) -> Dict[str, Any]:
            """Search for products across Instacart stores.
            
            Args:
                query: Search query for products
                store_id: Specific store to search in (optional)
                category: Product category filter (optional)
                max_results: Maximum number of results to return
                sort_by: Sort order for results
                
            Returns:
                List of matching products with pricing and availability
            """
            try:
                # For demo purposes, search in cached products
                # In production, this would make an API call
                matching_products = []
                
                query_lower = query.lower()
                for product in self._products_cache.values():
                    # Check if query matches product name, brand, or description
                    if (query_lower in product.name.lower() or 
                        query_lower in product.brand.lower() or 
                        query_lower in product.description.lower()):
                        
                        # Apply store filter if specified
                        if store_id and product.store_id != store_id:
                            continue
                        
                        # Apply category filter if specified
                        if category and category.lower() not in product.category.lower():
                            continue
                        
                        matching_products.append(product.dict())
                
                # Sort results
                if sort_by == "price_low":
                    matching_products.sort(key=lambda x: x["price"])
                elif sort_by == "price_high":
                    matching_products.sort(key=lambda x: x["price"], reverse=True)
                
                # Limit results
                matching_products = matching_products[:max_results]
                
                return {
                    "query": query,
                    "products": matching_products,
                    "total_results": len(matching_products),
                    "filters": {
                        "store_id": store_id,
                        "category": category,
                        "sort_by": sort_by
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error searching products: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(search_products)

    def _get_product_details_tool(self) -> FunctionTool:
        """Create tool for getting detailed product information."""
        async def get_product_details(product_id: str) -> Dict[str, Any]:
            """Get detailed information for a specific product.
            
            Args:
                product_id: Unique product identifier
                
            Returns:
                Detailed product information including nutrition, ingredients, etc.
            """
            try:
                if product_id not in self._products_cache:
                    return {"error": f"Product '{product_id}' not found", "success": False}
                
                product = self._products_cache[product_id]
                
                # In production, this might fetch additional details from API
                detailed_info = product.dict()
                
                # Add mock nutrition info if not present
                if not detailed_info.get("nutrition_info"):
                    detailed_info["nutrition_info"] = {
                        "calories_per_serving": 150,
                        "servings_per_container": 4,
                        "total_fat_g": 5,
                        "saturated_fat_g": 2,
                        "cholesterol_mg": 30,
                        "sodium_mg": 400,
                        "total_carbs_g": 15,
                        "dietary_fiber_g": 2,
                        "sugars_g": 3,
                        "protein_g": 12
                    }
                
                return {
                    "product": detailed_info,
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error getting product details: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_product_details)

    def _find_stores_tool(self) -> FunctionTool:
        """Create tool for finding nearby stores."""
        async def find_stores(
            zip_code: str,
            radius_miles: float = 10.0,
            delivery_only: bool = False
        ) -> Dict[str, Any]:
            """Find stores near a location.
            
            Args:
                zip_code: ZIP code to search near
                radius_miles: Search radius in miles
                delivery_only: Only return stores with delivery service
                
            Returns:
                List of nearby stores with delivery information
            """
            try:
                # For demo purposes, return cached stores
                # In production, this would use geolocation API
                available_stores = []
                
                for store in self._stores_cache.values():
                    # Apply delivery filter if specified
                    if delivery_only and not store.delivery_available:
                        continue
                    
                    # Add mock distance calculation
                    store_dict = store.dict()
                    store_dict["distance_miles"] = 2.5  # Mock distance
                    available_stores.append(store_dict)
                
                # Sort by distance
                available_stores.sort(key=lambda x: x["distance_miles"])
                
                return {
                    "zip_code": zip_code,
                    "stores": available_stores,
                    "total_stores": len(available_stores),
                    "search_radius": radius_miles,
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error finding stores: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(find_stores)

    def _get_store_details_tool(self) -> FunctionTool:
        """Create tool for getting store details."""
        async def get_store_details(store_id: str) -> Dict[str, Any]:
            """Get detailed information for a specific store.
            
            Args:
                store_id: Unique store identifier
                
            Returns:
                Detailed store information including hours, fees, etc.
            """
            try:
                if store_id not in self._stores_cache:
                    return {"error": f"Store '{store_id}' not found", "success": False}
                
                store = self._stores_cache[store_id]
                store_details = store.dict()
                
                # Add mock hours if not present
                if not store_details.get("hours"):
                    store_details["hours"] = {
                        "monday": "6:00 AM - 11:00 PM",
                        "tuesday": "6:00 AM - 11:00 PM",
                        "wednesday": "6:00 AM - 11:00 PM",
                        "thursday": "6:00 AM - 11:00 PM",
                        "friday": "6:00 AM - 11:00 PM",
                        "saturday": "6:00 AM - 11:00 PM",
                        "sunday": "7:00 AM - 10:00 PM"
                    }
                
                return {
                    "store": store_details,
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error getting store details: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_store_details)

    def _create_cart_tool(self) -> FunctionTool:
        """Create tool for creating a new shopping cart."""
        async def create_cart(store_id: str) -> Dict[str, Any]:
            """Create a new shopping cart for a specific store.
            
            Args:
                store_id: Store to create cart for
                
            Returns:
                New cart information
            """
            try:
                if store_id not in self.stores_cache:
                    return {"error": f"Store '{store_id}' not found", "success": False}
                
                cart_id = f"cart_{int(datetime.now().timestamp())}"
                store = self.stores_cache[store_id]
                
                cart = InstacartCart(
                    cart_id=cart_id,
                    store_id=store_id,
                    delivery_fee=store.delivery_fee
                )
                
                self._carts[cart_id] = cart
                
                return {
                    "cart": cart.dict(),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error creating cart: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(create_cart)

    def _add_to_cart_tool(self) -> FunctionTool:
        """Create tool for adding items to cart."""
        async def add_to_cart(
            cart_id: str,
            product_id: str,
            quantity: int = 1
        ) -> Dict[str, Any]:
            """Add a product to the shopping cart.
            
            Args:
                cart_id: Cart to add item to
                product_id: Product to add
                quantity: Quantity to add
                
            Returns:
                Updated cart information
            """
            try:
                if cart_id not in self._carts:
                    return {"error": f"Cart '{cart_id}' not found", "success": False}
                
                if product_id not in self._products_cache:
                    return {"error": f"Product '{product_id}' not found", "success": False}
                
                cart = self._carts[cart_id]
                product = self._products_cache[product_id]
                
                # Check if product is from the same store
                if product.store_id != cart.store_id:
                    return {
                        "error": f"Product is from different store. Cart store: {cart.store_id}, Product store: {product.store_id}",
                        "success": False
                    }
                
                # Check if item already in cart
                existing_item = None
                for item in cart.items:
                    if item["product_id"] == product_id:
                        existing_item = item
                        break
                
                if existing_item:
                    existing_item["quantity"] += quantity
                    existing_item["total_price"] = existing_item["quantity"] * product.price
                else:
                    cart_item = {
                        "product_id": product_id,
                        "name": product.name,
                        "brand": product.brand,
                        "price": float(product.price),
                        "quantity": quantity,
                        "total_price": float(product.price * quantity),
                        "unit": product.unit
                    }
                    cart.items.append(cart_item)
                
                # Recalculate cart totals
                self._update_cart_totals(cart)
                
                return {
                    "cart": cart.dict(),
                    "item_added": {
                        "product_id": product_id,
                        "name": product.name,
                        "quantity": quantity,
                        "price": float(product.price)
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error adding to cart: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(add_to_cart)

    def _update_cart_item_tool(self) -> FunctionTool:
        """Create tool for updating cart item quantities."""
        async def update_cart_item(
            cart_id: str,
            product_id: str,
            new_quantity: int
        ) -> Dict[str, Any]:
            """Update the quantity of an item in the cart.
            
            Args:
                cart_id: Cart containing the item
                product_id: Product to update
                new_quantity: New quantity (0 to remove)
                
            Returns:
                Updated cart information
            """
            try:
                if cart_id not in self._carts:
                    return {"error": f"Cart '{cart_id}' not found", "success": False}
                
                cart = self._carts[cart_id]
                
                # Find the item in cart
                item_found = False
                for i, item in enumerate(cart.items):
                    if item["product_id"] == product_id:
                        if new_quantity <= 0:
                            # Remove item
                            cart.items.pop(i)
                        else:
                            # Update quantity
                            item["quantity"] = new_quantity
                            item["total_price"] = new_quantity * item["price"]
                        item_found = True
                        break
                
                if not item_found:
                    return {"error": f"Product '{product_id}' not found in cart", "success": False}
                
                # Recalculate cart totals
                self._update_cart_totals(cart)
                
                return {
                    "cart": cart.dict(),
                    "updated_item": {
                        "product_id": product_id,
                        "new_quantity": new_quantity
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error updating cart item: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(update_cart_item)

    def _remove_from_cart_tool(self) -> FunctionTool:
        """Create tool for removing items from cart."""
        async def remove_from_cart(cart_id: str, product_id: str) -> Dict[str, Any]:
            """Remove a product from the shopping cart.
            
            Args:
                cart_id: Cart to remove item from
                product_id: Product to remove
                
            Returns:
                Updated cart information
            """
            return await self.update_cart_item(cart_id, product_id, 0)

        return FunctionTool(remove_from_cart)

    def _get_cart_tool(self) -> FunctionTool:
        """Create tool for getting cart details."""
        async def get_cart(cart_id: str) -> Dict[str, Any]:
            """Get current cart contents and totals.
            
            Args:
                cart_id: Cart to retrieve
                
            Returns:
                Complete cart information
            """
            try:
                if cart_id not in self._carts:
                    return {"error": f"Cart '{cart_id}' not found", "success": False}
                
                cart = self._carts[cart_id]
                
                return {
                    "cart": cart.dict(),
                    "item_count": len(cart.items),
                    "total_quantity": sum(item["quantity"] for item in cart.items),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error getting cart: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_cart)

    def _estimate_delivery_tool(self) -> FunctionTool:
        """Create tool for estimating delivery time and cost."""
        async def estimate_delivery(
            cart_id: str,
            delivery_address: Dict[str, str]
        ) -> Dict[str, Any]:
            """Estimate delivery time and cost for a cart.
            
            Args:
                cart_id: Cart to estimate delivery for
                delivery_address: Delivery address details
                
            Returns:
                Delivery time and cost estimates
            """
            try:
                if cart_id not in self._carts:
                    return {"error": f"Cart '{cart_id}' not found", "success": False}
                
                cart = self._carts[cart_id]
                store = self._stores_cache[cart.store_id]
                
                # Calculate estimated delivery time
                base_time = datetime.now() + timedelta(hours=2)  # Default 2 hours
                
                # Adjust based on time of day, store capacity, etc.
                current_hour = datetime.now().hour
                if current_hour >= 17:  # Evening rush
                    base_time += timedelta(minutes=30)
                
                return {
                    "cart_id": cart_id,
                    "store": store.dict(),
                    "delivery_address": delivery_address,
                    "estimates": {
                        "delivery_fee": float(store.delivery_fee),
                        "service_fee": float(cart.service_fee),
                        "estimated_delivery_time": base_time.isoformat(),
                        "delivery_window": f"{base_time.strftime('%I:%M %p')} - {(base_time + timedelta(hours=1)).strftime('%I:%M %p')}",
                        "minimum_order": float(store.minimum_order),
                        "meets_minimum": cart.subtotal >= store.minimum_order
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error estimating delivery: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(estimate_delivery)

    def _place_order_tool(self) -> FunctionTool:
        """Create tool for placing orders."""
        async def place_order(
            cart_id: str,
            delivery_address: Dict[str, str],
            payment_method: str,
            delivery_instructions: Optional[str] = None,
            tip_amount: float = 0.0
        ) -> Dict[str, Any]:
            """Place an order from a cart.
            
            Args:
                cart_id: Cart to order from
                delivery_address: Delivery address
                payment_method: Payment method identifier
                delivery_instructions: Special delivery instructions
                tip_amount: Tip amount for shopper
                
            Returns:
                Order confirmation details
            """
            try:
                if cart_id not in self._carts:
                    return {"error": f"Cart '{cart_id}' not found", "success": False}
                
                cart = self._carts[cart_id]
                store = self._stores_cache[cart.store_id]
                
                # Validate minimum order
                if cart.subtotal < store.minimum_order:
                    return {
                        "error": f"Order does not meet minimum of ${store.minimum_order}",
                        "current_subtotal": float(cart.subtotal),
                        "minimum_required": float(store.minimum_order),
                        "success": False
                    }
                
                # Update cart with tip
                cart.tip = Decimal(str(tip_amount))
                self._update_cart_totals(cart)
                
                # Create order
                order_id = f"order_{int(datetime.now().timestamp())}"
                estimated_delivery = datetime.now() + timedelta(hours=2)
                
                order = InstacartOrder(
                    order_id=order_id,
                    cart_id=cart_id,
                    status="confirmed",
                    store=store,
                    items=cart.items.copy(),
                    delivery_address=delivery_address,
                    delivery_instructions=delivery_instructions,
                    estimated_delivery=estimated_delivery,
                    total_amount=cart.total,
                    payment_method=payment_method,
                    tracking_url=f"https://instacart.com/track/{order_id}"
                )
                
                self._orders[order_id] = order
                
                return {
                    "order": order.dict(),
                    "confirmation": {
                        "order_id": order_id,
                        "estimated_delivery": estimated_delivery.isoformat(),
                        "total_amount": float(cart.total),
                        "tracking_url": order.tracking_url
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(place_order)

    def _track_order_tool(self) -> FunctionTool:
        """Create tool for tracking orders."""
        async def track_order(order_id: str) -> Dict[str, Any]:
            """Track the status of an order.
            
            Args:
                order_id: Order to track
                
            Returns:
                Current order status and tracking information
            """
            try:
                if order_id not in self._orders:
                    return {"error": f"Order '{order_id}' not found", "success": False}
                
                order = self._orders[order_id]
                
                # Simulate order progress
                time_since_order = datetime.now() - order.created_at
                
                if time_since_order < timedelta(minutes=15):
                    order.status = "confirmed"
                    status_message = "Order confirmed and being prepared"
                elif time_since_order < timedelta(hours=1):
                    order.status = "shopping"
                    status_message = "Shopper is gathering your items"
                    order.shopper_info = {
                        "name": "Sarah M.",
                        "rating": 4.9,
                        "phone": "+1-555-0123"
                    }
                elif time_since_order < timedelta(hours=2):
                    order.status = "delivered"
                    status_message = "Order delivered successfully"
                    order.actual_delivery = datetime.now()
                else:
                    order.status = "delivered"
                    status_message = "Order delivered successfully"
                    order.actual_delivery = order.estimated_delivery
                
                return {
                    "order": order.dict(),
                    "tracking": {
                        "status": order.status,
                        "status_message": status_message,
                        "estimated_delivery": order.estimated_delivery.isoformat(),
                        "actual_delivery": order.actual_delivery.isoformat() if order.actual_delivery else None,
                        "tracking_url": order.tracking_url
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error tracking order: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(track_order)

    def _get_product_alternatives_tool(self) -> FunctionTool:
        """Create tool for finding product alternatives."""
        async def get_product_alternatives(
            product_id: str,
            criteria: str = "price"  # price, brand, organic, size
        ) -> Dict[str, Any]:
            """Find alternative products based on criteria.
            
            Args:
                product_id: Original product to find alternatives for
                criteria: Criteria for alternatives (price, brand, organic, size)
                
            Returns:
                List of alternative products
            """
            try:
                if product_id not in self.products_cache:
                    return {"error": f"Product '{product_id}' not found", "success": False}
                
                original_product = self.products_cache[product_id]
                alternatives = []
                
                for product in self._products_cache.values():
                    if product.product_id == product_id:
                        continue
                    
                    # Check if it's in the same category
                    if product.category != original_product.category:
                        continue
                    
                    # Apply criteria-based filtering
                    if criteria == "price" and product.price >= original_product.price:
                        continue
                    elif criteria == "brand" and product.brand == original_product.brand:
                        continue
                    elif criteria == "organic" and not product.organic:
                        continue
                    
                    alternatives.append({
                        "product": product.dict(),
                        "price_difference": float(product.price - original_product.price),
                        "savings_percentage": float((original_product.price - product.price) / original_product.price * 100) if product.price < original_product.price else 0
                    })
                
                # Sort alternatives
                if criteria == "price":
                    alternatives.sort(key=lambda x: x["product"]["price"])
                
                return {
                    "original_product": original_product.dict(),
                    "alternatives": alternatives[:10],  # Top 10 alternatives
                    "criteria": criteria,
                    "total_alternatives": len(alternatives),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error finding alternatives: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_product_alternatives)

    def _check_product_availability_tool(self) -> FunctionTool:
        """Create tool for checking product availability."""
        async def check_product_availability(
            product_ids: List[str],
            store_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """Check availability of multiple products.
            
            Args:
                product_ids: List of product IDs to check
                store_id: Specific store to check (optional)
                
            Returns:
                Availability status for each product
            """
            try:
                availability_results = []
                
                for product_id in product_ids:
                    if product_id not in self.products_cache:
                        availability_results.append({
                            "product_id": product_id,
                            "available": False,
                            "reason": "Product not found"
                        })
                        continue
                    
                    product = self.products_cache[product_id]
                    
                    # Check store filter
                    if store_id and product.store_id != store_id:
                        availability_results.append({
                            "product_id": product_id,
                            "product_name": product.name,
                            "available": False,
                            "reason": f"Not available at store {store_id}"
                        })
                        continue
                    
                    # Check general availability
                    availability_results.append({
                        "product_id": product_id,
                        "product_name": product.name,
                        "available": product.availability,
                        "stock_level": product.stock_level,
                        "price": float(product.price),
                        "store_id": product.store_id,
                        "store_name": product.store_name
                    })
                
                available_count = sum(1 for result in availability_results if result["available"])
                
                return {
                    "products_checked": product_ids,
                    "availability_results": availability_results,
                    "summary": {
                        "total_products": len(product_ids),
                        "available_products": available_count,
                        "unavailable_products": len(product_ids) - available_count
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error checking availability: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(check_product_availability)

    def _get_weekly_deals_tool(self) -> FunctionTool:
        """Create tool for getting weekly deals and promotions."""
        async def get_weekly_deals(
            store_id: Optional[str] = None,
            category: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get current weekly deals and promotions.
            
            Args:
                store_id: Specific store to get deals for (optional)
                category: Product category filter (optional)
                
            Returns:
                List of current deals and promotions
            """
            try:
                # Mock weekly deals data
                deals = [
                    {
                        "deal_id": "deal_001",
                        "product_id": "chicken_breast_001",
                        "product_name": "Boneless Skinless Chicken Breast",
                        "regular_price": 4.99,
                        "sale_price": 3.99,
                        "discount_percentage": 20,
                        "savings": 1.00,
                        "store_id": "walmart_001",
                        "store_name": "Walmart Supercenter",
                        "category": "Meat & Seafood",
                        "promotion_type": "weekly_special",
                        "valid_until": (datetime.now() + timedelta(days=7)).isoformat(),
                        "limit_per_customer": 5
                    },
                    {
                        "deal_id": "deal_002",
                        "product_id": "bananas_001",
                        "product_name": "Bananas",
                        "regular_price": 0.68,
                        "sale_price": 0.48,
                        "discount_percentage": 29,
                        "savings": 0.20,
                        "store_id": "walmart_001",
                        "store_name": "Walmart Supercenter",
                        "category": "Produce",
                        "promotion_type": "flash_sale",
                        "valid_until": (datetime.now() + timedelta(days=3)).isoformat(),
                        "limit_per_customer": None
                    }
                ]
                
                # Apply filters
                filtered_deals = deals
                
                if store_id:
                    filtered_deals = [deal for deal in filtered_deals if deal["store_id"] == store_id]
                
                if category:
                    filtered_deals = [deal for deal in filtered_deals if category.lower() in deal["category"].lower()]
                
                # Calculate total potential savings
                total_savings = sum(deal["savings"] for deal in filtered_deals)
                
                return {
                    "deals": filtered_deals,
                    "filters": {
                        "store_id": store_id,
                        "category": category
                    },
                    "summary": {
                        "total_deals": len(filtered_deals),
                        "total_potential_savings": round(total_savings, 2),
                        "average_discount": round(sum(deal["discount_percentage"] for deal in filtered_deals) / len(filtered_deals), 1) if filtered_deals else 0
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error getting weekly deals: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_weekly_deals)

    def _update_cart_totals(self, cart: InstacartCart) -> None:
        """Update cart totals based on current items."""
        cart.subtotal = Decimal(str(sum(item["total_price"] for item in cart.items)))
        cart.tax = cart.subtotal * Decimal('0.0875')  # 8.75% tax rate
        cart.total = cart.subtotal + cart.tax + cart.delivery_fee + cart.service_fee + cart.tip
        cart.updated_at = datetime.now()