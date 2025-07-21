import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../lib/providers/bruno_provider.dart';
import '../../lib/models/shopping_item.dart';
import '../../lib/services/instacart_service.dart';

void main() {
  group('Shopping Integration Tests', () {
    late BrunoProvider provider;
    late InstacartService instacartService;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      provider = BrunoProvider();
      instacartService = InstacartService();
      await instacartService.initialize(mockMode: true);
    });

    test('should generate shopping list using InstacartService', () async {
      const keywords = ['chicken', 'rice', 'vegetables'];
      const store = 'Test Store';
      
      await provider.generateShoppingList(
        keywords: keywords,
        store: store,
        mockMode: true,
      );

      expect(provider.shoppingList.isNotEmpty, true);
      expect(provider.totalCost, greaterThan(0));
      expect(provider.isShoppingListReady, true);
      expect(provider.lastError, isNull);
    });

    test('should search for products and add to cart', () async {
      final response = await instacartService.searchProducts(
        query: 'chicken breast',
        store: 'Whole Foods',
        maxResults: 3,
      );

      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!.isNotEmpty, true);

      // Add first product to cart
      final product = response.data!.first;
      provider.addToShoppingList(product);

      expect(provider.shoppingList.length, equals(1));
      expect(provider.shoppingList.first.name, equals(product.name));
    });

    test('should update item quantities in shopping list', () async {
      final testItem = ShoppingItem(
        name: 'Test Chicken',
        price: 12.99,
        quantity: 1,
        category: 'Meat',
        unit: 'lb',
      );

      provider.addToShoppingList(testItem);
      expect(provider.shoppingList.length, equals(1));

      provider.updateItemQuantity(0, 3);
      expect(provider.shoppingList.first.quantity, equals(3));
    });

    test('should clear shopping list', () async {
      final testItems = [
        ShoppingItem(name: 'Item 1', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
        ShoppingItem(name: 'Item 2', price: 3.49, quantity: 2, category: 'Test', unit: 'item'),
      ];

      provider.updateShoppingList(testItems);
      expect(provider.shoppingList.length, equals(2));

      provider.clearShoppingList();
      expect(provider.shoppingList.isEmpty, true);
      expect(provider.totalCost, equals(0.0));
      expect(provider.isShoppingListReady, false);
    });

    test('should remove items from shopping list', () async {
      final testItems = [
        ShoppingItem(name: 'Item 1', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
        ShoppingItem(name: 'Item 2', price: 3.49, quantity: 2, category: 'Test', unit: 'item'),
      ];

      provider.updateShoppingList(testItems);
      expect(provider.shoppingList.length, equals(2));

      provider.removeFromShoppingList(0);
      expect(provider.shoppingList.length, equals(1));
      expect(provider.shoppingList.first.name, equals('Item 2'));
    });

    test('should calculate total cost correctly', () async {
      final testItems = [
        ShoppingItem(name: 'Item 1', price: 5.99, quantity: 2, category: 'Test', unit: 'item'), // $11.98
        ShoppingItem(name: 'Item 2', price: 3.49, quantity: 1, category: 'Test', unit: 'item'), // $3.49
      ];

      provider.updateShoppingList(testItems);
      
      expect(provider.totalCost, closeTo(15.47, 0.01)); // 11.98 + 3.49
    });

    test('should create cart deep link', () async {
      final testItems = [
        ShoppingItem(name: 'Chicken Breast', price: 12.99, quantity: 1, category: 'Meat', unit: 'lb'),
        ShoppingItem(name: 'Brown Rice', price: 4.99, quantity: 1, category: 'Grains', unit: 'bag'),
      ];

      final response = await instacartService.createCartDeepLink(
        items: testItems,
        store: 'Whole Foods',
      );

      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!, contains('instacart.com'));
    });

    test('should handle empty search gracefully', () async {
      const keywords = <String>[];
      const store = 'Test Store';
      
      await provider.generateShoppingList(
        keywords: keywords,
        store: store,
        mockMode: true,
      );

      expect(provider.lastError, isNotNull);
      expect(provider.shoppingList.isEmpty, true);
    });

    test('should update selected store', () async {
      const newStore = 'Target';
      
      provider.updateSelectedStore(newStore);
      
      expect(provider.selectedStore, equals(newStore));
    });

    test('should manage dietary restrictions', () async {
      const restriction = 'Vegetarian';
      
      provider.addDietaryRestriction(restriction);
      expect(provider.dietaryRestrictions.contains(restriction), true);
      
      provider.removeDietaryRestriction(restriction);
      expect(provider.dietaryRestrictions.contains(restriction), false);
    });
  });
}
