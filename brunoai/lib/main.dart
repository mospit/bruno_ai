import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/home_screen.dart';
import 'providers/bruno_provider.dart';
import 'theme/liquid_glass_theme.dart';

void main() {
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
        theme: LiquidGlassTheme.lightTheme,
        darkTheme: LiquidGlassTheme.darkTheme,
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
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