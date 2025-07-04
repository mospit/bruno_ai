class AppConstants {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const String websocketUrl = 'ws://localhost:8000/ws';
  
  // Environment
  static const bool isProduction = bool.fromEnvironment('dart.vm.product');
  static const String environment = isProduction ? 'production' : 'development';
  
  // App Information
  static const String appName = 'Bruno AI';
  static const String appVersion = '1.0.0';
  static const String appBuildNumber = '1';
  
  // Storage Keys
  static const String userIdKey = 'user_id';
  static const String userPreferencesKey = 'user_preferences';
  static const String chatHistoryKey = 'chat_history';
  static const String familySizeKey = 'family_size';
  static const String budgetKey = 'budget';
  static const String dietaryRestrictionsKey = 'dietary_restrictions';
  static const String preferredStoreKey = 'preferred_store';
  static const String deliveryTimeKey = 'delivery_time';
  static const String notificationSettingsKey = 'notification_settings';
  static const String themeKey = 'theme_mode';
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double borderRadius = 12.0;
  static const double cardElevation = 2.0;
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration normalAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
  
  // Chat Constants
  static const int maxMessageLength = 1000;
  static const int maxChatHistory = 100;
  static const Duration typingIndicatorDelay = Duration(seconds: 1);
  static const Duration brunoResponseDelay = Duration(seconds: 2);
  
  // Shopping Constants
  static const int maxShoppingItems = 50;
  static const double minItemPrice = 0.01;
  static const double maxItemPrice = 999.99;
  static const int maxItemQuantity = 20;
  
  // Validation
  static const int minFamilySize = 1;
  static const int maxFamilySize = 20;
  static const double minBudget = 10.0;
  static const double maxBudget = 10000.0;
  
  // Error Messages
  static const String networkErrorMessage = 'Please check your internet connection and try again.';
  static const String serverErrorMessage = 'Something went wrong. Please try again later.';
  static const String validationErrorMessage = 'Please check your input and try again.';
  static const String genericErrorMessage = 'An unexpected error occurred. Please try again.';
  
  // Success Messages
  static const String mealPlanCreatedMessage = 'Meal plan created successfully!';
  static const String shoppingListCreatedMessage = 'Shopping list created successfully!';
  static const String preferencesUpdatedMessage = 'Preferences updated successfully!';
  
  // Bruno Personality Constants
  static const List<String> brunoGreetings = [
    'Hey there! Bruno here, ready to help ya plan some amazing meals! 🐻',
    'Hi! It\'s Bruno, your friendly neighborhood budget bear! 🐻✨',
    'Hey! Bruno here with shopping superpowers! What can I do for ya? 🛒',
  ];
  
  static const List<String> brunoCelebrations = [
    'Bada-bing! Look at those savings! 🎉',
    'That\'s what I\'m talkin\' about! 💰',
    'Ya just saved some serious dough! 🐻',
    'Look at you go! Bruno\'s proud! ⭐',
  ];
  
  static const List<String> brunoEncouragement = [
    'Don\'t worry, I got ya back! 🐻',
    'Trust me on this one! 💪',
    'We\'re gonna make this work! ✨',
    'Bruno knows the way! 🗽',
  ];
  
  // Dietary Restrictions Options
  static const List<String> commonDietaryRestrictions = [
    'Vegetarian',
    'Vegan',
    'Gluten-Free',
    'Dairy-Free',
    'Nut-Free',
    'Low-Carb',
    'Keto',
    'Paleo',
    'Mediterranean',
    'Diabetic-Friendly',
    'Low-Sodium',
    'Heart-Healthy',
  ];
  
  // Store Options
  static const List<String> supportedStores = [
    'Whole Foods',
    'Safeway',
    'Kroger',
    'Target',
    'Walmart',
    'Costco',
    'Trader Joe\'s',
    'Sprouts',
  ];
  
  // Delivery Time Options
  static const List<String> deliveryTimeOptions = [
    'ASAP (1-2 hours)',
    'Today (3-5 hours)',
    'Tomorrow morning',
    'Tomorrow afternoon',
    'This weekend',
    'Next week',
  ];
  
  // Meal Categories
  static const List<String> mealCategories = [
    'Breakfast',
    'Lunch',
    'Dinner',
    'Snacks',
    'Desserts',
    'Beverages',
  ];
  
  // Cuisine Types
  static const List<String> cuisineTypes = [
    'American',
    'Italian',
    'Mexican',
    'Asian',
    'Mediterranean',
    'Indian',
    'Thai',
    'French',
    'Spanish',
    'Greek',
  ];
  
  // Analytics Events
  static const String eventAppOpened = 'app_opened';
  static const String eventMessageSent = 'message_sent';
  static const String eventMealPlanCreated = 'meal_plan_created';
  static const String eventShoppingListCreated = 'shopping_list_created';
  static const String eventInstacartCartCreated = 'instacart_cart_created';
  static const String eventPreferencesUpdated = 'preferences_updated';
  static const String eventErrorOccurred = 'error_occurred';
  
  // Notification Channels
  static const String mealPlanNotificationChannel = 'meal_plan_notifications';
  static const String dealsNotificationChannel = 'deals_notifications';
  static const String reminderNotificationChannel = 'reminder_notifications';
  
  // External URLs
  static const String instacartBaseUrl = 'https://www.instacart.com';
  static const String supportEmail = 'support@brunoai.app';
  static const String privacyPolicyUrl = 'https://brunoai.app/privacy';
  static const String termsOfServiceUrl = 'https://brunoai.app/terms';
  static const String feedbackUrl = 'https://brunoai.app/feedback';
}

enum AppTheme {
  light,
  dark,
  system,
}

enum MessageType {
  text,
  mealPlan,
  shoppingList,
  suggestion,
  error,
}

enum LoadingState {
  idle,
  loading,
  success,
  error,
}

enum NotificationType {
  mealPlan,
  deals,
  reminder,
  system,
}
