import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

/// Centralized animation management for performance and accessibility
class AnimationManager {
  static AnimationManager? _instance;
  static AnimationManager get instance => _instance ??= AnimationManager._();
  
  AnimationManager._();

  // Animation performance settings
  bool _enableHighPerformanceAnimations = true;
  bool _respectReducedMotion = true;
  int _maxConcurrentAnimations = 5;
  int _currentActiveAnimations = 0;

  // Animation duration multipliers based on device performance
  double _durationMultiplier = 1.0;

  // Track animation performance
  final Map<String, List<Duration>> _animationPerformance = {};

  /// Initialize with device capabilities
  void initialize() {
    _detectDeviceCapabilities();
    _setupPerformanceMonitoring();
  }

  void _detectDeviceCapabilities() {
    // Detect low-end devices and adjust settings
    // This is a simplified implementation - you might want to use
    // device_info_plus package for more detailed device detection
    if (kIsWeb) {
      _durationMultiplier = 0.8; // Slightly faster for web
    } else if (defaultTargetPlatform == TargetPlatform.android) {
      // Could check for RAM, CPU, etc. and adjust accordingly
      _enableHighPerformanceAnimations = true;
    }
  }

  void _setupPerformanceMonitoring() {
    if (kDebugMode) {
      // Monitor frame rendering performance in debug mode
      WidgetsBinding.instance.addTimingsCallback((timings) {
        for (final timing in timings) {
          if (timing.rasterDuration.inMilliseconds > 16) { // > 60fps
            debugPrint('Animation frame took ${timing.rasterDuration.inMilliseconds}ms');
          }
        }
      });
    }
  }

  /// Get appropriate duration based on settings and device capabilities
  Duration getDuration(Duration baseDuration, [BuildContext? context]) {
    // Check for reduced motion preference - safely handle context
    if (context != null) {
      try {
        final mediaQuery = MediaQuery.maybeOf(context);
        if (mediaQuery?.disableAnimations == true) {
          return Duration.zero;
        }
      } catch (e) {
        // If MediaQuery is not available, continue with normal duration
      }
    }

    if (!_respectReducedMotion || !_enableHighPerformanceAnimations) {
      return baseDuration; // Return normal duration instead of zero
    }

    // Apply device-based multiplier
    final adjustedMilliseconds = (baseDuration.inMilliseconds * _durationMultiplier).round();
    return Duration(milliseconds: adjustedMilliseconds);
  }

  /// Check if animation should be enabled
  bool shouldAnimate(BuildContext? context) {
    // Safely check for reduced motion preference
    if (context != null) {
      try {
        final mediaQuery = MediaQuery.maybeOf(context);
        if (mediaQuery?.disableAnimations == true) {
          return false;
        }
      } catch (e) {
        // If MediaQuery is not available, allow animations
      }
    }
    
    if (_currentActiveAnimations >= _maxConcurrentAnimations) {
      return false;
    }

    return _enableHighPerformanceAnimations;
  }

  /// Register animation start for performance tracking
  void registerAnimationStart(String animationName) {
    _currentActiveAnimations++;
    if (kDebugMode) {
      debugPrint('Animation started: $animationName (Active: $_currentActiveAnimations)');
    }
  }

  /// Register animation completion for performance tracking
  void registerAnimationComplete(String animationName, Duration duration) {
    _currentActiveAnimations = (_currentActiveAnimations - 1).clamp(0, _maxConcurrentAnimations);
    
    // Track performance
    _animationPerformance.putIfAbsent(animationName, () => []).add(duration);
    
    if (kDebugMode) {
      debugPrint('Animation completed: $animationName in ${duration.inMilliseconds}ms');
    }
  }

  /// Get performance stats for debugging
  Map<String, double> getPerformanceStats() {
    final stats = <String, double>{};
    for (final entry in _animationPerformance.entries) {
      final durations = entry.value;
      final averageMs = durations.map((d) => d.inMilliseconds).reduce((a, b) => a + b) / durations.length;
      stats[entry.key] = averageMs;
    }
    return stats;
  }

  /// Create a managed animation controller
  AnimationController createController({
    required Duration duration,
    required TickerProvider vsync,
    String? debugLabel,
    double? value,
    Duration? reverseDuration,
  }) {
    final controller = AnimationController(
      duration: getDuration(duration),
      vsync: vsync,
      debugLabel: debugLabel,
      value: value,
      reverseDuration: reverseDuration != null ? getDuration(reverseDuration) : null,
    );

    // Add performance tracking
    if (debugLabel != null) {
      controller.addStatusListener((status) {
        switch (status) {
          case AnimationStatus.forward:
          case AnimationStatus.reverse:
            registerAnimationStart(debugLabel);
            break;
          case AnimationStatus.completed:
          case AnimationStatus.dismissed:
            registerAnimationComplete(debugLabel, duration);
            break;
        }
      });
    }

    return controller;
  }
}

/// Animation constants with performance awareness
class AppAnimations {
  // Base durations - actual durations will be adjusted by AnimationManager
  static const Duration ultraFast = Duration(milliseconds: 100);
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration verySlow = Duration(milliseconds: 800);

  // Curves optimized for performance and feel
  static const Curve defaultCurve = Curves.easeInOutCubic;
  static const Curve fastCurve = Curves.easeOut;
  static const Curve slowCurve = Curves.easeInOut;
  static const Curve bouncyCurve = Curves.elasticOut;
  static const Curve snappyCurve = Curves.easeOutBack;

  // Get duration with performance considerations
  static Duration getDuration(Duration base, [BuildContext? context]) {
    return AnimationManager.instance.getDuration(base, context);
  }

  // Check if animations should be enabled
  static bool shouldAnimate([BuildContext? context]) {
    return AnimationManager.instance.shouldAnimate(context);
  }
}

/// Mixin for widgets that use animations
mixin AnimationMixin<T extends StatefulWidget> on State<T>, TickerProviderStateMixin<T> {
  final List<AnimationController> _controllers = [];

  /// Create a managed animation controller
  AnimationController createManagedController({
    required Duration duration,
    String? debugLabel,
    double? value,
    Duration? reverseDuration,
  }) {
    final controller = AnimationManager.instance.createController(
      duration: duration,
      vsync: this,
      debugLabel: debugLabel ?? widget.runtimeType.toString(),
      value: value,
      reverseDuration: reverseDuration,
    );
    
    _controllers.add(controller);
    return controller;
  }

  @override
  void dispose() {
    // Dispose all managed controllers
    for (final controller in _controllers) {
      if (controller.isAnimating) {
        controller.stop();
      }
      controller.dispose();
    }
    _controllers.clear();
    super.dispose();
  }
}

/// Extension for easy animation duration access
extension AnimatedWidgetExtensions on Widget {
  /// Wrap widget with performance-aware animation
  Widget animateIn({
    Duration? duration,
    Curve? curve,
    Offset? slideFrom,
    bool? fadeIn,
    double? scaleFrom,
  }) {
    return _AnimatedWrapper(
      duration: duration ?? AppAnimations.normal,
      curve: curve ?? AppAnimations.defaultCurve,
      slideFrom: slideFrom,
      fadeIn: fadeIn ?? true,
      scaleFrom: scaleFrom,
      child: this,
    );
  }
}

class _AnimatedWrapper extends StatefulWidget {
  final Duration duration;
  final Curve curve;
  final Offset? slideFrom;
  final bool fadeIn;
  final double? scaleFrom;
  final Widget child;

  const _AnimatedWrapper({
    required this.duration,
    required this.curve,
    this.slideFrom,
    required this.fadeIn,
    this.scaleFrom,
    required this.child,
  });

  @override
  State<_AnimatedWrapper> createState() => _AnimatedWrapperState();
}

class _AnimatedWrapperState extends State<_AnimatedWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationManager.instance.createController(
      duration: widget.duration,
      vsync: this,
      debugLabel: 'AnimatedWrapper',
    );

    _fadeAnimation = Tween<double>(
      begin: widget.fadeIn ? 0.0 : 1.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    _slideAnimation = Tween<Offset>(
      begin: widget.slideFrom ?? Offset.zero,
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    _scaleAnimation = Tween<double>(
      begin: widget.scaleFrom ?? 1.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    if (AppAnimations.shouldAnimate()) {
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
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        Widget result = widget.child;

        if (widget.scaleFrom != null) {
          result = Transform.scale(
            scale: _scaleAnimation.value,
            child: result,
          );
        }

        if (widget.slideFrom != null) {
          result = SlideTransition(
            position: _slideAnimation,
            child: result,
          );
        }

        if (widget.fadeIn) {
          result = FadeTransition(
            opacity: _fadeAnimation,
            child: result,
          );
        }

        return result;
      },
    );
  }
}
