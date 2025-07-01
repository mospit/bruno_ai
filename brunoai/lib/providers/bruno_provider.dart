import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../models/shopping_item.dart';

class BrunoProvider extends ChangeNotifier {
  // Chat state
  List<ChatMessage> _messages = [];
  bool _isTyping = false;
  String _currentBudget = '';
  int _familySize = 1;
  
  // Shopping state
  List<ShoppingItem> _shoppingList = [
    ShoppingItem(
      name: 'Organic Chicken Breast', 
      price: 12.99, 
      quantity: 2,
      category: 'Meat',
      unit: 'lbs',
      notes: 'Boneless, skinless'
    ),
    ShoppingItem(
      name: 'Fresh Broccoli', 
      price: 3.49, 
      quantity: 1,
      category: 'Vegetables',
      unit: 'bunch',
      notes: 'Organic preferred'
    ),
    ShoppingItem(
      name: 'Brown Rice', 
      price: 4.99, 
      quantity: 1,
      category: 'Grains',
      unit: 'bag',
      notes: '2 lbs bag'
    ),
  ];
  double _totalCost = 0.0;
  String _selectedStore = '';
  bool _isShoppingListReady = false;
  
  // User preferences
  List<String> _dietaryRestrictions = [];
  String _preferredDeliveryTime = '';
  
  // Favorites and Order History
  List<FavoriteMeal> _favoriteMeals = [
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
  
  List<PastOrder> _pastOrders = [
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
    FavoriteMeal? meal = _favoriteMeals.firstWhere((m) => m.id == mealId);
    if (meal != null) {
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
    }
  }
  
  // Order history methods
  void addPastOrder(PastOrder order) {
    _pastOrders.insert(0, order); // Add to beginning for chronological order
    notifyListeners();
  }
  
  void reorderPastOrder(String orderId) {
    PastOrder? order = _pastOrders.firstWhere((o) => o.id == orderId);
    if (order != null) {
      updateShoppingList([..._shoppingList, ...order.items]);
      updateSelectedStore(order.store);
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
  
  // Simulate Bruno AI response
  Future<void> sendMessageToBruno(String userMessage) async {
    // Add user message
    addMessage(ChatMessage(
      text: userMessage,
      isFromUser: true,
      timestamp: DateTime.now(),
    ));
    
    // Show typing indicator
    setTyping(true);
    
    // Simulate API delay
    await Future.delayed(const Duration(seconds: 2));
    
    // Generate Bruno response based on user input
    String brunoResponse = _generateBrunoResponse(userMessage);
    
    // Add Bruno response
    addMessage(ChatMessage(
      text: brunoResponse,
      isFromUser: false,
      timestamp: DateTime.now(),
      hasShoppingAction: userMessage.toLowerCase().contains('budget') || 
                        userMessage.toLowerCase().contains('meal'),
    ));
    
    setTyping(false);
  }
  
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
        ShoppingItem(name: 'Chicken breast', price: 8.99, quantity: 2),
        ShoppingItem(name: 'Sweet potatoes', price: 2.49, quantity: 3),
        ShoppingItem(name: 'Broccoli', price: 3.99, quantity: 1),
        ShoppingItem(name: 'Rice', price: 4.99, quantity: 1),
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