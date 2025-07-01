import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_constants.dart';

class AppProvider extends ChangeNotifier {
  // App state
  bool _isInitialized = false;
  AppTheme _themeMode = AppTheme.system;
  bool _notificationsEnabled = true;
  String _selectedLanguage = 'en';
  
  // User state
  String? _userId;
  bool _isFirstLaunch = true;
  
  // Loading states
  bool _isLoading = false;
  String? _errorMessage;
  
  // Getters
  bool get isInitialized => _isInitialized;
  AppTheme get themeMode => _themeMode;
  bool get notificationsEnabled => _notificationsEnabled;
  String get selectedLanguage => _selectedLanguage;
  String? get userId => _userId;
  bool get isFirstLaunch => _isFirstLaunch;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  
  // Theme helpers
  bool get isDarkMode => _themeMode == AppTheme.dark;
  bool get isLightMode => _themeMode == AppTheme.light;
  bool get isSystemMode => _themeMode == AppTheme.system;
  
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    setLoading(true);
    
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Load user preferences
      _userId = prefs.getString(AppConstants.userIdKey);
      _isFirstLaunch = prefs.getBool('is_first_launch') ?? true;
      _notificationsEnabled = prefs.getBool(AppConstants.notificationSettingsKey) ?? true;
      _selectedLanguage = prefs.getString('language') ?? 'en';
      
      // Load theme mode
      final themeIndex = prefs.getInt(AppConstants.themeKey) ?? AppTheme.system.index;
      _themeMode = AppTheme.values[themeIndex];
      
      // Generate user ID if needed
      if (_userId == null) {
        _userId = _generateUserId();
        await prefs.setString(AppConstants.userIdKey, _userId!);
      }
      
      _isInitialized = true;
      setLoading(false);
    } catch (e) {
      setError('Failed to initialize app: $e');
    }
  }
  
  Future<void> setThemeMode(AppTheme theme) async {
    _themeMode = theme;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(AppConstants.themeKey, theme.index);
  }
  
  Future<void> setNotificationsEnabled(bool enabled) async {
    _notificationsEnabled = enabled;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(AppConstants.notificationSettingsKey, enabled);
  }
  
  Future<void> setLanguage(String languageCode) async {
    _selectedLanguage = languageCode;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('language', languageCode);
  }
  
  Future<void> completeFirstLaunch() async {
    _isFirstLaunch = false;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('is_first_launch', false);
  }
  
  void setLoading(bool loading) {
    _isLoading = loading;
    if (loading) {
      _errorMessage = null;
    }
    notifyListeners();
  }
  
  void setError(String? error) {
    _errorMessage = error;
    _isLoading = false;
    notifyListeners();
  }
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  String _generateUserId() {
    return 'user_${DateTime.now().millisecondsSinceEpoch}';
  }
  
  // App lifecycle methods
  void onAppResumed() {
    // Handle app resume
  }
  
  void onAppPaused() {
    // Handle app pause
  }
  
  void onAppDetached() {
    // Handle app detached
  }
  
  Future<void> reset() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    
    _isInitialized = false;
    _themeMode = AppTheme.system;
    _notificationsEnabled = true;
    _selectedLanguage = 'en';
    _userId = null;
    _isFirstLaunch = true;
    _isLoading = false;
    _errorMessage = null;
    
    notifyListeners();
  }
}
