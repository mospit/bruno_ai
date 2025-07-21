import 'dart:convert';
import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter/foundation.dart';
import '../models/shopping_item.dart';

class ShoppingCacheService {
  static final ShoppingCacheService _instance = ShoppingCacheService._internal();
  factory ShoppingCacheService() => _instance;
  ShoppingCacheService._internal();

  static const String _boxName = 'shopping_cache';
  static const String _shoppingListsKey = 'shopping_lists';
  static const String _searchCacheKey = 'search_cache';
  static const String _productsKey = 'cached_products';
  static const String _metadataKey = 'cache_metadata';
  
  Box? _cacheBox;
  bool _isInitialized = false;

  // Cache expiry settings
  static const Duration _defaultCacheExpiry = Duration(hours: 6);
  static const Duration _searchCacheExpiry = Duration(minutes: 30);
  static const Duration _productCacheExpiry = Duration(hours: 2);

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      await Hive.initFlutter();
      _cacheBox = await Hive.openBox(_boxName);
      _isInitialized = true;
      
      // Clean expired cache on initialization
      await _cleanExpiredCache();
      
      if (kDebugMode) {
        print('Shopping cache service initialized');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to initialize shopping cache: $e');
      }
    }
  }

  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await initialize();
    }
  }

  // Cache shopping lists
  Future<void> cacheShoppingList({
    required String listId,
    required List<ShoppingItem> items,
    String? store,
    String? userId,
    Duration? expiry,
  }) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      final cacheData = {
        'id': listId,
        'items': items.map((item) => item.toJson()).toList(),
        'store': store,
        'user_id': userId,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'expiry_duration_ms': (expiry ?? _defaultCacheExpiry).inMilliseconds,
      };

      final existingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      existingLists[listId] = cacheData;
      
      await _cacheBox!.put(_shoppingListsKey, existingLists);
      
      if (kDebugMode) {
        print('Cached shopping list: $listId with ${items.length} items');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to cache shopping list: $e');
      }
    }
  }

  Future<List<ShoppingItem>?> getCachedShoppingList(String listId) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return null;

      final existingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      final listData = existingLists[listId] as Map<String, dynamic>?;
      
      if (listData == null) return null;
      
      // Check if expired
      final timestamp = listData['timestamp'] as int;
      final expiryDuration = Duration(milliseconds: listData['expiry_duration_ms'] as int);
      final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
      
      if (DateTime.now().isAfter(expiryTime)) {
        // Remove expired data
        existingLists.remove(listId);
        await _cacheBox!.put(_shoppingListsKey, existingLists);
        return null;
      }

      final itemsData = listData['items'] as List;
      final items = itemsData
          .map((itemJson) => ShoppingItem.fromJson(itemJson as Map<String, dynamic>))
          .toList();

      if (kDebugMode) {
        print('Retrieved cached shopping list: $listId with ${items.length} items');
      }

      return items;
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get cached shopping list: $e');
      }
      return null;
    }
  }

  // Cache search results
  Future<void> cacheSearchResults({
    required String searchQuery,
    required List<ShoppingItem> results,
    String? category,
    String? store,
  }) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      final searchKey = _generateSearchKey(searchQuery, category, store);
      final cacheData = {
        'query': searchQuery,
        'category': category,
        'store': store,
        'results': results.map((item) => item.toJson()).toList(),
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'expiry_duration_ms': _searchCacheExpiry.inMilliseconds,
      };

      final existingSearches = _getCachedData(_searchCacheKey) ?? <String, dynamic>{};
      existingSearches[searchKey] = cacheData;
      
      await _cacheBox!.put(_searchCacheKey, existingSearches);
      
      if (kDebugMode) {
        print('Cached search results for: $searchQuery (${results.length} items)');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to cache search results: $e');
      }
    }
  }

  Future<List<ShoppingItem>?> getCachedSearchResults({
    required String searchQuery,
    String? category,
    String? store,
  }) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return null;

      final searchKey = _generateSearchKey(searchQuery, category, store);
      final existingSearches = _getCachedData(_searchCacheKey) ?? <String, dynamic>{};
      final searchData = existingSearches[searchKey] as Map<String, dynamic>?;
      
      if (searchData == null) return null;
      
      // Check if expired
      final timestamp = searchData['timestamp'] as int;
      final expiryDuration = Duration(milliseconds: searchData['expiry_duration_ms'] as int);
      final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
      
      if (DateTime.now().isAfter(expiryTime)) {
        // Remove expired data
        existingSearches.remove(searchKey);
        await _cacheBox!.put(_searchCacheKey, existingSearches);
        return null;
      }

      final resultsData = searchData['results'] as List;
      final results = resultsData
          .map((itemJson) => ShoppingItem.fromJson(itemJson as Map<String, dynamic>))
          .toList();

      if (kDebugMode) {
        print('Retrieved cached search results for: $searchQuery (${results.length} items)');
      }

      return results;
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get cached search results: $e');
      }
      return null;
    }
  }

  // Cache individual products
  Future<void> cacheProduct(ShoppingItem product) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      final cacheData = {
        'product': product.toJson(),
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'expiry_duration_ms': _productCacheExpiry.inMilliseconds,
      };

      final existingProducts = _getCachedData(_productsKey) ?? <String, dynamic>{};
      existingProducts[product.id] = cacheData;
      
      await _cacheBox!.put(_productsKey, existingProducts);
    } catch (e) {
      if (kDebugMode) {
        print('Failed to cache product: $e');
      }
    }
  }

  Future<ShoppingItem?> getCachedProduct(String productId) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return null;

      final existingProducts = _getCachedData(_productsKey) ?? <String, dynamic>{};
      final productData = existingProducts[productId] as Map<String, dynamic>?;
      
      if (productData == null) return null;
      
      // Check if expired
      final timestamp = productData['timestamp'] as int;
      final expiryDuration = Duration(milliseconds: productData['expiry_duration_ms'] as int);
      final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
      
      if (DateTime.now().isAfter(expiryTime)) {
        // Remove expired data
        existingProducts.remove(productId);
        await _cacheBox!.put(_productsKey, existingProducts);
        return null;
      }

      return ShoppingItem.fromJson(productData['product'] as Map<String, dynamic>);
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get cached product: $e');
      }
      return null;
    }
  }

  // Get all cached shopping lists
  Future<List<Map<String, dynamic>>> getAllCachedShoppingLists() async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return [];

      final existingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      final validLists = <Map<String, dynamic>>[];

      for (final entry in existingLists.entries) {
        final listData = entry.value as Map<String, dynamic>;
        
        // Check if expired
        final timestamp = listData['timestamp'] as int;
        final expiryDuration = Duration(milliseconds: listData['expiry_duration_ms'] as int);
        final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
        
        if (!DateTime.now().isAfter(expiryTime)) {
          validLists.add({
            'id': entry.key,
            'store': listData['store'],
            'item_count': (listData['items'] as List).length,
            'created_at': DateTime.fromMillisecondsSinceEpoch(timestamp),
            'expires_at': expiryTime,
          });
        }
      }

      return validLists;
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get all cached shopping lists: $e');
      }
      return [];
    }
  }

  // Delete specific cached data
  Future<void> deleteCachedShoppingList(String listId) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      final existingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      existingLists.remove(listId);
      await _cacheBox!.put(_shoppingListsKey, existingLists);
      
      if (kDebugMode) {
        print('Deleted cached shopping list: $listId');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to delete cached shopping list: $e');
      }
    }
  }

  Future<void> clearAllCache() async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      await _cacheBox!.clear();
      
      if (kDebugMode) {
        print('Cleared all shopping cache');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to clear cache: $e');
      }
    }
  }

  Future<void> clearExpiredCache() async {
    await _cleanExpiredCache();
  }

  // Cache statistics
  Future<Map<String, dynamic>> getCacheStatistics() async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return {};

      final shoppingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      final searchResults = _getCachedData(_searchCacheKey) ?? <String, dynamic>{};
      final products = _getCachedData(_productsKey) ?? <String, dynamic>{};

      return {
        'shopping_lists_count': shoppingLists.length,
        'search_results_count': searchResults.length,
        'products_count': products.length,
        'total_cache_size': _cacheBox!.length,
        'last_cleanup': _getCachedData('${_metadataKey}_last_cleanup'),
      };
    } catch (e) {
      return {};
    }
  }

  // Helper methods
  String _generateSearchKey(String query, String? category, String? store) {
    return '${query}_${category ?? 'all'}_${store ?? 'all'}'.toLowerCase().replaceAll(' ', '_');
  }

  dynamic _getCachedData(String key) {
    try {
      return _cacheBox?.get(key);
    } catch (e) {
      return null;
    }
  }

  Future<void> _cleanExpiredCache() async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return;

      final now = DateTime.now();
      
      // Clean shopping lists
      final shoppingLists = _getCachedData(_shoppingListsKey) ?? <String, dynamic>{};
      final expiredListKeys = <String>[];
      
      shoppingLists.forEach((key, value) {
        final listData = value as Map<String, dynamic>;
        final timestamp = listData['timestamp'] as int;
        final expiryDuration = Duration(milliseconds: listData['expiry_duration_ms'] as int);
        final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
        
        if (now.isAfter(expiryTime)) {
          expiredListKeys.add(key);
        }
      });

      for (final key in expiredListKeys) {
        shoppingLists.remove(key);
      }
      if (expiredListKeys.isNotEmpty) {
        await _cacheBox!.put(_shoppingListsKey, shoppingLists);
      }

      // Clean search results
      final searchResults = _getCachedData(_searchCacheKey) ?? <String, dynamic>{};
      final expiredSearchKeys = <String>[];
      
      searchResults.forEach((key, value) {
        final searchData = value as Map<String, dynamic>;
        final timestamp = searchData['timestamp'] as int;
        final expiryDuration = Duration(milliseconds: searchData['expiry_duration_ms'] as int);
        final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
        
        if (now.isAfter(expiryTime)) {
          expiredSearchKeys.add(key);
        }
      });

      for (final key in expiredSearchKeys) {
        searchResults.remove(key);
      }
      if (expiredSearchKeys.isNotEmpty) {
        await _cacheBox!.put(_searchCacheKey, searchResults);
      }

      // Clean products
      final products = _getCachedData(_productsKey) ?? <String, dynamic>{};
      final expiredProductKeys = <String>[];
      
      products.forEach((key, value) {
        final productData = value as Map<String, dynamic>;
        final timestamp = productData['timestamp'] as int;
        final expiryDuration = Duration(milliseconds: productData['expiry_duration_ms'] as int);
        final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp).add(expiryDuration);
        
        if (now.isAfter(expiryTime)) {
          expiredProductKeys.add(key);
        }
      });

      for (final key in expiredProductKeys) {
        products.remove(key);
      }
      if (expiredProductKeys.isNotEmpty) {
        await _cacheBox!.put(_productsKey, products);
      }

      // Update cleanup metadata
      await _cacheBox!.put('${_metadataKey}_last_cleanup', now.millisecondsSinceEpoch);

      if (kDebugMode) {
        final totalExpired = expiredListKeys.length + expiredSearchKeys.length + expiredProductKeys.length;
        if (totalExpired > 0) {
          print('Cleaned $totalExpired expired cache entries');
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to clean expired cache: $e');
      }
    }
  }

  // Graceful degradation helpers
  Future<bool> hasCachedDataFor({
    String? listId,
    String? searchQuery,
    String? productId,
  }) async {
    try {
      await _ensureInitialized();
      if (_cacheBox == null) return false;

      if (listId != null) {
        return await getCachedShoppingList(listId) != null;
      } else if (searchQuery != null) {
        return await getCachedSearchResults(searchQuery: searchQuery) != null;
      } else if (productId != null) {
        return await getCachedProduct(productId) != null;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }

  bool get isInitialized => _isInitialized;

  void dispose() {
    _cacheBox?.close();
    _isInitialized = false;
  }
}
