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
          appBar: AppBar(
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
          extendBodyBehindAppBar: true,
          body: AnimatedBackground(
            child: SafeArea(
              child: const ChatInterface(),
            ),
          ),

        );
      },
    );
  }
  

  

}