import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/models/shopping_item.dart';

void main() {
  group('ShoppingItem Model', () {
    test('should create ShoppingItem with required parameters', () {
      final item = ShoppingItem(
        name: 'Organic Apples',
        price: 3.99,
        quantity: 2,
      );

      expect(item.name, equals('Organic Apples'));
      expect(item.price, equals(3.99));
      expect(item.quantity, equals(2));
      expect(item.category, equals('General'));
      expect(item.unit, equals('item'));
      expect(item.notes, isEmpty);
    });

    test('should create ShoppingItem with optional parameters', () {
      final item = ShoppingItem(
        name: 'Chicken Breast',
        price: 8.99,
        quantity: 2,
        category: 'Meat',
        unit: 'lbs',
        notes: 'Free-range organic',
      );

      expect(item.name, equals('Chicken Breast'));
      expect(item.price, equals(8.99));
      expect(item.quantity, equals(2));
      expect(item.category, equals('Meat'));
      expect(item.unit, equals('lbs'));
      expect(item.notes, equals('Free-range organic'));
    });

    test('should calculate total price correctly', () {
      final item = ShoppingItem(
        name: 'Bananas',
        price: 1.29,
        quantity: 3,
      );

      expect(item.totalPrice, equals(3.87));
    });

    test('should create ShoppingItem from JSON', () {
      final json = {
        'id': 'test-id',
        'name': 'Test Item',
        'price': 5.99,
        'quantity': 1,
        'category': 'Test Category',
        'unit': 'piece',
        'notes': 'Test notes',
        'originalPrice': 6.99,
      };

      final item = ShoppingItem.fromJson(json);

      expect(item.id, equals('test-id'));
      expect(item.name, equals('Test Item'));
      expect(item.price, equals(5.99));
      expect(item.quantity, equals(1));
      expect(item.category, equals('Test Category'));
      expect(item.unit, equals('piece'));
      expect(item.notes, equals('Test notes'));
      expect(item.originalPrice, equals(6.99));
    });

    test('should convert ShoppingItem to JSON', () {
      final item = ShoppingItem(
        name: 'Test Item',
        price: 4.99,
        quantity: 2,
        category: 'Test',
        unit: 'kg',
        notes: 'Some notes',
      );

      final json = item.toJson();

      expect(json['name'], equals('Test Item'));
      expect(json['price'], equals(4.99));
      expect(json['quantity'], equals(2));
      expect(json['category'], equals('Test'));
      expect(json['unit'], equals('kg'));
      expect(json['notes'], equals('Some notes'));
      expect(json['originalPrice'], equals(4.99));
      expect(json['totalPrice'], equals(9.98));
    });

    test('should create copy with updated values', () {
      final original = ShoppingItem(
        name: 'Original',
        price: 1.99,
        quantity: 1,
      );

      final updated = original.copyWith(
        name: 'Updated',
        quantity: 3,
        category: 'New Category',
      );

      expect(updated.name, equals('Updated'));
      expect(updated.price, equals(original.price));
      expect(updated.quantity, equals(3));
      expect(updated.category, equals('New Category'));
    });

    test('should handle original price correctly', () {
      final itemWithOriginalPrice = ShoppingItem(
        name: 'Discounted Item',
        price: 7.99,
        quantity: 1,
        originalPrice: 9.99,
      );

      final itemWithoutOriginalPrice = ShoppingItem(
        name: 'Regular Item',
        price: 5.99,
        quantity: 1,
      );

      expect(itemWithOriginalPrice.originalPrice, equals(9.99));
      expect(itemWithOriginalPrice.hasDiscount, isTrue);
      expect(itemWithOriginalPrice.discountAmount, equals(2.00));
      expect(itemWithOriginalPrice.discountPercentage, closeTo(20.02, 0.01));

      expect(itemWithoutOriginalPrice.originalPrice, equals(5.99));
      expect(itemWithoutOriginalPrice.hasDiscount, isFalse);
      expect(itemWithoutOriginalPrice.discountAmount, equals(0.0));
      expect(itemWithoutOriginalPrice.discountPercentage, equals(0.0));
    });

    test('should handle equality based on id', () {
      final item1 = ShoppingItem(
        id: 'same-id',
        name: 'Item 1',
        price: 1.99,
        quantity: 1,
      );

      final item2 = ShoppingItem(
        id: 'same-id',
        name: 'Item 2',
        price: 2.99,
        quantity: 2,
      );

      final item3 = ShoppingItem(
        id: 'different-id',
        name: 'Item 1',
        price: 1.99,
        quantity: 1,
      );

      expect(item1, equals(item2));
      expect(item1.hashCode, equals(item2.hashCode));
      expect(item1, isNot(equals(item3)));
    });

    test('should format display price correctly', () {
      final simpleItem = ShoppingItem(
        name: 'Simple',
        price: 5.99,
        quantity: 1,
      );

      final discountedItem = ShoppingItem(
        name: 'Discounted',
        price: 7.99,
        quantity: 1,
        originalPrice: 9.99,
      );

      expect(simpleItem.displayPrice, equals('\$5.99'));
      expect(discountedItem.displayPrice, equals('\$7.99 (was \$9.99)'));
    });

    test('should format unit display correctly', () {
      final itemWithUnit = ShoppingItem(
        name: 'Apples',
        price: 2.99,
        quantity: 3,
        unit: 'lbs',
      );

      final itemWithoutUnit = ShoppingItem(
        name: 'Bread',
        price: 3.99,
        quantity: 1,
      );

      expect(itemWithUnit.unitDisplay, equals('3 lbs'));
      expect(itemWithoutUnit.unitDisplay, equals('1'));
    });

    test('should check if item is on sale', () {
      final regularItem = ShoppingItem(
        name: 'Regular',
        price: 4.99,
        quantity: 1,
      );

      final saleItem = ShoppingItem(
        name: 'Sale',
        price: 3.99,
        quantity: 1,
        originalPrice: 5.99,
      );

      expect(regularItem.isOnSale, isFalse);
      expect(saleItem.isOnSale, isTrue);
    });

    test('should validate item data', () {
      expect(() => ShoppingItem(name: '', price: 1.99, quantity: 1),
          throwsAssertionError);
      expect(() => ShoppingItem(name: 'Test', price: -1.99, quantity: 1),
          throwsAssertionError);
      expect(() => ShoppingItem(name: 'Test', price: 1.99, quantity: 0),
          throwsAssertionError);
    });
  });
}
