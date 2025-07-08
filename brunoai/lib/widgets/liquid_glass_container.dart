import 'package:flutter/material.dart';
import 'dart:ui';
import '../theme/app_colors.dart';

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
    this.blurSigma = 3.0,
    this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultBackgroundColor = backgroundColor ?? 
        (isDark 
            ? AppColors.white.withOpacity(0.05)
            : AppColors.white.withOpacity(0.85));
    
    final defaultBorderColor = borderColor ?? 
        (isDark 
            ? AppColors.white.withOpacity(0.08)
            : AppColors.white.withOpacity(0.4));
    
    final defaultShadows = shadows ?? [
      BoxShadow(
        color: isDark 
            ? AppColors.shadowDark
            : AppColors.shadowLight,
        blurRadius: 20,
        offset: const Offset(0, 4),
        spreadRadius: 0,
      ),
      BoxShadow(
        color: isDark 
            ? AppColors.shadowMedium
            : AppColors.shadowLight.withOpacity(0.5),
        blurRadius: 40,
        offset: const Offset(0, 8),
        spreadRadius: 0,
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

class LiquidGlassButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final EdgeInsetsGeometry? padding;
  final BorderRadius? borderRadius;
  final bool isLoading;
  final bool isPrimary;
  
  const LiquidGlassButton({
    super.key,
    required this.child,
    this.onPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.padding,
    this.borderRadius,
    this.isLoading = false,
    this.isPrimary = false,
  });

  @override
  State<LiquidGlassButton> createState() => _LiquidGlassButtonState();
}

class _LiquidGlassButtonState extends State<LiquidGlassButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    if (widget.onPressed != null && !widget.isLoading) {
      setState(() => _isPressed = true);
      _animationController.forward();
    }
  }

  void _handleTapUp(TapUpDetails details) {
    _handleTapEnd();
  }

  void _handleTapCancel() {
    _handleTapEnd();
  }

  void _handleTapEnd() {
    if (_isPressed) {
      setState(() => _isPressed = false);
      _animationController.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return GestureDetector(
      onTap: widget.isLoading ? null : widget.onPressed,
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              decoration: BoxDecoration(
                gradient: widget.isPrimary
                    ? LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Theme.of(context).primaryColor,
                          Theme.of(context).primaryColor.withOpacity(0.8),
                        ],
                      )
                    : null,
                color: widget.isPrimary
                    ? null
                    : widget.backgroundColor ??
                        (isDark
                            ? AppColors.white.withOpacity(0.1)
                            : AppColors.white.withOpacity(0.9)),
                borderRadius: widget.borderRadius ?? BorderRadius.circular(16),
                border: Border.all(
                  color: widget.isPrimary
                      ? AppColors.white.withOpacity(0.2)
                      : widget.backgroundColor ??
                          (isDark
                              ? AppColors.white.withOpacity(0.2)
                              : AppColors.gray300.withOpacity(0.5)),
                  width: 1,
                ),
                boxShadow: [
                  BoxShadow(
                    color: widget.isPrimary
                        ? Theme.of(context).primaryColor.withOpacity(0.3)
                        : AppColors.shadowLight,
                    blurRadius: _isPressed ? 8 : 12,
                    offset: Offset(0, _isPressed ? 2 : 4),
                    spreadRadius: 0,
                  ),
                  if (!_isPressed)
                    BoxShadow(
                      color: AppColors.shadowLight.withOpacity(0.5),
                      blurRadius: 24,
                      offset: const Offset(0, 8),
                      spreadRadius: 0,
                    ),
                ],
              ),
              child: ClipRRect(
                borderRadius: widget.borderRadius ?? BorderRadius.circular(16),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 2.0, sigmaY: 2.0),
                  child: Padding(
                    padding: widget.padding ??
                        const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    child: widget.isLoading
                        ? SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                widget.foregroundColor ??
                                    (widget.isPrimary
                                        ? AppColors.white
                                        : Theme.of(context).primaryColor),
                              ),
                            ),
                          )
                        : DefaultTextStyle(
                            style: TextStyle(
                              color: widget.foregroundColor ??
                                  (widget.isPrimary
                                      ? AppColors.white
                                      : Theme.of(context).primaryColor),
                              fontWeight: FontWeight.w600,
                            ),
                            child: widget.child,
                          ),
                  ),
                ),
              ),
            ),
          );
        },
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