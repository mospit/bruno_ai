import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/liquid_glass_container.dart';
import '../widgets/animated_background.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: AnimatedBackground(
        child: SafeArea(
          child: Consumer<BrunoProvider>(
            builder: (context, provider, child) {
              return Column(
                children: [
                  // Header
                  _buildHeader(context),
                  
                  // Settings List
                  Expanded(
                    child: _buildSettingsList(context, provider),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return LiquidGlassContainer(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_rounded),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Settings',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Icon(
            Icons.settings_rounded,
            color: Theme.of(context).primaryColor,
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsList(BuildContext context, BrunoProvider provider) {
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      children: [
        // Profile Section
        _buildSectionHeader(context, 'Profile'),
        _buildSettingsTile(
          context,
          icon: Icons.person_rounded,
          title: 'Family Size',
          subtitle: '${provider.familySize} people',
          onTap: () => _showFamilySizeDialog(context, provider),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.attach_money_rounded,
          title: 'Budget',
          subtitle: provider.currentBudget.isEmpty ? 'Not set' : '\$${provider.currentBudget}',
          onTap: () => _showBudgetDialog(context, provider),
        ),
        
        const SizedBox(height: 24),
        
        // Preferences Section
        _buildSectionHeader(context, 'Preferences'),
        _buildSettingsTile(
          context,
          icon: Icons.restaurant_rounded,
          title: 'Dietary Restrictions',
          subtitle: provider.dietaryRestrictions.isEmpty 
              ? 'None set' 
              : provider.dietaryRestrictions.join(', '),
          onTap: () => _showDietaryRestrictionsDialog(context, provider),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.schedule_rounded,
          title: 'Preferred Delivery Time',
          subtitle: provider.preferredDeliveryTime,
          onTap: () => _showDeliveryTimeDialog(context, provider),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.store_rounded,
          title: 'Preferred Store',
          subtitle: provider.selectedStore,
          onTap: () => _showStoreSelectionDialog(context, provider),
        ),
        
        const SizedBox(height: 24),
        
        // Meals & Orders Section
        _buildSectionHeader(context, 'Meals & Orders'),
        _buildSettingsTile(
          context,
          icon: Icons.favorite_rounded,
          title: 'Favorite Meals',
          subtitle: '${provider.favoriteMeals.length} saved meals',
          onTap: () => _showFavoriteMeals(context, provider),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.history_rounded,
          title: 'Past Orders',
          subtitle: '${provider.pastOrders.length} previous orders',
          onTap: () => _showPastOrders(context, provider),
        ),
        
        const SizedBox(height: 24),
        
        // App Settings Section
        _buildSectionHeader(context, 'App Settings'),
        _buildSettingsTile(
          context,
          icon: Icons.notifications_rounded,
          title: 'Notifications',
          subtitle: 'Manage notification preferences',
          onTap: () => _showNotificationSettings(context),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.dark_mode_rounded,
          title: 'Theme',
          subtitle: Theme.of(context).brightness == Brightness.dark ? 'Dark' : 'Light',
          onTap: () => _showThemeDialog(context),
        ),
        
        const SizedBox(height: 24),
        
        // Support Section
        _buildSectionHeader(context, 'Support'),
        _buildSettingsTile(
          context,
          icon: Icons.help_rounded,
          title: 'Help & FAQ',
          subtitle: 'Get help and find answers',
          onTap: () => _showHelpDialog(context),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.feedback_rounded,
          title: 'Send Feedback',
          subtitle: 'Help us improve Bruno AI',
          onTap: () => _showFeedbackDialog(context),
        ),
        _buildSettingsTile(
          context,
          icon: Icons.info_rounded,
          title: 'About',
          subtitle: 'Version 1.0.0',
          onTap: () => _showAboutDialog(context),
        ),
        
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 12, top: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
          fontWeight: FontWeight.w600,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  Widget _buildSettingsTile(BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: LiquidGlassContainer(
        padding: const EdgeInsets.all(16),
        child: ListTile(
          contentPadding: EdgeInsets.zero,
          leading: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: Theme.of(context).primaryColor.withOpacity(0.1),
            ),
            child: Icon(
              icon,
              color: Theme.of(context).primaryColor,
              size: 20,
            ),
          ),
          title: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          subtitle: Text(
            subtitle,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
            ),
          ),
          trailing: Icon(
            Icons.chevron_right_rounded,
            color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5),
          ),
          onTap: onTap,
        ),
      ),
    );
  }

  void _showFamilySizeDialog(BuildContext context, BrunoProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Family Size',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(6, (index) {
                  final size = index + 1;
                  final isSelected = size == provider.familySize;
                  return GestureDetector(
                    onTap: () {
                      provider.updateFamilySize(size);
                      Navigator.pop(context);
                    },
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isSelected 
                            ? Theme.of(context).primaryColor
                            : Theme.of(context).primaryColor.withOpacity(0.1),
                        border: Border.all(
                          color: Theme.of(context).primaryColor,
                          width: isSelected ? 2 : 1,
                        ),
                      ),
                      child: Center(
                        child: Text(
                          size.toString(),
                          style: TextStyle(
                            color: isSelected ? Colors.white : Theme.of(context).primaryColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  );
                }),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showBudgetDialog(BuildContext context, BrunoProvider provider) {
    final controller = TextEditingController(text: provider.currentBudget);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Weekly Budget',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              TextField(
                controller: controller,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Budget Amount',
                  prefixText: '\$',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        provider.updateBudget(controller.text);
                        Navigator.pop(context);
                      },
                      child: const Text('Save'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showDietaryRestrictionsDialog(BuildContext context, BrunoProvider provider) {
    final restrictions = [
      'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 
      'Nut-Free', 'Keto', 'Paleo', 'Low-Carb'
    ];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Dietary Restrictions',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              ...restrictions.map((restriction) {
                final isSelected = provider.dietaryRestrictions.contains(restriction);
                return CheckboxListTile(
                  title: Text(restriction),
                  value: isSelected,
                  onChanged: (value) {
                    if (value == true) {
                      provider.addDietaryRestriction(restriction);
                    } else {
                      provider.removeDietaryRestriction(restriction);
                    }
                  },
                );
              }).toList(),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Done'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showDeliveryTimeDialog(BuildContext context, BrunoProvider provider) {
    final times = ['ASAP', '1-2 hours', '2-4 hours', 'Tomorrow', 'This weekend'];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Delivery Time',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              ...times.map((time) {
                return ListTile(
                  title: Text(time),
                  onTap: () {
                    provider.updatePreferredDeliveryTime(time);
                    Navigator.pop(context);
                  },
                  trailing: provider.preferredDeliveryTime == time
                      ? Icon(Icons.check, color: Theme.of(context).primaryColor)
                      : null,
                );
              }).toList(),
            ],
          ),
        ),
      ),
    );
  }

  void _showStoreSelectionDialog(BuildContext context, BrunoProvider provider) {
    final stores = ['Whole Foods', 'Safeway', 'Kroger', 'Target', 'Costco'];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Preferred Store',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              ...stores.map((store) {
                return ListTile(
                  title: Text(store),
                  onTap: () {
                    provider.updateSelectedStore(store);
                    Navigator.pop(context);
                  },
                  trailing: provider.selectedStore == store
                      ? Icon(Icons.check, color: Theme.of(context).primaryColor)
                      : null,
                );
              }).toList(),
            ],
          ),
        ),
      ),
    );
  }

  void _showNotificationSettings(BuildContext context) {
    // Placeholder for notification settings
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Notification settings coming soon!')),
    );
  }

  void _showThemeDialog(BuildContext context) {
    // Placeholder for theme settings
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Theme settings coming soon!')),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.help_rounded,
                size: 48,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(height: 16),
              Text(
                'Help & FAQ',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Bruno AI is your personal shopping assistant. Ask me about meal planning, recipes, and I\'ll help you create shopping lists and order ingredients through Instacart.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Got it!'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showFeedbackDialog(BuildContext context) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Send Feedback',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              TextField(
                controller: controller,
                maxLines: 4,
                decoration: InputDecoration(
                  labelText: 'Your feedback',
                  hintText: 'Tell us how we can improve Bruno AI...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Thank you for your feedback!')),
                        );
                      },
                      child: const Text('Send'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [
                      Theme.of(context).primaryColor,
                      Theme.of(context).primaryColor.withOpacity(0.7),
                    ],
                  ),
                ),
                child: const Icon(
                  Icons.smart_toy_rounded,
                  color: Colors.white,
                  size: 40,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Bruno AI',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Version 1.0.0',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Your AI-powered shopping assistant for meal planning and grocery delivery.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showFavoriteMeals(BuildContext context, BrunoProvider provider) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: LiquidGlassContainer(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.favorite_rounded,
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Favorite Meals',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close_rounded),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 400,
                child: provider.favoriteMeals.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.restaurant_rounded,
                              size: 64,
                              color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.3),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'No favorite meals yet',
                              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Ask Bruno to suggest meals and save your favorites!',
                              textAlign: TextAlign.center,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5),
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        itemCount: provider.favoriteMeals.length,
                        itemBuilder: (context, index) {
                          final meal = provider.favoriteMeals[index];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: LiquidGlassContainer(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              meal.name,
                                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              meal.description,
                                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      PopupMenuButton(
                                        icon: const Icon(Icons.more_vert_rounded),
                                        itemBuilder: (context) => [
                                          PopupMenuItem(
                                            value: 'reorder',
                                            child: const Row(
                                              children: [
                                                Icon(Icons.shopping_cart_rounded),
                                                SizedBox(width: 8),
                                                Text('Add to Cart'),
                                              ],
                                            ),
                                          ),
                                          PopupMenuItem(
                                            value: 'remove',
                                            child: const Row(
                                              children: [
                                                Icon(Icons.delete_rounded),
                                                SizedBox(width: 8),
                                                Text('Remove'),
                                              ],
                                            ),
                                          ),
                                        ],
                                        onSelected: (value) {
                                          if (value == 'reorder') {
                                            provider.reorderFavoriteMeal(meal.id);
                                            Navigator.pop(context);
                                            ScaffoldMessenger.of(context).showSnackBar(
                                              SnackBar(
                                                content: Text('${meal.name} added to cart!'),
                                                backgroundColor: Theme.of(context).primaryColor,
                                              ),
                                            );
                                          } else if (value == 'remove') {
                                            provider.removeFavoriteMeal(meal.id);
                                          }
                                        },
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: Theme.of(context).primaryColor.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Text(
                                          meal.category,
                                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                            color: Theme.of(context).primaryColor,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Icon(
                                        Icons.people_rounded,
                                        size: 16,
                                        color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        '${meal.servings} servings',
                                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Icon(
                                        Icons.timer_rounded,
                                        size: 16,
                                        color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        '${meal.cookingTime} min',
                                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                          color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                        ),
                                      ),
                                      const Spacer(),
                                      Text(
                                        '\$${meal.estimatedCost.toStringAsFixed(2)}',
                                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          color: Theme.of(context).primaryColor,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showPastOrders(BuildContext context, BrunoProvider provider) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: LiquidGlassContainer(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.history_rounded,
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Past Orders',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close_rounded),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 400,
                child: provider.pastOrders.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.shopping_bag_rounded,
                              size: 64,
                              color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.3),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'No past orders yet',
                              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Your order history will appear here after your first purchase.',
                              textAlign: TextAlign.center,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.5),
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        itemCount: provider.pastOrders.length,
                        itemBuilder: (context, index) {
                          final order = provider.pastOrders[index];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: LiquidGlassContainer(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              order.store,
                                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                            const SizedBox(height: 4),
                                            Text(
                                              '${order.date.day}/${order.date.month}/${order.date.year}',
                                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                                color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: order.status == 'Delivered' 
                                              ? Colors.green.withOpacity(0.1)
                                              : Theme.of(context).primaryColor.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Text(
                                          order.status,
                                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                            color: order.status == 'Delivered' 
                                                ? Colors.green
                                                : Theme.of(context).primaryColor,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      PopupMenuButton(
                                        icon: const Icon(Icons.more_vert_rounded),
                                        itemBuilder: (context) => [
                                          PopupMenuItem(
                                            value: 'reorder',
                                            child: const Row(
                                              children: [
                                                Icon(Icons.refresh_rounded),
                                                SizedBox(width: 8),
                                                Text('Reorder'),
                                              ],
                                            ),
                                          ),
                                        ],
                                        onSelected: (value) {
                                          if (value == 'reorder') {
                                            provider.reorderPastOrder(order.id);
                                            Navigator.pop(context);
                                            ScaffoldMessenger.of(context).showSnackBar(
                                              SnackBar(
                                                content: Text('Items from ${order.store} added to cart!'),
                                                backgroundColor: Theme.of(context).primaryColor,
                                              ),
                                            );
                                          }
                                        },
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    '${order.items.length} items',
                                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                      color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        'Total',
                                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      Text(
                                        '\$${order.totalAmount.toStringAsFixed(2)}',
                                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          color: Theme.of(context).primaryColor,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}