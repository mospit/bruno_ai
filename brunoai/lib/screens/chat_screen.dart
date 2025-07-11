import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/chat_interface.dart';
import '../widgets/bruno_avatar.dart';
import '../theme/app_colors.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  late AnimationController _headerAnimationController;
  late Animation<double> _headerAnimation;
  
  @override
  void initState() {
    super.initState();
    _headerAnimationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _headerAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _headerAnimationController,
        curve: Curves.easeOutBack,
      ),
    );
    _headerAnimationController.forward();
  }
  
  @override
  void dispose() {
    _headerAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            backgroundColor: AppColors.background,
            elevation: 0,
            toolbarHeight: 80,
            flexibleSpace: SafeArea(
              child: AnimatedBuilder(
                animation: _headerAnimation,
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(0, 20 * (1 - _headerAnimation.value)),
                    child: Opacity(
                      opacity: _headerAnimation.value,
                      child: _buildEnhancedHeader(context, provider),
                    ),
                  );
                },
              ),
            ),
            actions: [
              IconButton(
                icon: Icon(
                  Icons.more_vert,
                  color: AppColors.primary,
                ),
                onPressed: () {
                  HapticFeedback.lightImpact();
                  _showChatOptions(context);
                },
                tooltip: 'Chat options',
              ),
              const SizedBox(width: 8),
            ],
          ),
          body: const ChatInterface(),
        );
      },
    );
  }
  
  Widget _buildEnhancedHeader(BuildContext context, BrunoProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Enhanced Bruno Avatar with mood indication
          Stack(
            children: [
              BrunoAvatar(
                mood: _getBrunoMoodFromState(provider),
                size: 48,
                animate: true,
                isBreathing: true,
                onTap: () {
                  HapticFeedback.mediumImpact();
                  _showBrunoStatus(context, provider);
                },
              ),
              // Activity indicator
              if (provider.isTyping)
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: Container(
                    width: 16,
                    height: 16,
                    decoration: BoxDecoration(
                      color: AppColors.instacartGreen,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppColors.white,
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.instacartGreen.withOpacity(0.3),
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: Icon(
                      Icons.more_horiz,
                      size: 8,
                      color: AppColors.white,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: 16),
          // Enhanced header text with dynamic content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Bruno',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.instacartGreen.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'AI',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: AppColors.instacartGreen,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  provider.isTyping ? 'Chatting...' : _getStatusText(provider),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  BrunoMood _getBrunoMoodFromState(BrunoProvider provider) {
    if (provider.isTyping) return BrunoMood.thinking;
    if (provider.messages.isNotEmpty) {
      final lastMessage = provider.messages.last;
      if (lastMessage.isFromUser) return BrunoMood.helpful;
      if (lastMessage.text.toLowerCase().contains('great') ||
          lastMessage.text.toLowerCase().contains('awesome') ||
          lastMessage.text.toLowerCase().contains('perfect')) {
        return BrunoMood.excited;
      }
    }
    return BrunoMood.friendly;
  }
  
  String _getStatusText(BrunoProvider provider) {
    if (provider.isTyping) return 'Bruno is thinking...';
    if (provider.messages.isEmpty) return 'Ready to help with meal planning';
    return 'Online • Your AI kitchen companion';
  }
  
  void _showChatOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
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
            Text(
              'Chat Options',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 20),
            _buildChatOption(
              context,
              icon: Icons.clear_all,
              title: 'Clear Chat History',
              subtitle: 'Start fresh with Bruno',
              onTap: () {
                Navigator.pop(context);
                _showClearConfirmation(context);
              },
            ),
            _buildChatOption(
              context,
              icon: Icons.download,
              title: 'Export Chat',
              subtitle: 'Save conversation history',
              onTap: () {
                Navigator.pop(context);
                // Export functionality
              },
            ),
            _buildChatOption(
              context,
              icon: Icons.feedback,
              title: 'Send Feedback',
              subtitle: 'Help improve Bruno',
              onTap: () {
                Navigator.pop(context);
                // Feedback functionality
              },
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildChatOption(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: AppColors.primary,
      ),
      title: Text(
        title,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          color: AppColors.textSecondary(context),
        ),
      ),
      onTap: onTap,
    );
  }
  
  void _showClearConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Clear Chat History?',
          style: TextStyle(color: AppColors.primary),
        ),
        content: const Text(
          'This will permanently delete all messages with Bruno. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<BrunoProvider>().clearChatHistory();
              HapticFeedback.lightImpact();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
            ),
            child: const Text('Clear', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
  
  void _showBrunoStatus(BuildContext context, BrunoProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            BrunoAvatar(
              mood: _getBrunoMoodFromState(provider),
              size: 32,
              animate: true,
            ),
            const SizedBox(width: 12),
            Text(
              'Bruno Status',
              style: TextStyle(color: AppColors.primary),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${_getStatusText(provider)}'),
            const SizedBox(height: 8),
            Text('Mood: ${_getBrunoMoodFromState(provider).name}'),
            const SizedBox(height: 8),
            Text('Messages: ${provider.messages.length}'),
            if (provider.currentBudget.isNotEmpty)
              Text('Budget: \$${provider.currentBudget}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
