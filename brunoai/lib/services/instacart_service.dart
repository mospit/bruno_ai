import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/shopping_item.dart';
import '../utils/app_constants.dart' as constants;

class InstacartService {
  static final InstacartService _instance = InstacartService._internal();
  factory InstacartService() => _instance;
  InstacartService._internal();

  late Dio _dio;
  bool _isInitialized = false;
  bool _mockMode = false;
  SharedPreferences? _prefs;
  
  // Cache configuration
  static const String _cacheKeyPrefix = 'instacart_cache_';
  static const Duration _cacheExpiry = Duration(hours: 1);
  
  // Rate limiting
  DateTime? _lastRequestTime;
  static const Duration _rateLimitDelay = Duration(milliseconds: 500);
  int _dailyRequestCount = 0;
  DateTime? _lastResetDate;
  static const int _maxDailyRequests = 1000;

  Future<void> initialize({bool mockMode = false}) async {
    if (_isInitialized) return;

    _mockMode = mockMode;
    _prefs = await SharedPreferences.getInstance();
    _loadDailyRequestCount();

    if (!_mockMode) {
      _dio = Dio(BaseOptions(
        baseUrl: '${constants.AppConstants.apiBaseUrl}/api/instacart',
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'User-Agent': 'BrunoAI/1.0.0',
        },
      ));

      if (kDebugMode) {
        _dio.interceptors.add(LogInterceptor(
          requestBody: true,
          responseBody: true,
          requestHeader: true,
          responseHeader: false,
        ));
      }
    }

    _isInitialized = true;
  }

  void _loadDailyRequestCount() {
    final today = DateTime.now();
    final lastReset = _prefs?.getString('instacart_last_reset');
    
    if (lastReset != null) {
      final lastResetDate = DateTime.parse(lastReset);
      if (today.difference(lastResetDate).inDays >= 1) {
        // Reset daily count
        _dailyRequestCount = 0;
        _lastResetDate = today;
        _saveDailyRequestCount();
      } else {
        _dailyRequestCount = _prefs?.getInt('instacart_daily_requests') ?? 0;
        _lastResetDate = lastResetDate;
      }
    } else {
      _dailyRequestCount = 0;
      _lastResetDate = today;
      _saveDailyRequestCount();
    }
  }

  void _saveDailyRequestCount() {
    _prefs?.setInt('instacart_daily_requests', _dailyRequestCount);
    _prefs?.setString('instacart_last_reset', _lastResetDate!.toIso8601String());
  }

  Future<void> _enforceRateLimit() async {
    if (_lastRequestTime != null) {
      final timeSinceLastRequest = DateTime.now().difference(_lastRequestTime!);
      if (timeSinceLastRequest < _rateLimitDelay) {
        await Future.delayed(_rateLimitDelay - timeSinceLastRequest);
      }
    }
    _lastRequestTime = DateTime.now();
  }

  bool _checkDailyLimit() {
    _loadDailyRequestCount();
    return _dailyRequestCount < _maxDailyRequests;
  }

  void _incrementRequestCount() {
    _dailyRequestCount++;
    _saveDailyRequestCount();
  }

  // Product search by SKU or keyword
  Future<InstacartResponse<List<ShoppingItem>>> searchProducts({
    required String query,
    String? sku,
    String? category,
    String? store,
    int maxResults = 20,
    bool forceRefresh = false,
  }) async {
    try {
      if (!_isInitialized) {
        await initialize();
      }

      // Check cache first
      final cacheKey = _generateCacheKey('search', {
        'query': query,
        'sku': sku ?? '',
        'category': category ?? '',
        'store': store ?? '',
        'max_results': maxResults.toString(),
      });

      if (!forceRefresh) {
        final cachedResult = await _getCachedData<List<ShoppingItem>>(cacheKey);
        if (cachedResult != null) {
          return InstacartResponse.success(cachedResult);
        }
      }

      if (_mockMode) {
        return _getMockSearchResults(query, maxResults);
      }

      // Check rate limits
      if (!_checkDailyLimit()) {
        return InstacartResponse.error('Daily API quota exceeded. Using cached data or mock mode.');
      }

      await _enforceRateLimit();
      _incrementRequestCount();

      final response = await _dio.post('/search', data: {
        'query': query.trim(),
        'sku': sku,
        'category': category,
        'store': store,
        'max_results': maxResults,
        'sort_by': 'relevance',
        'include_pricing': true,
        'include_availability': true,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        final products = (data['products'] as List)
            .map((item) => ShoppingItem.fromJson(item))
            .toList();

        // Cache the results
        await _cacheData(cacheKey, products);

        return InstacartResponse.success(products);
      } else {
        return InstacartResponse.error('Failed to search products: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('Instacart API Error: ${e.message}');
      }
      
      // Fall back to cached data if available
      final cacheKey = _generateCacheKey('search', {
        'query': query,
        'sku': sku ?? '',
        'category': category ?? '',
        'store': store ?? '',
        'max_results': maxResults.toString(),
      });
      
      final cachedResult = await _getCachedData<List<ShoppingItem>>(cacheKey);
      if (cachedResult != null) {
        return InstacartResponse.success(cachedResult, fromCache: true);
      }
      
      // Fall back to mock data
      return _getMockSearchResults(query, maxResults);
    } catch (e) {
      if (kDebugMode) {
        print('Unexpected error in searchProducts: $e');
      }
      return InstacartResponse.error('Unexpected error occurred: $e');
    }
  }

  // Get product prices and availability
  Future<InstacartResponse<Map<String, dynamic>>> getProductInfo({
    required String productId,
    String? store,
    bool forceRefresh = false,
  }) async {
    try {
      if (!_isInitialized) {
        await initialize();
      }

      final cacheKey = _generateCacheKey('product_info', {
        'product_id': productId,
        'store': store ?? '',
      });

      if (!forceRefresh) {
        final cachedResult = await _getCachedData<Map<String, dynamic>>(cacheKey);
        if (cachedResult != null) {
          return InstacartResponse.success(cachedResult);
        }
      }

      if (_mockMode) {
        return _getMockProductInfo(productId);
      }

      if (!_checkDailyLimit()) {
        return InstacartResponse.error('Daily API quota exceeded.');
      }

      await _enforceRateLimit();
      _incrementRequestCount();

      final response = await _dio.get('/product/$productId', queryParameters: {
        'store': store,
        'include_pricing': true,
        'include_availability': true,
        'include_alternatives': true,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        await _cacheData(cacheKey, data);
        return InstacartResponse.success(data);
      } else {
        return InstacartResponse.error('Failed to get product info: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      // Fall back to cached data or mock
      final cacheKey = _generateCacheKey('product_info', {
        'product_id': productId,
        'store': store ?? '',
      });
      
      final cachedResult = await _getCachedData<Map<String, dynamic>>(cacheKey);
      if (cachedResult != null) {
        return InstacartResponse.success(cachedResult, fromCache: true);
      }
      
      return _getMockProductInfo(productId);
    } catch (e) {
      return InstacartResponse.error('Unexpected error: $e');
    }
  }

  // Generate deep link to Instacart with shopping list
  Future<InstacartResponse<String>> createCartDeepLink({
    required List<ShoppingItem> items,
    String? store,
  }) async {
    try {
      if (_mockMode) {
        return InstacartResponse.success('https://instacart.com/cart/mock-${DateTime.now().millisecondsSinceEpoch}');
      }

      if (!_checkDailyLimit()) {
        // Return a generic Instacart URL as fallback
        final itemNames = items.take(3).map((item) => item.name).join(', ');
        final fallbackUrl = '${constants.AppConstants.instacartBaseUrl}/store/search?query=${Uri.encodeComponent(itemNames)}';
        return InstacartResponse.success(fallbackUrl);
      }

      await _enforceRateLimit();
      _incrementRequestCount();

      final response = await _dio.post('/create-cart', data: {
        'items': items.map((item) => {
          'name': item.name,
          'quantity': item.quantity,
          'unit': item.unit,
          'category': item.category,
          'notes': item.notes,
        }).toList(),
        'store': store,
        'redirect_url': 'brunoai://cart-created',
      });

      if (response.statusCode == 200) {
        return InstacartResponse.success(response.data['deep_link']);
      } else {
        // Return fallback URL
        final itemNames = items.take(3).map((item) => item.name).join(', ');
        final fallbackUrl = '${constants.AppConstants.instacartBaseUrl}/store/search?query=${Uri.encodeComponent(itemNames)}';
        return InstacartResponse.success(fallbackUrl);
      }
    } catch (e) {
      // Return fallback URL for graceful degradation
      final itemNames = items.take(3).map((item) => item.name).join(', ');
      final fallbackUrl = '${constants.AppConstants.instacartBaseUrl}/store/search?query=${Uri.encodeComponent(itemNames)}';
      return InstacartResponse.success(fallbackUrl);
    }
  }

  // Cache management
  String _generateCacheKey(String operation, Map<String, String> params) {
    final paramString = params.entries
        .map((e) => '${e.key}=${e.value}')
        .join('&');
    return '${_cacheKeyPrefix}${operation}_${paramString.hashCode}';
  }

  Future<void> _cacheData(String key, dynamic data) async {
    final cacheEntry = {
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    };
    await _prefs?.setString(key, jsonEncode(cacheEntry));
  }

  Future<T?> _getCachedData<T>(String key) async {
    final cachedString = _prefs?.getString(key);
    if (cachedString == null) return null;

    try {
      final cacheEntry = jsonDecode(cachedString);
      final timestamp = DateTime.parse(cacheEntry['timestamp']);
      
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        await _prefs?.remove(key);
        return null;
      }

      return cacheEntry['data'] as T;
    } catch (e) {
      await _prefs?.remove(key);
      return null;
    }
  }

  Future<void> clearCache() async {
    final keys = _prefs?.getKeys() ?? <String>{};
    for (final key in keys) {
      if (key.startsWith(_cacheKeyPrefix)) {
        await _prefs?.remove(key);
      }
    }
  }

  // Mock data for development
  InstacartResponse<List<ShoppingItem>> _getMockSearchResults(String query, int maxResults) {
    final mockProducts = _generateMockProducts(query);
    final results = mockProducts.take(maxResults).toList();
    
    // Simulate network delay
    return InstacartResponse.success(results, fromCache: false);
  }

  InstacartResponse<Map<String, dynamic>> _getMockProductInfo(String productId) {
    return InstacartResponse.success({
      'product_id': productId,
      'name': 'Mock Product $productId',
      'price': 5.99 + (productId.hashCode % 20),
      'original_price': 7.99 + (productId.hashCode % 20),
      'is_available': true,
      'store': 'Mock Store',
      'category': 'Mock Category',
      'unit': 'item',
      'brand': 'Mock Brand',
      'image_url': null,
      'description': 'Mock product for development',
      'alternatives': [],
      'last_updated': DateTime.now().toIso8601String(),
    });
  }

  List<ShoppingItem> _generateMockProducts(String query) {
    final baseProducts = [
      {'name': 'Organic Chicken Breast', 'price': 12.99, 'category': 'Meat', 'unit': 'lb', 'brand': 'Perdue'},
      {'name': 'Fresh Broccoli', 'price': 3.49, 'category': 'Produce', 'unit': 'bunch', 'brand': null},
      {'name': 'Brown Rice', 'price': 4.99, 'category': 'Grains', 'unit': 'bag', 'brand': 'Uncle Ben\'s'},
      {'name': 'Greek Yogurt', 'price': 5.99, 'category': 'Dairy', 'unit': 'container', 'brand': 'Chobani'},
      {'name': 'Whole Wheat Bread', 'price': 3.99, 'category': 'Bakery', 'unit': 'loaf', 'brand': 'Dave\'s Killer'},
      {'name': 'Bananas', 'price': 1.99, 'category': 'Produce', 'unit': 'bunch', 'brand': null},
      {'name': 'Salmon Fillet', 'price': 18.99, 'category': 'Seafood', 'unit': 'lb', 'brand': null},
      {'name': 'Olive Oil', 'price': 8.99, 'category': 'Pantry', 'unit': 'bottle', 'brand': 'Bertolli'},
      {'name': 'Pasta', 'price': 2.49, 'category': 'Pantry', 'unit': 'box', 'brand': 'Barilla'},
      {'name': 'Tomato Sauce', 'price': 1.99, 'category': 'Pantry', 'unit': 'jar', 'brand': 'Ragu'},
    ];

    final queryLower = query.toLowerCase();
    final filteredProducts = baseProducts
        .where((product) => 
            product['name'].toString().toLowerCase().contains(queryLower) ||
            product['category'].toString().toLowerCase().contains(queryLower))
        .toList();

    // If no matches, return some random products
    final productsToUse = filteredProducts.isNotEmpty ? filteredProducts : baseProducts;

    return productsToUse.map((product) => ShoppingItem(
      name: product['name'] as String,
      price: (product['price'] as num).toDouble(),
      quantity: 1,
      category: product['category'] as String,
      unit: product['unit'] as String,
      brandName: product['brand'] as String?,
      isOnSale: DateTime.now().millisecondsSinceEpoch % 3 == 0,
      originalPrice: DateTime.now().millisecondsSinceEpoch % 3 == 0 
          ? (product['price'] as num).toDouble() + 2.0
          : null,
      store: 'Mock Store',
    )).toList();
  }

  // Getters
  bool get isInitialized => _isInitialized;
  bool get isMockMode => _mockMode;
  bool get hasRemainingQuota => _checkDailyLimit();
  int get remainingRequests => (_maxDailyRequests - _dailyRequestCount).clamp(0, _maxDailyRequests);

  void toggleMockMode() {
    _mockMode = !_mockMode;
  }
}

class InstacartResponse<T> {
  final T? data;
  final String? error;
  final bool isSuccess;
  final bool fromCache;

  InstacartResponse.success(this.data, {this.fromCache = false})
      : error = null,
        isSuccess = true;

  InstacartResponse.error(this.error, {this.fromCache = false})
      : data = null,
        isSuccess = false;

  bool get hasError => error != null;
}
