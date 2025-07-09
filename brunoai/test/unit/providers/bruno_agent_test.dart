import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/models/chat_message.dart';
import 'package:brunoai/models/shopping_item.dart';

/// Tests for Bruno AI agent functionality through the provider
/// These tests verify that the agent responses work correctly
void main() {
  group('Bruno AI Agent Provider Tests', () {
    late BrunoProvider provider;

    setUp(() {
      provider = BrunoProvider();
    });

    test('should initialize with empty state', () {
      expect(provider.messages, isEmpty);
      expect(provider.isTyping, isFalse);
      expect(provider.currentBudget, isEmpty);
      expect(provider.familySize, equals(1));
      expect(provider.shoppingList, isNotEmpty); // Has default items
    });

    test('should add user message when sending to Bruno', () async {
      const testMessage = 'Hello Bruno!';
      
      await provider.sendMessageToBruno(testMessage);
      
      // Should have at least user message
      expect(provider.messages.isNotEmpty, isTrue);
      expect(provider.messages.first.isUser, isTrue);
      expect(provider.messages.first.message, equals(testMessage));
    });

    test('should set typing indicator during message processing', () async {
      const testMessage = 'Test message';
      
      // Start the async operation
      final future = provider.sendMessageToBruno(testMessage);
      
      // Typing should be true during processing
      expect(provider.isTyping, isTrue);
      
      // Wait for completion
      await future;
      
      // Typing should be false after completion
      expect(provider.isTyping, isFalse);
    });

    test('should generate Bruno response after user message', () async {
      const testMessage = 'Hello Bruno!';
      
      await provider.sendMessageToBruno(testMessage);
      
      // Should have user message + Bruno response
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.messages.last.isUser, isFalse);
      expect(provider.messages.last.message.isNotEmpty, isTrue);
    });

    test('should extract and set budget from message', () async {
      const budgetMessage = 'My weekly budget is \$80';
      
      await provider.sendMessageToBruno(budgetMessage);
      
      // Budget should be extracted and set
      expect(provider.currentBudget, equals('80'));
      
      // Response should mention budget
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('budget') || lastMessage.contains('\$80'), isTrue);
    });

    test('should handle recipe requests', () async {
      const recipeMessage = 'I want a chicken recipe';
      
      await provider.sendMessageToBruno(recipeMessage);
      
      // Should have response about recipe
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('recipe') || lastMessage.contains('chicken'), isTrue);
    });

    test('should update shopping list for instacart requests', () async {
      const shoppingMessage = 'Add to instacart';
      
      final initialListSize = provider.shoppingList.length;
      await provider.sendMessageToBruno(shoppingMessage);
      
      // Shopping list should be updated
      expect(provider.shoppingList.length, greaterThanOrEqualTo(initialListSize));
      expect(provider.totalCost, greaterThan(0));
      
      // Response should mention shopping/cart
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('cart') || lastMessage.contains('shopping'), isTrue);
    });

    test('should handle multiple messages in sequence', () async {
      // Send multiple messages
      await provider.sendMessageToBruno('Hello');
      await provider.sendMessageToBruno('My budget is \$50');
      await provider.sendMessageToBruno('Plan meals');
      
      // Should have all messages
      expect(provider.messages.length, greaterThanOrEqualTo(6)); // 3 user + 3 Bruno
      expect(provider.currentBudget, equals('50'));
    });

    test('should handle budget extraction from various formats', () async {
      // Test different budget formats
      final budgetFormats = [
        'My budget is \$100',
        'I have \$75 to spend',
        'Budget: \$50',
        '\$200 weekly budget',
      ];
      
      for (int i = 0; i < budgetFormats.length; i++) {
        final newProvider = BrunoProvider();
        await newProvider.sendMessageToBruno(budgetFormats[i]);
        
        // Should extract budget correctly
        expect(newProvider.currentBudget.isNotEmpty, isTrue);
        expect(double.tryParse(newProvider.currentBudget), isA<double>());
      }
    });

    test('should provide helpful response for unclear messages', () async {
      const unclearMessage = 'asdfghjkl qwertyuiop';
      
      await provider.sendMessageToBruno(unclearMessage);
      
      // Should still provide a response
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.messages.last.isUser, isFalse);
      expect(provider.messages.last.message.isNotEmpty, isTrue);
    });

    test('should handle shopping list operations', () {
      // Test adding items
      final newItem = ShoppingItem(
        name: 'Test Item',
        price: 5.99,
        quantity: 1,
        category: 'Test',
        unit: 'item',
        notes: 'Test notes'
      );
      
      provider.addToShoppingList(newItem);
      expect(provider.shoppingList.contains(newItem), isTrue);
      
      // Test removing items
      final initialCount = provider.shoppingList.length;
      provider.removeFromShoppingList(0);
      expect(provider.shoppingList.length, equals(initialCount - 1));
      
      // Test clearing list
      provider.clearShoppingList();
      expect(provider.shoppingList, isEmpty);
      expect(provider.totalCost, equals(0.0));
    });

    test('should handle user preferences', () {
      // Test dietary restrictions
      provider.addDietaryRestriction('Vegetarian');
      expect(provider.dietaryRestrictions.contains('Vegetarian'), isTrue);
      
      // Test family size
      provider.setFamilySize(4);
      expect(provider.familySize, equals(4));
      
      // Test budget setting
      provider.setBudget('100');
      expect(provider.currentBudget, equals('100'));
    });

    test('should handle favorites and past orders', () {
      // Test favorites
      expect(provider.favoriteMeals.isNotEmpty, isTrue);
      
      // Test past orders
      expect(provider.pastOrders.isNotEmpty, isTrue);
      
      // Test reordering
      final initialShoppingListSize = provider.shoppingList.length;
      provider.reorderPastOrder(provider.pastOrders.first.id);
      expect(provider.shoppingList.length, greaterThan(initialShoppingListSize));
    });

    test('should generate contextual responses', () async {
      // Test greeting
      await provider.sendMessageToBruno('Hello');
      final greetingResponse = provider.messages.last.message.toLowerCase();
      expect(greetingResponse.contains('bruno') || greetingResponse.contains('hello'), isTrue);
      
      // Clear messages for next test
      provider.clearShoppingList();
      
      // Test meal planning
      final newProvider = BrunoProvider();
      await newProvider.sendMessageToBruno('Plan meals for this week');
      final planResponse = newProvider.messages.last.message.toLowerCase();
      expect(planResponse.contains('meal') || planResponse.contains('plan'), isTrue);
    });

    test('should handle budget constraints', () async {
      // Set low budget
      await provider.sendMessageToBruno('My budget is \$20');
      expect(provider.currentBudget, equals('20'));
      
      // Request expensive meal
      await provider.sendMessageToBruno('I want expensive lobster dinner');
      
      // Should provide budget-conscious response
      final response = provider.messages.last.message.toLowerCase();
      expect(response.contains('budget') || response.contains('affordable'), isTrue);
    });
  });

  group('Bruno AI Agent Message Processing', () {
    late BrunoProvider provider;

    setUp(() {
      provider = BrunoProvider();
    });

    test('should handle message types correctly', () async {
      final messageTypes = [
        'Hello Bruno!',
        'My budget is \$80',
        'Give me a recipe',
        'Add to instacart',
        'Plan meals for the week',
        'I need vegetarian options',
      ];

      for (final message in messageTypes) {
        final newProvider = BrunoProvider();
        await newProvider.sendMessageToBruno(message);
        
        // Should always have user message + response
        expect(newProvider.messages.length, greaterThanOrEqualTo(2));
        expect(newProvider.messages.first.isUser, isTrue);
        expect(newProvider.messages.last.isUser, isFalse);
        expect(newProvider.messages.last.message.isNotEmpty, isTrue);
      }
    });

    test('should maintain conversation context', () async {
      // Send related messages
      await provider.sendMessageToBruno('I want Italian food');
      await provider.sendMessageToBruno('What ingredients do I need?');
      
      // Should have multiple messages
      expect(provider.messages.length, greaterThanOrEqualTo(4));
      
      // Last response should be contextual
      final lastResponse = provider.messages.last.message.toLowerCase();
      expect(lastResponse.contains('italian') || lastResponse.contains('ingredient'), isTrue);
    });
  });
}
