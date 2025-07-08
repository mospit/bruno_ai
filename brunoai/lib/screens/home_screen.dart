import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/animated_background.dart';
import '../widgets/chat_interface.dart';
import '../widgets/shopping_cart.dart';
import '../widgets/smart_dashboard.dart';
import '../theme/app_colors.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isDashboardCollapsed = false;

  void _showShoppingCart(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(20),
            ),
          ),
          child: const ShoppingCart(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          backgroundColor: Colors.transparent,
          appBar: PreferredSize(
            preferredSize: const Size.fromHeight(kToolbarHeight),
            child: ClipRRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 5.0, sigmaY: 5.0),
                child: Container(
                  decoration: BoxDecoration(
                    color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.85),
                    border: Border(
                      bottom: BorderSide(
                        color: Theme.of(context).dividerColor.withOpacity(0.2),
                        width: 0.5,
                      ),
                    ),
                  ),
                  child: AppBar(
                    backgroundColor: Colors.transparent,
                    elevation: 0,
                    titleSpacing: 20,
                    title: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Theme.of(context).primaryColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            Icons.shopping_basket_rounded,
                            color: Theme.of(context).primaryColor,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Bruno AI',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.w600,
                            letterSpacing: -0.5,
                          ),
                        ),
                      ],
                    ),
                    actions: [
                      // Enhanced Shopping Cart Button
                      Container(
                        margin: const EdgeInsets.only(right: 4),
                        child: Stack(
                          clipBehavior: Clip.none,
                          children: [
                            Container(
                              decoration: BoxDecoration(
                                color: provider.shoppingList.isNotEmpty
                                    ? Theme.of(context).primaryColor.withOpacity(0.1)
                                    : AppColors.gray200.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: provider.shoppingList.isNotEmpty
                                      ? Theme.of(context).primaryColor.withOpacity(0.3)
                                      : AppColors.gray300.withOpacity(0.8),
                                  width: 1.5,
                                ),
                                boxShadow: [
                                  if (provider.shoppingList.isNotEmpty)
                                    BoxShadow(
                                      color: Theme.of(context).primaryColor.withOpacity(0.2),
                                      blurRadius: 8,
                                      offset: const Offset(0, 2),
                                    ),
                                ],
                              ),
                              child: Semantics(
                                button: true,
                                label: 'Shopping Cart',
                                child: IconButton(
                                  onPressed: () {
                                    HapticFeedback.lightImpact();
                                    _showShoppingCart(context);
                                  },
                                  icon: Icon(
                                    Icons.shopping_cart_rounded,
                                    color: provider.shoppingList.isNotEmpty 
                                        ? Theme.of(context).primaryColor
                                        : AppColors.gray600,
                                    size: 24,
                                  ),
                                  tooltip: 'Shopping Cart',
                                  splashRadius: 20,
                                ),
                              ),
                            ),
                            // Enhanced Cart badge
                            if (provider.shoppingList.isNotEmpty)
                              Positioned(
                                right: 4,
                                top: 4,
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [AppColors.error, AppColors.errorDark],
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                    ),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(
                                      color: AppColors.white,
                                      width: 2,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: AppColors.error.withOpacity(0.4),
                                        blurRadius: 8,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  constraints: const BoxConstraints(
                                    minWidth: 22,
                                    minHeight: 22,
                                  ),
                                  child: Text(
                                    '${provider.shoppingList.length}',
                                    style: const TextStyle(
                                      color: AppColors.white,
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Settings Button
                      Semantics(
                        button: true,
                        label: 'Settings',
                        child: IconButton(
                          onPressed: () {
                            HapticFeedback.lightImpact();
                            Navigator.push(
                              context,
                              PageRouteBuilder(
                                pageBuilder: (context, animation, secondaryAnimation) => 
                                    const SettingsScreen(),
                                transitionsBuilder: (context, animation, secondaryAnimation, child) {
                                  const begin = Offset(1.0, 0.0);
                                  const end = Offset.zero;
                                  const curve = Curves.easeInOutCubic;
                                  
                                  var tween = Tween(begin: begin, end: end).chain(
                                    CurveTween(curve: curve),
                                  );
                                  
                                  return SlideTransition(
                                    position: animation.drive(tween),
                                    child: child,
                                  );
                                },
                                transitionDuration: const Duration(milliseconds: 300),
                              ),
                            );
                          },
                          icon: Icon(
                            Icons.settings_rounded,
                            color: Theme.of(context).primaryColor,
                          ),
                          tooltip: 'Settings',
                          splashRadius: 24,
                        ),
                      ),
                      const SizedBox(width: 8),
                    ],
                  ),
                ),
              ),
            ),
          ),
          extendBodyBehindAppBar: true,
          body: AnimatedBackground(
            child: SafeArea(
              top: false,
              child: Column(
                children: [
                  // Smart Dashboard
                  SmartDashboard(
                    isCollapsed: _isDashboardCollapsed,
                    onToggle: () {
                      setState(() {
                        _isDashboardCollapsed = !_isDashboardCollapsed;
                      });
                    },
                  ),
                  
                  // Chat Interface
                  const Expanded(
                    child: ChatInterface(),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

}
