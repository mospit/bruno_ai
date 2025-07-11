import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';
import '../widgets/bruno_avatar.dart';

/// Bruno AI Component Library - 2025 Design
/// Standardized UI components with consistent styling across the app
class BrunoComponents {
  BrunoComponents._();

  /// Enhanced Dashboard Card with consistent styling
  static Widget dashboardCard({
    required BuildContext context,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color iconColor,
    required VoidCallback onTap,
    Widget? trailing,
    bool isExpanded = false,
    List<Widget>? expandedContent,
  }) {
    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppColors.gray200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadowLight,
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: iconColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: iconColor,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.primary,
                        ),
                      ),
                      Text(
                        subtitle,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.textSecondary(context),
                        ),
                      ),
                    ],
                  ),
                ),
                trailing ?? Icon(
                  Icons.arrow_forward_ios,
                  color: AppColors.gray400,
                  size: 16,
                ),
              ],
            ),
            if (isExpanded && expandedContent != null) ...[
              const SizedBox(height: 16),
              ...expandedContent,
            ],
          ],
        ),
      ),
    );
  }

  /// Enhanced Button with Bruno AI styling
  static Widget primaryButton({
    required String text,
    required VoidCallback onPressed,
    bool isLoading = false,
    bool isDisabled = false,
    IconData? icon,
    double? width,
    EdgeInsets? padding,
  }) {
    return SizedBox(
      width: width,
      child: ElevatedButton(
        onPressed: isDisabled || isLoading ? null : () {
          HapticFeedback.lightImpact();
          onPressed();
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.white,
          padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 0,
          shadowColor: Colors.transparent,
        ),
        child: isLoading
            ? SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.white),
                ),
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 18),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    text,
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// Secondary Button with outline styling
  static Widget secondaryButton({
    required String text,
    required VoidCallback onPressed,
    bool isLoading = false,
    bool isDisabled = false,
    IconData? icon,
    double? width,
    EdgeInsets? padding,
  }) {
    return SizedBox(
      width: width,
      child: OutlinedButton(
        onPressed: isDisabled || isLoading ? null : () {
          HapticFeedback.lightImpact();
          onPressed();
        },
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: BorderSide(color: AppColors.primary, width: 2),
          padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: isLoading
            ? SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                ),
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 18),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    text,
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// Enhanced Header with Bruno integration
  static Widget enhancedHeader({
    required BuildContext context,
    required String title,
    required String subtitle,
    BrunoMood mood = BrunoMood.friendly,
    List<Widget>? actions,
    VoidCallback? onBrunoTap,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          BrunoAvatar(
            mood: mood,
            size: 40,
            animate: true,
            onTap: onBrunoTap,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                ),
              ],
            ),
          ),
          if (actions != null) ...actions,
        ],
      ),
    );
  }

  /// Standard Modal Bottom Sheet
  static void showBrunoModal({
    required BuildContext context,
    required String title,
    required Widget content,
    List<Widget>? actions,
    bool isDismissible = true,
    double initialChildSize = 0.6,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      isDismissible: isDismissible,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: initialChildSize,
        minChildSize: 0.3,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: BoxDecoration(
            color: AppColors.white,
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(20),
            ),
          ),
          child: Column(
            children: [
              // Handle bar
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.gray300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              // Header
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
              ),
              // Content
              Expanded(
                child: SingleChildScrollView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: content,
                ),
              ),
              // Actions
              if (actions != null) ...[
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: actions,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// Enhanced List Tile with Bruno styling
  static Widget listTile({
    required BuildContext context,
    required String title,
    String? subtitle,
    IconData? leadingIcon,
    Color? leadingIconColor,
    Widget? trailing,
    VoidCallback? onTap,
    bool showDivider = false,
  }) {
    return Column(
      children: [
        ListTile(
          leading: leadingIcon != null
              ? Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: (leadingIconColor ?? AppColors.primary).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    leadingIcon,
                    color: leadingIconColor ?? AppColors.primary,
                    size: 20,
                  ),
                )
              : null,
          title: Text(
            title,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary(context),
            ),
          ),
          subtitle: subtitle != null
              ? Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary(context),
                  ),
                )
              : null,
          trailing: trailing,
          onTap: onTap != null
              ? () {
                  HapticFeedback.lightImpact();
                  onTap();
                }
              : null,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        if (showDivider)
          Divider(
            color: AppColors.gray200,
            height: 1,
            indent: 16,
            endIndent: 16,
          ),
      ],
    );
  }

  /// Filter Chip with Bruno styling
  static Widget filterChip({
    required String label,
    required bool isSelected,
    required ValueChanged<bool> onSelected,
    IconData? icon,
  }) {
    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16),
            const SizedBox(width: 4),
          ],
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        HapticFeedback.lightImpact();
        onSelected(selected);
      },
      selectedColor: AppColors.primary.withOpacity(0.2),
      checkmarkColor: AppColors.primary,
      backgroundColor: AppColors.gray100,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      labelStyle: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: isSelected ? AppColors.primary : AppColors.gray700,
      ),
    );
  }

  /// Enhanced Progress Indicator
  static Widget progressIndicator({
    required double value,
    Color? backgroundColor,
    Color? valueColor,
    double height = 8,
    String? label,
    String? trailingText,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null || trailingText != null)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              if (label != null)
                Text(
                  label,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: AppColors.gray700,
                  ),
                ),
              if (trailingText != null)
                Text(
                  trailingText,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
            ],
          ),
        if (label != null || trailingText != null) const SizedBox(height: 8),
        Container(
          height: height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(height / 2),
            color: backgroundColor ?? AppColors.gray200,
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(height / 2),
            child: LinearProgressIndicator(
              value: value.clamp(0.0, 1.0),
              backgroundColor: Colors.transparent,
              valueColor: AlwaysStoppedAnimation<Color>(
                valueColor ?? AppColors.primary,
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Empty State Component
  static Widget emptyState({
    required BuildContext context,
    required String title,
    required String description,
    required IconData icon,
    String? actionText,
    VoidCallback? onAction,
    Color? iconColor,
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: (iconColor ?? AppColors.gray400).withOpacity(0.1),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(
                icon,
                size: 64,
                color: iconColor ?? AppColors.gray400,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary(context),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary(context),
              ),
              textAlign: TextAlign.center,
            ),
            if (actionText != null && onAction != null) ...[
              const SizedBox(height: 24),
              primaryButton(
                text: actionText,
                onPressed: onAction,
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// Enhanced Card with consistent styling
  static Widget card({
    required Widget child,
    EdgeInsets? padding,
    EdgeInsets? margin,
    Color? backgroundColor,
    double borderRadius = 16,
    List<BoxShadow>? boxShadow,
    Border? border,
    VoidCallback? onTap,
  }) {
    final cardContent = Container(
      padding: padding ?? const EdgeInsets.all(16),
      margin: margin,
      decoration: BoxDecoration(
        color: backgroundColor ?? AppColors.white,
        borderRadius: BorderRadius.circular(borderRadius),
        border: border ?? Border.all(
          color: AppColors.gray200,
          width: 1,
        ),
        boxShadow: boxShadow ?? [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: child,
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: () {
          HapticFeedback.lightImpact();
          onTap();
        },
        child: cardContent,
      );
    }

    return cardContent;
  }
}
