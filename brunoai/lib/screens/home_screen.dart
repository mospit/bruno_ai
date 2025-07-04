import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/chat_interface.dart';
import '../widgets/shopping_cart.dart';
import '../widgets/animated_background.dart';
import '../widgets/liquid_glass_container.dart';
import 'settings_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          backgroundColor: Colors.transparent,
          appBar: PreferredSize(
            preferredSize: const Size.fromHeight(kToolbarHeight + 40), // Much taller for extended gradient
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 15.0, sigmaY: 15.0),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.98),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.96),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.93),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.89),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.84),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.78),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.71),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.63),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.54),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.44),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.34),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.25),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.17),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.11),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.06),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.03),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.01),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.005),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 1.0],
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.only(top: 20.0), // More padding for taller AppBar
                    child: AppBar(
                      backgroundColor: Colors.transparent,
                      elevation: 0,
                      title: Text(
                        'Bruno AI',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                      actions: [
                        IconButton(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const SettingsScreen(),
                              ),
                            );
                          },
                          icon: Icon(
                            Icons.settings_rounded,
                            color: Theme.of(context).primaryColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          extendBodyBehindAppBar: true,
          body: AnimatedBackground(
            child: Column(
              children: [
                // Extended fade area to blend with AppBar
                Container(
                  height: 40, // Match AppBar extension
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.005),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.002),
                        Theme.of(context).scaffoldBackgroundColor.withOpacity(0.001),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.3, 0.7, 1.0],
                    ),
                  ),
                ),
                Expanded(
                  child: SafeArea(
                    top: false, // Don't add top safe area since we handle it manually
                    child: const ChatInterface(),
                  ),
                ),
              ],
            ),
          ),

        );
      },
    );
  }
  

  

}