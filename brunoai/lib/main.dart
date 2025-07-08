import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'providers/bruno_provider.dart';
import 'screens/home_screen.dart';
import 'screens/pantry_screen.dart';
import 'theme/modern_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // TODO: Initialize services when Firebase is configured
  // await ApiService().initialize();
  // await NotificationService().initialize();
  // await AnalyticsService().initialize();
  
  runApp(const BrunoAIApp());
}

class BrunoAIApp extends StatelessWidget {
  const BrunoAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => BrunoProvider()),
      ],
      child: MaterialApp(
        title: 'Bruno AI',
        debugShowCheckedModeBanner: false,
        theme: ModernTheme.lightTheme,
        darkTheme: ModernTheme.darkTheme,
        themeMode: ThemeMode.system,
// Add route for pantry screen
        home: const HomeScreen(),
        routes: {
          '/pantry': (context) => PantryScreen(),
        },
        builder: (context, child) {
          return AnnotatedRegion<SystemUiOverlayStyle>(
            value: SystemUiOverlayStyle(
              statusBarColor: Colors.transparent,
              statusBarIconBrightness: Theme.of(context).brightness == Brightness.dark 
                  ? Brightness.light 
                  : Brightness.dark,
              systemNavigationBarColor: Colors.transparent,
              systemNavigationBarIconBrightness: Theme.of(context).brightness == Brightness.dark 
                  ? Brightness.light 
                  : Brightness.dark,
            ),
            child: child!,
          );
        },
      ),
    );
  }
}