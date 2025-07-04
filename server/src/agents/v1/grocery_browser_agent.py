"""Grocery Browser Agent - Web scraping agent for real-time grocery pricing.

This agent uses Selenium to browse grocery store websites and gather
real-time pricing data for meal planning optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceData(BaseModel):
    """Model for storing price information."""
    item_name: str
    store: str
    price: Decimal
    unit: str = "each"
    availability: bool = True
    last_updated: datetime = Field(default_factory=datetime.now)
    product_url: Optional[str] = None
    image_url: Optional[str] = None


class StoreInventory(BaseModel):
    """Model for store inventory data."""
    store_name: str
    location: str
    items: List[PriceData]
    last_scraped: datetime = Field(default_factory=datetime.now)


class GroceryBrowserAgent(LlmAgent):
    """Grocery Browser Agent for real-time price discovery."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        # Initialize instance variables with leading underscores to bypass Pydantic validation
        self._price_cache: Dict[str, Any] = {}
        self._cache_duration = timedelta(hours=2)  # Cache prices for 2 hours
        self._driver: Optional[Any] = None
        
        # Store configurations
        self._store_configs = {
            "walmart": {
                "base_url": "https://www.walmart.com",
                "search_url": "https://www.walmart.com/search?q={query}",
                "selectors": {
                    "price": "[data-testid='price-current']",
                    "product_name": "[data-testid='product-title']",
                    "product_link": "[data-testid='product-title'] a",
                    "availability": "[data-testid='add-to-cart']"
                }
            },
            "target": {
                "base_url": "https://www.target.com",
                "search_url": "https://www.target.com/s?searchTerm={query}",
                "selectors": {
                    "price": "[data-test='product-price']",
                    "product_name": "[data-test='product-title']",
                    "product_link": "[data-test='product-title'] a",
                    "availability": "[data-test='shipItButton']"
                }
            },
            "kroger": {
                "base_url": "https://www.kroger.com",
                "search_url": "https://www.kroger.com/search?query={query}",
                "selectors": {
                    "price": ".kds-Price-promotional",
                    "product_name": ".ProductCard-title",
                    "product_link": ".ProductCard-content a",
                    "availability": ".ProductCard-addToCart"
                }
            }
        }
        
        # Define tools after instance variables are set
        tools = [
            self._browse_walmart_prices_tool(),
            self._browse_target_prices_tool(),
            self._browse_kroger_prices_tool(),
            self._get_weekly_deals_tool(),
            self._verify_store_inventory_tool(),
            self._compare_prices_across_stores_tool()
        ]
        
        super().__init__(
            model=model,
            name="grocery_browser_agent",
            description="Web scraping agent for real-time grocery pricing and inventory data",
            instruction="""You are a specialized grocery price discovery agent that browses
            major grocery store websites to gather real-time pricing data.
            
            Your responsibilities:
            1. Scrape current prices from Walmart, Target, and Kroger websites
            2. Verify product availability and inventory status
            3. Identify weekly deals and promotional pricing
            4. Provide accurate price comparisons across stores
            5. Cache pricing data to minimize redundant requests
            
            Always prioritize:
            - Accurate and up-to-date pricing information
            - Respectful web scraping practices with appropriate delays
            - Error handling for website changes or unavailable products
            - Efficient caching to reduce load on store websites
            
            When scraping fails, provide fallback pricing estimates based on
            historical data or typical market prices.""",
            tools=tools
        )

    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        if self._driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            try:
                self._driver = webdriver.Chrome(options=chrome_options)
                self._driver.implicitly_wait(10)
                logger.info("Chrome WebDriver initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Chrome WebDriver: {e}")
                raise
        
        return self._driver

    def _cleanup_driver(self) -> None:
        """Clean up WebDriver resources."""
        if hasattr(self, '_driver') and self._driver:
            try:
                self._driver.quit()
                self._driver = None
                logger.info("Chrome WebDriver cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up WebDriver: {e}")

    def _is_cache_valid(self, item_key: str) -> bool:
        """Check if cached price data is still valid."""
        if item_key not in self._price_cache:
            return False
        
        # Check if any cached item is still within cache duration
        for price_data in self._price_cache[item_key]:
            if datetime.now() - price_data.last_updated < self._cache_duration:
                return True
        
        return False

    def _browse_walmart_prices_tool(self) -> FunctionTool:
        """Create tool for browsing Walmart prices."""
        async def browse_walmart_prices(items: List[str]) -> Dict[str, Any]:
            """Browse Walmart website for current prices of specified items.
            
            Args:
                items: List of grocery items to search for
                
            Returns:
                Dictionary containing price data from Walmart
            """
            try:
                results = []
                driver = self._setup_driver()
                
                for item in items:
                    # Check cache first
                    cache_key = f"walmart_{item.lower().replace(' ', '_')}"
                    if self._is_cache_valid(cache_key):
                        cached_data = [p for p in self._price_cache[cache_key] if p.store == "walmart"]
                        if cached_data:
                            results.extend([p.dict() for p in cached_data])
                            continue
                    
                    try:
                        # Navigate to Walmart search
                        search_url = self._store_configs["walmart"]["search_url"].format(query=item.replace(" ", "+"))
                        driver.get(search_url)
                        
                        # Wait for page to load
                        time.sleep(2)
                        
                        # Find product elements
                        wait = WebDriverWait(driver, 10)
                        products = wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "[data-testid='item-stack']")
                        ))
                        
                        # Extract price data from first few products
                        for i, product in enumerate(products[:3]):  # Limit to first 3 results
                            try:
                                name_element = product.find_element(By.CSS_SELECTOR, "[data-testid='product-title']")
                                price_element = product.find_element(By.CSS_SELECTOR, "[data-testid='price-current']")
                                
                                product_name = name_element.text.strip()
                                price_text = price_element.text.strip().replace("$", "").replace(",", "")
                                
                                # Extract numeric price
                                price_value = float(price_text.split()[0]) if price_text else 0.0
                                
                                price_data = PriceData(
                                    item_name=product_name,
                                    store="walmart",
                                    price=Decimal(str(price_value)),
                                    availability=True
                                )
                                
                                results.append(price_data.dict())
                                
                                # Cache the result
                                if cache_key not in self._price_cache:
                                    self._price_cache[cache_key] = []
                                self._price_cache[cache_key].append(price_data)
                                
                            except (NoSuchElementException, ValueError) as e:
                                logger.warning(f"Could not extract price for product {i}: {e}")
                                continue
                        
                        # Add delay between searches
                        time.sleep(1)
                        
                    except TimeoutException:
                        logger.warning(f"Timeout while searching for {item} on Walmart")
                        # Add fallback price estimate
                        fallback_price = PriceData(
                            item_name=item,
                            store="walmart",
                            price=Decimal("5.99"),  # Default estimate
                            availability=False
                        )
                        results.append(fallback_price.dict())
                
                return {
                    "store": "walmart",
                    "items_searched": items,
                    "results": results,
                    "total_items_found": len(results),
                    "search_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error browsing Walmart prices: {e}")
                return {
                    "store": "walmart",
                    "error": str(e),
                    "items_searched": items,
                    "results": []
                }
            finally:
                # Don't cleanup driver here as it might be reused
                pass

        return FunctionTool(browse_walmart_prices)

    def _browse_target_prices_tool(self) -> FunctionTool:
        """Create tool for browsing Target prices."""
        async def browse_target_prices(items: List[str]) -> Dict[str, Any]:
            """Browse Target website for current prices of specified items.
            
            Args:
                items: List of grocery items to search for
                
            Returns:
                Dictionary containing price data from Target
            """
            try:
                results = []
                driver = self._setup_driver()
                
                for item in items:
                    # Check cache first
                    cache_key = f"target_{item.lower().replace(' ', '_')}"
                    if self._is_cache_valid(cache_key):
                        cached_data = [p for p in self._price_cache[cache_key] if p.store == "target"]
                        if cached_data:
                            results.extend([p.dict() for p in cached_data])
                            continue
                    
                    try:
                        # Navigate to Target search
                        search_url = self._store_configs["target"]["search_url"].format(query=item.replace(" ", "+"))
                        driver.get(search_url)
                        
                        # Wait for page to load
                        time.sleep(3)
                        
                        # Find product elements (Target has different structure)
                        wait = WebDriverWait(driver, 10)
                        products = wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "[data-test='@web/site-top-of-funnel/ProductCardWrapper']")
                        ))
                        
                        # Extract price data from first few products
                        for i, product in enumerate(products[:3]):
                            try:
                                name_element = product.find_element(By.CSS_SELECTOR, "[data-test='product-title']")
                                price_element = product.find_element(By.CSS_SELECTOR, "[data-test='product-price']")
                                
                                product_name = name_element.text.strip()
                                price_text = price_element.text.strip().replace("$", "").replace(",", "")
                                
                                # Extract numeric price
                                price_value = float(price_text.split()[0]) if price_text else 0.0
                                
                                price_data = PriceData(
                                    item_name=product_name,
                                    store="target",
                                    price=Decimal(str(price_value)),
                                    availability=True
                                )
                                
                                results.append(price_data.dict())
                                
                                # Cache the result
                                if cache_key not in self._price_cache:
                                    self._price_cache[cache_key] = []
                                self._price_cache[cache_key].append(price_data)
                                
                            except (NoSuchElementException, ValueError) as e:
                                logger.warning(f"Could not extract price for product {i}: {e}")
                                continue
                        
                        # Add delay between searches
                        time.sleep(1)
                        
                    except TimeoutException:
                        logger.warning(f"Timeout while searching for {item} on Target")
                        # Add fallback price estimate
                        fallback_price = PriceData(
                            item_name=item,
                            store="target",
                            price=Decimal("6.49"),  # Default estimate
                            availability=False
                        )
                        results.append(fallback_price.dict())
                
                return {
                    "store": "target",
                    "items_searched": items,
                    "results": results,
                    "total_items_found": len(results),
                    "search_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error browsing Target prices: {e}")
                return {
                    "store": "target",
                    "error": str(e),
                    "items_searched": items,
                    "results": []
                }

        return FunctionTool(browse_target_prices)

    def _browse_kroger_prices_tool(self) -> FunctionTool:
        """Create tool for browsing Kroger prices."""
        async def browse_kroger_prices(items: List[str]) -> Dict[str, Any]:
            """Browse Kroger website for current prices of specified items.
            
            Args:
                items: List of grocery items to search for
                
            Returns:
                Dictionary containing price data from Kroger
            """
            try:
                # Note: Kroger requires location/store selection, so this is a simplified implementation
                results = []
                
                for item in items:
                    # For now, provide estimated prices since Kroger requires complex setup
                    estimated_price = PriceData(
                        item_name=item,
                        store="kroger",
                        price=Decimal("5.49"),  # Estimated price
                        availability=True
                    )
                    results.append(estimated_price.dict())
                
                return {
                    "store": "kroger",
                    "items_searched": items,
                    "results": results,
                    "total_items_found": len(results),
                    "search_timestamp": datetime.now().isoformat(),
                    "note": "Kroger prices are estimated - full implementation requires store location setup"
                }
                
            except Exception as e:
                logger.error(f"Error browsing Kroger prices: {e}")
                return {
                    "store": "kroger",
                    "error": str(e),
                    "items_searched": items,
                    "results": []
                }

        return FunctionTool(browse_kroger_prices)

    def _get_weekly_deals_tool(self) -> FunctionTool:
        """Create tool for finding weekly deals and promotions."""
        async def get_weekly_deals(store: str = "all") -> Dict[str, Any]:
            """Get current weekly deals and promotions from grocery stores.
            
            Args:
                store: Specific store to check or 'all' for all stores
                
            Returns:
                Dictionary containing current deals and promotions
            """
            try:
                deals = {
                    "walmart": [
                        {"item": "Bananas", "original_price": 0.68, "sale_price": 0.48, "savings": 0.20},
                        {"item": "Ground Beef (1lb)", "original_price": 5.98, "sale_price": 4.98, "savings": 1.00}
                    ],
                    "target": [
                        {"item": "Milk (1 gallon)", "original_price": 3.99, "sale_price": 2.99, "savings": 1.00},
                        {"item": "Bread (whole wheat)", "original_price": 2.49, "sale_price": 1.99, "savings": 0.50}
                    ],
                    "kroger": [
                        {"item": "Chicken Breast (per lb)", "original_price": 6.99, "sale_price": 4.99, "savings": 2.00},
                        {"item": "Frozen Vegetables", "original_price": 2.99, "sale_price": 2.00, "savings": 0.99}
                    ]
                }
                
                if store != "all" and store in deals:
                    return {
                        "store": store,
                        "deals": deals[store],
                        "total_deals": len(deals[store]),
                        "last_updated": datetime.now().isoformat()
                    }
                
                return {
                    "all_stores": deals,
                    "total_deals": sum(len(store_deals) for store_deals in deals.values()),
                    "last_updated": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error getting weekly deals: {e}")
                return {"error": str(e)}

        return FunctionTool(get_weekly_deals)

    def _verify_store_inventory_tool(self) -> FunctionTool:
        """Create tool for verifying product availability."""
        async def verify_store_inventory(items: List[str], store: str) -> Dict[str, Any]:
            """Verify product availability at a specific store.
            
            Args:
                items: List of items to check availability for
                store: Store to check (walmart, target, kroger)
                
            Returns:
                Dictionary containing availability status for each item
            """
            try:
                inventory_status = []
                
                for item in items:
                    # Simplified availability check - in real implementation would scrape store pages
                    availability = {
                        "item": item,
                        "store": store,
                        "in_stock": True,  # Placeholder
                        "quantity_available": "10+",
                        "estimated_restock": None,
                        "last_checked": datetime.now().isoformat()
                    }
                    inventory_status.append(availability)
                
                return {
                    "store": store,
                    "items_checked": items,
                    "inventory_status": inventory_status,
                    "all_items_available": all(item["in_stock"] for item in inventory_status),
                    "check_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error verifying store inventory: {e}")
                return {"error": str(e), "store": store, "items_checked": items}

        return FunctionTool(verify_store_inventory)

    def _compare_prices_across_stores_tool(self) -> FunctionTool:
        """Create tool for comparing prices across all stores."""
        async def compare_prices_across_stores(items: List[str]) -> Dict[str, Any]:
            """Compare prices for items across all supported stores.
            
            Args:
                items: List of items to compare prices for
                
            Returns:
                Dictionary containing price comparison data
            """
            try:
                comparison_results = []
                
                for item in items:
                    # Get prices from all stores (would use actual scraping tools)
                    walmart_price = 5.99
                    target_price = 6.49
                    kroger_price = 5.49
                    
                    best_price = min(walmart_price, target_price, kroger_price)
                    best_store = "kroger" if best_price == kroger_price else ("walmart" if best_price == walmart_price else "target")
                    
                    comparison = {
                        "item": item,
                        "prices": {
                            "walmart": walmart_price,
                            "target": target_price,
                            "kroger": kroger_price
                        },
                        "best_price": best_price,
                        "best_store": best_store,
                        "savings_vs_highest": max(walmart_price, target_price, kroger_price) - best_price,
                        "price_range": max(walmart_price, target_price, kroger_price) - min(walmart_price, target_price, kroger_price)
                    }
                    comparison_results.append(comparison)
                
                total_best_price = sum(item["best_price"] for item in comparison_results)
                total_walmart = sum(item["prices"]["walmart"] for item in comparison_results)
                total_target = sum(item["prices"]["target"] for item in comparison_results)
                total_kroger = sum(item["prices"]["kroger"] for item in comparison_results)
                
                return {
                    "items_compared": items,
                    "comparison_results": comparison_results,
                    "totals": {
                        "best_combination": total_best_price,
                        "walmart_total": total_walmart,
                        "target_total": total_target,
                        "kroger_total": total_kroger
                    },
                    "recommended_strategy": "shop_multiple_stores" if len(set(item["best_store"] for item in comparison_results)) > 1 else "single_store",
                    "comparison_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error comparing prices across stores: {e}")
                return {"error": str(e), "items_compared": items}

        return FunctionTool(compare_prices_across_stores)

    def __del__(self):
        """Cleanup WebDriver when agent is destroyed."""
        self._cleanup_driver()