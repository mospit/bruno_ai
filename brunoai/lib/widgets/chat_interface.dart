import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/bruno_provider.dart';
import '../widgets/liquid_glass_container.dart';
import '../widgets/shopping_cart.dart';
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
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _typingAnimationController.dispose();
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

  @override
  Widget build(BuildContext context) {
    return Consumer<BrunoProvider>(
      builder: (context, provider, child) {
        return Column(
          children: [
            // Chat Header
            _buildChatHeader(),
            
            // Messages List
            Expanded(
              child: _buildMessagesList(provider),
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

  Widget _buildChatHeader() {
    return LiquidGlassContainer(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
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
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Bruno AI',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Your AI Shopping Assistant',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: 12,
            height: 12,
            decoration: const BoxDecoration(
              color: Colors.green,
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessagesList(BrunoProvider provider) {
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

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.isUser;
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[

            Container(
              width: 32,
              height: 32,
              margin: const EdgeInsets.only(right: 12, top: 4),
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
                size: 18,
              ),
            ),
          ],
          Flexible(
            child: LiquidGlassContainer(
              backgroundColor: isUser
                  ? Theme.of(context).primaryColor.withOpacity(0.8)
                  : null,
              borderRadius: BorderRadius.circular(20),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.message,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: isUser ? Colors.white : null,
                    ),
                  ),
                  if (message.suggestions.isNotEmpty) ...[

                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: message.suggestions.map((suggestion) {
                        return _buildSuggestionChip(suggestion);
                      }).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (isUser) ...[

            Container(
              width: 32,
              height: 32,
              margin: const EdgeInsets.only(left: 12, top: 4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Theme.of(context).primaryColor.withOpacity(0.2),
              ),
              child: Icon(
                Icons.person_rounded,
                color: Theme.of(context).primaryColor,
                size: 18,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSuggestionChip(String suggestion) {
    return GestureDetector(
      onTap: () {
        _messageController.text = suggestion;
        _sendMessage();
      },
      child: LiquidGlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        borderRadius: BorderRadius.circular(16),
        backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
        borderColor: Theme.of(context).primaryColor.withOpacity(0.3),
        child: Text(
          suggestion,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).primaryColor,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            margin: const EdgeInsets.only(right: 12),
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
              size: 18,
            ),
          ),
          LiquidGlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            borderRadius: BorderRadius.circular(20),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Bruno is typing',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).textTheme.bodyMedium?.color?.withOpacity(0.7),
                  ),
                ),
                const SizedBox(width: 8),
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
                          margin: const EdgeInsets.symmetric(horizontal: 1),
                          child: Transform.translate(
                            offset: Offset(0, -4 * animationValue),
                            child: Container(
                              width: 4,
                              height: 4,
                              decoration: BoxDecoration(
                                color: Theme.of(context).primaryColor.withOpacity(
                                  0.3 + 0.7 * animationValue,
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
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 20,
                  offset: const Offset(0, 4),
                  spreadRadius: 0,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 40,
                  offset: const Offset(0, 8),
                  spreadRadius: 0,
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Text input field at the top
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Ask Bruno anything...',
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                        hintStyle: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 16,
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w400,
                        color: Colors.black87,
                      ),
                      maxLines: null,
                      textCapitalization: TextCapitalization.sentences,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(height: 16),
                // Buttons row at the bottom
                  Row(
                   mainAxisAlignment: MainAxisAlignment.spaceBetween,
                   children: [
                     // Shopping cart button (Enhanced ChatGPT style)
                     Stack(
                       children: [
                         Container(
                           decoration: BoxDecoration(
                             color: Colors.white,
                             borderRadius: BorderRadius.circular(24),
                             border: Border.all(
                               color: Colors.grey[200]!,
                               width: 1.5,
                             ),
                             boxShadow: [
                               BoxShadow(
                                 color: Colors.black.withOpacity(0.06),
                                 blurRadius: 12,
                                 offset: const Offset(0, 2),
                                 spreadRadius: 0,
                               ),
                             ],
                           ),
                           child: Material(
                             color: Colors.transparent,
                             child: InkWell(
                               onTap: () => _showShoppingCart(context),
                               borderRadius: BorderRadius.circular(24),
                               splashColor: Colors.grey[100],
                               highlightColor: Colors.grey[50],
                               child: Padding(
                                 padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                                 child: Row(
                                   mainAxisSize: MainAxisSize.min,
                                   children: [
                                     Icon(
                                       Icons.shopping_cart_rounded,
                                       color: Colors.grey[600],
                                       size: 20,
                                     ),
                                     const SizedBox(width: 8),
                                     Text(
                                       'Cart',
                                       style: TextStyle(
                                         color: Colors.grey[700],
                                         fontSize: 15,
                                         fontWeight: FontWeight.w500,
                                         letterSpacing: 0.2,
                                       ),
                                     ),
                                   ],
                                 ),
                               ),
                             ),
                           ),
                         ),
                         if (provider.shoppingList.isNotEmpty)
                           Positioned(
                             right: -3,
                             top: -3,
                             child: Container(
                               padding: const EdgeInsets.all(5),
                               decoration: BoxDecoration(
                                 gradient: LinearGradient(
                                   colors: [Colors.red[400]!, Colors.red[600]!],
                                   begin: Alignment.topLeft,
                                   end: Alignment.bottomRight,
                                 ),
                                 borderRadius: BorderRadius.circular(12),
                                 border: Border.all(
                                   color: Colors.white,
                                   width: 2.5,
                                 ),
                                 boxShadow: [
                                   BoxShadow(
                                     color: Colors.red.withOpacity(0.3),
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
                                   color: Colors.white,
                                   fontSize: 11,
                                   fontWeight: FontWeight.w700,
                                 ),
                                 textAlign: TextAlign.center,
                               ),
                             ),
                           ),
                       ],
                     ),
                     // Send button (Enhanced ChatGPT style)
                     Container(
                       decoration: BoxDecoration(
                         gradient: _messageController.text.trim().isEmpty 
                             ? null
                             : LinearGradient(
                                 colors: [
                                   Theme.of(context).primaryColor,
                                   Theme.of(context).primaryColor.withOpacity(0.8),
                                 ],
                                 begin: Alignment.topLeft,
                                 end: Alignment.bottomRight,
                               ),
                         color: _messageController.text.trim().isEmpty 
                             ? Colors.grey[200]
                             : null,
                         borderRadius: BorderRadius.circular(24),
                         boxShadow: _messageController.text.trim().isEmpty 
                             ? null
                             : [
                                 BoxShadow(
                                   color: Colors.black.withOpacity(0.2),
                                   blurRadius: 12,
                                   offset: const Offset(0, 3),
                                   spreadRadius: 0,
                                 ),
                               ],
                       ),
                       child: Material(
                         color: Colors.transparent,
                         child: InkWell(
                           onTap: _messageController.text.trim().isEmpty ? null : _sendMessage,
                           borderRadius: BorderRadius.circular(24),
                           splashColor: _messageController.text.trim().isEmpty 
                               ? null 
                               : Colors.white.withOpacity(0.1),
                           child: Padding(
                             padding: const EdgeInsets.all(12),
                             child: Icon(
                               Icons.arrow_upward_rounded,
                               color: _messageController.text.trim().isEmpty 
                                   ? Colors.grey[500]
                                   : Colors.white,
                               size: 22,
                             ),
                           ),
                         ),
                       ),
                     ),
                   ],
                 ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

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
}