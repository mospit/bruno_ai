import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../lib/services/instacart_service.dart';
import '../../lib/models/shopping_item.dart';

void main() {
  group('InstacartService', () {
    late InstacartService instacartService;

    setUp(() async {
      // Initialize shared preferences for testing
      SharedPreferences.setMockInitialValues({});
      instacartService = InstacartService();
    });

    tearDown(() {
      // Clean up
    });

    test('should initialize in mock mode', () async {
      await instacartService.initialize(mockMode: true);
      
      expect(instacartService.isInitialized, true);
      expect(instacartService.isMockMode, true);
    });

    test('should search products in mock mode', () async {
      await instacartService.initialize(mockMode: true);
      
      final response = await instacartService.searchProducts(
        query: 'chicken',
        maxResults: 5,
      );
      
      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!.length, greaterThan(0));
      expect(response.data!.length, lessThanOrEqualTo(5));
      
      // Check if results contain chicken-related products
      final hasChickenProduct = response.data!.any(
        (item) => item.name.toLowerCase().contains('chicken')
      );
      expect(hasChickenProduct, true);
    });

    test('should handle empty search query', () async {
      await instacartService.initialize(mockMode: true);
      
      final response = await instacartService.searchProducts(
        query: '',
        maxResults: 5,
      );
      
      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      // Should return some mock products even with empty query
      expect(response.data!.length, greaterThan(0));
    });

    test('should search with category filter', () async {
      await instacartService.initialize(mockMode: true);
      
      final response = await instacartService.searchProducts(
        query: 'organic',
        category: 'Produce',
        maxResults: 10,
      );
      
      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!.length, greaterThan(0));
    });

    test('should get product info in mock mode', () async {
      await instacartService.initialize(mockMode: true);
      
      final response = await instacartService.getProductInfo(
        productId: 'test_product_123',
      );
      
      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!['product_id'], equals('test_product_123'));
      expect(response.data!['name'], contains('Mock Product'));
      expect(response.data!['price'], isA<num>());
      expect(response.data!['is_available'], true);
    });

    test('should create cart deep link in mock mode', () async {
      await instacartService.initialize(mockMode: true);
      
      final items = [
        ShoppingItem(
          name: 'Test Item 1',
          price: 5.99,
          quantity: 2,
          category: 'Test',
          unit: 'item',
        ),
        ShoppingItem(
          name: 'Test Item 2', 
          price: 3.49,
          quantity: 1,
          category: 'Test',
          unit: 'item',
        ),
      ];
      
      final response = await instacartService.createCartDeepLink(
        items: items,
        store: 'Test Store',
      );
      
      expect(response.isSuccess, true);
      expect(response.data, isNotNull);
      expect(response.data!, startsWith('https://instacart.com'));
    });

    test('should track API quota correctly', () async {
      await instacartService.initialize(mockMode: false);
      
      expect(instacartService.hasRemainingQuota, true);
      expect(instacartService.remainingRequests, greaterThan(0));
    });

    test('should handle rate limiting', () async {
      await instacartService.initialize(mockMode: true);
      
      // Make multiple requests quickly
      final futures = List.generate(3, (index) => 
        instacartService.searchProducts(query: 'test_$index')
      );
      
      final responses = await Future.wait(futures);
      
      // All should succeed in mock mode
      for (final response in responses) {
        expect(response.isSuccess, true);
      }
    });

    test('should toggle mock mode', () async {
      await instacartService.initialize(mockMode: true);
      
      expect(instacartService.isMockMode, true);
      
      instacartService.toggleMockMode();
      expect(instacartService.isMockMode, false);
      
      instacartService.toggleMockMode();
      expect(instacartService.isMockMode, true);
    });

    test('should generate varied mock products', () async {
      await instacartService.initialize(mockMode: true);
      
      final response1 = await instacartService.searchProducts(query: 'chicken');
      final response2 = await instacartService.searchProducts(query: 'pasta');
      
      expect(response1.isSuccess, true);
      expect(response2.isSuccess, true);
      
      // Should have different categories for different searches
      final hasChicken = response1.data!.any((item) => item.name.toLowerCase().contains('chicken'));
      final hasPasta = response2.data!.any((item) => item.name.toLowerCase().contains('pasta'));
      
      expect(hasChicken, true);
      expect(hasPasta, true);
    });

    test('should handle product pricing correctly', () async {
      await instacartService.initialize(mockMode: true);
      
      final response = await instacartService.searchProducts(query: 'milk');
      
      expect(response.isSuccess, true);
      expect(response.data!.isNotEmpty, true);
      
      final product = response.data!.first;
      expect(product.price, greaterThan(0));
      expect(product.displayPrice, startsWith('\$'));
      expect(product.totalPrice, equals(product.price * product.quantity));
    });
  });
}
