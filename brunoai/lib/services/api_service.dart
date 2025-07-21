import 'dart:io';
import 'package:dio/dio.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/chat_message.dart';
import '../models/shopping_item.dart';
import '../models/pantry_item.dart';
import '../utils/app_constants.dart' as constants;
import 'retry_interceptor.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  bool _isInitialized = false;
  String? _authToken;
  String? _refreshToken;
  SharedPreferences? _prefs;

  Future<void> initialize() async {
    if (_isInitialized) return;
    
    // Initialize SharedPreferences
    _prefs = await SharedPreferences.getInstance();
    _loadTokensFromStorage();
    
    _dio = Dio(BaseOptions(
      baseUrl: constants.AppConstants.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptors for logging and error handling
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: false,
      ));
    }

    // Add authentication interceptor
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add authentication header if available
        final token = await _getAuthToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        // Handle 401 errors with token refresh
        if (error.response?.statusCode == 401 && _refreshToken != null) {
          try {
            final newToken = await _refreshAuthToken();
            if (newToken != null) {
              // Retry the request with new token
              final opts = error.requestOptions;
              opts.headers['Authorization'] = 'Bearer $newToken';
              final response = await _dio.fetch(opts);
              handler.resolve(response);
              return;
            }
          } catch (e) {
            // Refresh failed, clear tokens
            await clearAuth();
          }
        }
        _handleDioError(error);
        handler.next(error);
      },
    ));

    // Add retry interceptor
    _dio.interceptors.add(RetryInterceptor(
      dio: _dio,
      retries: 3,
      retryDelays: const [
        Duration(seconds: 1),
        Duration(seconds: 2),
        Duration(seconds: 3),
      ],
    ));

    _isInitialized = true;
  }

  Future<String?> _getAuthToken() async {
    return _authToken;
  }

  void _loadTokensFromStorage() {
    _authToken = _prefs?.getString('auth_token');
    _refreshToken = _prefs?.getString('refresh_token');
  }

  Future<void> _saveTokensToStorage() async {
    if (_authToken != null) {
      await _prefs?.setString('auth_token', _authToken!);
    }
    if (_refreshToken != null) {
      await _prefs?.setString('refresh_token', _refreshToken!);
    }
  }

  Future<String?> _refreshAuthToken() async {
    if (_refreshToken == null) return null;
    
    try {
      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': _refreshToken,
      });
      
      if (response.statusCode == 200) {
        _authToken = response.data['access_token'];
        _refreshToken = response.data['refresh_token'] ?? _refreshToken;
        await _saveTokensToStorage();
        return _authToken;
      }
    } catch (e) {
      if (kDebugMode) print('Token refresh failed: $e');
    }
    return null;
  }

  Future<bool> _checkConnectivity() async {
    final connectivityResult = await Connectivity().checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }

  void _handleDioError(DioException error) {
    if (kDebugMode) {
      print('API Error: ${error.type} - ${error.message}');
      if (error.response != null) {
        print('Response data: ${error.response?.data}');
        print('Response status: ${error.response?.statusCode}');
      }
    }
  }

  // Bruno AI Chat API - V2 Agent System
  Future<ApiResponse<ChatMessage>> sendMessageToBruno({
    required String message,
    String? userId,
    Map<String, dynamic>? context,
    double? budgetLimit,
    int? familySize,
    List<String>? dietaryRestrictions,
    String? zipCode,
    List<String>? preferredStores,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      // Send task to Bruno Master Agent through A2A Gateway
      final taskData = {
        'action': 'process_user_message',
        'context': {
          'user_id': userId ?? 'anonymous_user',
          'message': message,
          'user_context': context ?? {},
          'budget_limit': budgetLimit,
          'family_size': familySize,
          'dietary_restrictions': dietaryRestrictions ?? [],
          'zip_code': zipCode,
          'preferred_stores': preferredStores ?? [],
          'timestamp': DateTime.now().toIso8601String(),
        },
        'message': message,
        'priority': 'normal',
        'timeout': 30
      };

      final response = await _dio.post(
        '/agents/${constants.AppConstants.brunoMasterAgent}/task',
        data: taskData,
      );

      if (response.statusCode == 200) {
        final responseData = response.data;
        
        // Extract response from Bruno Master Agent
        final brunoMessage = ChatMessage(
          text: responseData['result']?['bruno_response'] ?? 
                responseData['response'] ?? 
                responseData['primary_response'] ?? 
                'I apologize, but I had trouble processing that request.',
          isFromUser: false,
          timestamp: DateTime.parse(responseData['timestamp'] ?? DateTime.now().toIso8601String()),
          hasShoppingAction: responseData['shopping_list'] != null || 
                           responseData['actions']?.containsKey('shopping_list') == true,
          type: responseData['shopping_list'] != null ? MessageType.shoppingList : MessageType.text,
          metadata: {
            'request_id': responseData['request_id'],
            'agent_responses': responseData['agent_responses'],
            'budget_info': responseData['budget_info'],
            'recommendations': responseData['recommendations'],
            'shopping_list': responseData['shopping_list'] ?? responseData['actions']?['shopping_list'],
            'total_cost': responseData['total_cost'],
            'processing_time_ms': responseData['processing_time_ms'],
            'actions': responseData['actions'],
            'agent_used': responseData['agent_used'],
          },
        );
        return ApiResponse.success(brunoMessage);
      } else {
        return ApiResponse.error('Failed to get response from Bruno Agent');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // Meal Planning API
  Future<ApiResponse<Map<String, dynamic>>> createMealPlan({
    required double budget,
    required int familySize,
    List<String> dietaryRestrictions = const [],
    String timeframe = 'week',
    Map<String, dynamic>? preferences,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/meal-plan', data: {
        'budget': budget,
        'family_size': familySize,
        'dietary_restrictions': dietaryRestrictions,
        'timeframe': timeframe,
        'preferences': preferences ?? {},
      });

      if (response.statusCode == 200) {
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Failed to create meal plan');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // Shopping List API
  Future<ApiResponse<List<ShoppingItem>>> createShoppingList({
    required List<String> recipes,
    required String location,
    Map<String, dynamic>? preferences,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/shopping-list', data: {
        'recipes': recipes,
        'location': location,
        'preferences': preferences ?? {},
      });

      if (response.statusCode == 200) {
        final items = (response.data['items'] as List)
            .map((item) => ShoppingItem.fromJson(item))
            .toList();
        return ApiResponse.success(items);
      } else {
        return ApiResponse.error('Failed to create shopping list');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // Instacart Integration API
  Future<ApiResponse<Map<String, dynamic>>> getInstacartDeals({
    required String location,
    List<String> products = const [],
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.get('/instacart/deals', queryParameters: {
        'location': location,
        'products': products.join(','),
      });

      if (response.statusCode == 200) {
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Failed to get Instacart deals');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<String>> createInstacartCart({
    required List<ShoppingItem> items,
    required String location,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/instacart/cart', data: {
        'items': items.map((item) => item.toJson()).toList(),
        'location': location,
      });

      if (response.statusCode == 200) {
        return ApiResponse.success(response.data['cart_url']);
      } else {
        return ApiResponse.error('Failed to create Instacart cart');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // User Preferences API
  Future<ApiResponse<Map<String, dynamic>>> saveUserPreferences({
    required String userId,
    required Map<String, dynamic> preferences,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.put('/user/$userId/preferences', data: preferences);

      if (response.statusCode == 200) {
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Failed to save preferences');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> getUserPreferences(String userId) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.get('/user/$userId/preferences');

      if (response.statusCode == 200) {
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Failed to load preferences');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // Authentication API
  Future<ApiResponse<Map<String, dynamic>>> login({
    required String email,
    required String password,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });

      if (response.statusCode == 200) {
        _authToken = response.data['access_token'];
        _refreshToken = response.data['refresh_token'];
        await _saveTokensToStorage();
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Login failed');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> signup({
    required String email,
    required String password,
    required String name,
  }) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/auth/signup', data: {
        'email': email,
        'password': password,
        'name': name,
      });

      if (response.statusCode == 201) {
        _authToken = response.data['access_token'];
        _refreshToken = response.data['refresh_token'];
        await _saveTokensToStorage();
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Signup failed');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<void> clearAuth() async {
    _authToken = null;
    _refreshToken = null;
    await _prefs?.remove('auth_token');
    await _prefs?.remove('refresh_token');
  }

  bool get isAuthenticated => _authToken != null;

  // Pantry API
  Future<ApiResponse<List<PantryItem>>> getPantryItems() async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.get('/pantry');

      if (response.statusCode == 200) {
        final items = (response.data['items'] as List)
            .map((item) => PantryItem.fromJson(item))
            .toList();
        return ApiResponse.success(items);
      } else {
        return ApiResponse.error('Failed to load pantry items');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<PantryItem>> addPantryItem(PantryItem item) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/pantry', data: item.toJson());

      if (response.statusCode == 201) {
        return ApiResponse.success(PantryItem.fromJson(response.data));
      } else {
        return ApiResponse.error('Failed to add pantry item');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<PantryItem>> updatePantryItem(String id, PantryItem item) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.put('/pantry/$id', data: item.toJson());

      if (response.statusCode == 200) {
        return ApiResponse.success(PantryItem.fromJson(response.data));
      } else {
        return ApiResponse.error('Failed to update pantry item');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<void>> deletePantryItem(String id) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.delete('/pantry/$id');

      if (response.statusCode == 204) {
        return ApiResponse.success(null);
      } else {
        return ApiResponse.error('Failed to delete pantry item');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  // Meal Plan API
  Future<ApiResponse<List<Map<String, dynamic>>>> getMealPlans() async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.get('/meal-plans');

      if (response.statusCode == 200) {
        final plans = (response.data['plans'] as List)
            .cast<Map<String, dynamic>>();
        return ApiResponse.success(plans);
      } else {
        return ApiResponse.error('Failed to load meal plans');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> saveMealPlan(Map<String, dynamic> mealPlan) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.post('/meal-plans', data: mealPlan);

      if (response.statusCode == 201) {
        return ApiResponse.success(response.data);
      } else {
        return ApiResponse.error('Failed to save meal plan');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  Future<ApiResponse<void>> deleteMealPlan(String id) async {
    try {
      if (!await _checkConnectivity()) {
        return ApiResponse.error('No internet connection');
      }

      final response = await _dio.delete('/meal-plans/$id');

      if (response.statusCode == 204) {
        return ApiResponse.success(null);
      } else {
        return ApiResponse.error('Failed to delete meal plan');
      }
    } on DioException catch (e) {
      return ApiResponse.error(_getDioErrorMessage(e));
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e');
    }
  }

  String _getDioErrorMessage(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Connection timeout. Please check your internet connection.';
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        if (statusCode == 400) {
          return 'Bad request. Please check your input.';
        } else if (statusCode == 401) {
          return 'Authentication failed. Please try again.';
        } else if (statusCode == 403) {
          return 'Access denied.';
        } else if (statusCode == 404) {
          return 'Service not found.';
        } else if (statusCode == 500) {
          return 'Server error. Please try again later.';
        } else {
          return 'Server error ($statusCode). Please try again.';
        }
      case DioExceptionType.cancel:
        return 'Request was cancelled.';
      case DioExceptionType.connectionError:
        return 'Connection error. Please check your internet connection.';
      case DioExceptionType.unknown:
        if (error.error is SocketException) {
          return 'No internet connection.';
        }
        return 'An unexpected error occurred.';
      default:
        return 'An unexpected error occurred.';
    }
  }
}

class ApiResponse<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResponse.success(this.data)
      : error = null,
        isSuccess = true;

  ApiResponse.error(this.error)
      : data = null,
        isSuccess = false;

  bool get hasError => error != null;
}
