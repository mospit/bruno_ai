import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_colors.dart';
import '../widgets/liquid_glass_container.dart';
import '../widgets/bruno_avatar.dart';
import '../models/shopping_item.dart';

class Meal {
  final String id;
  final String name;
  final String description;
  final double cost;
  final int servings;
  final int prepTime; // in minutes
  final String? imageUrl;
  final List<String> ingredients;
  final List<String> instructions;
  final String category;
  final Map<String, double> nutrition;
  final bool isHealthy;
  final bool isQuick; // under 30 minutes
  final String difficulty; // Easy, Medium, Hard

  Meal({
    required this.id,
    required this.name,
    required this.description,
    required this.cost,
    required this.servings,
    required this.prepTime,
    this.imageUrl,
    required this.ingredients,
    this.instructions = const [],
    this.category = 'Main Course',
    this.nutrition = const {},
    this.isHealthy = false,
    this.isQuick = false,
    this.difficulty = 'Easy',
  });

  double get costPerServing => cost / servings;

  List<ShoppingItem> get shoppingItems {
    return ingredients.map((ingredient) {
      // Simple ingredient parsing - could be made more sophisticated
      final parts = ingredient.split(' ');
      final quantity = int.tryParse(parts.first) ?? 1;
      final name = parts.skip(1).join(' ');
      
      return ShoppingItem(
        name: name,
        price: cost / ingredients.length, // Estimate
        quantity: quantity,
        category: _getIngredientCategory(name),
        unit: _getIngredientUnit(name),
        notes: 'For ${this.name}',
      );
    }).toList();
  }

  String _getIngredientCategory(String ingredient) {
    final lower = ingredient.toLowerCase();
    if (lower.contains('chicken') || lower.contains('beef') || lower.contains('pork')) {
      return 'Meat';
    } else if (lower.contains('milk') || lower.contains('cheese') || lower.contains('yogurt')) {
      return 'Dairy';
    } else if (lower.contains('tomato') || lower.contains('onion') || lower.contains('pepper')) {
      return 'Vegetables';
    } else if (lower.contains('rice') || lower.contains('pasta') || lower.contains('bread')) {
      return 'Grains';
    }
    return 'Pantry';
  }

  String _getIngredientUnit(String ingredient) {
    final lower = ingredient.toLowerCase();
    if (lower.contains('lb') || lower.contains('pound')) return 'lbs';
    if (lower.contains('cup')) return 'cups';
    if (lower.contains('tbsp') || lower.contains('tablespoon')) return 'tbsp';
    if (lower.contains('tsp') || lower.contains('teaspoon')) return 'tsp';
    return 'item';
  }
}

class MealPlanCard extends StatefulWidget {
  final Meal meal;
  final VoidCallback? onAddToCart;
  final VoidCallback? onViewRecipe;
  final bool isInCart;
  final bool showNutrition;

  const MealPlanCard({
    super.key,
    required this.meal,
    this.onAddToCart,
    this.onViewRecipe,
    this.isInCart = false,
    this.showNutrition = false,
  });

  @override
  State<MealPlanCard> createState() => _MealPlanCardState();
}

class _MealPlanCardState extends State<MealPlanCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.98,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    _animationController.forward();
  }

  void _handleTapUp(TapUpDetails details) {
    _animationController.reverse();
  }

  void _handleTapCancel() {
    _animationController.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      onTap: () {
        setState(() {
          _isExpanded = !_isExpanded;
        });
      },
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
              child: LiquidGlassContainer(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Main meal info
                    _buildMealHeader(context),
                    
                    // Expandable content
                    AnimatedCrossFade(
                      firstChild: const SizedBox.shrink(),
                      secondChild: _buildExpandedContent(context),
                      crossFadeState: _isExpanded 
                          ? CrossFadeState.showSecond 
                          : CrossFadeState.showFirst,
                      duration: const Duration(milliseconds: 300),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildMealHeader(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            // Meal image or icon
            _buildMealImage(context),
            const SizedBox(width: 16),
            
            // Meal details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          widget.meal.name,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      _buildCostBadge(context),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.meal.description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  _buildMealTags(context),
                ],
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 12),
        
        // Action buttons
        Row(
          children: [
            Expanded(
              child: _buildActionButton(
                context,
                widget.isInCart ? 'In Cart' : 'Add to Cart',
                widget.isInCart ? Icons.check_circle : Icons.add_shopping_cart,
                widget.isInCart ? Colors.green : Theme.of(context).primaryColor,
                widget.isInCart ? null : widget.onAddToCart,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildActionButton(
                context,
                'View Recipe',
                Icons.restaurant_menu,
                Colors.blue,
                widget.onViewRecipe,
              ),
            ),
            const SizedBox(width: 8),
            _buildExpandButton(context),
          ],
        ),
      ],
    );
  }

  Widget _buildMealImage(BuildContext context) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: widget.meal.imageUrl != null
            ? Image.network(
                widget.meal.imageUrl!,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return _buildDefaultMealIcon(context);
                },
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Center(
                    child: CircularProgressIndicator(
                      value: loadingProgress.expectedTotalBytes != null
                          ? loadingProgress.cumulativeBytesLoaded / 
                            loadingProgress.expectedTotalBytes!
                          : null,
                      strokeWidth: 2,
                    ),
                  );
                },
              )
            : _buildDefaultMealIcon(context),
      ),
    );
  }

  Widget _buildDefaultMealIcon(BuildContext context) {
    return Container(
      color: Theme.of(context).primaryColor.withOpacity(0.1),
      child: Icon(
        _getMealCategoryIcon(),
        color: Theme.of(context).primaryColor,
        size: 40,
      ),
    );
  }

  IconData _getMealCategoryIcon() {
    switch (widget.meal.category.toLowerCase()) {
      case 'breakfast':
        return Icons.breakfast_dining;
      case 'lunch':
        return Icons.lunch_dining;
      case 'dinner':
      case 'main course':
        return Icons.dinner_dining;
      case 'dessert':
        return Icons.cake;
      case 'snack':
        return Icons.fastfood;
      default:
        return Icons.restaurant;
    }
  }

  Widget _buildCostBadge(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).primaryColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        '\$${widget.meal.cost.toStringAsFixed(2)}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildMealTags(BuildContext context) {
    final tags = <Widget>[];
    
    // Servings
    tags.add(_buildTag(
      context,
      '${widget.meal.servings} servings',
      Icons.people,
      Colors.blue,
    ));
    
    // Prep time
    tags.add(_buildTag(
      context,
      '${widget.meal.prepTime} min',
      Icons.timer,
      Colors.orange,
    ));
    
    // Quick meal
    if (widget.meal.isQuick) {
      tags.add(_buildTag(
        context,
        'Quick',
        Icons.flash_on,
        Colors.yellow,
      ));
    }
    
    // Healthy
    if (widget.meal.isHealthy) {
      tags.add(_buildTag(
        context,
        'Healthy',
        Icons.favorite,
        Colors.green,
      ));
    }

    return Wrap(
      spacing: 6,
      runSpacing: 4,
      children: tags,
    );
  }

  Widget _buildTag(BuildContext context, String text, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 2),
          Text(
            text,
            style: TextStyle(
              fontSize: 10,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(BuildContext context, String text, IconData icon, Color color, VoidCallback? onPressed) {
    return GestureDetector(
      onTap: onPressed != null ? () {
        HapticFeedback.lightImpact();
        onPressed();
      } : null,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: onPressed != null ? color.withOpacity(0.1) : Colors.grey.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: onPressed != null ? color.withOpacity(0.3) : Colors.grey.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 16,
              color: onPressed != null ? color : Colors.grey,
            ),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                text,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: onPressed != null ? color : Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExpandButton(BuildContext context) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isExpanded = !_isExpanded;
        });
      },
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: Theme.of(context).primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: Theme.of(context).primaryColor.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: AnimatedRotation(
          turns: _isExpanded ? 0.5 : 0.0,
          duration: const Duration(milliseconds: 300),
          child: Icon(
            Icons.expand_more,
            color: Theme.of(context).primaryColor,
            size: 20,
          ),
        ),
      ),
    );
  }

  Widget _buildExpandedContent(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Divider
          Container(
            height: 1,
            color: Theme.of(context).dividerColor.withOpacity(0.3),
            margin: const EdgeInsets.only(bottom: 16),
          ),
          
          // Ingredients
          _buildSection(
            context,
            'Ingredients',
            Icons.list_alt,
            _buildIngredientsList(context),
          ),
          
          const SizedBox(height: 16),
          
          // Nutrition (if available)
          if (widget.meal.nutrition.isNotEmpty) ...[
            _buildSection(
              context,
              'Nutrition',
              Icons.favorite,
              _buildNutritionInfo(context),
            ),
            const SizedBox(height: 16),
          ],
          
          // Instructions preview
          if (widget.meal.instructions.isNotEmpty) ...[
            _buildSection(
              context,
              'Instructions Preview',
              Icons.format_list_numbered,
              _buildInstructionsPreview(context),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSection(BuildContext context, String title, IconData icon, Widget content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: Theme.of(context).primaryColor),
            const SizedBox(width: 6),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).primaryColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        content,
      ],
    );
  }

  Widget _buildIngredientsList(BuildContext context) {
    return Column(
      children: widget.meal.ingredients.take(5).map((ingredient) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            children: [
              Container(
                width: 4,
                height: 4,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  ingredient,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildNutritionInfo(BuildContext context) {
    return Row(
      children: widget.meal.nutrition.entries.take(3).map((entry) {
        return Expanded(
          child: Container(
            padding: const EdgeInsets.all(8),
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Text(
                  entry.value.toStringAsFixed(0),
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                Text(
                  entry.key,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.green,
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInstructionsPreview(BuildContext context) {
    final firstInstruction = widget.meal.instructions.first;
    return Text(
      firstInstruction.length > 100 
          ? '${firstInstruction.substring(0, 100)}...'
          : firstInstruction,
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
        fontStyle: FontStyle.italic,
      ),
    );
  }
}
