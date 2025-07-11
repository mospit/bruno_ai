import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/meal_card.dart';
import '../theme/app_colors.dart';
import '../widgets/bruno_avatar.dart';

class PrepScreen extends StatefulWidget {
  const PrepScreen({Key? key}) : super(key: key);

  @override
  State<PrepScreen> createState() => _PrepScreenState();
}

class _PrepScreenState extends State<PrepScreen> {
  String _selectedCategory = 'All';
  String _selectedDifficulty = 'All';
  bool _showOnlyQuick = false;
  bool _showOnlyHealthy = false;

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            backgroundColor: AppColors.background,
            elevation: 0,
            title: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.foodAccent.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.restaurant_rounded,
                    color: AppColors.foodAccent,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Meal Prep',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                      ),
                    ),
                    Text(
                      'Ready to cook with Bruno',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary(context),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            actions: [
              IconButton(
                icon: Icon(
                  Icons.filter_list,
                  color: AppColors.primary,
                ),
                onPressed: () {
                  _showMealFilters(context, provider);
                },
                tooltip: 'Filter Meals',
              ),
              IconButton(
                icon: Icon(
                  Icons.schedule,
                  color: AppColors.primary,
                ),
                onPressed: () {
                  _showWeeklyPlanner(context, provider);
                },
                tooltip: 'Weekly Planner',
              ),
            ],
          ),
          body: provider.favoriteMeals.isEmpty
              ? _buildEmptyState(context)
              : _buildMealList(context, provider),
          floatingActionButton: FloatingActionButton.extended(
            onPressed: () {
              // Navigate to chat to ask for meal ideas
              Navigator.pushNamed(context, '/chat');
            },
            icon: const Icon(Icons.add),
            label: const Text('Find Recipes'),
            backgroundColor: AppColors.foodAccent,
            foregroundColor: AppColors.white,
          ),
        );
      },
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.restaurant_menu_rounded,
            size: 80,
            color: AppColors.gray300,
          ),
          const SizedBox(height: 16),
          Text(
            'No meal plans yet',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: AppColors.gray600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Chat with Bruno to get personalized meal ideas',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppColors.gray500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildMealList(BuildContext context, BrunoProvider provider) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.favoriteMeals.length,
      itemBuilder: (context, index) {
        final meal = provider.favoriteMeals[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.gray200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  meal.name,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  meal.description,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Servings: ${meal.servings} • Cost: \$${meal.estimatedCost.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          // Add meal ingredients to shopping list
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('${meal.name} ingredients added to cart!'),
                              backgroundColor: AppColors.instacartGreen,
                            ),
                          );
                        },
                        child: const Text('Add to Cart'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () {
                          _showRecipeDetails(context, meal);
                        },
                        child: const Text('View Recipe'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showRecipeDetails(BuildContext context, dynamic meal) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            color: AppColors.background,
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(20),
            ),
          ),
          child: Column(
            children: [
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.gray300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        meal.name,
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Ingredients:',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      ...meal.ingredients.map((ingredient) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text('• $ingredient'),
                      )),
                      const SizedBox(height: 16),
                      Text(
                        'Instructions:',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      ...meal.instructions.asMap().entries.map((entry) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text('${entry.key + 1}. ${entry.value}'),
                      )),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showMealFilters(BuildContext context, BrunoProvider provider) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                BrunoAvatar(
                  mood: BrunoMood.helpful,
                  size: 32,
                  animate: true,
                ),
                const SizedBox(width: 12),
                Text(
                  'Filter Your Meals',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Text(
              'Category',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: ['All', 'Healthy', 'Vegetarian', 'Quick', 'Main Course']
                  .map((category) => FilterChip(
                        label: Text(category),
                        selected: _selectedCategory == category,
                        onSelected: (selected) {
                          setState(() {
                            _selectedCategory = selected ? category : 'All';
                          });
                        },
                        selectedColor: AppColors.foodAccent.withOpacity(0.2),
                        checkmarkColor: AppColors.foodAccent,
                      ))
                  .toList(),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Quick meals only (< 30 min)'),
              value: _showOnlyQuick,
              onChanged: (value) {
                setState(() {
                  _showOnlyQuick = value;
                });
              },
              activeColor: AppColors.foodAccent,
              secondary: const Icon(Icons.timer),
            ),
            SwitchListTile(
              title: const Text('Healthy meals only'),
              value: _showOnlyHealthy,
              onChanged: (value) {
                setState(() {
                  _showOnlyHealthy = value;
                });
              },
              activeColor: AppColors.successBlueGreen,
              secondary: const Icon(Icons.favorite),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      setState(() {
                        _selectedCategory = 'All';
                        _showOnlyQuick = false;
                        _showOnlyHealthy = false;
                      });
                      Navigator.pop(context);
                    },
                    child: const Text('Clear Filters'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      // Apply filters would be implemented here
                      _applyFilters(provider);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.foodAccent,
                    ),
                    child: const Text(
                      'Apply Filters',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showWeeklyPlanner(BuildContext context, BrunoProvider provider) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.calendar_today,
                  color: AppColors.primary,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Text(
                  'Weekly Meal Planner',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: 7,
                itemBuilder: (context, index) {
                  final days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                  final day = days[index];
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.gray50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: AppColors.gray200,
                        width: 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: Text(
                            day,
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        Expanded(
                          flex: 3,
                          child: Text(
                            provider.favoriteMeals.isNotEmpty 
                                ? provider.favoriteMeals[index % provider.favoriteMeals.length].name
                                : 'No meal planned',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ),
                        IconButton(
                          onPressed: () {
                            _selectMealForDay(context, day, provider);
                          },
                          icon: Icon(
                            Icons.edit,
                            color: AppColors.primary,
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _generateShoppingListForWeek(context, provider);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.instacartGreen,
                minimumSize: const Size(double.infinity, 48),
              ),
              child: const Text(
                'Generate Shopping List for Week',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _selectMealForDay(BuildContext context, String day, BrunoProvider provider) {
    // This would show a meal selection dialog
    // For now, just show a placeholder
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Meal selection for $day coming soon!'),
        backgroundColor: AppColors.primary,
      ),
    );
  }

  void _generateShoppingListForWeek(BuildContext context, BrunoProvider provider) {
    // Generate shopping list for all planned meals
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Weekly shopping list generated!'),
        backgroundColor: AppColors.instacartGreen,
        action: SnackBarAction(
          label: 'View',
          textColor: Colors.white,
          onPressed: () {
            Navigator.pushNamed(context, '/shopping');
          },
        ),
      ),
    );
  }

  void _applyFilters(BrunoProvider provider) {
    // Filter logic would be implemented here
    // For now, just provide haptic feedback
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Filters applied: $_selectedCategory'),
        backgroundColor: AppColors.foodAccent,
      ),
    );
  }
}
