import 'package:flutter/foundation.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import '../utils/app_constants.dart';

class AnalyticsService {
  static final AnalyticsService _instance = AnalyticsService._internal();
  factory AnalyticsService() => _instance;
  AnalyticsService._internal();

  late FirebaseAnalytics _analytics;
  late FirebaseAnalyticsObserver _observer;
  bool _isInitialized = false;

  FirebaseAnalyticsObserver get observer => _observer;

  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      _analytics = FirebaseAnalytics.instance;
      _observer = FirebaseAnalyticsObserver(analytics: _analytics);
      
      // Set analytics collection enabled based on environment
      await _analytics.setAnalyticsCollectionEnabled(AppConstants.isProduction);
      
      _isInitialized = true;
      
      if (kDebugMode) {
        print('Analytics service initialized successfully');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to initialize analytics: $e');
      }
    }
  }

  // App lifecycle events
  Future<void> logAppOpened() async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventAppOpened,
        parameters: {
          'timestamp': DateTime.now().toIso8601String(),
          'platform': 'flutter',
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging app opened: $e');
      }
    }
  }

  // Chat events
  Future<void> logMessageSent({
    required String messageType,
    required int messageLength,
    bool hasBudget = false,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventMessageSent,
        parameters: {
          'message_type': messageType,
          'message_length': messageLength,
          'has_budget': hasBudget,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging message sent: $e');
      }
    }
  }

  // Meal planning events
  Future<void> logMealPlanCreated({
    required double budget,
    required int familySize,
    required int recipesCount,
    List<String> dietaryRestrictions = const [],
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventMealPlanCreated,
        parameters: {
          'budget': budget,
          'family_size': familySize,
          'recipes_count': recipesCount,
          'dietary_restrictions_count': dietaryRestrictions.length,
          'has_dietary_restrictions': dietaryRestrictions.isNotEmpty,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging meal plan created: $e');
      }
    }
  }

  // Shopping events
  Future<void> logShoppingListCreated({
    required int itemsCount,
    required double totalCost,
    required String store,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventShoppingListCreated,
        parameters: {
          'items_count': itemsCount,
          'total_cost': totalCost,
          'store': store,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging shopping list created: $e');
      }
    }
  }

  Future<void> logInstacartCartCreated({
    required double totalCost,
    required int itemsCount,
    required double estimatedSavings,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventInstacartCartCreated,
        parameters: {
          'total_cost': totalCost,
          'items_count': itemsCount,
          'estimated_savings': estimatedSavings,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging Instacart cart created: $e');
      }
    }
  }

  // User preference events
  Future<void> logPreferencesUpdated({
    required Map<String, dynamic> preferences,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventPreferencesUpdated,
        parameters: {
          'family_size': preferences['family_size'],
          'budget_range': preferences['budget'],
          'dietary_restrictions_count': (preferences['dietary_restrictions'] as List?)?.length ?? 0,
          'preferred_store': preferences['preferred_store'],
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging preferences updated: $e');
      }
    }
  }

  // Error tracking
  Future<void> logError({
    required String errorType,
    required String errorMessage,
    String? context,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: AppConstants.eventErrorOccurred,
        parameters: {
          'error_type': errorType,
          'error_message': errorMessage.length > 100 
              ? errorMessage.substring(0, 100) 
              : errorMessage,
          'context': context ?? 'unknown',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging error event: $e');
      }
    }
  }

  // User properties
  Future<void> setUserProperties({
    String? userId,
    int? familySize,
    String? preferredStore,
    List<String>? dietaryRestrictions,
  }) async {
    if (!_isInitialized) return;
    
    try {
      if (userId != null) {
        await _analytics.setUserId(id: userId);
      }
      
      if (familySize != null) {
        await _analytics.setUserProperty(
          name: 'family_size',
          value: familySize.toString(),
        );
      }
      
      if (preferredStore != null) {
        await _analytics.setUserProperty(
          name: 'preferred_store',
          value: preferredStore,
        );
      }
      
      if (dietaryRestrictions != null) {
        await _analytics.setUserProperty(
          name: 'dietary_restrictions_count',
          value: dietaryRestrictions.length.toString(),
        );
        
        await _analytics.setUserProperty(
          name: 'has_dietary_restrictions',
          value: dietaryRestrictions.isNotEmpty.toString(),
        );
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error setting user properties: $e');
      }
    }
  }

  // Screen tracking
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logScreenView(
        screenName: screenName,
        screenClass: screenClass ?? screenName,
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging screen view: $e');
      }
    }
  }

  // Custom events for Bruno-specific interactions
  Future<void> logBrunoInteraction({
    required String interactionType,
    String? userMessage,
    String? brunoResponse,
    bool wasHelpful = false,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: 'bruno_interaction',
        parameters: {
          'interaction_type': interactionType,
          'user_message_length': userMessage?.length ?? 0,
          'bruno_response_length': brunoResponse?.length ?? 0,
          'was_helpful': wasHelpful,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging Bruno interaction: $e');
      }
    }
  }

  Future<void> logDealFound({
    required String itemName,
    required double originalPrice,
    required double salePrice,
    required String store,
  }) async {
    if (!_isInitialized) return;
    
    try {
      final savings = originalPrice - salePrice;
      final savingsPercent = ((savings / originalPrice) * 100);
      
      await _analytics.logEvent(
        name: 'deal_found',
        parameters: {
          'item_name': itemName,
          'original_price': originalPrice,
          'sale_price': salePrice,
          'savings_amount': savings,
          'savings_percent': savingsPercent,
          'store': store,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging deal found: $e');
      }
    }
  }

  // Performance tracking
  Future<void> logPerformanceMetric({
    required String metricName,
    required int value,
    String? unit,
  }) async {
    if (!_isInitialized) return;
    
    try {
      await _analytics.logEvent(
        name: 'performance_metric',
        parameters: {
          'metric_name': metricName,
          'value': value,
          'unit': unit ?? 'ms',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
    } catch (e) {
      if (kDebugMode) {
        print('Error logging performance metric: $e');
      }
    }
  }
}
