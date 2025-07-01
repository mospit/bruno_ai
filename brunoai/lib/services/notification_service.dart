import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import '../utils/app_constants.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  late FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin;
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    _flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

    // Initialize notification settings for Android
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    // Initialize notification settings for iOS
    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const InitializationSettings initializationSettings =
        InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );

    await _flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Create notification channels for Android
    if (!kIsWeb) {
      await _createNotificationChannels();
    }

    _isInitialized = true;
  }

  Future<void> _createNotificationChannels() async {
    // Meal plan notifications
    const AndroidNotificationChannel mealPlanChannel =
        AndroidNotificationChannel(
      AppConstants.mealPlanNotificationChannel,
      'Meal Plan Notifications',
      description: 'Notifications about your meal plans and recipes',
      importance: Importance.high,
      enableVibration: true,
    );

    // Deals notifications
    const AndroidNotificationChannel dealsChannel = AndroidNotificationChannel(
      AppConstants.dealsNotificationChannel,
      'Deal Alerts',
      description: 'Notifications about special deals and savings',
      importance: Importance.defaultImportance,
      enableVibration: false,
    );

    // Reminder notifications
    const AndroidNotificationChannel reminderChannel =
        AndroidNotificationChannel(
      AppConstants.reminderNotificationChannel,
      'Reminders',
      description: 'Shopping and meal preparation reminders',
      importance: Importance.high,
      enableVibration: true,
    );

    final plugin = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();

    if (plugin != null) {
      await plugin.createNotificationChannel(mealPlanChannel);
      await plugin.createNotificationChannel(dealsChannel);
      await plugin.createNotificationChannel(reminderChannel);
    }
  }

  void _onNotificationTapped(NotificationResponse response) {
    if (kDebugMode) {
      print('Notification tapped: ${response.payload}');
    }
    // Handle notification tap - could navigate to specific screens
    // This would typically be handled by a navigation service
  }

  Future<bool> requestPermissions() async {
    final plugin = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();

    if (plugin != null) {
      return await plugin.requestNotificationsPermission() ?? false;
    }

    final iosPlugin = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
            IOSFlutterLocalNotificationsPlugin>();

    if (iosPlugin != null) {
      return await iosPlugin.requestPermissions(
            alert: true,
            badge: true,
            sound: true,
          ) ??
          false;
    }

    return false;
  }

  Future<void> showMealPlanNotification({
    required String title,
    required String body,
    Map<String, dynamic>? payload,
  }) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      AppConstants.mealPlanNotificationChannel,
      'Meal Plan Notifications',
      channelDescription: 'Notifications about your meal plans and recipes',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      largeIcon: DrawableResourceAndroidBitmap('@mipmap/ic_launcher'),
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _flutterLocalNotificationsPlugin.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload != null ? _encodePayload(payload) : null,
    );
  }

  Future<void> showDealsNotification({
    required String title,
    required String body,
    Map<String, dynamic>? payload,
  }) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      AppConstants.dealsNotificationChannel,
      'Deal Alerts',
      channelDescription: 'Notifications about special deals and savings',
      importance: Importance.defaultImportance,
      priority: Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: false,
    );

    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _flutterLocalNotificationsPlugin.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload != null ? _encodePayload(payload) : null,
    );
  }

  Future<void> scheduleShoppingReminder({
    required DateTime scheduledTime,
    required String title,
    required String body,
    Map<String, dynamic>? payload,
  }) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      AppConstants.reminderNotificationChannel,
      'Reminders',
      channelDescription: 'Shopping and meal preparation reminders',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _flutterLocalNotificationsPlugin.zonedSchedule(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      tz.TZDateTime.from(scheduledTime, tz.local),
      details,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: payload != null ? _encodePayload(payload) : null,
    );
  }

  Future<void> cancelAllNotifications() async {
    await _flutterLocalNotificationsPlugin.cancelAll();
  }

  Future<void> cancelNotification(int id) async {
    await _flutterLocalNotificationsPlugin.cancel(id);
  }

  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _flutterLocalNotificationsPlugin.pendingNotificationRequests();
  }

  String _encodePayload(Map<String, dynamic> payload) {
    try {
      return Uri.encodeComponent(payload.toString());
    } catch (e) {
      if (kDebugMode) {
        print('Error encoding notification payload: $e');
      }
      return '';
    }
  }

  // Bruno-specific notification helpers
  Future<void> notifyMealPlanReady({
    required String mealPlanName,
    required double totalCost,
    required double savings,
  }) async {
    await showMealPlanNotification(
      title: '🐻 Meal Plan Ready!',
      body: 'Bruno created "$mealPlanName" for \$${totalCost.toStringAsFixed(2)} - saving you \$${savings.toStringAsFixed(2)}!',
      payload: {
        'type': 'meal_plan_ready',
        'meal_plan_name': mealPlanName,
        'total_cost': totalCost,
        'savings': savings,
      },
    );
  }

  Future<void> notifyGreatDeal({
    required String itemName,
    required double originalPrice,
    required double salePrice,
    required String store,
  }) async {
    final savings = originalPrice - salePrice;
    final savingsPercent = ((savings / originalPrice) * 100).round();
    
    await showDealsNotification(
      title: '🎉 Great Deal Alert!',
      body: '$itemName is $savingsPercent% off at $store! Save \$${savings.toStringAsFixed(2)}',
      payload: {
        'type': 'deal_alert',
        'item_name': itemName,
        'store': store,
        'savings': savings,
      },
    );
  }

  Future<void> scheduleWeeklyMealPlanReminder() async {
    final nextSunday = _getNextSunday();
    
    await scheduleShoppingReminder(
      scheduledTime: nextSunday,
      title: '🐻 Time to Plan Next Week!',
      body: 'Hey! Bruno here. Ready to plan some amazing meals for next week?',
      payload: {
        'type': 'weekly_reminder',
        'action': 'plan_meals',
      },
    );
  }

  DateTime _getNextSunday() {
    final now = DateTime.now();
    final daysUntilSunday = 7 - now.weekday;
    return DateTime(
      now.year,
      now.month,
      now.day + daysUntilSunday,
      10, // 10 AM
      0,
    );
  }
}
