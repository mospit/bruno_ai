import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_colors.dart';

/// Bruno AI Animation Standards
/// Comprehensive animation utilities following the design guide
class BrunoAnimations {
  BrunoAnimations._();

  // Animation Durations
  static const Duration microInteraction = Duration(milliseconds: 200);
  static const Duration shortTransition = Duration(milliseconds: 250);
  static const Duration standardTransition = Duration(milliseconds: 300);
  static const Duration longTransition = Duration(milliseconds: 400);
  static const Duration slowTransition = Duration(milliseconds: 500);

  // Animation Curves
  static const Curve defaultCurve = Curves.easeInOut;
  static const Curve playfulCurve = Curves.bounceIn;
  static const Curve gentleCurve = Curves.easeOut;
  static const Curve snapCurve = Curves.easeInBack;

  /// Check if animations should be disabled based on accessibility settings
  static bool shouldDisableAnimations(BuildContext context) {
    return MediaQuery.of(context).disableAnimations;
  }

  /// Check if device is low-end based on memory and performance indicators
  static bool isLowEndDevice() {
    // Simple heuristic - in production, you might want more sophisticated detection
    return false; // For now, assume all devices can handle animations
  }

  /// Provide haptic feedback for animation actions
  static void triggerHapticFeedback({Duration duration = const Duration(milliseconds: 50)}) {
    HapticFeedback.lightImpact();
  }

  /// Get animation color based on state
  static Color getAnimationColor(AnimationState state, BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    switch (state) {
      case AnimationState.success:
        return Colors.green.shade400;
      case AnimationState.error:
        return AppColors.error;
      case AnimationState.loading:
        return isDark ? AppColors.primary : AppColors.primaryLight;
      case AnimationState.neutral:
        return isDark ? AppColors.gray400 : AppColors.gray600;
    }
  }
}

enum AnimationState {
  success,
  error,
  loading,
  neutral,
}

/// Animated card that fades in with optional slide
class AnimatedCard extends StatefulWidget {
  final Widget child;
  final Duration delay;
  final Duration duration;
  final bool slideFromBottom;
  final double slideDistance;

  const AnimatedCard({
    super.key,
    required this.child,
    this.delay = Duration.zero,
    this.duration = BrunoAnimations.standardTransition,
    this.slideFromBottom = false,
    this.slideDistance = 20.0,
  });

  @override
  State<AnimatedCard> createState() => _AnimatedCardState();
}

class _AnimatedCardState extends State<AnimatedCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: BrunoAnimations.defaultCurve,
    ));

    _slideAnimation = Tween<Offset>(
      begin: widget.slideFromBottom 
          ? Offset(0, widget.slideDistance / 100)
          : Offset.zero,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: BrunoAnimations.defaultCurve,
    ));

    // Start animation after delay
    Future.delayed(widget.delay, () {
      if (mounted && !BrunoAnimations.shouldDisableAnimations(context)) {
        _controller.forward();
      } else if (mounted) {
        // Skip animation but still show content
        _controller.value = 1.0;
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (BrunoAnimations.shouldDisableAnimations(context)) {
      return widget.child;
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return FadeTransition(
          opacity: _fadeAnimation,
          child: SlideTransition(
            position: _slideAnimation,
            child: widget.child,
          ),
        );
      },
    );
  }
}

/// Bouncy button animation for positive feedback
class BounceButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double scaleFactor;
  final Duration duration;

  const BounceButton({
    super.key,
    required this.child,
    this.onTap,
    this.scaleFactor = 0.95,
    this.duration = BrunoAnimations.microInteraction,
  });

  @override
  State<BounceButton> createState() => _BounceButtonState();
}

class _BounceButtonState extends State<BounceButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.scaleFactor,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: BrunoAnimations.playfulCurve,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTap() {
    if (!BrunoAnimations.shouldDisableAnimations(context)) {
      _controller.forward().then((_) {
        _controller.reverse();
      });
      BrunoAnimations.triggerHapticFeedback();
    }
    widget.onTap?.call();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _handleTap,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: widget.child,
          );
        },
      ),
    );
  }
}

/// Animated checkbox with scale and fill animation
class AnimatedCheckbox extends StatefulWidget {
  final bool value;
  final ValueChanged<bool?>? onChanged;
  final Color? activeColor;
  final Color? checkColor;

  const AnimatedCheckbox({
    super.key,
    required this.value,
    this.onChanged,
    this.activeColor,
    this.checkColor,
  });

  @override
  State<AnimatedCheckbox> createState() => _AnimatedCheckboxState();
}

class _AnimatedCheckboxState extends State<AnimatedCheckbox>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _fillController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fillAnimation;

  @override
  void initState() {
    super.initState();
    
    _scaleController = AnimationController(
      duration: BrunoAnimations.microInteraction,
      vsync: this,
    );
    
    _fillController = AnimationController(
      duration: BrunoAnimations.shortTransition,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: BrunoAnimations.playfulCurve,
    ));

    _fillAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fillController,
      curve: BrunoAnimations.defaultCurve,
    ));

    if (widget.value) {
      _fillController.value = 1.0;
    }
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _fillController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(AnimatedCheckbox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      if (widget.value) {
        _animateToChecked();
      } else {
        _animateToUnchecked();
      }
    }
  }

  void _animateToChecked() {
    if (!BrunoAnimations.shouldDisableAnimations(context)) {
      _scaleController.forward().then((_) {
        _scaleController.reverse();
      });
      _fillController.forward();
      BrunoAnimations.triggerHapticFeedback();
    } else {
      _fillController.value = 1.0;
    }
  }

  void _animateToUnchecked() {
    if (!BrunoAnimations.shouldDisableAnimations(context)) {
      _fillController.reverse();
    } else {
      _fillController.value = 0.0;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => widget.onChanged?.call(!widget.value),
      child: AnimatedBuilder(
        animation: Listenable.merge([_scaleAnimation, _fillAnimation]),
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                  color: widget.activeColor ?? AppColors.primary,
                  width: 2,
                ),
                color: Color.lerp(
                  Colors.transparent,
                  widget.activeColor ?? AppColors.primary,
                  _fillAnimation.value,
                ),
              ),
              child: _fillAnimation.value > 0.5
                  ? Icon(
                      Icons.check,
                      size: 16,
                      color: widget.checkColor ?? Colors.white,
                    )
                  : null,
            ),
          );
        },
      ),
    );
  }
}

/// Animated progress bar with smooth transitions
class AnimatedProgressBar extends StatefulWidget {
  final double progress;
  final Color? backgroundColor;
  final Color? progressColor;
  final double height;
  final BorderRadius? borderRadius;
  final Duration duration;

  const AnimatedProgressBar({
    super.key,
    required this.progress,
    this.backgroundColor,
    this.progressColor,
    this.height = 8.0,
    this.borderRadius,
    this.duration = BrunoAnimations.longTransition,
  });

  @override
  State<AnimatedProgressBar> createState() => _AnimatedProgressBarState();
}

class _AnimatedProgressBarState extends State<AnimatedProgressBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  double _currentProgress = 0.0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: widget.progress,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: BrunoAnimations.defaultCurve,
    ));

    if (!BrunoAnimations.shouldDisableAnimations(context)) {
      _controller.forward();
    } else {
      _controller.value = 1.0;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(AnimatedProgressBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.progress != oldWidget.progress) {
      _animateToProgress(widget.progress);
    }
  }

  void _animateToProgress(double newProgress) {
    _progressAnimation = Tween<double>(
      begin: _currentProgress,
      end: newProgress,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: BrunoAnimations.defaultCurve,
    ));

    _currentProgress = newProgress;

    if (!BrunoAnimations.shouldDisableAnimations(context)) {
      _controller.reset();
      _controller.forward();
    } else {
      _controller.value = 1.0;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: widget.height,
      decoration: BoxDecoration(
        color: widget.backgroundColor ?? AppColors.gray200,
        borderRadius: widget.borderRadius ?? BorderRadius.circular(widget.height / 2),
      ),
      child: AnimatedBuilder(
        animation: _progressAnimation,
        builder: (context, child) {
          return FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: _progressAnimation.value.clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(
                color: widget.progressColor ?? AppColors.primary,
                borderRadius: widget.borderRadius ?? BorderRadius.circular(widget.height / 2),
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Custom page transitions following Bruno AI standards
class BrunoPageTransition extends PageTransitionsBuilder {
  @override
  Widget buildTransitions<T extends Object?>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    if (BrunoAnimations.shouldDisableAnimations(context)) {
      return child;
    }

    return FadeTransition(
      opacity: CurvedAnimation(
        parent: animation,
        curve: BrunoAnimations.defaultCurve,
      ),
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.0, 0.1),
          end: Offset.zero,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: BrunoAnimations.defaultCurve,
        )),
        child: child,
      ),
    );
  }
}
