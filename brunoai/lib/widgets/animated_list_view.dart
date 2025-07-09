import 'package:flutter/material.dart';

class AnimatedListView extends StatefulWidget {
  final List<Widget> children;
  final Duration itemDelay;
  final Duration itemDuration;
  final Curve curve;
  final ScrollController? scrollController;
  final EdgeInsetsGeometry? padding;

  const AnimatedListView({
    super.key,
    required this.children,
    this.itemDelay = const Duration(milliseconds: 100),
    this.itemDuration = const Duration(milliseconds: 400),
    this.curve = Curves.easeOutCubic,
    this.scrollController,
    this.padding,
  });

  @override
  State<AnimatedListView> createState() => _AnimatedListViewState();
}

class _AnimatedListViewState extends State<AnimatedListView>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;
  
  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _controllers = List.generate(
      widget.children.length,
      (index) => AnimationController(
        duration: widget.itemDuration,
        vsync: this,
      ),
    );

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(parent: controller, curve: widget.curve),
      );
    }).toList();

    // Stagger the animations
    _startStaggeredAnimations();
  }

  void _startStaggeredAnimations() {
    for (int i = 0; i < _controllers.length; i++) {
      Future.delayed(widget.itemDelay * i, () {
        if (mounted) {
          _controllers[i].forward();
        }
      });
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: widget.scrollController,
      padding: widget.padding,
      itemCount: widget.children.length,
      itemBuilder: (context, index) {
        return AnimatedBuilder(
          animation: _animations[index],
          builder: (context, child) {
            final animationValue = _animations[index].value;
            return Transform.translate(
              offset: Offset(0, 30 * (1 - animationValue)),
              child: Opacity(
                opacity: animationValue,
                child: Transform.scale(
                  scale: 0.8 + (0.2 * animationValue),
                  child: widget.children[index],
                ),
              ),
            );
          },
        );
      },
    );
  }
}

// Specific implementation for shopping items
class AnimatedShoppingItemCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onRemove;
  final Duration animationDuration;

  const AnimatedShoppingItemCard({
    super.key,
    required this.child,
    this.onRemove,
    this.animationDuration = const Duration(milliseconds: 300),
  });

  @override
  State<AnimatedShoppingItemCard> createState() => _AnimatedShoppingItemCardState();
}

class _AnimatedShoppingItemCardState extends State<AnimatedShoppingItemCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInBack,
    ));

    _opacityAnimation = Tween<double>(
      begin: 1.0,
      end: 0.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: Offset.zero,
      end: const Offset(1.0, 0.0),
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInCubic,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void animateRemoval() {
    _controller.forward().then((_) {
      widget.onRemove?.call();
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return SlideTransition(
          position: _slideAnimation,
          child: ScaleTransition(
            scale: _scaleAnimation,
            child: FadeTransition(
              opacity: _opacityAnimation,
              child: widget.child,
            ),
          ),
        );
      },
    );
  }
}
