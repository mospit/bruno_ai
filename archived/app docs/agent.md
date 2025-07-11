# **Bruno AI Agent Architecture Document**
# **Optimized Multi-Agent System with Google A2A Protocol**

---

## **1. Overview**

Bruno AI utilizes Google's Agent Development Kit (ADK) with the Agent-to-Agent (A2A) protocol to create a streamlined, efficient multi-agent system for budget-first meal planning. The optimized architecture eliminates redundant web scraping by leveraging Instacart API as the primary data source, resulting in improved reliability and performance.

### **Architecture Benefits**
- **Modularity**: Each agent can be developed, tested, and deployed independently
- **Efficiency**: Streamlined 6-agent system with clear responsibilities
- **Reliability**: Single source of truth through Instacart API eliminates web scraping issues
- **Scalability**: Cloud-native architecture with horizontal scaling capabilities
- **Cost-Effective**: Reduced infrastructure needs and optimized API usage

---

## **2. Agent Ecosystem Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Bruno A2A Ecosystem                      │
├─────────────────────────────────────────────────────────────┤
│  Mobile App (React Native + Expo)                          │
│  ├── A2A Client SDK                                         │
│  ├── Bruno Conversational UI                                │
│  └── Real-time Streaming Interface                          │
└─────────────────────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   A2A Gateway   │
                    │  (Load Balancer │
                    │   & Router)     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Bruno   │         │Instacart│         │Recipe   │
   │ Master  │◄────────┤Integration │◄────┤Chef     │
   │ Agent   │         │Agent    │         │Agent    │
   │(Primary)│         │         │         │         │
   └─────────┘         └─────────┘         └─────────┘
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │Budget   │         │Pantry   │         │Nutrition│
   │Analyst  │         │Manager  │         │Guide    │
   │Agent    │         │Agent    │         │Agent    │
   └─────────┘         └─────────┘         └─────────┘
```

---

## **3. Agent Definitions & Implementation**

### **3.1 Bruno Master Agent (Orchestrator)**

The central coordinator that manages user interactions and delegates tasks to specialized agents.

#### **Agent Card Definition**
```python
from google.adk.agents import Agent
from a2a_sdk import AgentCard

BRUNO_MASTER_CARD = AgentCard(
    name="Bruno Master Agent",
    version="1.0.0",
    description="Bruno AI - Your friendly budget meal planning bear who coordinates specialized helpers",
    capabilities={
        "skills": [
            {
                "id": "orchestrate_meal_planning",
                "name": "Orchestrate Meal Planning",
                "description": "Bruno coordinates multiple agents to create comprehensive budget meal plans",
                "examples": [
                    "Bruno, plan meals for $75 this week",
                    "Feed my family of 4 on $100 budget",
                    "Create a week of gluten-free meals under $60"
                ],
                "tags": ["orchestration", "meal-planning", "budget", "coordination"]
            },
            {
                "id": "provide_budget_coaching",
                "name": "Provide Budget Coaching", 
                "description": "Bruno helps users understand spending patterns and optimization opportunities",
                "examples": [
                    "Why am I overspending on groceries?",
                    "Help me save $20 this week",
                    "Show me where my money goes"
                ],
                "tags": ["coaching", "budget-analysis", "savings", "education"]
            }
        ]
    },
    interfaces={
        "input": ["text", "voice", "structured_data"],
        "output": ["text", "json", "streaming"]
    },
    model_info={
        "primary": "gemini-2.5-flash",
        "fallback": "gemini-2.5-pro"
    }
)
```

#### **Implementation**
```python
from google.adk.agents import Agent
from google.adk.tools import google_search
from a2a_sdk import A2AClient
import asyncio

class BrunoMasterAgent:
    def __init__(self):
        self.agent = Agent(
            model="gemini-2.5-flash",
            name="bruno_master_agent",
            instruction="""
            You are Bruno AI, a warm and friendly bear who helps families eat well on any budget.
            
            PERSONALITY & COMMUNICATION:
            - Speak as Bruno in first person: "I found great deals" not "the system found"
            - Be encouraging and empathetic about budget constraints
            - Use natural bear expressions: "hunting for deals", "sniffed out savings"
            - Celebrate user wins: "That's fantastic! You saved $12 this week!"
            - Ask clarifying questions when needed: "How many people am I cooking for?"
            
            CORE RESPONSIBILITIES:
            1. Understand user budget constraints and family needs
            2. Coordinate with specialized agents through A2A protocol
            3. Synthesize responses into actionable, personalized meal plans
            4. Ensure ALL suggestions stay within user's budget
            5. Provide budget education and money-saving tips
            
            AGENT COORDINATION:
            - grocery_browser_agent: Real-time price discovery via web browsing
            - recipe_chef_agent: Budget-optimized recipe creation and adaptation
            - nutrition_guide_agent: Dietary requirements and health validation
            - pantry_manager_agent: Inventory tracking and waste reduction
            - budget_analyst_agent: Spending analysis and optimization
            
            WORKFLOW EXAMPLE:
            1. User: "Bruno, plan meals for $80 this week for family of 4"
            2. Extract: budget=$80, family_size=4, timeframe=week
            3. Delegate to grocery_browser_agent: "Find best deals for family staples"
            4. Delegate to recipe_chef_agent: "Create 7 family meals using deal ingredients"
            5. Delegate to nutrition_guide_agent: "Validate nutritional balance"
            6. Synthesize into complete meal plan with shopping list
            7. Present with Bruno personality: "I found amazing deals and created..."
            
            ALWAYS:
            - Never exceed the user's stated budget
            - Provide specific savings amounts: "This saves you $8.50"
            - Include store locations and deal details
            - Explain your reasoning in simple terms
            """,
            tools=[
                self.discover_agents,
                self.delegate_to_agent,
                self.track_budget,
                self.save_user_preferences
            ]
        )
        
        # A2A Client for agent communication
        self.a2a_client = A2AClient()
        self.available_agents = {}
        
    async def discover_agents(self) -> str:
        """Bruno discovers available specialized agents"""
        try:
            agents = await self.a2a_client.list_remote_agents()
            self.available_agents = {agent['name']: agent for agent in agents}
            
            agent_summary = []
            for agent in agents:
                skills = len(agent.get('skills', []))
                agent_summary.append(f"- {agent['name']}: {skills} specialized skills")
            
            return f"Bruno discovered {len(agents)} specialized helpers:\n" + "\n".join(agent_summary)
            
        except Exception as e:
            return f"Bruno had trouble finding his helpers: {str(e)}"
    
    async def delegate_to_agent(self, agent_name: str, task: str, context: dict = None) -> dict:
        """Bruno delegates specific tasks to specialized agents"""
        if agent_name not in self.available_agents:
            return {"error": f"Bruno couldn't find the {agent_name} helper"}
        
        agent_url = self.available_agents[agent_name]['url']
        
        try:
            # Create task with context
            task_data = {
                "task": task,
                "context": context or {},
                "requestor": "bruno_master_agent",
                "priority": "normal"
            }
            
            response = await self.a2a_client.create_task(agent_url, task_data)
            return {
                "success": True,
                "agent": agent_name,
                "response": response,
                "task_id": response.get('task_id')
            }
            
        except Exception as e:
            return {
                "success": False,
                "agent": agent_name, 
                "error": str(e)
            }
    
    async def track_budget(self, budget: float, expenses: list) -> dict:
        """Bruno tracks budget vs actual spending"""
        total_cost = sum(expense.get('amount', 0) for expense in expenses)
        remaining = budget - total_cost
        
        return {
            "budget": budget,
            "spent": total_cost,
            "remaining": remaining,
            "percentage_used": (total_cost / budget) * 100,
            "status": "under_budget" if remaining >= 0 else "over_budget",
            "bruno_message": self._generate_budget_message(budget, total_cost, remaining)
        }
    
    def _generate_budget_message(self, budget: float, spent: float, remaining: float) -> str:
        """Generate Bruno's personality-driven budget message"""
        if remaining >= 0:
            percentage_saved = (remaining / budget) * 100
            if percentage_saved > 15:
                return f"🎉 Fantastic! I kept you ${remaining:.2f} under budget - that's {percentage_saved:.1f}% savings!"
            elif percentage_saved > 5:
                return f"👍 Great job! You're ${remaining:.2f} under budget with smart choices!"
            else:
                return f"✅ Perfect! Right on target with ${remaining:.2f} to spare!"
        else:
            overage = abs(remaining)
            return f"😅 Oops! We're ${overage:.2f} over budget. Let me find some savings..."

# A2A Server Setup
def create_bruno_master_server():
    bruno = BrunoMasterAgent()
    
    from a2a_sdk import A2AServer, ADKAgentExecutor
    
    server = A2AServer(
        agent_executor=ADKAgentExecutor(bruno.agent),
        agent_card=BRUNO_MASTER_CARD,
        port=8080,
        host="0.0.0.0"
    )
    
    return server
```

---

### **3.2 Instacart Integration Agent (Central Data Provider)**

This agent integrates directly with Instacart API to provide comprehensive grocery data, pricing, and ordering capabilities, eliminating the need for unreliable web scraping.

#### **Agent Card Definition**
```python
INSTACART_INTEGRATION_CARD = AgentCard(
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
```

#### **Implementation with Browser Automation**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import asyncio
import json
from typing import List, Dict
import re

class GroceryBrowserAgent:
    def __init__(self):
        self.agent = Agent(
            model="gemini-2.5-flash",
            name="grocery_browser_agent", 
            instruction="""
            You are Bruno's specialized grocery price hunter. Your job is to browse grocery store 
            websites and find the best deals for families on a budget.
            
            CORE CAPABILITIES:
            1. Real-time price scraping from major grocery store websites
            2. Weekly deal and promotion discovery
            3. Stock availability verification
            4. Price comparison across multiple stores
            5. Location-based pricing (different stores, different prices)
            
            SUPPORTED STORES:
            - Walmart.com (primary for low prices)
            - Target.com (good for organic/specialty items)
            - Kroger.com (excellent weekly deals)
            - Safeway.com (regional pricing)
            - Wegmans.com (premium quality options)
            
            OUTPUT FORMAT:
            Always return structured data with:
            - item_name: Exact product name
            - store: Store name and location
            - price: Current price with unit (per lb, per item, etc.)
            - original_price: If on sale, show original price
            - savings: Amount saved if on sale
            - stock_status: available/limited/out_of_stock
            - deal_type: regular/sale/clearance/digital_coupon
            - expires: Deal expiration date if applicable
            - url: Direct product URL
            
            BROWSING STRATEGY:
            1. Use location-specific store searches when ZIP code provided
            2. Check weekly ad sections first for best deals
            3. Look for digital coupons and member-only pricing
            4. Verify stock at specific store locations
            5. Handle anti-bot measures gracefully
            """,
            tools=[
                self.browse_walmart_prices,
                self.browse_target_prices, 
                self.browse_kroger_prices,
                self.get_weekly_deals,
                self.verify_store_inventory
            ]
        )
        
        # Browser setup
        self.setup_browser()
        
    def setup_browser(self):
        """Configure browser for grocery store scraping"""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent rotation for anti-bot evasion
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    
    async def browse_walmart_prices(self, items: List[str], zip_code: str = None) -> List[Dict]:
        """Browse Walmart.com for current prices"""
        results = []
        
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # Set location if zip code provided
            if zip_code:
                driver.get("https://www.walmart.com")
                await self._set_walmart_location(driver, zip_code)
            
            for item in items:
                try:
                    # Search for item
                    search_url = f"https://www.walmart.com/search?q={item.replace(' ', '+')}"
                    driver.get(search_url)
                    
                    # Wait for results to load
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='item-stack']")))
                    
                    # Extract product information
                    products = driver.find_elements(By.CSS_SELECTOR, "[data-testid='item-stack']")
                    
                    for product in products[:3]:  # Top 3 results
                        try:
                            name_element = product.find_element(By.CSS_SELECTOR, "[data-automation-id='product-title']")
                            price_element = product.find_element(By.CSS_SELECTOR, "[itemprop='price']")
                            
                            # Extract price information
                            price_text = price_element.text
                            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            
                            if price_match:
                                price = float(price_match.group(1))
                                
                                # Check for sale indicators
                                original_price = None
                                savings = None
                                
                                try:
                                    was_price = product.find_element(By.CSS_SELECTOR, "[data-automation-id='was-price']")
                                    was_match = re.search(r'\$(\d+\.?\d*)', was_price.text)
                                    if was_match:
                                        original_price = float(was_match.group(1))
                                        savings = original_price - price
                                except:
                                    pass
                                
                                # Get product URL
                                link_element = product.find_element(By.CSS_SELECTOR, "a")
                                product_url = link_element.get_attribute("href")
                                
                                results.append({
                                    "item_name": name_element.text,
                                    "store": "Walmart",
                                    "price": price,
                                    "original_price": original_price,
                                    "savings": savings,
                                    "deal_type": "sale" if savings else "regular",
                                    "stock_status": "available",
                                    "url": product_url,
                                    "scraped_at": datetime.now().isoformat()
                                })
                                
                        except Exception as e:
                            print(f"Error parsing product: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error searching for {item}: {e}")
                    continue
                    
        finally:
            driver.quit()
            
        return results
    
    async def browse_target_prices(self, items: List[str], zip_code: str = None) -> List[Dict]:
        """Browse Target.com for current prices"""
        results = []
        
        driver = webdriver.Chrome(options=self.chrome_options)
        
        try:
            # Set store location for Target
            if zip_code:
                driver.get("https://www.target.com")
                await self._set_target_location(driver, zip_code)
            
            for item in items:
                try:
                    # Target search URL
                    search_url = f"https://www.target.com/s?searchTerm={item.replace(' ', '+')}"
                    driver.get(search_url)
                    
                    # Wait for search results
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='@web/site-top-of-funnel/ProductCardWrapper']")))
                    
                    # Extract product cards
                    products = driver.find_elements(By.CSS_SELECTOR, "[data-test='@web/site-top-of-funnel/ProductCardWrapper']")
                    
                    for product in products[:3]:
                        try:
                            # Product name
                            name_element = product.find_element(By.CSS_SELECTOR, "[data-test='product-title']")
                            
                            # Price information
                            price_element = product.find_element(By.CSS_SELECTOR, "[data-test='product-price']")
                            price_text = price_element.text
                            
                            # Extract current price
                            current_price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            if not current_price_match:
                                continue
                                
                            current_price = float(current_price_match.group(1))
                            
                            # Check for Circle deals or sales
                            deal_type = "regular"
                            savings = None
                            original_price = None
                            
                            try:
                                # Look for Circle member pricing
                                circle_element = product.find_element(By.CSS_SELECTOR, "[data-test='circle-offers']")
                                if circle_element:
                                    deal_type = "circle_deal"
                            except:
                                pass
                            
                            try:
                                # Look for regular sale price
                                reg_price_element = product.find_element(By.CSS_SELECTOR, "[data-test='product-price-reg']")
                                reg_price_match = re.search(r'\$(\d+\.?\d*)', reg_price_element.text)
                                if reg_price_match:
                                    original_price = float(reg_price_match.group(1))
                                    savings = original_price - current_price
                                    deal_type = "sale"
                            except:
                                pass
                            
                            # Product URL
                            link_element = product.find_element(By.CSS_SELECTOR, "a")
                            product_url = "https://www.target.com" + link_element.get_attribute("href")
                            
                            results.append({
                                "item_name": name_element.text,
                                "store": "Target",
                                "price": current_price,
                                "original_price": original_price,
                                "savings": savings,
                                "deal_type": deal_type,
                                "stock_status": "available",
                                "url": product_url,
                                "scraped_at": datetime.now().isoformat()
                            })
                            
                        except Exception as e:
                            print(f"Error parsing Target product: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error searching Target for {item}: {e}")
                    continue
                    
        finally:
            driver.quit()
            
        return results
    
    async def get_weekly_deals(self, store: str, zip_code: str = None) -> List[Dict]:
        """Get weekly deals and promotions from store websites"""
        if store.lower() == "kroger":
            return await self._get_kroger_weekly_deals(zip_code)
        elif store.lower() == "target":
            return await self._get_target_weekly_deals(zip_code)
        elif store.lower() == "walmart":
            return await self._get_walmart_weekly_deals(zip_code)
        else:
            return []
    
    async def _get_kroger_weekly_deals(self, zip_code: str = None) -> List[Dict]:
        """Scrape Kroger weekly ad for deals"""
        driver = webdriver.Chrome(options=self.chrome_options)
        deals = []
        
        try:
            # Go to Kroger weekly ad
            driver.get("https://www.kroger.com/weeklyad")
            
            # Set location if provided
            if zip_code:
                await self._set_kroger_location(driver, zip_code)
            
            # Wait for weekly ad to load
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='weekly-ad-item']")))
            
            # Extract deal items
            deal_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid='weekly-ad-item']")
            
            for item in deal_items:
                try:
                    # Product name
                    name_element = item.find_element(By.CSS_SELECTOR, "[data-testid='item-title']")
                    
                    # Sale price
                    sale_price_element = item.find_element(By.CSS_SELECTOR, "[data-testid='sale-price']")
                    sale_price_text = sale_price_element.text
                    
                    # Regular price  
                    try:
                        reg_price_element = item.find_element(By.CSS_SELECTOR, "[data-testid='regular-price']")
                        reg_price_text = reg_price_element.text
                    except:
                        reg_price_text = None
                    
                    # Extract prices
                    sale_match = re.search(r'\$(\d+\.?\d*)', sale_price_text)
                    if sale_match:
                        sale_price = float(sale_match.group(1))
                        
                        regular_price = None
                        savings = None
                        
                        if reg_price_text:
                            reg_match = re.search(r'\$(\d+\.?\d*)', reg_price_text)
                            if reg_match:
                                regular_price = float(reg_match.group(1))
                                savings = regular_price - sale_price
                        
                        deals.append({
                            "item_name": name_element.text,
                            "store": "Kroger",
                            "price": sale_price,
                            "original_price": regular_price,
                            "savings": savings,
                            "deal_type": "weekly_special",
                            "stock_status": "available",
                            "expires": self._get_week_end_date(),
                            "scraped_at": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    print(f"Error parsing Kroger deal: {e}")
                    continue
                    
        finally:
            driver.quit()
            
        return deals

# A2A Server for Grocery Browser Agent
def create_grocery_browser_server():
    grocery_agent = GroceryBrowserAgent()
    
    server = A2AServer(
        agent_executor=ADKAgentExecutor(grocery_agent.agent),
        agent_card=GROCERY_BROWSER_CARD,
        port=8081,
        host="0.0.0.0"
    )
    
    return server
```

---

### **3.3 Recipe Chef Agent**

Specializes in creating and adapting recipes based on budget constraints and available ingredients.

#### **Agent Card Definition**
```python
RECIPE_CHEF_CARD = AgentCard(
    name="Recipe Chef Agent",
    version="1.0.0",
    description="Bruno's creative culinary mind - crafts delicious, budget-friendly recipes",
    capabilities={
        "skills": [
            {
                "id": "create_budget_recipe",
                "name": "Create Budget Recipe",
                "description": "Creates delicious recipes within specific cost constraints",
                "examples": [
                    "Create dinner for 4 people under $10",
                    "Make a healthy lunch for $3 per person",
                    "Recipe using chicken thighs and rice under $8"
                ],
                "tags": ["recipe-creation", "budget-optimization", "cost-analysis"]
            },
            {
                "id": "adapt_expensive_recipe",
                "name": "Adapt Expensive Recipe", 
                "description": "Modifies existing recipes to reduce cost while maintaining flavor",
                "examples": [
                    "Make this salmon recipe cheaper using chicken",
                    "Budget version of beef bourguignon",
                    "Substitute expensive ingredients in pasta dish"
                ],
                "tags": ["recipe-adaptation", "ingredient-substitution", "cost-reduction"]
            },
            {
                "id": "optimize_leftovers",
                "name": "Optimize Leftovers",
                "description": "Creates new meals from leftover ingredients to minimize waste",
                "examples": [
                    "What can I make with leftover roast chicken?",
                    "Use yesterday's rice in a new dish",
                    "Transform leftover vegetables into soup"
                ],
                "tags": ["leftover-utilization", "waste-reduction", "creative-cooking"]
            }
        ]
    },
    specialized_knowledge=[
        "ingredient_cost_database",
        "nutritional_equivalents", 
        "cooking_techniques",
        "flavor_profiles",
        "portion_sizing"
    ]
)
```

#### **Implementation**
```python
from google.adk.agents import Agent
import json
from typing import Dict, List
import re

class RecipeChefAgent:
    def __init__(self):
        # Load ingredient cost database and substitution rules
        self.ingredient_costs = self._load_ingredient_costs()
        self.substitution_rules = self._load_substitution_rules()
        
        self.agent = Agent(
            model="gemini-2.5-pro",  # Using Pro for complex recipe generation
            name="recipe_chef_agent",
            instruction="""
            You are Bruno's creative Recipe Chef Agent, specializing in budget-friendly cooking.
            
            CORE MISSION:
            Create delicious, nutritious recipes that fit strict budget constraints without sacrificing 
            flavor or family appeal.
            
            EXPERTISE AREAS:
            1. Cost-effective ingredient selection and substitutions
            2. Flavor optimization using budget ingredients
            3. Portion control for family meals
            4. Nutritional balance on a budget
            5. Creative leftover utilization
            6. Seasonal ingredient advantages
            
            RECIPE CREATION PROCESS:
            1. Analyze budget constraint and family size
            2. Calculate cost per serving target
            3. Select base ingredients for best value (protein, starch, vegetables)
            4. Build flavor profile using affordable seasonings and techniques
            5. Ensure nutritional balance within budget
            6. Provide cooking tips for best results
            7. Calculate exact costs and savings
            
            SUBSTITUTION STRATEGY:
            - Expensive proteins: salmon → chicken thighs, beef → ground turkey
            - Premium vegetables: asparagus → green beans, bell peppers → carrots  
            - Dairy: heavy cream → milk + butter, fresh herbs → dried herbs
            - Pantry staples: quinoa → rice, pine nuts → sunflower seeds
            
            OUTPUT FORMAT:
            Always provide:
            - Recipe name with cost per serving
            - Ingredient list with individual costs
            - Step-by-step instructions optimized for home cooking
            - Total recipe cost and cost per serving
            - Nutritional highlights
            - Money-saving tips and substitution options
            - Leftover suggestions
            
            COST CALCULATION:
            Use current market prices and calculate exact costs:
            -
            ```python
            COST CALCULATION:
            Use current market prices and calculate exact costs:
            - Track ingredient quantities and unit costs
            - Account for waste and trim (e.g., chicken bones, vegetable peels)
            - Calculate cost per serving accurately
            - Highlight savings vs expensive alternatives
            - Factor in pantry staples users likely have (salt, oil, basic spices)
            
            DIETARY CONSIDERATIONS:
            - Accommodate common restrictions (gluten-free, dairy-free, vegetarian)
            - Ensure adequate protein, especially for growing families
            - Include vegetables for nutritional balance
            - Consider cultural preferences and family traditions
            
            COOKING SKILL LEVELS:
            - Beginner: Simple techniques, minimal equipment, clear instructions
            - Intermediate: Some technique variety, standard kitchen tools
            - Advanced: Complex flavors, specialized techniques, efficiency tips
            """,
            tools=[
                self.calculate_recipe_cost,
                self.suggest_substitutions,
                self.optimize_portions,
                self.create_shopping_list,
                self.analyze_nutrition
            ]
        )
    
    def _load_ingredient_costs(self) -> Dict:
        """Load average ingredient costs database"""
        return {
            # Proteins (per lb)
            "chicken_thighs": 1.99,
            "chicken_breast": 3.99,
            "ground_turkey": 2.99,
            "ground_beef": 4.99,
            "eggs": 2.99,  # per dozen
            "canned_tuna": 1.29,  # per can
            "dried_beans": 1.99,  # per lb
            "tofu": 2.49,  # per lb
            
            # Carbohydrates
            "white_rice": 0.89,  # per lb
            "brown_rice": 1.29,
            "pasta": 1.00,
            "potatoes": 0.79,
            "sweet_potatoes": 1.29,
            "bread": 1.99,  # per loaf
            
            # Vegetables (per lb unless noted)
            "onions": 0.89,
            "carrots": 0.99,
            "celery": 1.49,
            "frozen_mixed_vegetables": 1.99,
            "canned_tomatoes": 1.29,  # per can
            "garlic": 0.50,  # per head
            "bell_peppers": 1.99,
            "broccoli": 1.99,
            
            # Pantry staples
            "olive_oil": 0.25,  # per tablespoon
            "salt": 0.01,  # per teaspoon
            "black_pepper": 0.05,  # per teaspoon
            "garlic_powder": 0.03,
            "onion_powder": 0.03,
            "paprika": 0.05,
            "dried_oregano": 0.04,
            "flour": 0.50,  # per cup
            "butter": 0.25,  # per tablespoon
        }
    
    def _load_substitution_rules(self) -> Dict:
        """Load ingredient substitution rules for cost savings"""
        return {
            "expensive_to_cheap": {
                "salmon": "chicken_thighs",
                "beef_tenderloin": "ground_beef",
                "asparagus": "green_beans", 
                "pine_nuts": "sunflower_seeds",
                "heavy_cream": "milk_plus_butter",
                "fresh_herbs": "dried_herbs",
                "quinoa": "brown_rice",
                "organic_vegetables": "conventional_vegetables"
            },
            "ratios": {
                "heavy_cream_to_milk": {"milk": "3/4 cup", "butter": "1/4 cup"},
                "fresh_to_dried_herbs": "1:3",  # 1 tbsp fresh = 1 tsp dried
                "expensive_nuts": "1:1 substitution with cheaper nuts or seeds"
            },
            "flavor_preservation": {
                "salmon_to_chicken": "add lemon zest and dill",
                "beef_to_turkey": "add worcestershire and mushrooms",
                "asparagus_to_beans": "add garlic and almonds"
            }
        }
    
    async def calculate_recipe_cost(self, ingredients: List[Dict], servings: int) -> Dict:
        """Calculate total recipe cost and cost per serving"""
        total_cost = 0.0
        cost_breakdown = []
        
        for ingredient in ingredients:
            name = ingredient.get('name', '').lower()
            quantity = ingredient.get('quantity', 0)
            unit = ingredient.get('unit', '')
            
            # Look up ingredient cost
            unit_cost = self.ingredient_costs.get(name, 0)
            
            # Calculate ingredient cost based on quantity and unit
            ingredient_cost = self._calculate_ingredient_cost(name, quantity, unit, unit_cost)
            
            total_cost += ingredient_cost
            cost_breakdown.append({
                "ingredient": ingredient.get('display_name', name),
                "quantity": f"{quantity} {unit}",
                "cost": round(ingredient_cost, 2)
            })
        
        cost_per_serving = total_cost / servings if servings > 0 else 0
        
        return {
            "total_cost": round(total_cost, 2),
            "cost_per_serving": round(cost_per_serving, 2),
            "servings": servings,
            "breakdown": cost_breakdown,
            "budget_rating": self._get_budget_rating(cost_per_serving)
        }
    
    def _calculate_ingredient_cost(self, name: str, quantity: float, unit: str, unit_cost: float) -> float:
        """Calculate cost for specific ingredient quantity"""
        # Convert units to standard pricing units
        unit_conversions = {
            "cups": {"rice": 0.5, "flour": 0.25, "pasta": 0.25},  # cups to lbs
            "tablespoons": {"oil": 1, "butter": 1},  # already priced per tbsp
            "teaspoons": {"spices": 1},  # already priced per tsp
            "pieces": {"eggs": 1/12},  # eggs per dozen
            "cans": {"tuna": 1, "tomatoes": 1},  # already priced per can
        }
        
        # Apply conversion if needed
        if unit in unit_conversions and name in unit_conversions[unit]:
            conversion_factor = unit_conversions[unit][name]
            return quantity * conversion_factor * unit_cost
        else:
            return quantity * unit_cost
    
    def _get_budget_rating(self, cost_per_serving: float) -> str:
        """Rate recipe affordability"""
        if cost_per_serving <= 2.00:
            return "Very Budget-Friendly"
        elif cost_per_serving <= 3.50:
            return "Budget-Friendly"
        elif cost_per_serving <= 5.00:
            return "Moderate"
        else:
            return "Higher Cost"
    
    async def suggest_substitutions(self, recipe: Dict, target_cost: float) -> Dict:
        """Suggest ingredient substitutions to meet target cost"""
        current_cost = recipe.get('total_cost', 0)
        needed_savings = current_cost - target_cost
        
        if needed_savings <= 0:
            return {"message": "Recipe already within budget!", "substitutions": []}
        
        substitutions = []
        potential_savings = 0
        
        for ingredient in recipe.get('ingredients', []):
            name = ingredient.get('name', '').lower()
            
            # Check if expensive ingredient has cheaper substitute
            if name in self.substitution_rules['expensive_to_cheap']:
                cheaper_option = self.substitution_rules['expensive_to_cheap'][name]
                
                # Calculate savings
                original_cost = self.ingredient_costs.get(name, 0)
                substitute_cost = self.ingredient_costs.get(cheaper_option, 0)
                savings_per_unit = original_cost - substitute_cost
                
                if savings_per_unit > 0:
                    quantity = ingredient.get('quantity', 1)
                    total_savings = savings_per_unit * quantity
                    
                    substitutions.append({
                        "original": ingredient.get('display_name', name),
                        "substitute": cheaper_option.replace('_', ' ').title(),
                        "savings": round(total_savings, 2),
                        "cooking_notes": self.substitution_rules['flavor_preservation'].get(f"{name}_to_{cheaper_option}", "Direct substitution")
                    })
                    
                    potential_savings += total_savings
        
        # Sort by highest savings first
        substitutions.sort(key=lambda x: x['savings'], reverse=True)
        
        return {
            "needed_savings": round(needed_savings, 2),
            "potential_savings": round(potential_savings, 2), 
            "substitutions": substitutions,
            "recommendation": "Apply top substitutions until target cost is reached"
        }
    
    async def create_shopping_list(self, recipes: List[Dict]) -> Dict:
        """Create consolidated shopping list from multiple recipes"""
        shopping_list = {}
        total_cost = 0
        
        # Consolidate ingredients across recipes
        for recipe in recipes:
            for ingredient in recipe.get('ingredients', []):
                name = ingredient.get('name')
                quantity = ingredient.get('quantity', 0)
                unit = ingredient.get('unit', '')
                
                key = f"{name}_{unit}"
                
                if key in shopping_list:
                    shopping_list[key]['quantity'] += quantity
                else:
                    shopping_list[key] = {
                        'name': ingredient.get('display_name', name),
                        'quantity': quantity,
                        'unit': unit,
                        'estimated_cost': self.ingredient_costs.get(name, 0) * quantity
                    }
                
                total_cost += shopping_list[key]['estimated_cost']
        
        # Organize by store sections
        organized_list = self._organize_by_store_section(list(shopping_list.values()))
        
        return {
            "total_estimated_cost": round(total_cost, 2),
            "total_items": len(shopping_list),
            "organized_list": organized_list,
            "money_saving_tips": [
                "Buy larger quantities of non-perishables when on sale",
                "Check weekly ads before shopping",
                "Consider store brands for 20-30% savings",
                "Buy whole chickens and cut them yourself"
            ]
        }
    
    def _organize_by_store_section(self, items: List[Dict]) -> Dict:
        """Organize shopping list by grocery store sections"""
        sections = {
            "Produce": [],
            "Meat & Seafood": [],
            "Dairy & Eggs": [],
            "Pantry & Dry Goods": [],
            "Frozen": [],
            "Canned Goods": []
        }
        
        section_mapping = {
            # Produce
            "onions": "Produce", "carrots": "Produce", "celery": "Produce",
            "garlic": "Produce", "bell_peppers": "Produce", "broccoli": "Produce",
            
            # Meat & Seafood  
            "chicken_thighs": "Meat & Seafood", "chicken_breast": "Meat & Seafood",
            "ground_turkey": "Meat & Seafood", "ground_beef": "Meat & Seafood",
            "canned_tuna": "Canned Goods",
            
            # Dairy & Eggs
            "eggs": "Dairy & Eggs", "butter": "Dairy & Eggs", "milk": "Dairy & Eggs",
            
            # Pantry & Dry Goods
            "rice": "Pantry & Dry Goods", "pasta": "Pantry & Dry Goods",
            "flour": "Pantry & Dry Goods", "olive_oil": "Pantry & Dry Goods",
            "dried_beans": "Pantry & Dry Goods",
            
            # Frozen
            "frozen_mixed_vegetables": "Frozen",
            
            # Canned Goods
            "canned_tomatoes": "Canned Goods"
        }
        
        for item in items:
            name_key = item['name'].lower().replace(' ', '_')
            section = section_mapping.get(name_key, "Pantry & Dry Goods")
            sections[section].append(item)
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}

# A2A Server for Recipe Chef Agent
def create_recipe_chef_server():
    recipe_agent = RecipeChefAgent()
    
    server = A2AServer(
        agent_executor=ADKAgentExecutor(recipe_agent.agent),
        agent_card=RECIPE_CHEF_CARD,
        port=8082,
        host="0.0.0.0"
    )
    
    return server
```

---

### **3.4 A2A Gateway & Service Discovery**

The central routing system that manages agent discovery and communication.

#### **Gateway Implementation**
```python
from fastapi import FastAPI, HTTPException
from typing import Dict, List
import httpx
import asyncio
import json
from datetime import datetime

class BrunoA2AGateway:
    def __init__(self):
        self.app = FastAPI(title="Bruno A2A Gateway", version="1.0.0")
        self.registered_agents = {}
        self.health_check_interval = 30  # seconds
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.post("/register_agent")
        async def register_agent(agent_info: dict):
            """Register a new agent with the gateway"""
            agent_name = agent_info.get('name')
            agent_url = agent_info.get('url')
            
            if not agent_name or not agent_url:
                raise HTTPException(status_code=400, detail="Missing agent name or URL")
            
            # Verify agent is accessible
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{agent_url}/health")
                    if response.status_code != 200:
                        raise HTTPException(status_code=400, detail="Agent health check failed")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Cannot reach agent: {str(e)}")
            
            # Store agent information
            self.registered_agents[agent_name] = {
                **agent_info,
                "registered_at": datetime.now().isoformat(),
                "last_health_check": datetime.now().isoformat(),
                "status": "healthy"
            }
            
            return {"message": f"Agent {agent_name} registered successfully"}
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            return {"agents": list(self.registered_agents.values())}
        
        @self.app.post("/agents/{agent_name}/task")
        async def create_task(agent_name: str, task_data: dict):
            """Create a task for a specific agent"""
            if agent_name not in self.registered_agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent_url = self.registered_agents[agent_name]['url']
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(f"{agent_url}/task", json=task_data)
                    return response.json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")
        
        @self.app.get("/agents/{agent_name}/health")
        async def check_agent_health(agent_name: str):
            """Check health of a specific agent"""
            if agent_name not in self.registered_agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent_url = self.registered_agents[agent_name]['url']
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{agent_url}/health")
                    
                    if response.status_code == 200:
                        self.registered_agents[agent_name]['status'] = 'healthy'
                        self.registered_agents[agent_name]['last_health_check'] = datetime.now().isoformat()
                        return {"status": "healthy", "agent": agent_name}
                    else:
                        self.registered_agents[agent_name]['status'] = 'unhealthy'
                        return {"status": "unhealthy", "agent": agent_name}
                        
            except Exception as e:
                self.registered_agents[agent_name]['status'] = 'unreachable'
                return {"status": "unreachable", "agent": agent_name, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Background task to monitor agent health"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            
            for agent_name in list(self.registered_agents.keys()):
                try:
                    await self.check_agent_health(agent_name)
                except:
                    # If health check fails, mark agent as unhealthy
                    self.registered_agents[agent_name]['status'] = 'unhealthy'

# Docker configuration for gateway
gateway_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "3000"]
"""

# Gateway requirements.txt
gateway_requirements = """
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
pydantic==2.4.2
"""
```

---

### **3.5 Agent Deployment & Orchestration**

#### **Docker Compose Configuration**
```yaml
# docker-compose.yml for Bruno A2A Ecosystem
version: '3.8'

services:
  # A2A Gateway - Central routing and discovery
  bruno-gateway:
    build: ./gateway
    ports:
      - "3000:3000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    volumes:
      - ./config/gateway.json:/app/config.json
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  # Bruno Master Agent - Main orchestrator
  bruno-master:
    build: ./agents/master
    ports:
      - "8080:8080"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=bruno_master_agent
      - AGENT_PORT=8080
    depends_on:
      - bruno-gateway
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    
  # Grocery Browser Agent - Price discovery via web scraping
  grocery-browser:
    build: ./agents/grocery_browser
    ports:
      - "8081:8081"
    environment:
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=grocery_browser_agent
      - AGENT_PORT=8081
      - CHROME_BIN=/usr/bin/chromium-browser
    volumes:
      - ./browser_cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    # Add Chrome for web scraping
    cap_add:
      - SYS_ADMIN
    
  # Recipe Chef Agent - Recipe creation and optimization
  recipe-chef:
    build: ./agents/recipe_chef
    ports:
      - "8082:8082"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=recipe_chef_agent
      - AGENT_PORT=8082
    volumes:
      - ./recipe_data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Budget Analyst Agent - Financial analysis and optimization
  budget-analyst:
    build: ./agents/budget_analyst
    ports:
      - "8083:8083"
    environment:
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=budget_analyst_agent
      - AGENT_PORT=8083
    volumes:
      - ./budget_data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Nutrition Guide Agent - Dietary analysis and recommendations
  nutrition-guide:
    build: ./agents/nutrition
    ports:
      - "8084:8084"
    environment:
      - NUTRITION_API_KEY=${NUTRITION_API_KEY}
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=nutrition_guide_agent
      - AGENT_PORT=8084
    volumes:
      - ./nutrition_data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Pantry Manager Agent - Inventory tracking and waste reduction
  pantry-manager:
    build: ./agents/pantry
    ports:
      - "8085:8085"
    environment:
      - REDIS_URL=redis://redis:6379
      - A2A_GATEWAY_URL=http://bruno-gateway:3000
      - AGENT_NAME=pantry_manager_agent
      - AGENT_PORT=8085
    depends_on:
      - redis
    restart: unless-stopped
    
  # Redis for caching and session storage
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  # PostgreSQL for persistent data storage
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=bruno_db
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:

networks:
  default:
    name: bruno_network
```

#### **Agent Auto-Registration Script**
```python
# agent_startup.py - Auto-registration with A2A Gateway
import asyncio
import httpx
import os
import time
from typing import Dict

class AgentRegistration:
    def __init__(self, agent_name: str, agent_port: int, capabilities: Dict):
        self.agent_name = agent_name
        self.agent_port = agent_port
        self.capabilities = capabilities
        self.gateway_url = os.getenv('A2A_GATEWAY_URL', 'http://localhost:3000')
        
    async def register_with_gateway(self) -> bool:
        """Register this agent with the A2A Gateway"""
        registration_data = {
            "name": self.agent_name,
            "url": f"http://{self.get_agent_hostname()}:{self.agent_port}",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "health_endpoint": "/health",
            "task_endpoint": "/task"
        }
        
        max_retries = 5
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.gateway_url}/register_agent",
                        json=registration_data,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Agent {self.agent_name} registered successfully with gateway")
                        return True
                    else:
                        print(f"❌ Registration failed: {response.status_code} - {response.text}")
                        
            except Exception as e:
                print(f"⚠️ Registration attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        print(f"❌ Failed to register agent {self.agent_name} after {max_retries} attempts")
        return False
    
    def get_agent_hostname(self) -> str:
        """Get the hostname/IP for this agent"""
        # In Docker, use the service name
        hostname = os.getenv('HOSTNAME', 'localhost')
        if 'docker' in hostname or os.getenv('DOCKER_CONTAINER'):
            return self.agent_name.replace('_', '-')  # Convert to service name
        return 'localhost'
    
    async def start_heartbeat(self):
        """Send periodic heartbeats to the gateway"""
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(f"{self.gateway_url}/agents/{self.agent_name}/health")
            except Exception as e:
                print(f"⚠️ Heartbeat failed: {str(e)}")
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds

# Example usage in agent startup
async def start_bruno_master_agent():
    """Startup script for Bruno Master Agent"""
    
    # Define agent capabilities
    capabilities = {
        "skills": [
            {
                "id": "orchestrate_meal_planning",
                "name": "Orchestrate Meal Planning",
                "description": "Bruno coordinates multiple agents to create budget meal plans",
                "tags": ["orchestration", "meal-planning", "budget"]
            }
        ],
        "model": "gemini-2.5-flash",
        "specializations": ["coordination", "budget_analysis", "user_interaction"]
    }
    
    # Initialize registration
    registration = AgentRegistration(
        agent_name="bruno_master_agent",
        agent_port=8080,
        capabilities=capabilities
    )
    
    # Register with gateway
    if await registration.register_with_gateway():
        print("🚀 Bruno Master Agent starting up...")
        
        # Start the agent server and heartbeat in parallel
        await asyncio.gather(
            start_agent_server(),  # Your agent's main server
            registration.start_heartbeat()  # Heartbeat to gateway
        )
    else:
        print("💥 Failed to register with gateway. Exiting.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(start_bruno_master_agent())
```

---

### **3.6 Testing & Validation Framework**

#### **Agent Integration Tests**
```python
# test_bruno_agents.py
import pytest
import asyncio
from unittest.mock import Mock, patch
import httpx

class TestBrunoAgentEcosystem:
    
    @pytest.fixture
    async def bruno_ecosystem(self):
        """Setup test environment with all agents"""
        # Start test versions of all agents
        test_gateway = await self.start_test_gateway()
        test_agents = await self.start_test_agents()
        
        yield {
            "gateway": test_gateway,
            "agents": test_agents
        }
        
        # Cleanup
        await self.cleanup_test_environment()
    
    @pytest.mark.asyncio
    async def test_bruno_meal_planning_workflow(self, bruno_ecosystem):
        """Test complete meal planning workflow through A2A"""
        
        # Simulate user request to Bruno Master Agent
        user_request = {
            "message": "Bruno, plan meals for $75 this week for family of 4",
            "context": {
                "budget": 75,
                "family_size": 4,
                "location": {"zip": "60601", "city": "Chicago"}
            }
        }
        
        # Send request to Bruno Master Agent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8080/task",
                json=user_request
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify Bruno coordinated with other agents
        assert "meal_plan" in result
        assert "shopping_list" in result
        assert "total_cost" in result
        assert result["total_cost"] <= 75  # Within budget
        
        # Verify agent delegation occurred
        assert "agents_used" in result
        expected_agents = ["grocery_browser_agent", "recipe_chef_agent"]
        assert all(agent in result["agents_used"] for agent in expected_agents)
    
    @pytest.mark.asyncio
    async def test_grocery_browser_price_discovery(self):
        """Test grocery browser agent's web scraping capabilities"""
        
        # Mock web scraping for testing
        with patch('selenium.webdriver.Chrome') as mock_driver:
            mock_driver.return_value.find_elements.return_value = [
                Mock(text="Chicken Thighs - $1.99/lb"),
                Mock(text="Ground Turkey - $2.99/lb")
            ]
            
            grocery_agent = GroceryBrowserAgent()
            results = await grocery_agent.browse_walmart_prices(
                items=["chicken thighs", "ground turkey"],
                zip_code="60601"
            )
            
            assert len(results) >= 2
            assert all("price" in item for item in results)
            assert all("store" in item for item in results)
    
    @pytest.mark.asyncio 
    async def test_recipe_chef_budget_optimization(self):
        """Test recipe creation within budget constraints"""
        
        recipe_agent = RecipeChefAgent()
        
        recipe_request = {
            "target_cost": 10.00,
            "servings": 4,
            "dietary_restrictions": [],
            "available_ingredients": ["chicken_thighs", "rice", "carrots"]
        }
        
        recipe = await recipe_agent.create_budget_recipe(**recipe_request)
        
        assert recipe["total_cost"] <= 10.00
        assert recipe["servings"] == 4
        assert "ingredients" in recipe
        assert "instructions" in recipe
        assert recipe["cost_per_serving"] <= 2.50
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, bruno_ecosystem):
        """Test system resilience when agents fail"""
        
        # Simulate grocery agent failure
        await self.stop_agent("grocery_browser_agent")
        
        # Bruno should still provide meal plan with cached/estimated prices
        user_request = {
            "message": "Bruno, plan meals for $50 this week",
            "context": {"budget": 50, "family_size": 2}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8080/task",
                json=user_request
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify Bruno provided fallback response
        assert "meal_plan" in result
        assert "warning" in result  # Should warn about limited price data
        assert "using_estimated_prices" in result["warning"]
    
    async def test_a2a_protocol_compliance(self):
        """Test that all agents comply with A2A protocol standards"""
        
        required_endpoints = ["/health", "/task",