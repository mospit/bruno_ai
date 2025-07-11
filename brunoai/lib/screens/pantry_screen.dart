import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_colors.dart';
import '../animations/bruno_animations.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/bruno_avatar.dart';

class PantryScreen extends StatefulWidget {
  const PantryScreen({super.key});
  
  @override
  State<PantryScreen> createState() => _PantryScreenState();
}

class _PantryScreenState extends State<PantryScreen> {
  bool _isGridView = true;
  bool _showBrunoSidebar = false;
  String _searchQuery = '';
  String _selectedCategory = 'All';
  
  final List<String> _categories = [
    'All', 'Produce', 'Meat', 'Dairy', 'Pantry Staples', 'Frozen'
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.surfaceSecondary(context),
      appBar: _buildAppBar(),
      body: Consumer<BrunoProvider>(
        builder: (context, provider, child) => Stack(
          children: [
            Column(
              children: [
                _buildSearchAndFilter(),
                Expanded(
                  child: _buildPantryContent(provider),
                ),
                _buildSummaryBar(provider),
              ],
            ),
            if (_showBrunoSidebar) _buildBrunoSidebar(),
          ],
        ),
      ),
      floatingActionButton: _buildScanFAB(),
    );
  }
  
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text(
        'Pantry',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: AppColors.primary,
        ),
      ),
      backgroundColor: Colors.transparent,
      elevation: 0,
      actions: [
        // Grid/List toggle
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          decoration: BoxDecoration(
            color: AppColors.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: IconButton(
            icon: Icon(
              _isGridView ? Icons.view_list : Icons.grid_view,
              color: AppColors.primary,
            ),
            onPressed: () {
              HapticFeedback.lightImpact();
              setState(() {
                _isGridView = !_isGridView;
              });
            },
          ),
        ),
        // Filter button
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          decoration: BoxDecoration(
            color: const Color(0xFF228B22).withOpacity(0.1), // Deep Forest Green
            borderRadius: BorderRadius.circular(8),
          ),
          child: IconButton(
            icon: const Icon(
              Icons.filter_list,
              color: Color(0xFF228B22),
            ),
            onPressed: () {
              HapticFeedback.lightImpact();
              _showFilterDialog();
            },
          ),
        ),
      ],
    );
  }
  
  Widget _buildSearchAndFilter() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Search bar
          TextField(
            decoration: InputDecoration(
              hintText: 'Search pantry items...',
              prefixIcon: const Icon(
                Icons.search,
                color: AppColors.primary,
              ),
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
            ),
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
              });
            },
          ),
          const SizedBox(height: 12),
          // Category filter chips
          SizedBox(
            height: 40,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _categories.length,
              itemBuilder: (context, index) {
                final category = _categories[index];
                final isSelected = _selectedCategory == category;
                return Container(
                  margin: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(category),
                    selected: isSelected,
                    onSelected: (selected) {
                      HapticFeedback.lightImpact();
                      setState(() {
                        _selectedCategory = category;
                      });
                    },
                    selectedColor: const Color(0xFF228B22).withOpacity(0.2),
                    labelStyle: TextStyle(
                      color: isSelected ? const Color(0xFF228B22) : AppColors.textSecondary(context),
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildPantryContent(provider) {
    // Mock pantry data since provider might be empty
    final mockItems = [
      {'name': 'Rice', 'quantity': '2 lbs', 'daysLeft': 2, 'photo': '🍚'},
      {'name': 'Milk', 'quantity': '1 gallon', 'daysLeft': 1, 'photo': '🥛'},
      {'name': 'Bananas', 'quantity': '6 pieces', 'daysLeft': 3, 'photo': '🍌'},
      {'name': 'Chicken', 'quantity': '2 lbs', 'daysLeft': 5, 'photo': '🍗'},
      {'name': 'Bread', 'quantity': '1 loaf', 'daysLeft': 4, 'photo': '🍞'},
      {'name': 'Tomatoes', 'quantity': '1 lb', 'daysLeft': 7, 'photo': '🍅'},
    ];
    
    if (_isGridView) {
      return GridView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 0.8,
        ),
        itemCount: mockItems.length,
        itemBuilder: (context, index) {
          final item = mockItems[index];
          return _buildPantryItemCard(item);
        },
      );
    } else {
      return ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: mockItems.length,
        itemBuilder: (context, index) {
          final item = mockItems[index];
          return _buildPantryItemRow(item);
        },
      );
    }
  }
  
  Widget _buildPantryItemCard(Map<String, dynamic> item) {
    final daysLeft = item['daysLeft'] as int;
    final isExpiring = daysLeft <= 3;
    final isFresh = daysLeft > 7;
    
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        _showItemDetails(item);
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Item photo placeholder
                  Center(
                    child: Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: AppColors.gray100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          item['photo'],
                          style: const TextStyle(fontSize: 32),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  // Item name
                  Text(
                    item['name'],
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary(context),
                    ),
                  ),
                  const SizedBox(height: 4),
                  // Quantity
                  Text(
                    'Qty: ${item['quantity']}',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary(context),
                    ),
                  ),
                  const SizedBox(height: 4),
                  // Expiration
                  Text(
                    'Exp: ${daysLeft}d',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: isExpiring ? Colors.orange.shade700 : AppColors.textSecondary(context),
                      fontWeight: isExpiring ? FontWeight.w600 : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
            // Color status tag
            Positioned(
              top: 8,
              right: 8,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: isExpiring ? Colors.yellow : (isFresh ? Colors.green : Colors.orange),
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildPantryItemRow(Map<String, dynamic> item) {
    final daysLeft = item['daysLeft'] as int;
    final isExpiring = daysLeft <= 3;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Row(
        children: [
          // Photo
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: AppColors.gray100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                item['photo'],
                style: const TextStyle(fontSize: 24),
              ),
            ),
          ),
          const SizedBox(width: 16),
          // Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item['name'],
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Qty: ${item['quantity']}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                ),
              ],
            ),
          ),
          // Status and expiration
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isExpiring ? Colors.yellow.shade100 : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Exp: ${daysLeft}d',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isExpiring ? Colors.orange.shade700 : Colors.green.shade700,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildSummaryBar(provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.gray100,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Summary: 45 Items',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
          Text(
            '~\$120',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
          GestureDetector(
            onTap: () {
              HapticFeedback.lightImpact();
              setState(() {
                _showBrunoSidebar = !_showBrunoSidebar;
              });
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: AppColors.primary.withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  BrunoAvatar(
                    mood: BrunoMood.helpful,
                    size: 20,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Tips',
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildBrunoSidebar() {
    return Positioned(
      right: 0,
      top: 0,
      bottom: 100,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: _showBrunoSidebar ? 280 : 0,
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 16,
              offset: const Offset(-4, 0),
            ),
          ],
        ),
        child: _showBrunoSidebar ? Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                border: Border(
                  bottom: BorderSide(
                    color: AppColors.primary.withOpacity(0.2),
                    width: 1,
                  ),
                ),
              ),
              child: Row(
                children: [
                  BrunoAvatar(
                    mood: BrunoMood.helpful,
                    size: 32,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Bruno\'s Suggestions',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      setState(() {
                        _showBrunoSidebar = false;
                      });
                    },
                  ),
                ],
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildBrunoSuggestion(
                      '🥛 Use up milk before it expires!',
                      'Make pancakes or add to coffee',
                      Colors.orange,
                    ),
                    const SizedBox(height: 16),
                    _buildBrunoSuggestion(
                      '🍌 Bananas perfect for smoothies',
                      'Great for breakfast bowls too',
                      Colors.yellow.shade700,
                    ),
                    const SizedBox(height: 16),
                    _buildBrunoSuggestion(
                      '🍚 Rice pairs well with everything',
                      'Try making fried rice tonight',
                      Colors.green,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ) : null,
      ),
    );
  }
  
  Widget _buildBrunoSuggestion(String title, String subtitle, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: TextStyle(
              color: AppColors.textSecondary(context),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildScanFAB() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.instacartGreen.withOpacity(0.4),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: FloatingActionButton.extended(
        onPressed: () {
          HapticFeedback.lightImpact();
          _showScanOptions();
        },
        backgroundColor: AppColors.instacartGreen,
        icon: const Icon(
          Icons.camera_alt,
          color: Colors.white,
        ),
        label: const Text(
          'Scan/Add',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
  
  void _showFilterDialog() {
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
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Filter Options',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text('Sort by expiration date'),
                  Text('Show only expiring items'),
                  Text('Filter by location'),
                  const SizedBox(height: 20),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  void _showItemDetails(Map<String, dynamic> item) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        margin: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                item['name'],
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text('Quantity: ${item['quantity']}'),
              Text('Expires in: ${item['daysLeft']} days'),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Edit'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Use in Recipe'),
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
  
  void _showScanOptions() {
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
                  ListTile(
                    leading: const Icon(Icons.camera_alt, color: AppColors.instacartGreen),
                    title: const Text('Scan Barcode'),
                    subtitle: const Text('Scan item barcode to add'),
                    onTap: () {
                      Navigator.pop(context);
                      HapticFeedback.lightImpact();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Barcode scanning coming soon!'),
                          backgroundColor: AppColors.instacartGreen,
                        ),
                      );
                    },
                  ),
                  ListTile(
                    leading: const Icon(Icons.add, color: AppColors.primary),
                    title: const Text('Add Manually'),
                    subtitle: const Text('Enter item details manually'),
                    onTap: () {
                      Navigator.pop(context);
                      HapticFeedback.lightImpact();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Manual entry coming soon!'),
                          backgroundColor: AppColors.primary,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

