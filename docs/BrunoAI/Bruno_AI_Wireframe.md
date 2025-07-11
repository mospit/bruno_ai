### Wireframes for Bruno AI App Screens

Below, I've created text-based wireframes for the five key screens identified in the design process: Home/Dashboard, Chat Interface, Pantry Management, Shopping, and Meal Prep. These are represented using ASCII art for layout visualization, followed by detailed descriptions of elements, interactions, and rationale. The designs prioritize intuition, collaboration, and user empowerment, with a mobile portrait view (e.g., 375x812px iPhone standard). Elements use placeholders like [Icon] for visuals, and colors are noted (e.g., Warm Brown #8B4513). Wireframes are minimalist to focus on structure.

#### 1. Home/Dashboard Screen
**ASCII Wireframe** (Scrollable Vertical Layout):
```
+---------------------------+
| [Bruno Avatar] Hey, ready?|
+---------------------------+
| Search: [Bar] [Voice Icon]|
+---------------------------+
| Pantry Highlights         |
| [Carousel: Item1 | Item2] |
| Rice (Exp: 2d) [Yellow]   |
| + Add Item [FAB]          |
+---------------------------+
| Shopping Suggestions      |
| Budget: [Progress Bar 75%]|
| Deals: Plantains $1.99    |
| [Add Button Green]        |
+---------------------------+
| Meal Prep Ideas           |
| [Grid: Idea1 | Idea2]     |
| Caribbean Rice: 20min     |
| [Customize Button Brown]  |
+---------------------------+
| [Bottom Tab Bar: Home etc]|
+---------------------------+
```

**Description**:
- **Header**: Bruno's avatar (smiling bear) with personalized greeting bubble in Warm Brown.
- **Search Bar**: Full-width with auto-suggest dropdown; voice icon in Instacart Green.
- **Cards**: Expandable (tap to full view); Soft Beige background with shadows. Carousel for highlights uses swipe gestures.
- **Interactions**: Tap cards to navigate; FAB floats for quick adds; scroll for more cards.
- **Rationale**: Provides at-a-glance collaboration starters, reducing steps to key tasks.

#### 2. Chat Interface Screen
**ASCII Wireframe** (Scrollable Chat History):
```
+---------------------------+
| [Bruno Avatar] Chatting...|
+---------------------------+
| Bruno: Got your query...  |
| [Brown Bubble Left]       |
| [Inline Button: Refine]   |
+---------------------------+
| You: Caribbean for 4 $200 |
| [Beige Bubble Right]      |
+---------------------------+
| Bruno: Here's a plan...   |
| [Brown Bubble Left]       |
| List: [Item1 $10]         |
| [Thumbs Up/Down Feedback] |
+---------------------------+
| [Input Bar: Text Field]   |
| [Voice | Photo | Send]    |
| [Green Send Button]       |
+---------------------------+
| [Bottom Tab Bar]          |
+---------------------------+
```

**Description**:
- **Header**: Bruno's avatar with status (e.g., "Thinking..." animation).
- **Bubbles**: Left for Bruno (Warm Brown, rounded); right for user (Soft Beige). Inline elements like lists/buttons in Instacart Green.
- **Input Bar**: Bottom-fixed; voice (mic icon), photo (camera), send (arrow).
- **Interactions**: Tap bubbles for copy/edit; real-time indicators (dots for typing); swipe up for history.
- **Rationale**: Feels like a natural conversation, with quick actions for collaborative refinements.

#### 3. Pantry Management Screen
**ASCII Wireframe** (Grid/List Toggle):
```
+---------------------------+
| Pantry [Grid/List Toggle] |
| Search: [Bar] [Filter]    |
+---------------------------+
| [Grid View Example]       |
| [Item1 Photo] Rice        |
| Qty:2 Exp:2d [Yellow Tag] |
| [Item2] [Item3] [Item4]   |
+---------------------------+
| Summary: 45 Items ~$120   |
| [Brown Text]              |
+---------------------------+
| Bruno: Suggest uses?      |
| [Sidebar Bubble]          |
+---------------------------+
| [FAB: Scan/Add] [Green]   |
| [Bottom Tab Bar]          |
+---------------------------+
```

**Description**:
- **Top Bar**: Toggle switch (icons for grid/list); search with category filters (dropdown in Deep Forest Green).
- **Grid/List**: Cards/rows with photos, details, and color tags (green fresh, yellow expiring).
- **Summary**: Fixed footer-like bar in Light Gray.
- **Bruno Sidebar**: Collapsible panel on right for suggestions.
- **Interactions**: Drag to reorder; tap for edit modal; camera overlay for scan.
- **Rationale**: Visual and searchable for easy management, with Bruno hint for optional collaboration.

#### 4. Shopping Screen
**ASCII Wireframe** (Vertical List with Sections):
```
+---------------------------+
| Shopping [Sort/Filter]    |
| Budget: [$175/$200 Bar]   |
| [Green Progress Circle]   |
+---------------------------+
| Essentials                |
| - Rice $5 [Checkbox]      |
|   Subtotal: $20           |
+---------------------------+
| Caribbean Specials        |
| - Plantains $10 [Chk]     |
|   [Swap Button Brown]     |
+---------------------------+
| Total: $175 Savings:$25   |
| [Yellow Highlight]        |
+---------------------------+
| [Order Now Green Button]  |
| [Bottom Tab Bar]          |
+---------------------------+
```

**Description**:
- **Top Bar**: Budget tracker (progress bar in #43B02A); sort dropdown (e.g., "Cheapest").
- **Sections**: Collapsible accordions with checkboxes and prices (real-time).
- **Item Rows**: Swipe for delete/substitute; badges for deals (#FFD700).
- **Footer**: Totals with Instacart preview map.
- **Interactions**: Drag from pantry to add; voice: "Add item."
- **Rationale**: Budget-focused for practical shopping, with easy adaptations.

#### 5. Meal Prep Screen
**ASCII Wireframe** (Carousel + Detail View):
```
+---------------------------+
| Meal Prep [Search]        |
+---------------------------+
| [Carousel: Idea1 | Idea2] |
| Caribbean Rice for 4      |
| Time:20min [Brown Card]   |
+---------------------------+
| Steps:                    |
| 1. Boil rice [Timer Btn]  |
| 2. Add spices             |
| [Accordion Expand]        |
+---------------------------+
| Ingredients: [List]       |
| From Pantry: Rice [Green] |
| Need: Plantains [Add Btn] |
+---------------------------+
| Bruno: Tweak? [Bubble]    |
| [Bottom Tab Bar]          |
+---------------------------+
```

**Description**:
- **Top Bar**: Search for ideas; filter chips (e.g., "Under 30min").
- **Carousel**: Horizontal swipe cards with images/titles.
- **Detail Section**: Numbered steps with timers (tap to start); ingredients linked to shopping/pantry.
- **Bruno Note**: Bottom bubble for customization.
- **Interactions**: Drag steps to reorder; voice readout.
- **Rationale**: Step-by-step guidance with ties to other features for seamless collaboration.

These wireframes are ready for prototyping (e.g., in Figma). They enhance usability with 2025 trends like gesture-heavy interfaces. If adjustments or more screens are needed, let me know!