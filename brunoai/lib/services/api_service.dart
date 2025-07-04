import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import '../models/chat_message.dart';
import '../models/shopping_item.dart';
import '../utils/app_constants.dart' as constants;

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;
    
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

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Add authentication header if available
        final token = _getAuthToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        _handleDioError(error);
        handler.next(error);
      },
    ));

    _isInitialized = true;
  }

  String? _getAuthToken() {
    // TODO: Implement token storage and retrieval
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

  // Bruno AI Chat API
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

      final response = await _dio.post('/chat', data: {
        'user_id': userId ?? 'anonymous_user',
        'message': message,
        'context': context ?? {},
        'budget_limit': budgetLimit,
        'family_size': familySize,
        'dietary_restrictions': dietaryRestrictions ?? [],
        'zip_code': zipCode,
        'preferred_stores': preferredStores ?? [],
      });

      if (response.statusCode == 200) {
        // Extract the primary response from Bruno AI server
        final responseData = response.data;
        final brunoMessage = ChatMessage(
          text: responseData['primary_response'] ?? 'I apologize, but I had trouble processing that request.',
          isFromUser: false,
          timestamp: DateTime.parse(responseData['timestamp'] ?? DateTime.now().toIso8601String()),
          hasShoppingAction: responseData['shopping_list'] != null,
          type: responseData['shopping_list'] != null ? MessageType.shoppingList : MessageType.text,
          metadata: {
            'request_id': responseData['request_id'],
            'agent_responses': responseData['agent_responses'],
            'budget_info': responseData['budget_info'],
            'recommendations': responseData['recommendations'],
            'shopping_list': responseData['shopping_list'],
            'total_cost': responseData['total_cost'],
            'processing_time_ms': responseData['processing_time_ms'],
          },
        );
        return ApiResponse.success(brunoMessage);
      } else {
        return ApiResponse.error('Failed to get response from Bruno');
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
          return 'Server error (${statusCode}). Please try again.';
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
