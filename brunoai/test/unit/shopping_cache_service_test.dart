import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:io';
import '../../lib/services/shopping_cache_service.dart';
import '../../lib/models/shopping_item.dart';

void main() {
  group('ShoppingCacheService', () {
    late ShoppingCacheService cacheService;
    late Directory testDirectory;

    setUpAll(() async {
      // Create a temporary directory for testing
      testDirectory = await Directory.systemTemp.createTemp('shopping_cache_test');
      Hive.init(testDirectory.path);
    });

    setUp(() async {
      cacheService = ShoppingCacheService();
      await cacheService.initialize();
    });

    tearDown(() async {
      await cacheService.clearAllCache();
      cacheService.dispose();
    });

    tearDownAll(() async {
      await Hive.close();
      if (testDirectory.existsSync()) {
        testDirectory.deleteSync(recursive: true);
      }
    });

    test('should initialize successfully', () async {
      expect(cacheService.isInitialized, true);
    });

    test('should cache and retrieve shopping list', () async {
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

      const listId = 'test_list_1';
      
      // Cache the shopping list
      await cacheService.cacheShoppingList(
        listId: listId,
        items: items,
        store: 'Test Store',
      );

      // Retrieve the cached list
      final cachedItems = await cacheService.getCachedShoppingList(listId);

      expect(cachedItems, isNotNull);
      expect(cachedItems!.length, equals(2));
      expect(cachedItems[0].name, equals('Test Item 1'));
      expect(cachedItems[0].price, equals(5.99));
      expect(cachedItems[1].name, equals('Test Item 2'));
      expect(cachedItems[1].price, equals(3.49));
    });

    test('should cache and retrieve search results', () async {
      final searchResults = [
        ShoppingItem(
          name: 'Chicken Breast',
          price: 12.99,
          quantity: 1,
          category: 'Meat',
          unit: 'lb',
        ),
        ShoppingItem(
          name: 'Chicken Thighs',
          price: 8.99,
          quantity: 1,
          category: 'Meat',
          unit: 'lb',
        ),
      ];

      const query = 'chicken';
      const category = 'Meat';
      const store = 'Whole Foods';

      // Cache search results
      await cacheService.cacheSearchResults(
        searchQuery: query,
        results: searchResults,
        category: category,
        store: store,
      );

      // Retrieve cached search results
      final cachedResults = await cacheService.getCachedSearchResults(
        searchQuery: query,
        category: category,
        store: store,
      );

      expect(cachedResults, isNotNull);
      expect(cachedResults!.length, equals(2));
      expect(cachedResults[0].name, equals('Chicken Breast'));
      expect(cachedResults[1].name, equals('Chicken Thighs'));
    });

    test('should cache and retrieve individual product', () async {
      final product = ShoppingItem(
        name: 'Premium Salmon',
        price: 24.99,
        quantity: 1,
        category: 'Seafood',
        unit: 'lb',
      );

      // Cache the product
      await cacheService.cacheProduct(product);

      // Retrieve the cached product
      final cachedProduct = await cacheService.getCachedProduct(product.id);

      expect(cachedProduct, isNotNull);
      expect(cachedProduct!.name, equals('Premium Salmon'));
      expect(cachedProduct.price, equals(24.99));
      expect(cachedProduct.category, equals('Seafood'));
    });

    test('should return null for non-existent cached data', () async {
      final result = await cacheService.getCachedShoppingList('non_existent_id');
      expect(result, isNull);

      final searchResult = await cacheService.getCachedSearchResults(
        searchQuery: 'non_existent_query',
      );
      expect(searchResult, isNull);

      final productResult = await cacheService.getCachedProduct('non_existent_product');
      expect(productResult, isNull);
    });

    test('should get all cached shopping lists', () async {
      final items1 = [
        ShoppingItem(name: 'Item 1', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];
      final items2 = [
        ShoppingItem(name: 'Item 2', price: 3.49, quantity: 2, category: 'Test', unit: 'item'),
      ];

      await cacheService.cacheShoppingList(
        listId: 'list_1',
        items: items1,
        store: 'Store 1',
      );

      await cacheService.cacheShoppingList(
        listId: 'list_2',
        items: items2,
        store: 'Store 2',
      );

      final allLists = await cacheService.getAllCachedShoppingLists();

      expect(allLists.length, equals(2));
      expect(allLists.any((list) => list['id'] == 'list_1'), true);
      expect(allLists.any((list) => list['id'] == 'list_2'), true);
    });

    test('should delete specific cached shopping list', () async {
      final items = [
        ShoppingItem(name: 'Test Item', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];

      const listId = 'delete_test_list';

      // Cache the list
      await cacheService.cacheShoppingList(
        listId: listId,
        items: items,
      );

      // Verify it exists
      var cachedList = await cacheService.getCachedShoppingList(listId);
      expect(cachedList, isNotNull);

      // Delete the list
      await cacheService.deleteCachedShoppingList(listId);

      // Verify it's deleted
      cachedList = await cacheService.getCachedShoppingList(listId);
      expect(cachedList, isNull);
    });

    test('should clear all cache', () async {
      // Cache some data
      final items = [
        ShoppingItem(name: 'Test Item', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];

      await cacheService.cacheShoppingList(
        listId: 'test_list',
        items: items,
      );

      await cacheService.cacheSearchResults(
        searchQuery: 'test_query',
        results: items,
      );

      await cacheService.cacheProduct(items.first);

      // Clear all cache
      await cacheService.clearAllCache();

      // Verify all data is cleared
      final cachedList = await cacheService.getCachedShoppingList('test_list');
      expect(cachedList, isNull);

      final cachedSearch = await cacheService.getCachedSearchResults(searchQuery: 'test_query');
      expect(cachedSearch, isNull);

      final cachedProduct = await cacheService.getCachedProduct(items.first.id);
      expect(cachedProduct, isNull);
    });

    test('should get cache statistics', () async {
      final items = [
        ShoppingItem(name: 'Test Item', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];

      // Cache some data
      await cacheService.cacheShoppingList(listId: 'list_1', items: items);
      await cacheService.cacheSearchResults(searchQuery: 'query_1', results: items);
      await cacheService.cacheProduct(items.first);

      final stats = await cacheService.getCacheStatistics();

      expect(stats['shopping_lists_count'], equals(1));
      expect(stats['search_results_count'], equals(1));
      expect(stats['products_count'], equals(1));
      expect(stats['total_cache_size'], greaterThan(0));
    });

    test('should check if cached data exists', () async {
      final items = [
        ShoppingItem(name: 'Test Item', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];

      const listId = 'exists_test_list';
      const query = 'exists_test_query';
      final productId = items.first.id;

      // Before caching
      var hasListData = await cacheService.hasCachedDataFor(listId: listId);
      var hasSearchData = await cacheService.hasCachedDataFor(searchQuery: query);
      var hasProductData = await cacheService.hasCachedDataFor(productId: productId);

      expect(hasListData, false);
      expect(hasSearchData, false);
      expect(hasProductData, false);

      // Cache data
      await cacheService.cacheShoppingList(listId: listId, items: items);
      await cacheService.cacheSearchResults(searchQuery: query, results: items);
      await cacheService.cacheProduct(items.first);

      // After caching
      hasListData = await cacheService.hasCachedDataFor(listId: listId);
      hasSearchData = await cacheService.hasCachedDataFor(searchQuery: query);
      hasProductData = await cacheService.hasCachedDataFor(productId: productId);

      expect(hasListData, true);
      expect(hasSearchData, true);
      expect(hasProductData, true);
    });

    test('should handle cache key generation consistently', () async {
      final items = [
        ShoppingItem(name: 'Test Item', price: 5.99, quantity: 1, category: 'Test', unit: 'item'),
      ];

      // Cache with same parameters should override
      await cacheService.cacheSearchResults(
        searchQuery: 'test query',
        results: items,
        category: 'Test Cat',
        store: 'Test Store',
      );

      // Update with different results but same parameters
      final updatedItems = [
        ShoppingItem(name: 'Updated Item', price: 9.99, quantity: 2, category: 'Test', unit: 'item'),
      ];

      await cacheService.cacheSearchResults(
        searchQuery: 'test query',
        results: updatedItems,
        category: 'Test Cat',
        store: 'Test Store',
      );

      // Should get the updated results
      final cachedResults = await cacheService.getCachedSearchResults(
        searchQuery: 'test query',
        category: 'Test Cat',
        store: 'Test Store',
      );

      expect(cachedResults, isNotNull);
      expect(cachedResults!.length, equals(1));
      expect(cachedResults[0].name, equals('Updated Item'));
      expect(cachedResults[0].price, equals(9.99));
    });
  });
}
