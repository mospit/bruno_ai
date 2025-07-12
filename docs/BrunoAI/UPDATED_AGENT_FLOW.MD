# Comprehensive Example of Agent Flow in Bruno AI V3.1

This guide demonstrates a detailed agent flow in the Bruno AI V3.1 system, using the user's query: "I want Caribbean meals for 4 on a $200 budget." It showcases how the 5 agents collaborate via FastA2A (A2A protocol for peer messaging), PydanticAI (agent orchestration with Claude models), Redis/Postgres (memory/state), and Instacart API (tools). The flow emphasizes user-driven adaptation—agents confirm wants, iterate on feedback, and deliver practical outputs without prescription. 

The example is step-by-step, including code snippets for implementation in Python. Assumptions: Server running on Uvicorn; user query via mobile app API. Flow duration: ~5-10s; tokens: <5K avg with optimizations.

## 1. Flow Overview
- **Trigger**: User sends query to Gateway endpoint (FastA2A-exposed PydanticAI chain).
- **Orchestration**: No master—Gateway chains agents sequentially/parallel via PydanticAI (e.g., Pantry check parallel to Budget).
- **Collaboration**: Agents exchange via A2A JSON-RPC (e.g., Recipe Chef sends context_id to Instacart for pricing).
- **Memory/Token**: Redis caches results (e.g., inventory); Haiku compresses contexts before Sonnet calls.
- **User Focus**: Reflection Agent queries "Any tweaks to match your wants?" for iteration.

## 2. Step-by-Step Agent Flow
### Step 1: Query Intake at Gateway (PydanticAI Chain + FastA2A)
- **Action**: App POSTs to /query endpoint; Gateway (chained agents) parses intent, generates context_id, and spawns parallel: Pantry Manager + Budget Analyst.
- **Claude Role**: Haiku for quick parse (low tokens).
- **Code Snippet** (Gateway in app.py):
  ```python
  from pydantic_ai import chain
  from fasta2a import to_a2a
  import uuid

  # Agents from setup
  gateway_chain = chain(pantry_manager | budget_analyst >> instacart_integration >> recipe_chef >> reflection_feedback)  # | parallel, >> sequential

  app = to_a2a(gateway_chain)

  @app.post("/query")
  async def handle_query(request):
      context_id = str(uuid.uuid4())  # Generate for memory
      result = await gateway_chain(request.body['query'], context_id=context_id)
      return {"response": result, "context_id": context_id}  # For app to continue
  ```
- **Output**: Initial ack: "Processing your Caribbean request for 4 under $200—checking pantry and budget."

### Step 2: Parallel Initial Checks (Pantry Manager + Budget Analyst)
- **Pantry Manager (Haiku)**: Queries Redis/Postgres for inventory; uses tool to scan for Caribbean items (e.g., rice). Compresses results if >1K tokens.
- **Budget Analyst (Sonnet 4)**: Validates $200 feasibility; tools for forecasts.
- **A2A Exchange**: Pantry sends inventory to Budget via JSON-RPC ({"context_id": "abc", "inventory": [...]}).
- **Code Snippet** (Pantry Agent Example):
  ```python
  pantry_agent = token_optimized_agent('anthropic:claude-3.5-haiku', 'Check inventory for user wants; suggest uses if asked')

  # In flow: Fetch from DB tool
  result = pantry_agent(query, context_id)  # Compressed wrapper applied
  # A2A send to Budget: await a2a_client.send_message(result, to='budget', context_id=context_id)
  ```

### Step 3: Instacart Integration (Haiku)
- **Action**: Receives A2A from Budget (e.g., adjusted items); calls Instacart tool for pricing/availability under $200.
- **Tool Call**: MCP-like: Inputs items/budget; outputs list with totals.
- **Code Snippet** (Instacart Tool in Agent):
  ```python
  instacart_agent.tools = [InstacartTool()]  # From previous guide
  priced_list = instacart_agent("Price for Caribbean items", context_id)
  # A2A to Recipe: Send priced_list
  ```

### Step 4: Recipe Chef (Sonnet 4)
- **Action**: Generates/adapts Caribbean ideas for 4; incorporates A2A inventory/pricing.
- **User Adaptation**: If unclear, queues Reflection for query.
- **Code Snippet**:
  ```python
  recipe_result = recipe_chef(priced_list, context_id)  # Sonnet for reasoning
  ```

### Step 5: Reflection & Feedback (Sonnet 4) – Iteration Loop
- **Action**: Aggregates outputs; prompts user via app (e.g., "Plan totals $180—match your wants? Tweak for spice?").
- **Loop**: If feedback, re-chain via PydanticAI loop until satisfied.
- **Code Snippet**:
  ```python
  feedback = reflection_feedback(recipe_result, context_id)
  if 'refine' in feedback:
      # Re-run chain with updates
  ```

### Step 6: Final Delivery and Persistence
- **Action**: Gateway returns aggregated response (list, prep ideas) to app; persists in Redis/Postgres for future sessions.
- **A2A Close**: Update task status to "completed" with context_id.

## 3. Full End-to-End Benefits
- **User Experience**: Adaptive loop ensures "wants" fulfillment (e.g., refined for "more seafood").
- **Efficiency**: Tokens <5K; Latency <5s; Scalable via FastA2A Broker.

This flow maximizes the system for practical, collaborative assistance.
