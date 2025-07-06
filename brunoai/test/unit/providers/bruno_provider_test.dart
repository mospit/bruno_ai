import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/models/chat_message.dart';
import 'package:brunoai/models/shopping_item.dart';
import 'package:fake_async/fake_async.dart';

void main() {
  group('BrunoProvider', () {
    late BrunoProvider provider;

    setUp(() {
      provider = BrunoProvider();
    });

    group('Chat Messages', () {
      test('should start with empty messages list', () {
        expect(provider.messages, isEmpty);
      });

      test('should add message to list', () {
        final message = ChatMessage(
          text: 'Hello',
          isFromUser: true,
          timestamp: DateTime.now(),
        );

        provider.addMessage(message);

        expect(provider.messages, hasLength(1));
        expect(provider.messages.first.text, equals('Hello'));
        expect(provider.messages.first.isFromUser, isTrue);
      });

      test('should add multiple messages', () {
        provider.addMessage(ChatMessage(
          text: 'Message 1',
          isFromUser: true,
          timestamp: DateTime.now(),
        ));
        provider.addMessage(ChatMessage(
          text: 'Message 2',
          isFromUser: false,
          timestamp: DateTime.now(),
        ));

        expect(provider.messages, hasLength(2));
        expect(provider.messages.first.text, equals('Message 1'));
        expect(provider.messages.last.text, equals('Message 2'));
      });
    });

    group('Typing State', () {
      test('should start with typing as false', () {
        expect(provider.isTyping, isFalse);
      });

      test('should set typing state', () {
        provider.setTyping(true);
        expect(provider.isTyping, isTrue);

        provider.setTyping(false);
        expect(provider.isTyping, isFalse);
      });
    });

    group('Shopping List', () {
      test('should start with pre-loaded shopping list', () {
        expect(provider.shoppingList, isNotEmpty);
      });

      test('should add item to shopping list', () {
        final initialLength = provider.shoppingList.length;
        final item = ShoppingItem(name: 'Chicken', price: 8.99, quantity: 1);
        provider.addToShoppingList(item);

        expect(provider.shoppingList, hasLength(initialLength + 1));
        expect(provider.shoppingList.last.name, equals('Chicken'));
      });

      test('should remove item from shopping list', () {
        final initialLength = provider.shoppingList.length;
        provider.removeFromShoppingList(0);
        expect(provider.shoppingList, hasLength(initialLength - 1));
      });

      test('should update entire shopping list', () {
        final items = [
          ShoppingItem(name: 'Chicken', price: 8.99, quantity: 2),
          ShoppingItem(name: 'Rice', price: 4.99, quantity: 1),
        ];

        provider.updateShoppingList(items);

        expect(provider.shoppingList, hasLength(2));
        expect(provider.totalCost, equals(22.97)); // (8.99 * 2) + 4.99
      });

      test('should clear shopping list', () {
        provider.clearShoppingList();
        expect(provider.shoppingList, isEmpty);
        expect(provider.totalCost, equals(0.0));
      });

      test('should calculate total cost correctly', () {
        final items = [
          ShoppingItem(name: 'Chicken', price: 8.99, quantity: 2),
          ShoppingItem(name: 'Rice', price: 4.99, quantity: 1),
          ShoppingItem(name: 'Broccoli', price: 3.99, quantity: 3),
        ];

        provider.updateShoppingList(items);

        final expectedTotal = (8.99 * 2) + (4.99 * 1) + (3.99 * 3);
        expect(provider.totalCost, equals(expectedTotal));
      });
    });

    group('Budget Management', () {
      test('should start with empty budget', () {
        expect(provider.currentBudget, isEmpty);
      });

      test('should set budget', () {
        provider.setBudget('100');
        expect(provider.currentBudget, equals('100'));
      });

      test('should update budget', () {
        provider.setBudget('50');
        expect(provider.currentBudget, equals('50'));

        provider.setBudget('75');
        expect(provider.currentBudget, equals('75'));
      });
    });

    group('User Preferences', () {
      test('should start with empty dietary restrictions', () {
        expect(provider.dietaryRestrictions, isEmpty);
      });

      test('should update dietary restrictions', () {
        final restrictions = ['vegetarian', 'gluten-free'];
        provider.updateDietaryRestrictions(restrictions);

        expect(provider.dietaryRestrictions, hasLength(2));
        expect(provider.dietaryRestrictions, contains('vegetarian'));
        expect(provider.dietaryRestrictions, contains('gluten-free'));
      });

      test('should start with empty preferred delivery time', () {
        expect(provider.preferredDeliveryTime, isEmpty);
      });

      test('should set preferred delivery time', () {
        provider.setPreferredDeliveryTime('2 hours');
        expect(provider.preferredDeliveryTime, equals('2 hours'));
      });
    });

    group('Bruno AI Response', () {
      test('should send message to Bruno and get response', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('Hello');
          
          // Check user message was added
          expect(provider.messages, hasLength(1));
          expect(provider.messages.first.text, equals('Hello'));
          expect(provider.messages.first.isFromUser, isTrue);
          expect(provider.isTyping, isTrue);

          // Fast forward time to complete the async operation
          async.elapse(const Duration(seconds: 3));

          // Check Bruno response was added
          expect(provider.messages, hasLength(2));
          expect(provider.messages.last.isFromUser, isFalse);
          expect(provider.isTyping, isFalse);
        });
      });

      test('should handle budget messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('My budget is \$100');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.currentBudget, equals('100'));
          expect(provider.messages.last.text, contains('Perfect! I\'ll create delicious meals'));
          expect(provider.messages.last.text, contains('\$100'));
        });
      });

      test('should handle recipe messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('I need a recipe');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.messages.last.text, contains('Bruno\'s Budget Chicken Stir-Fry'));
          expect(provider.messages.last.text, contains('Serves 4 people'));
        });
      });

      test('should handle shopping messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('Add to instacart');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.shoppingList, hasLength(4));
          expect(provider.shoppingList, 
            contains(predicate<ShoppingItem>((item) => item.name == 'Chicken breast')));
          expect(provider.messages.last.text, contains('Done! 🎉'));
        });
      });

      test('should handle greeting messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('Hello');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.messages.last.text, contains('Hi! I\'m Bruno'));
          expect(provider.messages.last.text, contains('meal planning bear'));
        });
      });

      test('should handle generic messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('Random message');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.messages.last.text, contains('I\'m here to help'));
          expect(provider.messages.last.text, contains('meal plan'));
        });
      });

      test('should set hasShoppingAction for budget and meal messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('My budget is \$50');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.messages.last.hasShoppingAction, isTrue);
        });
      });

      test('should set hasShoppingAction for meal messages', () async {
        fakeAsync((async) {
          provider.sendMessageToBruno('I want a meal plan');
          
          async.elapse(const Duration(seconds: 3));

          expect(provider.messages.last.hasShoppingAction, isTrue);
        });
      });
    });

    group('Data Models', () {
      test('should create FavoriteMeal correctly', () {
        final meal = FavoriteMeal(
          id: 'test_meal',
          name: 'Test Meal',
          description: 'A test meal',
          ingredients: ['ingredient1', 'ingredient2'],
          estimatedCost: 15.0,
          servings: 4,
          cookingTime: 30,
          category: 'Main',
          dateAdded: DateTime.now(),
        );

        expect(meal.id, equals('test_meal'));
        expect(meal.name, equals('Test Meal'));
        expect(meal.estimatedCost, equals(15.0));
        expect(meal.servings, equals(4));
      });

      test('should create PastOrder correctly', () {
        final items = [
          ShoppingItem(name: 'Item 1', price: 5.0, quantity: 1),
          ShoppingItem(name: 'Item 2', price: 10.0, quantity: 2),
        ];

        final order = PastOrder(
          id: 'test_order',
          date: DateTime.now(),
          store: 'Test Store',
          items: items,
          totalAmount: 25.0,
          status: 'Delivered',
        );

        expect(order.id, equals('test_order'));
        expect(order.store, equals('Test Store'));
        expect(order.items, hasLength(2));
        expect(order.totalAmount, equals(25.0));
        expect(order.status, equals('Delivered'));
      });
    });
  });
}
