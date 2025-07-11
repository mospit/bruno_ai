import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../theme/app_colors.dart';
import '../widgets/bruno_avatar.dart';

class ShoppingScreen extends StatefulWidget {
  const ShoppingScreen({Key? key}) : super(key: key);

  @override
  State<ShoppingScreen> createState() => _ShoppingScreenState();
}

class _ShoppingScreenState extends State<ShoppingScreen> {
  String _sortBy = 'cheapest';
  final Map<String, bool> _sectionExpanded = {
    'Essentials': true,
    'Caribbean Specials': true,
    'Produce': false,
    'Pantry Items': false,
  };
  
  final Map<String, bool> _itemChecked = {
    'Rice': false,
    'Plantains': false,
    'Coconut Milk': false,
    'Black Beans': false,
    'Bell Peppers': false,
    'Onions': false,
  };
  
  double get budget => 200.0;
  double get currentTotal => 175.0;
  double get savings => 25.0;

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
                    color: AppColors.instacartGreen.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.shopping_cart_rounded,
                    color: AppColors.instacartGreen,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Shopping List',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                      ),
                    ),
                    Text(
                      '${provider.shoppingList.length} items • \$${provider.totalCost.toStringAsFixed(2)}',
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
                  _showFilterOptions(context, provider);
                },
                tooltip: 'Filter & Sort',
              ),
              if (provider.shoppingList.isNotEmpty)
                IconButton(
                  icon: Icon(
                    Icons.clear_all,
                    color: AppColors.primary,
                  ),
                  onPressed: () {
                    _showClearConfirmation(context, provider);
                  },
                  tooltip: 'Clear list',
                ),
            ],
          ),
          body: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildBudgetBar(),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children:
                      _sectionExpanded.keys.map((section) => _buildSection(provider, section)).toList(),
                ),
              ),
              _buildFooter(),
            ],
          ),
          floatingActionButton: FloatingActionButton.extended(
            onPressed: () {
              // Navigate to chat or show add item dialog
              Navigator.pushNamed(context, '/chat');
            },
            icon: const Icon(Icons.add_shopping_cart),
            label: const Text('Add Items'),
            backgroundColor: AppColors.instacartGreen,
            foregroundColor: AppColors.white,
          ),
        );
      },
    );
  }

  void _showFilterOptions(BuildContext context, BrunoProvider provider) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            ListTile(
              leading: const Icon(Icons.sort_by_alpha),
              title: const Text('Sort By Name'),
              onTap: () {
                setState(() {
                  _sortBy = 'name';
                  _sortItems(provider);
                });
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.attach_money),
              title: const Text('Sort By Price'),
              onTap: () {
                setState(() {
                  _sortBy = 'price';
                  _sortItems(provider);
                });
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.category),
              title: const Text('Sort By Category'),
              onTap: () {
                setState(() {
                  _sortBy = 'category';
                  _sortItems(provider);
                });
                Navigator.pop(context);
              },
            ),
            // Note: Removed _sortAscending as it's not used in the wireframe
          ],
        );
      },
    );
  }

  void _showClearConfirmation(BuildContext context, BrunoProvider provider) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Clear Shopping List'),
          content: const Text('Are you sure you want to clear the shopping list?'),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancel'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text('Clear'),
              style: TextButton.styleFrom(
                foregroundColor: AppColors.error,
              ),
              onPressed: () {
                provider.clearShoppingList();
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  void _sortItems(BrunoProvider provider) {
    // Mock method - would sort actual items in real implementation
  }
  
  Widget _buildBudgetBar() {
    final progressValue = currentTotal / budget;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Shopping',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.primary.withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _sortBy,
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    icon: Icon(
                      Icons.arrow_drop_down,
                      color: AppColors.primary,
                      size: 20,
                    ),
                    onChanged: (String? newValue) {
                      if (newValue != null) {
                        setState(() {
                          _sortBy = newValue;
                        });
                      }
                    },
                    items: [
                      'cheapest',
                      'name',
                      'category',
                    ].map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value.substring(0, 1).toUpperCase() + value.substring(1)),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Budget: \$${currentTotal.toStringAsFixed(0)}/\$${budget.toStringAsFixed(0)}',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary(context),
            ),
          ),
          const SizedBox(height: 8),
          Stack(
            children: [
              Container(
                height: 8,
                decoration: BoxDecoration(
                  color: AppColors.gray200,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              FractionallySizedBox(
                widthFactor: progressValue.clamp(0.0, 1.0),
                child: Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: AppColors.instacartGreen,
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.instacartGreen.withOpacity(0.4),
                        blurRadius: 4,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: AppColors.instacartGreen.withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.instacartGreen,
                    width: 3,
                  ),
                ),
                child: Center(
                  child: Text(
                    '${(progressValue * 100).toInt()}%',
                    style: TextStyle(
                      color: AppColors.instacartGreen,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  progressValue < 0.9
                      ? 'Great! You\'re staying within budget'
                      : 'Getting close to budget limit',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildSection(BrunoProvider provider, String sectionName) {
    final isExpanded = _sectionExpanded[sectionName] ?? false;
    final sectionItems = _getSectionItems(sectionName);
    final sectionTotal = _getSectionTotal(sectionName);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Section header
          GestureDetector(
            onTap: () {
              HapticFeedback.lightImpact();
              setState(() {
                _sectionExpanded[sectionName] = !isExpanded;
              });
            },
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isExpanded
                    ? AppColors.instacartGreen.withOpacity(0.05)
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  Text(
                    sectionName,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                  const Spacer(),
                  if (sectionTotal > 0)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.instacartGreen.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Subtotal: \$${sectionTotal.toStringAsFixed(0)}',
                        style: TextStyle(
                          color: AppColors.instacartGreen,
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  const SizedBox(width: 8),
                  Icon(
                    isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: AppColors.primary,
                  ),
                ],
              ),
            ),
          ),
          // Section items
          if (isExpanded)
            Column(
              children: sectionItems.map((item) => _buildShoppingItem(item)).toList(),
            ),
        ],
      ),
    );
  }
  
  Widget _buildShoppingItem(Map<String, dynamic> item) {
    final isChecked = _itemChecked[item['name']] ?? false;
    final hasDiscount = item['originalPrice'] != null;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          // Checkbox
          Checkbox(
            value: isChecked,
            onChanged: (bool? value) {
              HapticFeedback.lightImpact();
              setState(() {
                _itemChecked[item['name']] = value ?? false;
              });
            },
            activeColor: AppColors.instacartGreen,
          ),
          const SizedBox(width: 8),
          // Item details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      item['name'],
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                        decoration: isChecked ? TextDecoration.lineThrough : null,
                        color: isChecked
                            ? AppColors.textSecondary(context)
                            : AppColors.textPrimary(context),
                      ),
                    ),
                    if (hasDiscount) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFD700), // Yellow badge for deals
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'DEAL',
                          style: TextStyle(
                            color: Colors.orange.shade800,
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                if (item['description'] != null)
                  Text(
                    item['description'],
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary(context),
                    ),
                  ),
              ],
            ),
          ),
          // Price and swap button
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (hasDiscount)
                Text(
                  '\$${item['originalPrice']}',
                  style: TextStyle(
                    color: AppColors.textSecondary(context),
                    fontSize: 12,
                    decoration: TextDecoration.lineThrough,
                  ),
                ),
              Text(
                '\$${item['price']}',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: hasDiscount ? AppColors.instacartGreen : AppColors.textPrimary(context),
                ),
              ),
              const SizedBox(height: 4),
              GestureDetector(
                onTap: () {
                  HapticFeedback.lightImpact();
                  _showSwapOptions(item['name']);
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: AppColors.primary.withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    'Swap',
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Column(
          children: [
            // Total and savings
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFFFD700).withOpacity(0.2), // Yellow highlight
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFFFFD700),
                  width: 2,
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Total: \$${currentTotal.toStringAsFixed(0)}',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary(context),
                        ),
                      ),
                      Text(
                        'Savings: \$${savings.toStringAsFixed(0)}',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.instacartGreen,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  Icon(
                    Icons.savings,
                    color: Colors.orange.shade600,
                    size: 32,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Order Now button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () {
                  HapticFeedback.mediumImpact();
                  _showOrderConfirmation();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.instacartGreen,
                  foregroundColor: Colors.white,
                  elevation: 4,
                  shadowColor: AppColors.instacartGreen.withOpacity(0.4),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.shopping_cart_checkout,
                      size: 24,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Order Now',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  List<Map<String, dynamic>> _getSectionItems(String sectionName) {
    switch (sectionName) {
      case 'Essentials':
        return [
          {'name': 'Rice', 'price': 5, 'description': '2 lb bag'},
          {'name': 'Black Beans', 'price': 3, 'originalPrice': 4, 'description': 'Canned, 15oz'},
        ];
      case 'Caribbean Specials':
        return [
          {'name': 'Plantains', 'price': 10, 'originalPrice': 12, 'description': 'Green, 2 lbs'},
          {'name': 'Coconut Milk', 'price': 4, 'description': 'Canned, 14oz'},
        ];
      case 'Produce':
        return [
          {'name': 'Bell Peppers', 'price': 6, 'description': 'Mixed colors, 3 pack'},
          {'name': 'Onions', 'price': 3, 'description': 'Yellow, 2 lb bag'},
        ];
      case 'Pantry Items':
        return [];
      default:
        return [];
    }
  }
  
  double _getSectionTotal(String sectionName) {
    final items = _getSectionItems(sectionName);
    return items.fold(0.0, (sum, item) => sum + (item['price'] as num).toDouble());
  }
  
  void _showSwapOptions(String itemName) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        margin: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.symmetric(vertical: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    'Swap $itemName',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 20),
                  ListTile(
                    leading: const Icon(Icons.swap_horiz, color: AppColors.primary),
                    title: const Text('Find Similar Items'),
                    subtitle: const Text('Browse alternatives'),
                    onTap: () => Navigator.pop(context),
                  ),
                  ListTile(
                    leading: const Icon(Icons.delete, color: AppColors.error),
                    title: const Text('Remove Item'),
                    subtitle: const Text('Delete from list'),
                    onTap: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  void _showOrderConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.shopping_cart_checkout,
              color: AppColors.instacartGreen,
            ),
            const SizedBox(width: 8),
            const Text('Order Confirmation'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Total: \$${currentTotal.toStringAsFixed(2)}'),
            Text('Savings: \$${savings.toStringAsFixed(2)}'),
            const SizedBox(height: 16),
            const Text('This would redirect to Instacart for checkout.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Order functionality coming soon!'),
                  backgroundColor: AppColors.instacartGreen,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.instacartGreen,
              foregroundColor: Colors.white,
            ),
            child: const Text('Proceed'),
          ),
        ],
      ),
    );
  }
}
