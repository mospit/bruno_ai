import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/models/chat_message.dart';
import 'package:brunoai/models/shopping_item.dart';
import 'package:brunoai/widgets/meal_card.dart';
import 'package:provider/provider.dart';

/// Test utilities and helpers for Bruno AI tests
class TestUtils {
  /// Creates a test app wrapper with provider
  static Widget createTestApp({
    required Widget child,
    BrunoProvider? provider,
  }) {
    return MaterialApp(
      home: ChangeNotifierProvider<BrunoProvider>(
        create: (_) => provider ?? BrunoProvider(),
        child: child,
      ),
    );
  }

  /// Creates a mock chat message
  static ChatMessage createMockChatMessage({
    String text = 'Test message',
    bool isFromUser = true,
    DateTime? timestamp,
    bool hasShoppingAction = false,
  }) {
    return ChatMessage(
      text: text,
      isFromUser: isFromUser,
      timestamp: timestamp ?? DateTime.now(),
      hasShoppingAction: hasShoppingAction,
    );
  }

  /// Creates a mock shopping item
  static ShoppingItem createMockShoppingItem({
    String name = 'Test Item',
    double price = 5.99,
    int quantity = 1,
    String category = 'Pantry',
    String unit = 'item',
    String notes = '',
  }) {
    return ShoppingItem(
      name: name,
      price: price,
      quantity: quantity,
      category: category,
      unit: unit,
      notes: notes,
    );
  }

  /// Creates a mock meal
  static Meal createMockMeal({
    String id = 'test_meal',
    String name = 'Test Meal',
    String description = 'A test meal',
    double cost = 15.99,
    int servings = 4,
    int prepTime = 30,
    String? imageUrl,
    List<String>? ingredients,
    List<String>? instructions,
    String category = 'Main Course',
    Map<String, double>? nutrition,
    bool isHealthy = false,
    bool isQuick = false,
    String difficulty = 'Easy',
  }) {
    return Meal(
      id: id,
      name: name,
      description: description,
      cost: cost,
      servings: servings,
      prepTime: prepTime,
      imageUrl: imageUrl,
      ingredients: ingredients ?? ['ingredient1', 'ingredient2'],
      instructions: instructions ?? ['step1', 'step2'],
      category: category,
      nutrition: nutrition ?? {},
      isHealthy: isHealthy,
      isQuick: isQuick,
      difficulty: difficulty,
    );
  }

  /// Creates a mock BrunoProvider with sample data
  static BrunoProvider createMockProvider({
    List<ChatMessage>? messages,
    List<ShoppingItem>? shoppingList,
    String currentBudget = '',
    bool isTyping = false,
    List<String>? dietaryRestrictions,
    String preferredDeliveryTime = '',
  }) {
    final provider = BrunoProvider();
    
    // Add mock messages
    if (messages != null) {
      for (final message in messages) {
        provider.addMessage(message);
      }
    }
    
    // Add mock shopping items
    if (shoppingList != null) {
      provider.updateShoppingList(shoppingList);
    }
    
    // Set budget
    if (currentBudget.isNotEmpty) {
      provider.setBudget(currentBudget);
    }
    
    // Set typing state
    provider.setTyping(isTyping);
    
    // Set dietary restrictions
    if (dietaryRestrictions != null) {
      provider.updateDietaryRestrictions(dietaryRestrictions);
    }
    
    // Set delivery time
    if (preferredDeliveryTime.isNotEmpty) {
      provider.setPreferredDeliveryTime(preferredDeliveryTime);
    }
    
    return provider;
  }

  /// Waits for animations to complete
  static Future<void> waitForAnimations(WidgetTester tester, {
    Duration duration = const Duration(milliseconds: 500),
  }) async {
    await tester.pump();
    await tester.pump(duration);
  }

  /// Pumps the widget tree until no more frames are scheduled
  static Future<void> pumpUntilNoMoreFrames(WidgetTester tester) async {
    int pumpCount = 0;
    const maxPumps = 100;
    
    while (tester.binding.hasScheduledFrame && pumpCount < maxPumps) {
      await tester.pump(const Duration(milliseconds: 16));
      pumpCount++;
    }
  }

  /// Creates sample shopping list
  static List<ShoppingItem> createSampleShoppingList() {
    return [
      createMockShoppingItem(
        name: 'Chicken breast',
        price: 8.99,
        quantity: 2,
        category: 'Meat',
        unit: 'lbs',
      ),
      createMockShoppingItem(
        name: 'Broccoli',
        price: 3.99,
        quantity: 1,
        category: 'Vegetables',
        unit: 'item',
      ),
      createMockShoppingItem(
        name: 'Rice',
        price: 4.99,
        quantity: 1,
        category: 'Grains',
        unit: 'item',
      ),
    ];
  }

  /// Creates sample chat conversation
  static List<ChatMessage> createSampleConversation() {
    return [
      createMockChatMessage(
        text: 'Hello Bruno',
        isFromUser: true,
        timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
      createMockChatMessage(
        text: 'Hi! I\'m Bruno, your meal planning bear! What\'s your budget?',
        isFromUser: false,
        timestamp: DateTime.now().subtract(const Duration(minutes: 4)),
      ),
      createMockChatMessage(
        text: 'My budget is \$100',
        isFromUser: true,
        timestamp: DateTime.now().subtract(const Duration(minutes: 3)),
        hasShoppingAction: true,
      ),
      createMockChatMessage(
        text: 'Perfect! I\'ll create meals for \$100. Here are some options...',
        isFromUser: false,
        timestamp: DateTime.now().subtract(const Duration(minutes: 2)),
        hasShoppingAction: true,
      ),
    ];
  }

  /// Finds widget by text that contains the given substring
  static Finder findTextContaining(String substring) {
    return find.byWidgetPredicate(
      (widget) => widget is Text && 
                   widget.data != null && 
                   widget.data!.contains(substring),
    );
  }

  /// Finds widget by type and property
  static Finder findByTypeAndProperty<T extends Widget>(
    bool Function(T widget) predicate,
  ) {
    return find.byWidgetPredicate(
      (widget) => widget is T && predicate(widget),
    );
  }

  /// Verifies that a widget is visible and rendered
  static void verifyWidgetVisible(WidgetTester tester, Finder finder) {
    expect(finder, findsOneWidget);
    final widget = tester.widget(finder);
    expect(widget, isNotNull);
  }

  /// Simulates a tap and waits for animations
  static Future<void> tapAndWait(WidgetTester tester, Finder finder) async {
    await tester.tap(finder);
    await tester.pump();
    await waitForAnimations(tester);
  }

  /// Enters text and simulates send action
  static Future<void> enterTextAndSend(
    WidgetTester tester,
    Finder textField,
    String text,
  ) async {
    await tester.enterText(textField, text);
    await tester.testTextInput.receiveAction(TextInputAction.send);
    await tester.pump();
  }

  /// Verifies provider state
  static void verifyProviderState(
    WidgetTester tester,
    Finder widgetFinder, {
    int? expectedMessageCount,
    int? expectedShoppingItemCount,
    double? expectedTotalCost,
    String? expectedBudget,
    bool? expectedIsTyping,
  }) {
    final provider = tester.element(widgetFinder).read<BrunoProvider>();
    
    if (expectedMessageCount != null) {
      expect(provider.messages.length, equals(expectedMessageCount));
    }
    
    if (expectedShoppingItemCount != null) {
      expect(provider.shoppingList.length, equals(expectedShoppingItemCount));
    }
    
    if (expectedTotalCost != null) {
      expect(provider.totalCost, equals(expectedTotalCost));
    }
    
    if (expectedBudget != null) {
      expect(provider.currentBudget, equals(expectedBudget));
    }
    
    if (expectedIsTyping != null) {
      expect(provider.isTyping, equals(expectedIsTyping));
    }
  }
}

/// Custom matchers for testing
class CustomMatchers {
  /// Matcher for shopping items with specific properties
  static Matcher isShoppingItemWith({
    String? name,
    double? price,
    int? quantity,
    String? category,
  }) {
    return predicate<ShoppingItem>((item) {
      return (name == null || item.name == name) &&
             (price == null || item.price == price) &&
             (quantity == null || item.quantity == quantity) &&
             (category == null || item.category == category);
    });
  }

  /// Matcher for chat messages with specific properties
  static Matcher isChatMessageWith({
    String? text,
    bool? isFromUser,
    bool? hasShoppingAction,
  }) {
    return predicate<ChatMessage>((message) {
      return (text == null || message.text.contains(text)) &&
             (isFromUser == null || message.isFromUser == isFromUser) &&
             (hasShoppingAction == null || message.hasShoppingAction == hasShoppingAction);
    });
  }

  /// Matcher for meals with specific properties
  static Matcher isMealWith({
    String? name,
    double? cost,
    int? servings,
    String? category,
    bool? isHealthy,
    bool? isQuick,
  }) {
    return predicate<Meal>((meal) {
      return (name == null || meal.name == name) &&
             (cost == null || meal.cost == cost) &&
             (servings == null || meal.servings == servings) &&
             (category == null || meal.category == category) &&
             (isHealthy == null || meal.isHealthy == isHealthy) &&
             (isQuick == null || meal.isQuick == isQuick);
    });
  }
}
