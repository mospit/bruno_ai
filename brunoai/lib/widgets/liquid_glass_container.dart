import 'package:flutter/material.dart';
import 'dart:ui';

class LiquidGlassContainer extends StatelessWidget {
  final Widget child;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;
  final Color? borderColor;
  final double borderWidth;
  final List<BoxShadow>? shadows;
  final bool enableBlur;
  final double blurSigma;
  final Gradient? gradient;
  
  const LiquidGlassContainer({
    super.key,
    required this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.borderRadius,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth = 1.0,
    this.shadows,
    this.enableBlur = true,
    this.blurSigma = 10.0,
    this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultBackgroundColor = backgroundColor ?? 
        (isDark 
            ? Colors.black.withOpacity(0.3)
            : Colors.white.withOpacity(0.7));
    
    final defaultBorderColor = borderColor ?? 
        (isDark 
            ? Colors.white.withOpacity(0.1)
            : Colors.white.withOpacity(0.3));
    
    final defaultShadows = shadows ?? [
      BoxShadow(
        color: isDark 
            ? Colors.black.withOpacity(0.3)
            : Colors.black.withOpacity(0.1),
        blurRadius: 20,
        offset: const Offset(0, 10),
      ),
      BoxShadow(
        color: isDark 
            ? Colors.white.withOpacity(0.05)
            : Colors.white.withOpacity(0.8),
        blurRadius: 1,
        offset: const Offset(0, 1),
      ),
    ];
    
    Widget container = Container(
      width: width,
      height: height,
      margin: margin,
      decoration: BoxDecoration(
        gradient: gradient ?? LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            defaultBackgroundColor,
            defaultBackgroundColor.withOpacity(0.8),
          ],
        ),
        borderRadius: borderRadius ?? BorderRadius.circular(20),
        border: Border.all(
          color: defaultBorderColor,
          width: borderWidth,
        ),
        boxShadow: defaultShadows,
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(16),
        child: child,
      ),
    );
    
    if (enableBlur) {
      return ClipRRect(
        borderRadius: borderRadius ?? BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: container,
        ),
      );
    }
    
    return container;
  }
}

// Specialized Liquid Glass variants
class LiquidGlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final VoidCallback? onTap;
  
  const LiquidGlassCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Widget card = LiquidGlassContainer(
      padding: padding ?? const EdgeInsets.all(20),
      margin: margin,
      borderRadius: BorderRadius.circular(24),
      child: child,
    );
    
    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        child: card,
      );
    }
    
    return card;
  }
}

class LiquidGlassButton extends StatelessWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final EdgeInsetsGeometry? padding;
  final BorderRadius? borderRadius;
  final bool isLoading;
  
  const LiquidGlassButton({
    super.key,
    required this.child,
    this.onPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.padding,
    this.borderRadius,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return GestureDetector(
      onTap: isLoading ? null : onPressed,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        child: LiquidGlassContainer(
          padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          borderRadius: borderRadius ?? BorderRadius.circular(16),
          backgroundColor: backgroundColor ?? 
              (isDark 
                  ? Colors.white.withOpacity(0.1)
                  : Colors.white.withOpacity(0.9)),
          borderColor: backgroundColor ?? 
              (isDark 
                  ? Colors.white.withOpacity(0.2)
                  : Colors.white.withOpacity(0.5)),
          child: isLoading 
              ? SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      foregroundColor ?? Theme.of(context).primaryColor,
                    ),
                  ),
                )
              : DefaultTextStyle(
                  style: TextStyle(
                    color: foregroundColor ?? Theme.of(context).primaryColor,
                    fontWeight: FontWeight.w600,
                  ),
                  child: child,
                ),
        ),
      ),
    );
  }
}

class LiquidGlassAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool centerTitle;
  
  const LiquidGlassAppBar({
    super.key,
    required this.title,
    this.actions,
    this.leading,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.8),
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).dividerColor.withOpacity(0.2),
                width: 0.5,
              ),
            ),
          ),
          child: AppBar(
            title: Text(title),
            actions: actions,
            leading: leading,
            centerTitle: centerTitle,
            backgroundColor: Colors.transparent,
            elevation: 0,
          ),
        ),
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}