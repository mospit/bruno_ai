import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../models/shopping_item.dart';
import '../models/pantry_item.dart';
import '../repositories/chat_repository.dart';
import '../repositories/pantry_repository.dart';
import '../repositories/meal_plan_repository.dart';
import '../repositories/auth_repository.dart';
import '../services/instacart_service.dart';

class BrunoProvider extends ChangeNotifier {
  // Chat state
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;
  String _currentBudget = '';
  int _familySize = 1;
  
  // Repositories
  final ChatRepository _chatRepository = ChatRepository();
  final PantryRepository _pantryRepository = PantryRepository();
  final MealPlanRepository _mealPlanRepository = MealPlanRepository();
  final AuthRepository _authRepository = AuthRepository();
  bool _isInitialized = false;
  
  // State flags
  bool _isLoading = false;
  String? _lastError;
  
// Shopping state
  List<ShoppingItem> _shoppingList = [
    ShoppingItem(name: 'Organic Apples', price: 3.99, quantity: 1, category: 'Fruits', unit: 'bag', notes: ''),
    ShoppingItem(name: 'Whole Milk', price: 2.49, quantity: 1, category: 'Dairy', unit: 'gallon', notes: ''),
    ShoppingItem(name: 'Bread', price: 1.99, quantity: 1, category: 'Bakery', unit: 'loaf', notes: ''),
  ];
  double _totalCost = 0.0;
  String _selectedStore = '';
  bool _isShoppingListReady = false;
  
// Generated shopping list
  Future<void> generateShoppingList({
    required List<String> keywords,
    required String store,
    bool mockMode = false,
  }) async {
    final instacartService = InstacartService();
    await instacartService.initialize(mockMode: mockMode);

    List<ShoppingItem> fetchedItems = [];

    for (final keyword in keywords) {
      final response = await instacartService.searchProducts(query: keyword, store: store);
      if (response.isSuccess && response.data != null) {
        fetchedItems.addAll(response.data!);
      }
    }

    if (fetchedItems.isEmpty) {
      _lastError = 'Failed to generate shopping list. Try again later.';
    } else {
      _shoppingList = fetchedItems;
      _totalCost = _calculateTotalCost();
      _isShoppingListReady = true;
      _lastError = null;
    }

    notifyListeners();
  }

  double _calculateTotalCost() {
    return _shoppingList.fold(0.0, (total, item) => total + item.totalPrice);
  }
  List<String> _dietaryRestrictions = [];
  String _preferredDeliveryTime = '';
  
  // Favorites and Order History
  final List<FavoriteMeal> _favoriteMeals = [
    FavoriteMeal(
      id: '1',
      name: 'Grilled Chicken & Vegetables',
      description: 'Healthy grilled chicken breast with seasonal vegetables',
      ingredients: ['Chicken breast', 'Broccoli', 'Carrots', 'Olive oil'],
      estimatedCost: 18.50,
      servings: 4,
      cookingTime: 25,
      category: 'Healthy',
      dateAdded: DateTime.now().subtract(const Duration(days: 5)),
    ),
    FavoriteMeal(
      id: '2',
      name: 'Pasta Primavera',
      description: 'Fresh pasta with seasonal vegetables in light sauce',
      ingredients: ['Pasta', 'Bell peppers', 'Zucchini', 'Cherry tomatoes', 'Parmesan'],
      estimatedCost: 14.25,
      servings: 3,
      cookingTime: 20,
      category: 'Vegetarian',
      dateAdded: DateTime.now().subtract(const Duration(days: 12)),
    ),
  ];
  
  final List<PastOrder> _pastOrders = [
    PastOrder(
      id: 'order_001',
      date: DateTime.now().subtract(const Duration(days: 3)),
      store: 'Whole Foods',
      items: [
        ShoppingItem(name: 'Organic Chicken', price: 15.99, quantity: 2, category: 'Meat', unit: 'lbs', notes: ''),
        ShoppingItem(name: 'Fresh Spinach', price: 3.49, quantity: 1, category: 'Vegetables', unit: 'bag', notes: ''),
      ],
      totalAmount: 22.47,
      status: 'Delivered',
    ),
    PastOrder(
      id: 'order_002',
      date: DateTime.now().subtract(const Duration(days: 8)),
      store: 'Safeway',
      items: [
        ShoppingItem(name: 'Salmon Fillet', price: 18.99, quantity: 1, category: 'Seafood', unit: 'lb', notes: ''),
        ShoppingItem(name: 'Asparagus', price: 4.99, quantity: 1, category: 'Vegetables', unit: 'bunch', notes: ''),
      ],
      totalAmount: 26.97,
      status: 'Delivered',
    ),
  ];
  
  // Getters
  List<ChatMessage> get messages => _messages;
  bool get isTyping => _isTyping;
  String get currentBudget => _currentBudget;
  int get familySize => _familySize;
  List<ShoppingItem> get shoppingList => _shoppingList;
  double get totalCost => _totalCost;
  String get selectedStore => _selectedStore;
  bool get isShoppingListReady => _isShoppingListReady;
  List<String> get dietaryRestrictions => _dietaryRestrictions;
  String get preferredDeliveryTime => _preferredDeliveryTime;
  List<FavoriteMeal> get favoriteMeals => _favoriteMeals;
  List<PastOrder> get pastOrders => _pastOrders;
  
  // Chat methods
  void addMessage(ChatMessage message) {
    _messages.add(message);
    notifyListeners();
  }
  
  void setTyping(bool typing) {
    _isTyping = typing;
    notifyListeners();
  }
  
  void setBudget(String budget) {
    _currentBudget = budget;
    notifyListeners();
  }
  
  void setFamilySize(int size) {
    _familySize = size;
    notifyListeners();
  }
  
  void clearChatHistory() {
    _messages.clear();
    _isTyping = false;
    notifyListeners();
  }
  
// Pantry state
  List<PantryItem> _pantryList = [
    PantryItem(
      name: 'Whole Milk',
      quantity: 1.0,
      unit: 'gallon',
      expirationDate: DateTime.now().add(const Duration(days: 5)),
      location: 'Refrigerator',
      category: 'Dairy',
      brand: 'Organic Valley',
      originalQuantity: 1.0,
    ),
    PantryItem(
      name: 'Greek Yogurt',
      quantity: 2.0,
      unit: 'containers',
      expirationDate: DateTime.now().add(const Duration(days: 2)),
      location: 'Refrigerator',
      category: 'Dairy',
      brand: 'Chobani',
      originalQuantity: 4.0,
    ),
    PantryItem(
      name: 'Bananas',
      quantity: 6.0,
      unit: 'pieces',
      expirationDate: DateTime.now().add(const Duration(days: 3)),
      location: 'Counter',
      category: 'Fruits',
      originalQuantity: 8.0,
    ),
    PantryItem(
      name: 'Chicken Breast',
      quantity: 2.0,
      unit: 'lbs',
      expirationDate: DateTime.now().add(const Duration(days: 1)),
      location: 'Freezer',
      category: 'Meat',
      brand: 'Perdue',
      originalQuantity: 3.0,
    ),
    PantryItem(
      name: 'Brown Rice',
      quantity: 1.5,
      unit: 'lbs',
      expirationDate: DateTime.now().add(const Duration(days: 365)),
      location: 'Pantry',
      category: 'Grains',
      originalQuantity: 2.0,
    ),
  ];

  List<PantryItem> get pantryList => _pantryList;
  
  List<PantryItem> get expiringItems => _pantryList.where((item) => item.isExpiringSoon || item.isExpired).toList();
  
  List<PantryItem> get lowStockItems => _pantryList.where((item) => item.isLowStock).toList();
  
  int get itemsNeedingAttention => _pantryList.where((item) => item.needsAttention).length;

  void updatePantryList(List<PantryItem> items) {
    _pantryList = items;
    notifyListeners();
  }

  Future<void> addToPantry(PantryItem item) async {
    try {
      await _pantryRepository.addPantryItem(item);
      // Reload the list to reflect changes
      await loadPantryData();
    } catch (e) {
      _lastError = 'Failed to add item to pantry: $e';
      notifyListeners();
    }
  }

  Future<void> removePantryItem(String id) async {
    try {
      await _pantryRepository.deletePantryItem(id);
      // Reload the list to reflect changes
      await loadPantryData();
    } catch (e) {
      _lastError = 'Failed to remove pantry item: $e';
      notifyListeners();
    }
  }
  
  Future<void> updatePantryItem(String id, PantryItem updatedItem) async {
    try {
      await _pantryRepository.updatePantryItem(updatedItem);
      // Reload the list to reflect changes
      await loadPantryData();
    } catch (e) {
      _lastError = 'Failed to update pantry item: $e';
      notifyListeners();
    }
  }
  
  Future<void> updatePantryQuantity(String id, double newQuantity) async {
    try {
      final result = await _pantryRepository.updateItemQuantity(id, newQuantity);
      if (result.isSuccess) {
        // Reload the list to reflect changes
        await loadPantryData();
      } else {
        _lastError = result.message;
        notifyListeners();
      }
    } catch (e) {
      _lastError = 'Failed to update pantry quantity: $e';
      notifyListeners();
    }
  }
  
  Future<void> markItemAsUsed(String id, double usedQuantity) async {
    try {
      final index = _pantryList.indexWhere((item) => item.id == id);
      if (index != -1) {
        final item = _pantryList[index];
        final newQuantity = (item.quantity - usedQuantity).clamp(0.0, double.infinity);
        final updatedItem = item.copyWith(quantity: newQuantity);
        await _pantryRepository.updatePantryItem(updatedItem);
        // Reload the list to reflect changes
        await loadPantryData();
      }
    } catch (e) {
      _lastError = 'Failed to mark item as used: $e';
      notifyListeners();
    }
  }

  // Shopping methods
  void updateShoppingList(List<ShoppingItem> items) {
    _shoppingList = items;
    _totalCost = items.fold(0.0, (sum, item) => sum + (item.price * item.quantity));
    _isShoppingListReady = items.isNotEmpty;
    notifyListeners();
  }
  
  void updateSelectedStore(String store) {
    _selectedStore = store;
    notifyListeners();
  }

  void updateFamilySize(int size) {
    _familySize = size;
    notifyListeners();
  }

  void updateBudget(String budget) {
    _currentBudget = budget;
    notifyListeners();
  }

  void addDietaryRestriction(String restriction) {
    if (!_dietaryRestrictions.contains(restriction)) {
      _dietaryRestrictions.add(restriction);
      notifyListeners();
    }
  }

  void removeDietaryRestriction(String restriction) {
    _dietaryRestrictions.remove(restriction);
    notifyListeners();
  }

  void updatePreferredDeliveryTime(String time) {
    _preferredDeliveryTime = time;
    notifyListeners();
  }

  void updateItemQuantity(int index, int newQuantity) {
    if (index >= 0 && index < _shoppingList.length && newQuantity > 0) {
      _shoppingList[index] = ShoppingItem(
        name: _shoppingList[index].name,
        price: _shoppingList[index].price,
        quantity: newQuantity,
        category: _shoppingList[index].category,
        unit: _shoppingList[index].unit,
        notes: _shoppingList[index].notes,
      );
      notifyListeners();
    }
  }

  void clearShoppingList() {
    _shoppingList.clear();
    _totalCost = 0.0;
    _isShoppingListReady = false;
    notifyListeners();
  }

  void removeFromShoppingList(int index) {
    if (index >= 0 && index < _shoppingList.length) {
      _shoppingList.removeAt(index);
      notifyListeners();
    }
  }

  void addToShoppingList(ShoppingItem item) {
    _shoppingList.add(item);
    notifyListeners();
  }
  
  // Favorites methods
  void addFavoriteMeal(FavoriteMeal meal) {
    _favoriteMeals.add(meal);
    notifyListeners();
  }
  
  void removeFavoriteMeal(String mealId) {
    _favoriteMeals.removeWhere((meal) => meal.id == mealId);
    notifyListeners();
  }
  
  void reorderFavoriteMeal(String mealId) {
    try {
      FavoriteMeal meal = _favoriteMeals.firstWhere((m) => m.id == mealId);
      // Convert favorite meal to shopping list
      List<ShoppingItem> mealItems = meal.ingredients.map((ingredient) {
        return ShoppingItem(
          name: ingredient,
          price: (meal.estimatedCost / meal.ingredients.length),
          quantity: 1,
          category: 'Ingredient',
          unit: 'item',
          notes: 'From ${meal.name}',
        );
      }).toList();
      
      updateShoppingList([..._shoppingList, ...mealItems]);
    } catch (e) {
      // Meal not found, handle gracefully
    }
  }
  
  // Order history methods
  void addPastOrder(PastOrder order) {
    _pastOrders.insert(0, order); // Add to beginning for chronological order
    notifyListeners();
  }
  
  void reorderPastOrder(String orderId) {
    try {
      PastOrder order = _pastOrders.firstWhere((o) => o.id == orderId);
      updateShoppingList([..._shoppingList, ...order.items]);
      updateSelectedStore(order.store);
    } catch (e) {
      // Order not found, handle gracefully
    }
  }
  
  // User preferences
  void updateDietaryRestrictions(List<String> restrictions) {
    _dietaryRestrictions = restrictions;
    notifyListeners();
  }
  
  void setPreferredDeliveryTime(String time) {
    _preferredDeliveryTime = time;
    notifyListeners();
  }
  
  // Additional getters for new state
  bool get isLoading => _isLoading;
  String? get lastError => _lastError;
  
  // Initialize repositories and load data
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      _isLoading = true;
      _lastError = null;
      notifyListeners();
      
      // Load chat history
      await loadChatHistory();
      
      // Load pantry data
      await loadPantryData();
      
      _isInitialized = true;
    } catch (e) {
      _lastError = 'Failed to initialize: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Load chat history from repository
  Future<void> loadChatHistory() async {
    try {
      final history = await _chatRepository.getChatHistory();
      _messages.clear();
      _messages.addAll(history);
      notifyListeners();
    } catch (e) {
      print('Failed to load chat history: $e');
    }
  }
  
  // Load pantry data from repository  
  Future<void> loadPantryData() async {
    try {
      final items = await _pantryRepository.getPantryItems();
      _pantryList = items;
      notifyListeners();
    } catch (e) {
      print('Failed to load pantry data: $e');
      // Keep default mock data if loading fails
    }
  }
  
  // Send message to Bruno using ChatRepository
  Future<void> sendMessageToBruno(String userMessage) async {
    setTyping(true);
    _lastError = null;
    
    // Add user message first
    final userChatMessage = ChatMessage(
      text: userMessage,
      isFromUser: true,
      timestamp: DateTime.now(),
    );
    addMessage(userChatMessage);
    
    try {
      // Use mock response as fallback for now
      final responseText = _generateBrunoResponse(userMessage);
      
      // Determine if this should have shopping action
      bool hasShoppingAction = false;
      if (userMessage.toLowerCase().contains('budget') || 
          userMessage.toLowerCase().contains('meal') ||
          userMessage.toLowerCase().contains('plan') ||
          userMessage.toLowerCase().contains('recipe')) {
        hasShoppingAction = true;
      }
      
      final botMessage = ChatMessage(
        text: responseText,
        isFromUser: false,
        timestamp: DateTime.now(),
        hasShoppingAction: hasShoppingAction,
      );
      
      // Small delay to simulate typing
      await Future.delayed(const Duration(milliseconds: 500));
      
      addMessage(botMessage);
      
    } catch (e) {
      _lastError = 'Error sending message: $e';
      notifyListeners();
    } finally {
      setTyping(false);
    }
  }
  
  // Keep the mock response as fallback
  String _generateBrunoResponse(String userMessage) {
    String message = userMessage.toLowerCase();
    
    if (message.contains('budget') && message.contains('\$')) {
      // Extract budget amount
      RegExp budgetRegex = RegExp(r'\$(\d+)');
      Match? match = budgetRegex.firstMatch(message);
      if (match != null) {
        setBudget(match.group(1)!);
        return "Perfect! I'll create delicious meals for your family within \$${match.group(1)}. Let me find the best deals this week! 🐻\n\n🎯 Found amazing deals:\n• Chicken thighs: \$1.99/lb at Whole Foods\n• Sweet potatoes: \$0.89/lb at Costco\n\nI created 7 family-friendly meals for \$${(int.parse(match.group(1)!) * 0.95).toStringAsFixed(2)}!\n\n🛒 Want me to add everything to your Instacart cart?";
      }
    }
    
    if (message.contains('recipe') || message.contains('cook')) {
      return "Great choice! 🥢 Let me create a budget-friendly recipe for you...\n\nRecipe: Bruno's Budget Chicken Stir-Fry\n• Serves 4 people\n• Total cost: \$12.80 (\$3.20 per serving)\n• Prep time: 15 minutes\n\n🛒 Ready to order all ingredients on Instacart?";
    }
    
    if (message.contains('instacart') || message.contains('order') || message.contains('shop')) {
      updateShoppingList([
        ShoppingItem(name: 'Chicken breast', price: 8.99, quantity: 2, category: 'Meat', unit: 'lbs', notes: ''),
        ShoppingItem(name: 'Sweet potatoes', price: 2.49, quantity: 3, category: 'Vegetables', unit: 'lbs', notes: ''),
        ShoppingItem(name: 'Broccoli', price: 3.99, quantity: 1, category: 'Vegetables', unit: 'bunch', notes: ''),
        ShoppingItem(name: 'Rice', price: 4.99, quantity: 1, category: 'Grains', unit: 'bag', notes: ''),
      ]);
      return "Done! 🎉 I created your shopping list with ${_shoppingList.length} items for \$${_totalCost.toStringAsFixed(2)}.\n\nYour order will be ready for delivery from Whole Foods in 2 hours!\nYou saved \$${(double.parse(_currentBudget.isEmpty ? '80' : _currentBudget) - _totalCost).toStringAsFixed(2)} under budget! 💰";
    }
    
    if (message.contains('hello') || message.contains('hi')) {
      return "Hi! I'm Bruno, your meal planning bear with shopping superpowers! 🐻🛒\n\nWhat's your budget this week? I'll help you create delicious, affordable meals and get them delivered right to your door!";
    }
    
    return "I'm here to help you plan amazing meals within your budget! Tell me your weekly grocery budget and family size, and I'll create a perfect meal plan with Instacart delivery. 🐻✨";
  }
}


// Data Models
class FavoriteMeal {
  final String id;
  final String name;
  final String description;
  final List<String> ingredients;
  final double estimatedCost;
  final int servings;
  final int cookingTime; // in minutes
  final String category;
  final DateTime dateAdded;

  FavoriteMeal({
    required this.id,
    required this.name,
    required this.description,
    required this.ingredients,
    required this.estimatedCost,
    required this.servings,
    required this.cookingTime,
    required this.category,
    required this.dateAdded,
  });
}

class PastOrder {
  final String id;
  final DateTime date;
  final String store;
  final List<ShoppingItem> items;
  final double totalAmount;
  final String status;

  PastOrder({
    required this.id,
    required this.date,
    required this.store,
    required this.items,
    required this.totalAmount,
    required this.status,
  });
}