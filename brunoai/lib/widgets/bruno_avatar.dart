import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import '../theme/app_colors.dart';

enum BrunoMood {
  friendly,    // Default smile
  excited,     // Found great deals!
  thinking,    // Processing meal plans
  celebrating, // Budget saved!
  concerned,   // Over budget warning
  helpful,     // Providing assistance
  sleepy,      // Waiting for input
}

class BrunoAvatar extends StatefulWidget {
  final BrunoMood mood;
  final double size;
  final bool animate;
  final VoidCallback? onTap;
  final bool showBudgetProgress;
  final double budgetProgress;
  final bool isBreathing;
  final bool showSpeechBubble;
  final String? speechText;
  final bool enableHaptics;

  const BrunoAvatar({
    super.key,
    this.mood = BrunoMood.friendly,
    this.size = 60,
    this.animate = true,
    this.onTap,
    this.showBudgetProgress = false,
    this.budgetProgress = 0.0,
    this.isBreathing = true,
    this.showSpeechBubble = false,
    this.speechText,
    this.enableHaptics = true,
  });

  @override
  State<BrunoAvatar> createState() => _BrunoAvatarState();
}

class _BrunoAvatarState extends State<BrunoAvatar>
    with TickerProviderStateMixin {
  late AnimationController _blinkController;
  late AnimationController _bounceController;
  late AnimationController _rotateController;
  late AnimationController _breatheController;
  late AnimationController _gestureController;
  late Animation<double> _blinkAnimation;
  late Animation<double> _bounceAnimation;
  late Animation<double> _rotateAnimation;
  late Animation<double> _breatheAnimation;
  late Animation<double> _gestureAnimation;

  @override
  void initState() {
    super.initState();
    
    // Blink animation
    _blinkController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    _blinkAnimation = Tween<double>(begin: 1.0, end: 0.1).animate(
      CurvedAnimation(parent: _blinkController, curve: Curves.easeInOut),
    );

    // Bounce animation
    _bounceController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _bounceAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _bounceController, curve: Curves.elasticOut),
    );

    // Rotate animation for thinking
    _rotateController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    _rotateAnimation = Tween<double>(begin: 0.0, end: 2 * math.pi).animate(
      CurvedAnimation(parent: _rotateController, curve: Curves.linear),
    );

    // Breathing animation
    _breatheController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    );
    _breatheAnimation = Tween<double>(begin: 1.0, end: 1.08).animate(
      CurvedAnimation(parent: _breatheController, curve: Curves.easeInOut),
    );

    // Gesture animation
    _gestureController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _gestureAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _gestureController, curve: Curves.elasticOut),
    );

    if (widget.animate) {
      _startAnimations();
    }
  }

  void _startAnimations() {
    // Breathing animation
    if (widget.isBreathing) {
      _breatheController.repeat(reverse: true);
    }

    // Random blinking
    Future.delayed(Duration(milliseconds: math.Random().nextInt(3000) + 2000), () {
      if (mounted) {
        _blinkController.forward().then((_) {
          _blinkController.reverse();
          _startAnimations();
        });
      }
    });

    // Mood-based animations
    switch (widget.mood) {
      case BrunoMood.excited:
      case BrunoMood.celebrating:
        _bounceController.repeat(reverse: true);
        break;
      case BrunoMood.thinking:
        _rotateController.repeat();
        break;
      default:
        break;
    }
  }

  void _triggerGesture() {
    _gestureController.forward().then((_) {
      _gestureController.reverse();
    });
  }

  @override
  void didUpdateWidget(BrunoAvatar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood) {
      _updateAnimationForMood();
    }
  }

  void _updateAnimationForMood() {
    // Stop all animations first
    _bounceController.stop();
    _rotateController.stop();

    // Start appropriate animation for new mood
    switch (widget.mood) {
      case BrunoMood.excited:
      case BrunoMood.celebrating:
        _bounceController.repeat(reverse: true);
        break;
      case BrunoMood.thinking:
        _rotateController.repeat();
        break;
      default:
        break;
    }
  }

  @override
  void dispose() {
    _blinkController.dispose();
    _bounceController.dispose();
    _rotateController.dispose();
    _breatheController.dispose();
    _gestureController.dispose();
    super.dispose();
  }

  Color _getBrunoColor() {
    switch (widget.mood) {
      case BrunoMood.excited:
        return AppColors.primary.withOpacity(0.9);
      case BrunoMood.celebrating:
        return AppColors.instacartGreen;
      case BrunoMood.concerned:
        return AppColors.foodAccent;
      case BrunoMood.thinking:
        return AppColors.interactiveBlue;
      case BrunoMood.helpful:
        return AppColors.primary;
      case BrunoMood.sleepy:
        return AppColors.primary.withOpacity(0.6);
      default:
        return AppColors.primary;
    }
  }

  Widget _buildEyes() {
    return AnimatedBuilder(
      animation: _blinkAnimation,
      builder: (context, child) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildEye(),
            _buildEye(),
          ],
        );
      },
    );
  }

  Widget _buildEye() {
    double eyeHeight = widget.size * 0.15 * _blinkAnimation.value;
    
    if (widget.mood == BrunoMood.sleepy) {
      eyeHeight = widget.size * 0.05; // Sleepy eyes
    }

    return Container(
      width: widget.size * 0.12,
      height: eyeHeight,
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(widget.size * 0.06),
      ),
    );
  }

  Widget _buildMouth() {
    switch (widget.mood) {
      case BrunoMood.excited:
      case BrunoMood.celebrating:
        return Container(
          width: widget.size * 0.25,
          height: widget.size * 0.15,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.black87, width: 2),
            borderRadius: BorderRadius.circular(widget.size * 0.1),
          ),
        );
      case BrunoMood.concerned:
        return Transform.rotate(
          angle: math.pi,
          child: Container(
            width: widget.size * 0.2,
            height: widget.size * 0.1,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.black87, width: 2),
              borderRadius: BorderRadius.circular(widget.size * 0.05),
            ),
          ),
        );
      case BrunoMood.thinking:
        return Container(
          width: widget.size * 0.15,
          height: widget.size * 0.15,
          decoration: BoxDecoration(
            color: Colors.black87,
            shape: BoxShape.circle,
          ),
        );
      default:
        return Container(
          width: widget.size * 0.2,
          height: widget.size * 0.1,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.black87, width: 2),
            borderRadius: BorderRadius.circular(widget.size * 0.05),
          ),
        );
    }
  }

  Widget _buildAccessories() {
    if (widget.mood == BrunoMood.thinking) {
      return Positioned(
        top: -widget.size * 0.1,
        right: widget.size * 0.1,
        child: AnimatedBuilder(
          animation: _rotateAnimation,
          builder: (context, child) {
            return Transform.rotate(
              angle: _rotateAnimation.value,
              child: Container(
                width: widget.size * 0.3,
                height: widget.size * 0.3,
                decoration: BoxDecoration(
                  color: Colors.transparent,
                  border: Border.all(
                    color: Colors.black26,
                    width: 1,
                  ),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Text(
                    '?',
                    style: TextStyle(
                      fontSize: widget.size * 0.15,
                      fontWeight: FontWeight.bold,
                      color: Colors.black54,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      );
    }

    if (widget.mood == BrunoMood.celebrating) {
      return Positioned(
        top: -widget.size * 0.05,
        left: 0,
        right: 0,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Text('🎉', style: TextStyle(fontSize: widget.size * 0.2)),
            Text('🎉', style: TextStyle(fontSize: widget.size * 0.2)),
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildSpeechBubble() {
    if (!widget.showSpeechBubble || widget.speechText == null) {
      return const SizedBox.shrink();
    }

    return Positioned(
      bottom: widget.size + 10,
      left: -40,
      child: Container(
        constraints: BoxConstraints(maxWidth: 150),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
        child: Text(
          widget.speechText!,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.black87,
            fontWeight: FontWeight.w500,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  Widget _buildBudgetProgressRing() {
    if (!widget.showBudgetProgress) {
      return const SizedBox.shrink();
    }

    return SizedBox(
      width: widget.size + 10,
      height: widget.size + 10,
      child: CircularProgressIndicator(
        value: widget.budgetProgress.clamp(0.0, 1.0),
        strokeWidth: 4,
        backgroundColor: Colors.grey.withOpacity(0.2),
        valueColor: AlwaysStoppedAnimation<Color>(
          widget.budgetProgress < 0.7
              ? Colors.green
              : widget.budgetProgress < 0.9
                  ? Colors.orange
                  : Colors.red,
        ),
      ),
    );
  }

  Widget _buildGestureOverlay() {
    if (_gestureAnimation.value <= 0) return const SizedBox.shrink();

    String emoji;
    switch (widget.mood) {
      case BrunoMood.celebrating:
        emoji = '🎉';
        break;
      case BrunoMood.helpful:
        emoji = '👍';
        break;
      case BrunoMood.thinking:
        emoji = '💭';
        break;
      case BrunoMood.excited:
        emoji = '✨';
        break;
      default:
        emoji = '❤️';
    }

    return Positioned(
      top: -10,
      right: -10,
      child: Transform.scale(
        scale: _gestureAnimation.value,
        child: Text(
          emoji,
          style: TextStyle(fontSize: widget.size * 0.3),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        if (widget.enableHaptics) {
          HapticFeedback.lightImpact();
        }
        _triggerGesture();
        widget.onTap?.call();
      },
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Speech bubble
          _buildSpeechBubble(),
          // Budget progress ring
          Center(child: _buildBudgetProgressRing()),
          // Main avatar
          AnimatedBuilder(
            animation: Listenable.merge([
              _bounceAnimation,
              _rotateAnimation,
              _breatheAnimation,
              _gestureAnimation,
            ]),
            builder: (context, child) {
              double scale = 1.0;
              double rotation = 0.0;

              // Apply breathing animation
              scale *= _breatheAnimation.value;

              // Apply mood-specific scaling
              if (widget.mood == BrunoMood.excited ||
                  widget.mood == BrunoMood.celebrating) {
                scale *= 1.0 + (_bounceAnimation.value * 0.1);
              }

              if (widget.mood == BrunoMood.thinking) {
                rotation = _rotateAnimation.value * 0.05;
              }

              return Transform.scale(
                scale: scale,
                child: Transform.rotate(
                  angle: rotation,
                  child: Container(
                    width: widget.size,
                    height: widget.size,
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        colors: [
                          _getBrunoColor(),
                          _getBrunoColor().withOpacity(0.8),
                        ],
                      ),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: _getBrunoColor().withOpacity(0.3),
                          blurRadius: widget.size * 0.15,
                          offset: Offset(0, widget.size * 0.08),
                          spreadRadius: 2,
                        ),
                        BoxShadow(
                          color: Colors.white.withOpacity(0.3),
                          blurRadius: widget.size * 0.1,
                          offset: Offset(-widget.size * 0.03, -widget.size * 0.03),
                        ),
                      ],
                    ),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Bear ears
                        Positioned(
                          top: widget.size * 0.1,
                          left: widget.size * 0.15,
                          child: Container(
                            width: widget.size * 0.2,
                            height: widget.size * 0.2,
                            decoration: BoxDecoration(
                              color: _getBrunoColor(),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 2,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                          ),
                        ),
                        Positioned(
                          top: widget.size * 0.1,
                          right: widget.size * 0.15,
                          child: Container(
                            width: widget.size * 0.2,
                            height: widget.size * 0.2,
                            decoration: BoxDecoration(
                              color: _getBrunoColor(),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 2,
                                  offset: const Offset(0, 1),
                                ),
                              ],
                            ),
                          ),
                        ),

                        // Inner ear
                        Positioned(
                          top: widget.size * 0.15,
                          left: widget.size * 0.2,
                          child: Container(
                            width: widget.size * 0.1,
                            height: widget.size * 0.1,
                            decoration: BoxDecoration(
                              color: Colors.pink.withOpacity(0.7),
                              shape: BoxShape.circle,
                            ),
                          ),
                        ),
                        Positioned(
                          top: widget.size * 0.15,
                          right: widget.size * 0.2,
                          child: Container(
                            width: widget.size * 0.1,
                            height: widget.size * 0.1,
                            decoration: BoxDecoration(
                              color: Colors.pink.withOpacity(0.7),
                              shape: BoxShape.circle,
                            ),
                          ),
                        ),

                        // Face
                        Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(height: widget.size * 0.1),
                            // Eyes
                            SizedBox(
                              width: widget.size * 0.4,
                              child: _buildEyes(),
                            ),
                            SizedBox(height: widget.size * 0.1),
                            // Nose
                            Container(
                              width: widget.size * 0.08,
                              height: widget.size * 0.06,
                              decoration: BoxDecoration(
                                color: Colors.black87,
                                borderRadius:
                                    BorderRadius.circular(widget.size * 0.02),
                              ),
                            ),
                            SizedBox(height: widget.size * 0.05),
                            // Mouth
                            _buildMouth(),
                          ],
                        ),

                        // Accessories
                        _buildAccessories(),

                        // Gesture overlay
                        _buildGestureOverlay(),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

// Helper extension to get Bruno mood from message context
extension BrunoMoodExtension on String {
  BrunoMood getBrunoMood() {
    final lowerMessage = toLowerCase();
    
    if (lowerMessage.contains('save') || lowerMessage.contains('deal') || lowerMessage.contains('budget')) {
      return BrunoMood.celebrating;
    } else if (lowerMessage.contains('think') || lowerMessage.contains('plan') || lowerMessage.contains('find')) {
      return BrunoMood.thinking;
    } else if (lowerMessage.contains('excited') || lowerMessage.contains('great') || lowerMessage.contains('perfect')) {
      return BrunoMood.excited;
    } else if (lowerMessage.contains('over') || lowerMessage.contains('expensive') || lowerMessage.contains('too much')) {
      return BrunoMood.concerned;
    } else if (lowerMessage.contains('help') || lowerMessage.contains('assist') || lowerMessage.contains('guide')) {
      return BrunoMood.helpful;
    } else {
      return BrunoMood.friendly;
    }
  }
}
