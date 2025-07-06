import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/models/shopping_item.dart';

void main() {
  group('PastOrder', () {
    late PastOrder pastOrder;
    late DateTime testDate;
    late List<ShoppingItem> testItems;

    setUp(() {
      testDate = DateTime(2025, 1, 1);
      testItems = [
        ShoppingItem(name: 'Chicken breast', price: 8.99, quantity: 2),
        ShoppingItem(name: 'Broccoli', price: 3.99, quantity: 1),
        ShoppingItem(name: 'Rice', price: 4.99, quantity: 1),
      ];
      
      pastOrder = PastOrder(
        id: 'order_1',
        date: testDate,
        store: 'Whole Foods',
        items: testItems,
        totalAmount: 26.96,
        status: 'Delivered',
      );
    });

    test('should create PastOrder with all properties', () {
      expect(pastOrder.id, equals('order_1'));
      expect(pastOrder.date, equals(testDate));
      expect(pastOrder.store, equals('Whole Foods'));
      expect(pastOrder.items, hasLength(3));
      expect(pastOrder.totalAmount, equals(26.96));
      expect(pastOrder.status, equals('Delivered'));
    });

    test('should contain expected items', () {
      expect(pastOrder.items, hasLength(3));
      expect(pastOrder.items[0].name, equals('Chicken breast'));
      expect(pastOrder.items[1].name, equals('Broccoli'));
      expect(pastOrder.items[2].name, equals('Rice'));
    });

    test('should calculate total from items', () {
      final calculatedTotal = pastOrder.items.fold<double>(
        0.0,
        (sum, item) => sum + (item.price * item.quantity),
      );
      expect(calculatedTotal, equals(26.96));
    });

    test('should support different order statuses', () {
      final pendingOrder = PastOrder(
        id: 'order_2',
        date: testDate,
        store: 'Costco',
        items: testItems,
        totalAmount: 26.96,
        status: 'Pending',
      );

      expect(pendingOrder.status, equals('Pending'));
    });
  });
}
