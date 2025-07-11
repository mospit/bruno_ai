
# Comprehensive UI Redesign Plan for Bruno AI

## 1. Overview
The current UI needs to be completely redesigned to align with the new **Bruno AI Style Guide** and **UI Design** documentation. The redesign will transform the current chat-heavy interface into a modern, bear-themed collaborative experience with intuitive navigation and personalized widgets.

## 2. Key Changes Required

### A. Navigation & Layout Structure
**Current:** Single home screen with chat interface
**New:** Bottom tab bar navigation with 5 core sections

**Files to modify:**
- `lib/main.dart` - Update routing system
- `lib/screens/home_screen.dart` - Convert to dashboard layout
- Create new screen files:
  - `lib/screens/chat_screen.dart` (dedicated chat)
  - `lib/screens/pantry_screen.dart` (enhance existing)
  - `lib/screens/shopping_screen.dart` (new)
  - `lib/screens/prep_screen.dart` (new meal prep)

### B. Color Scheme Update
**Current:** Modern indigo/purple palette
**New:** Warm earth tones with bear-themed colors

**Files to modify:**
- `lib/theme/app_colors.dart` - Replace with new color palette:
  - Primary: Warm Brown (#8B4513)
  - Secondary: Instacart Green (#43B02A)
  - Accent: Soft Beige (#D2B48C)
  - Supporting: Deep Forest Green (#228B22)

### C. Typography Updates
**Current:** Inter font family
**New:** Maintain Inter but adjust hierarchy per style guide

**Files to modify:**
- `lib/theme/modern_theme.dart` - Update typography scales

### D. Component Redesign
**Current:** Modern glass containers
**New:** Bear-themed rounded components with warm personality

## 3. Detailed Implementation Plan

### Phase 1: Core Navigation Structure
- [x] **Bottom Tab Bar Implementation**
  - [x] Home (dashboard icon)
  - [x] Chat (speech bubble with Bruno)
  - [x] Pantry (refrigerator/paw print)
  - [x] Shopping (shopping cart)
  - [x] Prep (plate/utensils)
- [x] **Floating Action Button**
- [x] **Top Header Redesign**

### Phase 2: Home/Dashboard Screen
- [x] **Dashboard Cards**
  - [x] Pantry highlights card
  - [x] Quick shopping suggestions card
  - [x] Meal prep ideas card
  - [x] Budget tracker widget
- [x] **Personalization Features**
  - [x] Bruno's collaborative suggestions
  - [x] AI-driven personalized content
  - [x] Interactive suggestion chips

### Phase 3: Chat Interface Redesign
- [x] **Move from Home to Dedicated Screen**
  - [x] Enhanced ChatScreen with improved header design
  - [x] Animated Bruno Avatar with mood-based states
  - [x] Dynamic status indicators and activity feedback
  - [x] Chat options menu with clear history functionality
- [x] **Bruno Avatar Integration**
  - [x] Interactive Bruno avatar with tappable status info
  - [x] Mood-based avatar animations (thinking, friendly, helpful, excited)
  - [x] Real-time typing indicators
  - [x] Enhanced breathing animations and visual feedback

### Phase 4: New Screens
- [x] **Shopping Screen**
  - [x] Enhanced UI with filtering and sorting capabilities
  - [x] Sort by name, price, or category with ascending/descending options
  - [x] Clear confirmation dialog with improved UX
  - [x] Improved header design with better visual hierarchy
- [x] **Prep Screen**
  - [x] Advanced meal filtering with category chips and switches
  - [x] Weekly meal planner with day-by-day planning interface
  - [x] Enhanced recipe details modal with improved layout
  - [x] Integration with shopping list generation
  - [x] Bruno avatar integration in filter interface
- [ ] **Enhanced Pantry Screen** (existing screen needs enhancement)

### Phase 5: Theme & Component Updates
- [x] **Color System Migration**
  - [x] Bruno AI color palette fully implemented
  - [x] Bear-themed warm earth tones integrated
  - [x] Light and dark theme support
  - [x] Consistent color usage across all components
- [x] **Component Library**
  - [x] BrunoComponents library with standardized UI elements
  - [x] Enhanced dashboard cards with consistent styling
  - [x] Primary and secondary button components
  - [x] Enhanced headers with Bruno avatar integration
  - [x] Standard modal bottom sheets
  - [x] Enhanced list tiles and filter chips
  - [x] Progress indicators and empty states
  - [x] Unified card component with haptic feedback
- [x] **Theme System Standardization**
  - [x] Modern theme with Google Fonts integration
  - [x] Consistent typography hierarchy
  - [x] Material 3 design system implementation
  - [x] Comprehensive component theming

## 4. New Files to Create
```
lib/
├── screens/
│   ├── chat_screen.dart              # Dedicated chat interface
│   ├── shopping_screen.dart          # Shopping list management
│   ├── prep_screen.dart              # Meal preparation
│   └── main_navigation.dart          # Bottom tab navigator
├── widgets/
│   ├── bottom_navigation_bar.dart    # Custom bottom nav
│   ├── dashboard_card.dart           # Reusable dashboard cards
│   ├── bruno_greeting.dart           # Top header with Bruno
│   ├── smart_suggestions.dart        # AI-driven suggestions
│   ├── budget_tracker.dart           # Budget widget
│   └── recipe_gallery.dart           # Recipe display
├── theme/
│   ├── bruno_theme.dart              # New bear-themed colors
│   └── component_themes.dart         # Updated component styles
└── utils/
    ├── bruno_animations.dart         # Bruno-specific animations
    └── gesture_handlers.dart         # Swipe and gesture support
```

