import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../models/chat_message.dart';
import '../theme/app_colors.dart';
import '../controllers/voice_input_controller.dart';
import 'liquid_glass_container.dart';
import 'bruno_avatar.dart';
import 'meal_card.dart';
import 'voice_input_button.dart';
import 'dart:math' as math;

class ChatInterface extends StatefulWidget {
  const ChatInterface({super.key});

  @override
  State<ChatInterface> createState() => _ChatInterfaceState();
}

class _ChatInterfaceState extends State<ChatInterface>
    with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final VoiceInputController _voiceController = VoiceInputController();
  late AnimationController _typingAnimationController;
  late Animation<double> _typingAnimation;

  @override
  void initState() {
    super.initState();
    _typingAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _typingAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _typingAnimationController,
      curve: Curves.easeInOut,
    ));
    _typingAnimationController.repeat(reverse: true);
    
    // Initialize voice controller
    _voiceController.initialize();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _typingAnimationController.dispose();
    _voiceController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _sendMessage() {
    final message = _messageController.text.trim();
    if (message.isNotEmpty) {
      context.read<BrunoProvider>().sendMessageToBruno(message);
      _messageController.clear();
      _scrollToBottom();
    }
  }
  
  void _onVoiceRecognitionComplete(String recognizedText) {
    if (recognizedText.isNotEmpty) {
      // Append recognized text to current text or replace if empty
      final currentText = _messageController.text.trim();
      if (currentText.isEmpty) {
        _messageController.text = recognizedText;
      } else {
        _messageController.text = '$currentText $recognizedText';
      }
      
      // Move cursor to end
      _messageController.selection = TextSelection.fromPosition(
        TextPosition(offset: _messageController.text.length),
      );
      
      // Refresh UI
      setState(() {});
      
      // Show feedback
      if (_voiceController.recognizedText.isNotEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.mic_rounded, color: Colors.white, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Voice input: "$recognizedText"',
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            backgroundColor: Theme.of(context).primaryColor,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Column(
          children: [
            // Messages List
            Expanded(
              child: _buildChatMessages(provider),
            ),
            
            // Typing Indicator
            if (provider.isTyping) _buildTypingIndicator(),
            
            // Message Input
            _buildMessageInput(),
          ],
        );
      },
    );
  }


  Widget _buildChatMessages(BrunoProvider provider) {
    return ListView(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      children: [
        // Sample conversation matching wireframe
        _buildWireframeBrunoMessage("Got your query..."),
        _buildRefineButtonRow(),
        const SizedBox(height: 16),
        
        _buildWireframeUserMessage("Caribbean for 4 \$200"),
        const SizedBox(height: 16),
        
        _buildWireframeBrunoMessage("Here's a plan..."),
        _buildSampleList(),
        _buildFeedbackButtons(),
        
        const SizedBox(height: 20),
      ],
    );
  }
  
  Widget _buildMessagesList(BrunoProvider provider) {
    if (provider.messages.isEmpty) {
      return _buildWelcomeScreen(provider);
    }
    
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: provider.messages.length,
      itemBuilder: (context, index) {
        final message = provider.messages[index];
        return _buildMessageBubble(message);
      },
    );
  }
  
  Widget _buildWelcomeScreen(BrunoProvider provider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          const SizedBox(height: 60),
          
          // Bruno's welcome message
          LiquidGlassContainer(
            padding: const EdgeInsets.all(32),
            borderRadius: BorderRadius.circular(32),
            shadows: [
              BoxShadow(
                color: AppColors.shadowMedium,
                blurRadius: 24,
                offset: const Offset(0, 12),
                spreadRadius: 0,
              ),
              BoxShadow(
                color: AppColors.shadowLight,
                blurRadius: 48,
                offset: const Offset(0, 24),
                spreadRadius: 0,
              ),
            ],
            child: Column(
              children: [
                BrunoAvatar(
                  mood: BrunoMood.friendly,
                  size: 120,
                  animate: true,
                ),
                const SizedBox(height: 20),
                Text(
                  '👋 Hi there! I\'m Bruno',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Text(
                  'Your friendly AI bear with meal planning superpowers! I can help you create delicious meals within your budget and get everything delivered through Instacart.',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Theme.of(context).textTheme.bodyLarge?.color?.withOpacity(0.8),
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Quick start options
          Text(
            'Quick Start',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: AppColors.gray900,
            ),
          ),
          const SizedBox(height: 20),
          
          // Quick action cards
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  context,
                  icon: Icons.restaurant_menu_rounded,
                  title: 'Plan Meals',
                  subtitle: 'Weekly meal planning',
                  onTap: () => _quickSendMessage('Help me plan meals for this week'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  context,
                  icon: Icons.attach_money_rounded,
                  title: 'Set Budget',
                  subtitle: 'Budget-friendly options',
                  onTap: () => _quickSendMessage('My weekly budget is \$80'),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  context,
                  icon: Icons.local_grocery_store_rounded,
                  title: 'Quick Shop',
                  subtitle: 'Fast ingredient lookup',
                  onTap: () => _quickSendMessage('I need ingredients for chicken dinner'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  context,
                  icon: Icons.favorite_rounded,
                  title: 'Favorites',
                  subtitle: 'Reorder past meals',
                  onTap: () => _showFavorites(context, provider),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Sample conversations
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.8),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 20,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.lightbulb_outline_rounded,
                      color: Theme.of(context).primaryColor,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Try asking me...',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ..._buildSampleQuestions(),
              ],
            ),
          ),
          
          const SizedBox(height: 40),
        ],
      ),
    );
  }
  
  Widget _buildQuickActionCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.gray200,
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 16,
            offset: const Offset(0, 6),
            spreadRadius: 0,
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    icon,
                    color: AppColors.primary,
                    size: 28,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  List<Widget> _buildSampleQuestions() {
    final questions = [
      '"Plan 5 meals for \$60 this week"',
      '"I need a quick chicken recipe"',
      '"Find vegetarian options under \$15"',
      '"Reorder my last grocery list"',
    ];
    
    return questions.map((question) {
      return Container(
        margin: const EdgeInsets.only(bottom: 8),
        child: GestureDetector(
          onTap: () => _quickSendMessage(question.replaceAll('"', '')),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 16,
                  color: Theme.of(context).primaryColor.withOpacity(0.7),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    question,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).primaryColor,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_rounded,
                  size: 16,
                  color: Theme.of(context).primaryColor.withOpacity(0.5),
                ),
              ],
            ),
          ),
        ),
      );
    }).toList();
  }
  
  void _quickSendMessage(String message) {
    _messageController.text = message;
    _sendMessage();
  }
  
  void _showFavorites(BuildContext context, BrunoProvider provider) {
    if (provider.favoriteMeals.isEmpty) {
      _quickSendMessage('Show me some popular meal options');
      return;
    }
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.9,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
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
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Icon(
                      Icons.favorite_rounded,
                      color: Theme.of(context).primaryColor,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Favorite Meals',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: provider.favoriteMeals.length,
                  itemBuilder: (context, index) {
                    final meal = provider.favoriteMeals[index];
                    return _buildFavoriteMealCard(context, meal, provider);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildFavoriteMealCard(BuildContext context, dynamic meal, BrunoProvider provider) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
                          fontWeight: FontWeight.bold,
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
                Text(
                  '\$${meal.estimatedCost.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.people_rounded,
                  size: 16,
                  color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                ),
                const SizedBox(width: 4),
                Text(
                  '${meal.servings} servings',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(width: 16),
                Icon(
                  Icons.schedule_rounded,
                  size: 16,
                  color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                ),
                const SizedBox(width: 4),
                Text(
                  '${meal.cookingTime} min',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
            const SizedBox(height: 12),
            LiquidGlassButton(
              onPressed: () {
                Navigator.pop(context);
                _quickSendMessage('I want to reorder ${meal.name}');
              },
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.add_shopping_cart_rounded, size: 18),
                  const SizedBox(width: 8),
                  const Text('Reorder'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.isUser;
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            Container(
              margin: const EdgeInsets.only(right: 12, bottom: 4),
              child: BrunoAvatar(
                mood: message.message.getBrunoMood(),
                size: 40,
                animate: true,
                isBreathing: false,
                enableHaptics: true,
              ),
            ),
          ],
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
                minWidth: 120,
              ),
              child: Column(
                crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                children: [
                  // Main message bubble
                  Container(
                    decoration: BoxDecoration(
                      // Brown bubble for Bruno, beige for user
                      color: isUser
                          ? const Color(0xFFF5F1E8) // Beige color
                          : const Color(0xFF8B4513), // Brown color
                      borderRadius: _getBubbleBorderRadius(isUser),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                          spreadRadius: 0,
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      child: _buildMessageContent(context, message, isUser),
                    ),
                  ),
                  
                  // Inline refine button for user messages
                  if (isUser && message.message.contains('budget')) ...[
                    const SizedBox(height: 8),
                    Container(
                      margin: const EdgeInsets.only(right: 12),
                      child: _buildRefineButton(),
                    ),
                  ],
                  
                  // Suggestion chips (only for Bruno messages)
                  if (!isUser && message.suggestions.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Container(
                      margin: const EdgeInsets.only(left: 12),
                      child: Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: message.suggestions.map((suggestion) {
                          return _buildSuggestionChip(suggestion);
                        }).toList(),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (isUser) ...[
            Container(
              width: 40,
              height: 40,
              margin: const EdgeInsets.only(left: 12, bottom: 4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF8B4513), // Brown color for user avatar
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(
                Icons.person_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
          ],
        ],
      ),
    );
  }
  
  BorderRadius _getBubbleBorderRadius(bool isUser) {
    if (isUser) {
      return const BorderRadius.only(
        topLeft: Radius.circular(20),
        topRight: Radius.circular(20),
        bottomLeft: Radius.circular(20),
        bottomRight: Radius.circular(6),
      );
    } else {
      return const BorderRadius.only(
        topLeft: Radius.circular(6),
        topRight: Radius.circular(20),
        bottomLeft: Radius.circular(20),
        bottomRight: Radius.circular(20),
      );
    }
  }
  
  String _formatMessageTime(DateTime time) {
    final hour = time.hour;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = hour >= 12 ? 'PM' : 'AM';
    final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
    return '$displayHour:$minute $period';
  }

  Widget _buildSuggestionChip(String suggestion) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        _messageController.text = suggestion;
        _sendMessage();
      },
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Theme.of(context).primaryColor.withOpacity(0.08),
              Theme.of(context).primaryColor.withOpacity(0.12),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Theme.of(context).primaryColor.withOpacity(0.2),
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
              spreadRadius: 0,
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          child: Text(
            suggestion,
            style: TextStyle(
              color: Theme.of(context).primaryColor,
              fontSize: 13,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.1,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRefineButton() {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        // Show refine options or edit previous message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Refine functionality coming soon!'),
            backgroundColor: const Color(0xFF8B4513), // Brown color
          ),
        );
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xFF8B4513), // Brown color
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
              spreadRadius: 0,
            ),
          ],
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.tune_rounded,
              color: Colors.white,
              size: 14,
            ),
            SizedBox(width: 4),
            Text(
              'Refine',
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        children: [
          Container(
            margin: const EdgeInsets.only(right: 10, bottom: 4),
            child: BrunoAvatar(
              mood: BrunoMood.thinking,
              size: 36,
              animate: true,
              isBreathing: false,
              enableHaptics: false,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Colors.white,
                  Colors.grey[50]!,
                ],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(6),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
              border: Border.all(
                color: Colors.grey.withOpacity(0.12),
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.02),
                  blurRadius: 4,
                  offset: const Offset(0, 1),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Bruno is thinking',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(width: 12),
                AnimatedBuilder(
                  animation: _typingAnimation,
                  builder: (context, child) {
                    return Row(
                      children: List.generate(3, (index) {
                        final delay = index * 0.2;
                        final animationValue = math.max(
                          0.0,
                          math.min(
                            1.0,
                            (_typingAnimation.value - delay) / 0.6,
                          ),
                        );
                        return Container(
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          child: Transform.translate(
                            offset: Offset(0, -3 * animationValue),
                            child: Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: Theme.of(context).primaryColor.withOpacity(
                                  0.4 + 0.6 * animationValue,
                                ),
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                        );
                      }),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageInput() {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Container(
          padding: const EdgeInsets.fromLTRB(16, 20, 16, 24),
          decoration: BoxDecoration(
            color: AppColors.surfaceSecondary(context), // Use secondary surface color from theme
            boxShadow: [
              BoxShadow(
                color: AppColors.shadowMedium,
                blurRadius: 16,
                offset: const Offset(0, -4),
                spreadRadius: 0,
              ),
              BoxShadow(
                color: AppColors.shadowLight,
                blurRadius: 8,
                offset: const Offset(0, -2),
                spreadRadius: 0,
              ),
            ],
          ),
          child: SafeArea(
            top: false,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Quick suggestion chips (only on empty state)
                if (provider.messages.isEmpty && provider.shoppingList.isEmpty)
                  _buildQuickSuggestionChips(context, provider),
                
                // Main input area
                Container(
                  constraints: const BoxConstraints(
                    minHeight: 56,
                  ),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor, // Solid background from theme
                    borderRadius: BorderRadius.circular(32),
                    border: Border.all(
                      color: AppColors.border(context),
                      width: 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.shadowLight,
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                        spreadRadius: 0,
                      ),
                    ],
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // Text input field
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: TextField(
                            controller: _messageController,
                            decoration: InputDecoration(
                              hintText: _getSmartPlaceholder(),
                              border: InputBorder.none,
                              focusedBorder: InputBorder.none,
                              enabledBorder: InputBorder.none,
                              fillColor: Colors.transparent, // Make TextField transparent
                              filled: false, // Don't fill the TextField
                              contentPadding: const EdgeInsets.symmetric(vertical: 16),
                              hintStyle: TextStyle(
                                color: AppColors.textSecondary(context).withOpacity(0.6),
                                fontSize: 15,
                                fontWeight: FontWeight.w400,
                              ),
                            ),
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w400,
                            color: AppColors.textPrimary(context), // Use theme text color
                          ),
                          maxLines: 5,
                          minLines: 1,
                          textCapitalization: TextCapitalization.sentences,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => _sendMessage(),
                          onChanged: (_) => setState(() {}),
                          ),
                        ),
                      ),
                      
                      // Voice input button when empty, send button when text present
                      _messageController.text.trim().isEmpty
                          ? Container(
                              width: 48,
                              height: 48,
                              margin: const EdgeInsets.all(4),
                              child: VoiceInputButton(
                                voiceController: _voiceController,
                                onTap: () => _onVoiceRecognitionComplete(_voiceController.recognizedText),
                                size: 48.0,
                              ),
                            )
                          : Container(
                              width: 48,
                              height: 48,
                              margin: const EdgeInsets.all(4),
                              decoration: BoxDecoration(
                                color: Theme.of(context).primaryColor,
                                borderRadius: BorderRadius.circular(24),
                              ),
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(24),
                                  onTap: () {
                                    HapticFeedback.lightImpact();
                                    _sendMessage();
                                  },
                                  child: const Icon(
                                    Icons.arrow_upward_rounded,
                                    color: Colors.white,
                                    size: 20,
                                  ),
                                ),
                              ),
                            ),
                    ],
                  ),
                ),
                
                // Bottom spacing only - cart moved to main UI
                const SizedBox(height: 8),
              ],
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildQuickSuggestionChips(BuildContext context, BrunoProvider provider) {
    final suggestions = [
      'Set \$80 budget',
      'Plan this week',
      'Quick recipe',
      'Healthy options',
    ];
    
    return Container(
      height: 36,
      margin: const EdgeInsets.only(bottom: 16),
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: suggestions.length,
        separatorBuilder: (context, index) => const SizedBox(width: 10),
        itemBuilder: (context, index) {
          final suggestion = suggestions[index];
          return GestureDetector(
            onTap: () {
              HapticFeedback.lightImpact();
              switch (index) {
                case 0:
                  _quickSendMessage('My weekly budget is \$80');
                  break;
                case 1:
                  _quickSendMessage('Plan meals for this week within my budget');
                  break;
                case 2:
                  _quickSendMessage('I need a quick 30-minute recipe');
                  break;
                case 3:
                  _quickSendMessage('Find healthy meal options under \$15');
                  break;
              }
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(
                  color: Theme.of(context).primaryColor.withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: Text(
                suggestion,
                style: TextStyle(
                  color: Theme.of(context).primaryColor,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
  
  
  Widget _buildAttachmentButton(BuildContext context) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        _showAttachmentOptions(context);
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: Colors.grey[300]!,
            width: 1.5,
          ),
        ),
        child: Icon(
          Icons.add_rounded,
          color: Colors.grey[600],
          size: 20,
        ),
      ),
    );
  }
  
  void _showAttachmentOptions(BuildContext context) {
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
                  _buildAttachmentOption(
                    context,
                    'Upload Recipe Photo',
                    Icons.camera_alt_rounded,
                    () => _handlePhotoUpload(),
                  ),
                  const SizedBox(height: 12),
                  _buildAttachmentOption(
                    context,
                    'Share Shopping List',
                    Icons.share_rounded,
                    () => _shareShoppingList(),
                  ),
                  const SizedBox(height: 12),
                  _buildAttachmentOption(
                    context,
                    'Set Location',
                    Icons.location_on_rounded,
                    () => _setLocation(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildAttachmentOption(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: () {
        Navigator.pop(context);
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: Colors.grey[200]!,
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: Theme.of(context).primaryColor,
              size: 24,
            ),
            const SizedBox(width: 16),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            Icon(
              Icons.arrow_forward_ios_rounded,
              color: Colors.grey[400],
              size: 16,
            ),
          ],
        ),
      ),
    );
  }
  
  void _handlePhotoUpload() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            BrunoAvatar(mood: BrunoMood.helpful, size: 20),
            const SizedBox(width: 8),
            const Text('Photo upload coming soon!'),
          ],
        ),
        backgroundColor: Theme.of(context).primaryColor,
      ),
    );
  }
  
  void _shareShoppingList() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            BrunoAvatar(mood: BrunoMood.helpful, size: 20),
            const SizedBox(width: 8),
            const Text('Sharing coming soon!'),
          ],
        ),
        backgroundColor: Theme.of(context).primaryColor,
      ),
    );
  }
  
  void _setLocation() {
    HapticFeedback.lightImpact();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            BrunoAvatar(mood: BrunoMood.helpful, size: 20),
            const SizedBox(width: 8),
            const Text('Location services coming soon!'),
          ],
        ),
        backgroundColor: Theme.of(context).primaryColor,
      ),
    );
  }

  
  String _getSmartPlaceholder() {
    final provider = context.read<BrunoProvider>();
    
    // Dynamic placeholders based on state
    if (provider.messages.isEmpty) {
      final placeholders = [
        'What\'s your weekly budget?',
        'Plan meals for 4 people',
        'I need a quick dinner recipe',
        'Find healthy meal options',
        'Reorder my last shopping list',
      ];
      return placeholders[DateTime.now().millisecond % placeholders.length];
    }
    
    if (provider.shoppingList.isNotEmpty) {
      return 'Add more items or ask about recipes...';
    }
    
    if (provider.currentBudget.isNotEmpty) {
      return 'What type of meals do you want?';
    }
    
    return 'Ask Bruno anything...';
  }

  Widget _buildMessageContent(BuildContext context, ChatMessage message, bool isUser) {
    if (isUser) {
      return Text(
        message.message,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
          color: const Color(0xFF5D4037), // Dark brown text for beige bubble
        ),
      );
    }

    // Bruno messages with white text on brown background
    return Text(
      message.message,
      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
        color: Colors.white,
      ),
    );
  }

  Widget _buildStandardMessageCard(BuildContext context, ChatMessage message) {
    return Text(
      message.message,
      style: Theme.of(context).textTheme.bodyLarge,
    );
  }

  Widget _buildRecipeMessageCard(BuildContext context, ChatMessage message) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          message.message,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        if (message.message.contains('Chicken Stir-Fry')) ...[
          const SizedBox(height: 12),
          _buildQuickRecipeCard(context),
        ],
      ],
    );
  }

  Widget _buildBudgetMessageCard(BuildContext context, ChatMessage message) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          message.message,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 12),
        _buildBudgetSummaryCard(context),
      ],
    );
  }

  Widget _buildShoppingMessageCard(BuildContext context, ChatMessage message) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          message.message,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 12),
        _buildShoppingSummaryCard(context),
      ],
    );
  }

  Widget _buildQuickRecipeCard(BuildContext context) {
    final recipe = Meal(
      id: 'quick_recipe_1',
      name: 'Bruno\'s Budget Chicken Stir-Fry',
      description: 'Quick and delicious stir-fry perfect for busy weeknights',
      cost: 12.80,
      servings: 4,
      prepTime: 15,
      ingredients: [
        '1 lb Chicken breast',
        '2 cups Mixed vegetables',
        '2 tbsp Soy sauce',
        '1 tbsp Oil',
        '2 cloves Garlic',
      ],
      instructions: [
        'Heat oil in a large pan or wok over medium-high heat.',
        'Add chicken and cook until golden brown.',
        'Add vegetables and stir-fry for 3-4 minutes.',
        'Add soy sauce and garlic, cook for another minute.',
        'Serve hot over rice or noodles.',
      ],
      category: 'Main Course',
      isHealthy: true,
      isQuick: true,
    );

    return MealPlanCard(
      meal: recipe,
      onAddToCart: () {
        final provider = context.read<BrunoProvider>();
        for (final item in recipe.shoppingItems) {
          provider.addToShoppingList(item);
        }
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${recipe.name} ingredients added to cart!'),
            backgroundColor: Theme.of(context).primaryColor,
          ),
        );
      },
      onViewRecipe: () {
        _showRecipeDetails(context, recipe);
      },
    );
  }

  Widget _buildBudgetSummaryCard(BuildContext context) {
    final provider = context.read<BrunoProvider>();
    final budget = double.tryParse(provider.currentBudget) ?? 0.0;
    final spent = provider.totalCost;
    final remaining = budget - spent;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.green.withOpacity(0.1),
            Colors.green.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.green.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          BrunoAvatar(mood: BrunoMood.celebrating, size: 40),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Budget Summary',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                  ),
                ),
                Text(
                  'Spent: \$${spent.toStringAsFixed(2)} / \$${budget.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                Text(
                  'Remaining: \$${remaining.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.green.shade600,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShoppingSummaryCard(BuildContext context) {
    final provider = context.read<BrunoProvider>();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).primaryColor.withOpacity(0.1),
            Theme.of(context).primaryColor.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).primaryColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          BrunoAvatar(mood: BrunoMood.excited, size: 40),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Shopping List Ready!',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).primaryColor,
                  ),
                ),
                Text(
                  '${provider.shoppingList.length} items • \$${provider.totalCost.toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).primaryColor.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.shopping_cart,
                  size: 16,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 4),
                Text(
                  'View in Header',
                  style: TextStyle(
                    color: Theme.of(context).primaryColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _startVoiceInput() {
    HapticFeedback.lightImpact();
    // Voice input implementation would go here
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            BrunoAvatar(mood: BrunoMood.helpful, size: 20),
            const SizedBox(width: 8),
            Text('Voice input coming soon!'),
          ],
        ),
        backgroundColor: Theme.of(context).primaryColor,
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context, BrunoProvider provider) {
    return Container(
      height: 50,
      margin: const EdgeInsets.symmetric(horizontal: 20),
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          _buildQuickActionButton(
            context,
            'Set Budget',
            Icons.attach_money_rounded,
            () => _quickSendMessage('My weekly budget is \$80'),
            Theme.of(context).primaryColor,
          ),
          const SizedBox(width: 8),
          _buildQuickActionButton(
            context,
            'Plan Week',
            Icons.calendar_month_rounded,
            () => _quickSendMessage('Plan meals for this week'),
            Colors.blue,
          ),
          const SizedBox(width: 8),
          _buildQuickActionButton(
            context,
            'Quick Recipe',
            Icons.restaurant_rounded,
            () => _quickSendMessage('I need a quick 30-minute recipe'),
            Colors.orange,
          ),
          const SizedBox(width: 8),
          _buildQuickActionButton(
            context,
            'Healthy Options',
            Icons.favorite_rounded,
            () => _quickSendMessage('Find healthy meal options under \$15'),
            Colors.green,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton(
    BuildContext context,
    String label,
    IconData icon,
    VoidCallback onPressed,
    Color color,
  ) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        onPressed();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(25),
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: color,
              size: 18,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showRecipeDetails(BuildContext context, Meal recipe) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => LiquidGlassContainer(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Row(
                children: [
                  BrunoAvatar(mood: BrunoMood.helpful, size: 40),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      recipe.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(
                child: SingleChildScrollView(
                  controller: scrollController,
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
                      ...recipe.ingredients.map((ingredient) => Padding(
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
                      ...recipe.instructions.asMap().entries.map((entry) => Padding(
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

  // Wireframe-specific methods
  Widget _buildWireframeBrunoMessage(String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Container(
          margin: const EdgeInsets.only(right: 12, bottom: 4),
          child: BrunoAvatar(
            mood: BrunoMood.helpful,
            size: 40,
            animate: true,
          ),
        ),
        Flexible(
          child: Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            decoration: BoxDecoration(
              color: const Color(0xFF8B4513), // Brown color
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(6),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
              child: Text(
                text,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWireframeUserMessage(String text) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Flexible(
          child: Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            decoration: BoxDecoration(
              color: const Color(0xFFF5F1E8), // Beige color
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(6),
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
              child: Text(
                text,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: const Color(0xFF5D4037), // Dark brown text
                ),
              ),
            ),
          ),
        ),
        Container(
          width: 40,
          height: 40,
          margin: const EdgeInsets.only(left: 12, bottom: 4),
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: const Color(0xFF8B4513), // Brown color
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Icon(
            Icons.person_rounded,
            color: Colors.white,
            size: 20,
          ),
        ),
      ],
    );
  }

  Widget _buildRefineButtonRow() {
    return Row(
      children: [
        const SizedBox(width: 52), // Space for avatar
        Container(
          margin: const EdgeInsets.only(top: 8),
          child: _buildRefineButton(),
        ),
      ],
    );
  }

  Widget _buildSampleList() {
    return Container(
      margin: const EdgeInsets.only(left: 52, top: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF43B02A).withOpacity(0.1), // Instacart Green background
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF43B02A).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'List:',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: const Color(0xFF43B02A),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(
                Icons.check_circle,
                color: Color(0xFF43B02A),
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                'Rice & Beans - \$10',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              const Icon(
                Icons.check_circle,
                color: Color(0xFF43B02A),
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                'Plantains - \$8',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              const Icon(
                Icons.check_circle,
                color: Color(0xFF43B02A),
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                'Coconut Milk - \$6',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackButtons() {
    return Container(
      margin: const EdgeInsets.only(left: 52, top: 12),
      child: Row(
        children: [
          GestureDetector(
            onTap: () {
              HapticFeedback.lightImpact();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Thanks for the positive feedback!'),
                  backgroundColor: Color(0xFF43B02A),
                ),
              );
            },
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF43B02A).withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: const Color(0xFF43B02A).withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: const Icon(
                Icons.thumb_up_rounded,
                color: Color(0xFF43B02A),
                size: 20,
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: () {
              HapticFeedback.lightImpact();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Thanks for the feedback! Let me improve.'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Colors.orange.withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: const Icon(
                Icons.thumb_down_rounded,
                color: Colors.orange,
                size: 20,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
