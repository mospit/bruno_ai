import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/bruno_avatar.dart';
import '../widgets/liquid_glass_container.dart';

class SmartDashboard extends StatefulWidget {
  final bool isCollapsed;
  final VoidCallback? onToggle;
  final bool showTrends;
  final bool enableHaptics;

  const SmartDashboard({
    super.key,
    this.isCollapsed = false,
    this.onToggle,
    this.showTrends = true,
    this.enableHaptics = true,
  });

  @override
  State<SmartDashboard> createState() => _SmartDashboardState();
}

class _SmartDashboardState extends State<SmartDashboard>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _progressController;
  late AnimationController _pulseController;
  late Animation<double> _heightAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<double> _progressAnimation;
  late Animation<double> _pulseAnimation;
  
  bool _showProgressDetails = false;
  String? _lastBudgetStatus;
  double _previousBudgetProgress = 0.0;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );

    _progressController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _heightAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOutCubic,
    ));

    _opacityAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeIn,
    ));

    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _progressController,
      curve: Curves.easeOutQuart,
    ));

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    if (!widget.isCollapsed) {
      _animationController.forward();
    }
    
    _progressController.forward();
  }

  @override
  void didUpdateWidget(SmartDashboard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.isCollapsed != widget.isCollapsed) {
      if (widget.isCollapsed) {
        _animationController.reverse();
      } else {
        _animationController.forward();
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _progressController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  double _calculateBudgetProgress(BrunoProvider provider) {
    if (provider.currentBudget.isEmpty) return 0.0;
    final budget = double.tryParse(provider.currentBudget) ?? 0.0;
    if (budget <= 0) return 0.0;
    return (provider.totalCost / budget).clamp(0.0, 1.0);
  }

  double _calculateSavings(BrunoProvider provider) {
    return provider.shoppingList.fold(0.0, (total, item) => total + item.savings);
  }

  BrunoMood _getBudgetMood(double progress) {
    if (progress > 0.95) return BrunoMood.concerned;
    if (progress > 0.8) return BrunoMood.thinking;
    if (progress > 0.5) return BrunoMood.helpful;
    return BrunoMood.celebrating;
  }

  void _triggerHapticFeedback() {
    if (widget.enableHaptics) {
      HapticFeedback.lightImpact();
    }
  }

  void _checkBudgetChanges(double currentProgress) {
    // Trigger pulse animation if budget status changed significantly
    if ((currentProgress - _previousBudgetProgress).abs() > 0.1) {
      _pulseController.forward().then((_) => _pulseController.reverse());
      _previousBudgetProgress = currentProgress;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        final budgetProgress = _calculateBudgetProgress(provider);
        final savings = _calculateSavings(provider);
        final budget = double.tryParse(provider.currentBudget.isEmpty ? "0" : provider.currentBudget) ?? 0.0;
        
        // Check for budget changes
        _checkBudgetChanges(budgetProgress);

        return AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: budgetProgress > 0.9 ? _pulseAnimation.value : 1.0,
                child: LiquidGlassContainer(
                margin: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                padding: const EdgeInsets.all(24),
                borderRadius: BorderRadius.circular(28),
                shadows: [
                  BoxShadow(
                    color: AppColors.shadowMedium,
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                    spreadRadius: 0,
                  ),
                  BoxShadow(
                    color: AppColors.shadowLight,
                    blurRadius: 40,
                    offset: const Offset(0, 16),
                    spreadRadius: 0,
                  ),
                ],
                child: Column(
                  children: [
                    // Enhanced Header with interactive Bruno avatar
                    GestureDetector(
                      onTap: () {
                        _triggerHapticFeedback();
                        setState(() {
                          _showProgressDetails = !_showProgressDetails;
                        });
                      },
                      child: Row(
                        children: [
                          BrunoAvatar(
                            mood: _getBudgetMood(budgetProgress),
                            size: 45,
                            showBudgetProgress: budget > 0,
                            budgetProgress: budgetProgress,
                            isBreathing: true,
                            showSpeechBubble: budgetProgress > 0.9,
                            speechText: budgetProgress > 0.95 ? "Watch spending!" : "Almost there!",
                            enableHaptics: widget.enableHaptics,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Text(
                                      'Smart Dashboard',
                                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    if (widget.showTrends && budget > 0)
                                      Padding(
                                        padding: const EdgeInsets.only(left: 8),
                                        child: _buildTrendIndicator(budgetProgress),
                                      ),
                                  ],
                                ),
                                if (budget > 0)
                                  AnimatedSwitcher(
                                    duration: const Duration(milliseconds: 300),
                                    child: Text(
                                      _getBudgetStatusText(budgetProgress, provider.totalCost, budget),
                                      key: ValueKey(_getBudgetStatusText(budgetProgress, provider.totalCost, budget)),
                                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                        color: _getBudgetStatusColor(budgetProgress),
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          IconButton(
                            onPressed: () {
                              _triggerHapticFeedback();
                              widget.onToggle?.call();
                            },
                            icon: AnimatedRotation(
                              turns: widget.isCollapsed ? 0.0 : 0.5,
                              duration: const Duration(milliseconds: 400),
                              child: Icon(
                                Icons.expand_more_rounded,
                                color: Theme.of(context).primaryColor,
                                size: 28,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Enhanced Collapsible content
                    AnimatedBuilder(
                      animation: _heightAnimation,
                      builder: (context, child) {
                        return SizeTransition(
                          sizeFactor: _heightAnimation,
                          child: FadeTransition(
                            opacity: _opacityAnimation,
                            child: Column(
                              children: [
                                const SizedBox(height: 20),

                                // Enhanced Budget Progress with details
                                if (budget > 0) ...[
                                  _buildEnhancedBudgetProgress(context, provider, budgetProgress, budget),
                                  const SizedBox(height: 24),
                                ],

                                // Enhanced Quick Stats with animations
                                _buildEnhancedQuickStats(context, provider, savings),

                                // Smart Quick Actions
                                if (!widget.isCollapsed) ...[
                                  const SizedBox(height: 20),
                                  _buildSmartQuickActions(context, provider),
                                ],
                                const SizedBox(height: 4),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildTrendIndicator(double progress) {
    IconData icon;
    Color color;
    
    if (progress > _previousBudgetProgress) {
      icon = Icons.trending_up_rounded;
      color = Colors.red;
    } else if (progress < _previousBudgetProgress) {
      icon = Icons.trending_down_rounded;
      color = Colors.green;
    } else {
      icon = Icons.trending_flat_rounded;
      color = Colors.grey;
    }

    return Icon(
      icon,
      size: 16,
      color: color,
    );
  }

  Widget _buildEnhancedBudgetProgress(BuildContext context, BrunoProvider provider, double progress, double budget) {
    return GestureDetector(
      onTap: () {
        _triggerHapticFeedback();
        setState(() {
          _showProgressDetails = !_showProgressDetails;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: _showProgressDetails ? 140 : 120,
        height: _showProgressDetails ? 140 : 120,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Background circle
            SizedBox(
              width: _showProgressDetails ? 140 : 120,
              height: _showProgressDetails ? 140 : 120,
              child: CircularProgressIndicator(
                value: 1.0,
                strokeWidth: _showProgressDetails ? 10 : 8,
                backgroundColor: Colors.transparent,
                valueColor: AlwaysStoppedAnimation<Color>(
                  Colors.grey.withOpacity(0.15),
                ),
              ),
            ),
            // Animated Progress circle
            AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return SizedBox(
                  width: _showProgressDetails ? 140 : 120,
                  height: _showProgressDetails ? 140 : 120,
                  child: CircularProgressIndicator(
                    value: progress * _progressAnimation.value,
                    strokeWidth: _showProgressDetails ? 10 : 8,
                    backgroundColor: Colors.transparent,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _getBudgetStatusColor(progress),
                    ),
                  ),
                );
              },
            ),
            // Enhanced Center content with details
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: _showProgressDetails
                  ? _buildDetailedProgress(context, provider, progress, budget)
                  : _buildSimpleProgress(context, provider, progress, budget),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSimpleProgress(BuildContext context, BrunoProvider provider, double progress, double budget) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '\$${provider.totalCost.toStringAsFixed(0)}',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: _getBudgetStatusColor(progress),
          ),
        ),
        Text(
          '/ \$${budget.toStringAsFixed(0)}',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
          ),
        ),
        Text(
          '${(progress * 100).toStringAsFixed(0)}%',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: _getBudgetStatusColor(progress),
          ),
        ),
      ],
    );
  }

  Widget _buildDetailedProgress(BuildContext context, BrunoProvider provider, double progress, double budget) {
    final remaining = budget - provider.totalCost;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '\$${provider.totalCost.toStringAsFixed(2)}',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: _getBudgetStatusColor(progress),
          ),
        ),
        Text(
          'of \$${budget.toStringAsFixed(0)}',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.6),
            fontSize: 10,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          '${(progress * 100).toStringAsFixed(1)}%',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: _getBudgetStatusColor(progress),
            fontSize: 11,
          ),
        ),
        Text(
          remaining > 0 ? '\$${remaining.toStringAsFixed(0)} left' : 'Over budget',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: remaining > 0 ? Colors.green : Colors.red,
            fontSize: 9,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildEnhancedQuickStats(BuildContext context, BrunoProvider provider, double savings) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildEnhancedQuickStat(
            context,
            'Items',
            '${provider.shoppingList.length}',
            Icons.inventory_2_rounded,
            Theme.of(context).primaryColor,
            null, // Removed cart functionality from dashboard
          ),
          _buildEnhancedQuickStat(
            context,
            'Saved',
            '\$${savings.toStringAsFixed(0)}',
            Icons.savings_rounded,
            Colors.green,
            () => _showSavingsBreakdown(context, provider),
          ),
          _buildEnhancedQuickStat(
            context,
            'Store',
            provider.selectedStore.isEmpty ? 'None' : _truncateStoreName(provider.selectedStore),
            Icons.store_rounded,
            Theme.of(context).primaryColor,
            () => _showStoreOptions(context, provider),
          ),
        ],
      ),
    );
  }

  Widget _buildEnhancedQuickStat(BuildContext context, String label, String value, IconData icon, Color color, VoidCallback? onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: () {
          _triggerHapticFeedback();
          onTap?.call();
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: color.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 22,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                value,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                  fontSize: 11,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSmartQuickActions(BuildContext context, BrunoProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        children: [
          Expanded(
            child: _buildSmartActionButton(
              context,
              'Set Budget',
              Icons.attach_money_rounded,
              () => _showEnhancedBudgetDialog(context, provider),
              Theme.of(context).primaryColor,
              provider.currentBudget.isEmpty,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: _buildSmartActionButton(
              context,
              'Plan Week',
              Icons.calendar_today_rounded,
              () => _triggerWeekPlanning(context, provider),
              Colors.blue,
              false,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: _buildSmartActionButton(
              context,
              'Recipes',
              Icons.restaurant_menu_rounded,
              () => _showRecipeLibrary(context, provider),
              Colors.orange,
              false,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSmartActionButton(BuildContext context, String label, IconData icon, VoidCallback onPressed, Color color, bool isHighlighted) {
    return GestureDetector(
      onTap: () {
        _triggerHapticFeedback();
        onPressed();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 10),
        decoration: BoxDecoration(
          color: isHighlighted ? color.withOpacity(0.15) : color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isHighlighted ? color.withOpacity(0.4) : color.withOpacity(0.2),
            width: isHighlighted ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: color,
              size: 18,
            ),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: isHighlighted ? FontWeight.bold : FontWeight.w600,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBudgetProgress(BuildContext context, BrunoProvider provider, double progress, double budget) {
    return Container(
      width: 120,
      height: 120,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          SizedBox(
            width: 120,
            height: 120,
            child: CircularProgressIndicator(
              value: 1.0,
              strokeWidth: 8,
              backgroundColor: Colors.transparent,
              valueColor: AlwaysStoppedAnimation<Color>(
                Colors.grey.withOpacity(0.2),
              ),
            ),
          ),
          // Progress circle
          SizedBox(
            width: 120,
            height: 120,
            child: CircularProgressIndicator(
              value: progress,
              strokeWidth: 8,
              backgroundColor: Colors.transparent,
              valueColor: AlwaysStoppedAnimation<Color>(
                _getBudgetStatusColor(progress),
              ),
            ),
          ),
          // Center content
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '\$${provider.totalCost.toStringAsFixed(0)}',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: _getBudgetStatusColor(progress),
                ),
              ),
              Text(
                '/ \$${budget.toStringAsFixed(0)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                ),
              ),
              Text(
                '${(progress * 100).toStringAsFixed(0)}%',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: _getBudgetStatusColor(progress),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context, BrunoProvider provider, double savings) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildQuickStat(
          context,
          'Cart',
          '${provider.shoppingList.length}',
          Icons.shopping_cart_rounded,
          Theme.of(context).primaryColor,
        ),
        _buildQuickStat(
          context,
          'Saved',
          '\$${savings.toStringAsFixed(0)}',
          Icons.savings_rounded,
          Colors.green,
        ),
        _buildQuickStat(
          context,
          'Store',
          provider.selectedStore.isEmpty ? 'None' : _truncateStoreName(provider.selectedStore),
          Icons.store_rounded,
          Theme.of(context).primaryColor,
        ),
      ],
    );
  }

  Widget _buildQuickStat(BuildContext context, String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                color: color,
                size: 20,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
              textAlign: TextAlign.center,
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context, BrunoProvider provider) {
    return Row(
      children: [
        Expanded(
          child: _buildQuickActionButton(
            context,
            'Set Budget',
            Icons.attach_money_rounded,
            () => _showBudgetDialog(context, provider),
            Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildQuickActionButton(
            context,
            'Plan Week',
            Icons.calendar_today_rounded,
            () => _triggerWeekPlanning(context, provider),
            Colors.blue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildQuickActionButton(
            context,
            'View Cart',
            Icons.shopping_cart_checkout_rounded,
            () => _showShoppingCart(context),
            Colors.green,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionButton(BuildContext context, String label, IconData icon, VoidCallback onPressed, Color color) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3), width: 1),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getBudgetStatusText(double progress, double spent, double budget) {
    final remaining = budget - spent;
    
    if (progress > 0.95) {
      return 'Over budget by \$${(spent - budget).toStringAsFixed(2)}';
    } else if (progress > 0.8) {
      return '\$${remaining.toStringAsFixed(2)} remaining';
    } else {
      return 'On track! \$${remaining.toStringAsFixed(2)} left';
    }
  }

  Color _getBudgetStatusColor(double progress) {
    if (progress > 0.95) return Colors.red;
    if (progress > 0.8) return Colors.orange;
    return Colors.green;
  }

  String _truncateStoreName(String storeName) {
    if (storeName.length > 8) {
      return '${storeName.substring(0, 8)}...';
    }
    return storeName;
  }

  void _showBudgetDialog(BuildContext context, BrunoProvider provider) {
    final TextEditingController budgetController = TextEditingController(
      text: provider.currentBudget,
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrunoAvatar(mood: BrunoMood.helpful, size: 50),
              const SizedBox(height: 16),
              Text(
                'Set Your Weekly Budget',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: budgetController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Budget Amount',
                  prefixText: '\$',
                  hintText: '80',
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: LiquidGlassButton(
                      onPressed: () => Navigator.pop(context),
                      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                      foregroundColor: Theme.of(context).primaryColor,
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: LiquidGlassButton(
                      onPressed: () {
                        provider.setBudget(budgetController.text);
                        Navigator.pop(context);
                      },
                      backgroundColor: Theme.of(context).primaryColor,
                      foregroundColor: Colors.white,
                      child: const Text('Set Budget'),
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

  void _triggerWeekPlanning(BuildContext context, BrunoProvider provider) {
    _triggerHapticFeedback();
    provider.sendMessageToBruno('Plan meals for this week within my budget');
  }

  void _showRecipeLibrary(BuildContext context, BrunoProvider provider) {
    _triggerHapticFeedback();
    provider.sendMessageToBruno('Show me quick and healthy recipe options');
  }

  void _showSavingsBreakdown(BuildContext context, BrunoProvider provider) {
    _triggerHapticFeedback();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrunoAvatar(mood: BrunoMood.celebrating, size: 40),
              const SizedBox(height: 12),
              Text(
                'Your Savings',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              ...provider.shoppingList.where((item) => item.savings > 0).map(
                (item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          item.name,
                          style: Theme.of(context).textTheme.bodySmall,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        '\$${item.savings.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showStoreOptions(BuildContext context, BrunoProvider provider) {
    _triggerHapticFeedback();
    // Show store selection options
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrunoAvatar(mood: BrunoMood.helpful, size: 40),
              const SizedBox(height: 12),
              Text(
                'Store Options',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Store selection coming soon!',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showEnhancedBudgetDialog(BuildContext context, BrunoProvider provider) {
    final TextEditingController budgetController = TextEditingController(
      text: provider.currentBudget,
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.transparent,
        content: LiquidGlassContainer(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrunoAvatar(
                mood: BrunoMood.helpful,
                size: 50,
                showSpeechBubble: true,
                speechText: "Let's set your budget!",
              ),
              const SizedBox(height: 20),
              Text(
                'Set Your Weekly Budget',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Bruno will help you stay on track!',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              TextField(
                controller: budgetController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Budget Amount',
                  prefixText: '\$',
                  hintText: '80',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Theme.of(context).cardColor.withOpacity(0.5),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                        foregroundColor: Theme.of(context).primaryColor,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        _triggerHapticFeedback();
                        provider.setBudget(budgetController.text);
                        Navigator.pop(context);
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        backgroundColor: Theme.of(context).primaryColor,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('Set Budget'),
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

  void _showShoppingCart(BuildContext context) {
    _triggerHapticFeedback();
    // This would trigger the shopping cart modal
    // Implementation depends on how the shopping cart is currently shown
    Navigator.pushNamed(context, '/shopping-cart');
  }
}
