import 'package:flutter/material.dart';
import '../utils/animation_manager.dart';

class SkeletonLoader extends StatefulWidget {
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final Color? baseColor;
  final Color? highlightColor;
  final bool enabled;
  final Widget? child;

  const SkeletonLoader({
    super.key,
    this.width,
    this.height,
    this.borderRadius,
    this.baseColor,
    this.highlightColor,
    this.enabled = true,
    this.child,
  });

  @override
  State<SkeletonLoader> createState() => _SkeletonLoaderState();
}

class _SkeletonLoaderState extends State<SkeletonLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationManager.instance.createController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
      debugLabel: 'SkeletonLoader',
    );

    _animation = Tween<double>(
      begin: -1.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    if (widget.enabled && AppAnimations.shouldAnimate()) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return widget.child ?? const SizedBox.shrink();
    }

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final baseColor = widget.baseColor ?? 
        (isDark ? Colors.grey[800]! : Colors.grey[300]!);
    final highlightColor = widget.highlightColor ?? 
        (isDark ? Colors.grey[700]! : Colors.grey[100]!);

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                baseColor,
                highlightColor,
                baseColor,
              ],
              stops: [
                (_animation.value - 0.5).clamp(0.0, 1.0),
                _animation.value.clamp(0.0, 1.0),
                (_animation.value + 0.5).clamp(0.0, 1.0),
              ],
            ),
          ),
        );
      },
    );
  }
}

// Predefined skeleton shapes
class SkeletonText extends StatelessWidget {
  final double? width;
  final double fontSize;
  final int lines;
  final double lineSpacing;

  const SkeletonText({
    super.key,
    this.width,
    this.fontSize = 14,
    this.lines = 1,
    this.lineSpacing = 4,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(lines, (index) {
        final isLastLine = index == lines - 1;
        final lineWidth = isLastLine && lines > 1 
            ? (width ?? 200) * 0.7 
            : width ?? 200;
            
        return Padding(
          padding: EdgeInsets.only(
            bottom: isLastLine ? 0 : lineSpacing,
          ),
          child: SkeletonLoader(
            width: lineWidth,
            height: fontSize * 1.2,
            borderRadius: BorderRadius.circular(fontSize * 0.3),
          ),
        );
      }),
    );
  }
}

class SkeletonCard extends StatelessWidget {
  final double? width;
  final double? height;
  final bool hasImage;
  final bool hasTitle;
  final bool hasSubtitle;
  final int descriptionLines;

  const SkeletonCard({
    super.key,
    this.width,
    this.height,
    this.hasImage = true,
    this.hasTitle = true,
    this.hasSubtitle = true,
    this.descriptionLines = 2,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (hasImage) ...[
            SkeletonLoader(
              width: double.infinity,
              height: 120,
              borderRadius: BorderRadius.circular(8),
            ),
            const SizedBox(height: 12),
          ],
          if (hasTitle) ...[
            const SkeletonText(
              width: 180,
              fontSize: 16,
            ),
            const SizedBox(height: 8),
          ],
          if (hasSubtitle) ...[
            const SkeletonText(
              width: 120,
              fontSize: 14,
            ),
            const SizedBox(height: 8),
          ],
          SkeletonText(
            width: double.infinity,
            fontSize: 12,
            lines: descriptionLines,
            lineSpacing: 6,
          ),
          const Spacer(),
          Row(
            children: [
              const SkeletonLoader(
                width: 80,
                height: 32,
                borderRadius: BorderRadius.all(Radius.circular(16)),
              ),
              const Spacer(),
              const SkeletonLoader(
                width: 40,
                height: 32,
                borderRadius: BorderRadius.all(Radius.circular(16)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class SkeletonList extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  final EdgeInsetsGeometry? padding;
  final Widget Function(int index)? itemBuilder;

  const SkeletonList({
    super.key,
    this.itemCount = 3,
    this.itemHeight = 80,
    this.padding,
    this.itemBuilder,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: padding,
      itemCount: itemCount,
      separatorBuilder: (context, index) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        if (itemBuilder != null) {
          return itemBuilder!(index);
        }
        
        return Container(
          height: itemHeight,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              const SkeletonLoader(
                width: 48,
                height: 48,
                borderRadius: BorderRadius.all(Radius.circular(24)),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SkeletonText(
                      width: 150,
                      fontSize: 14,
                    ),
                    const SizedBox(height: 8),
                    SkeletonText(
                      width: 100,
                      fontSize: 12,
                    ),
                  ],
                ),
              ),
              const SkeletonLoader(
                width: 60,
                height: 24,
                borderRadius: BorderRadius.all(Radius.circular(12)),
              ),
            ],
          ),
        );
      },
    );
  }
}

// Specialized skeleton for Bruno AI components
class SkeletonMealCard extends StatelessWidget {
  const SkeletonMealCard({super.key});

  @override
  Widget build(BuildContext context) {
    return const SkeletonCard(
      hasImage: true,
      hasTitle: true,
      hasSubtitle: true,
      descriptionLines: 2,
    );
  }
}

class SkeletonShoppingItem extends StatelessWidget {
  const SkeletonShoppingItem({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const SkeletonLoader(
            width: 40,
            height: 40,
            borderRadius: BorderRadius.all(Radius.circular(8)),
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SkeletonText(width: 120, fontSize: 14),
                SizedBox(height: 4),
                SkeletonText(width: 80, fontSize: 12),
              ],
            ),
          ),
          const SkeletonLoader(
            width: 50,
            height: 24,
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        ],
      ),
    );
  }
}
