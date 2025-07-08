import 'package:flutter/material.dart';
import '../lib/widgets/animated_list_view.dart';
import '../lib/widgets/skeleton_loader.dart';
import '../lib/utils/animation_manager.dart';

// Example 1: Enhanced Shopping Cart with Animated Items
class EnhancedShoppingCartExample extends StatefulWidget {
  @override
  State<EnhancedShoppingCartExample> createState() => _EnhancedShoppingCartExampleState();
}

class _EnhancedShoppingCartExampleState extends State<EnhancedShoppingCartExample> {
  bool isLoading = false;
  List<String> items = ['Apples', 'Bananas', 'Chicken', 'Rice'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Enhanced Shopping Cart')),
      body: Column(
        children: [
          // Loading state with skeletons
          if (isLoading)
            Expanded(
              child: SkeletonList(
                itemCount: 5,
                itemBuilder: (index) => const SkeletonShoppingItem(),
              ),
            )
          else
            // Animated list with staggered entrance
            Expanded(
              child: AnimatedListView(
                children: items.map((item) => 
                  _buildShoppingItem(item).animateIn(
                    slideFrom: const Offset(0.3, 0),
                    scaleFrom: 0.8,
                  ),
                ).toList(),
                itemDelay: const Duration(milliseconds: 80),
              ),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          setState(() {
            isLoading = !isLoading;
          });
        },
        child: Icon(isLoading ? Icons.stop : Icons.refresh),
      ),
    );
  }

  Widget _buildShoppingItem(String item) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.shopping_bag,
              color: Theme.of(context).primaryColor,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              item,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          IconButton(
            onPressed: () {
              setState(() {
                items.remove(item);
              });
            },
            icon: const Icon(Icons.remove_circle_outline),
          ),
        ],
      ),
    );
  }
}

// Example 2: Performance-Aware Bruno Avatar
class PerformanceAwareBrunoExample extends StatefulWidget {
  @override
  State<PerformanceAwareBrunoExample> createState() => _PerformanceAwareBrunoExampleState();
}

class _PerformanceAwareBrunoExampleState extends State<PerformanceAwareBrunoExample>
    with TickerProviderStateMixin, AnimationMixin {
  late AnimationController _scaleController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    
    // Use managed animation controller
    _scaleController = createManagedController(
      duration: AppAnimations.normal,
      debugLabel: 'BrunoScale',
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: AppAnimations.bouncyCurve,
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Performance-Aware Bruno')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Performance stats (debug only)
            if (AppAnimations.shouldAnimate(context))
              Container(
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Text('Animation Performance Stats:'),
                    ...AnimationManager.instance.getPerformanceStats().entries.map(
                      (entry) => Text('${entry.key}: ${entry.value.toStringAsFixed(1)}ms'),
                    ),
                  ],
                ),
              ),
            
            // Animated Bruno with performance management
            AnimatedBuilder(
              animation: _scaleAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _scaleAnimation.value,
                  child: Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.pets,
                      color: Colors.white,
                      size: 50,
                    ),
                  ),
                );
              },
            ),
            
            const SizedBox(height: 32),
            
            ElevatedButton(
              onPressed: () {
                if (_scaleController.isCompleted) {
                  _scaleController.reverse();
                } else {
                  _scaleController.forward();
                }
              },
              child: Text('Animate Bruno'),
            ),
          ],
        ),
      ),
    );
  }
}

// Example 3: Context-Aware Animations
class ContextAwareAnimationsExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Context-Aware Animations')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Card that respects reduced motion
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Accessibility Aware',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'This card will not animate if the user has reduced motion enabled.',
                    ),
                  ],
                ),
              ),
            ).animateIn(
              duration: AppAnimations.getDuration(AppAnimations.normal, context),
              slideFrom: const Offset(0, 0.3),
            ),
            
            const SizedBox(height: 20),
            
            // Performance-aware list
            Text(
              'Performance Managed List',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            
            ...List.generate(5, (index) {
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: CircleAvatar(child: Text('${index + 1}')),
                  title: Text('Item ${index + 1}'),
                  subtitle: Text('Animated with performance awareness'),
                  tileColor: Colors.grey[100],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ).animateIn(
                duration: AppAnimations.getDuration(
                  Duration(milliseconds: 200 + (index * 50)),
                  context,
                ),
                slideFrom: Offset(0.2, 0),
                scaleFrom: 0.9,
              );
            }),
          ],
        ),
      ),
    );
  }
}

// Example 4: Meal Card with Enhanced Animations
class EnhancedMealCardExample extends StatefulWidget {
  @override
  State<EnhancedMealCardExample> createState() => _EnhancedMealCardExampleState();
}

class _EnhancedMealCardExampleState extends State<EnhancedMealCardExample> {
  bool showSkeleton = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Enhanced Meal Cards')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Toggle button
            ElevatedButton(
              onPressed: () {
                setState(() {
                  showSkeleton = !showSkeleton;
                });
              },
              child: Text(showSkeleton ? 'Show Content' : 'Show Loading'),
            ),
            
            const SizedBox(height: 20),
            
            // Meal cards with loading states
            if (showSkeleton)
              ...List.generate(3, (index) => 
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: const SkeletonMealCard(),
                ),
              )
            else
              AnimatedListView(
                children: List.generate(3, (index) => 
                  _buildMealCard('Delicious Meal ${index + 1}', '\$${12 + index * 2}.99'),
                ),
                itemDelay: const Duration(milliseconds: 150),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMealCard(String title, String price) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            height: 120,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: const Center(
              child: Icon(Icons.restaurant, size: 40, color: Colors.grey),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      price,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).primaryColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'A delicious meal prepared with fresh ingredients and love.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.add_shopping_cart, size: 16),
                        label: const Text('Add to Cart'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.favorite_border),
                      style: IconButton.styleFrom(
                        backgroundColor: Colors.grey[100],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
