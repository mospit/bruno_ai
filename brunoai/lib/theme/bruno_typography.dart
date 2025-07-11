import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// Bruno AI Typography Theme - 2025 Design
/// Implements Nunito font family for warm, approachable bear-themed design
/// Following the recommended typography hierarchy from the style guide
class BrunoTypography {
  // Private constructor
  BrunoTypography._();

  /// Get Nunito text theme for light mode
  static TextTheme get lightTextTheme {
    return GoogleFonts.nunitoTextTheme().copyWith(
      // H1 - Screen titles (e.g., "Pantry Management")
      headlineLarge: GoogleFonts.nunito(
        fontSize: 24,
        fontWeight: FontWeight.w700, // Bold
        color: AppColors.primary, // Warm Brown (#8B4513)
        letterSpacing: 0.5,
        height: 1.5,
      ),
      
      // H2 - Card titles, section headers (e.g., "Shopping Suggestions")
      headlineMedium: GoogleFonts.nunito(
        fontSize: 18,
        fontWeight: FontWeight.w500, // Medium
        color: const Color(0xFF228B22), // Deep Forest Green
        letterSpacing: 0.5,
        height: 1.5,
      ),
      
      // Title Large - Main card titles
      titleLarge: GoogleFonts.nunito(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppColors.primary,
        letterSpacing: -0.01,
        height: 1.3,
      ),
      
      // Title Medium - Secondary titles
      titleMedium: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: AppColors.primary,
        height: 1.4,
      ),
      
      // Body Large - Main content, item descriptions
      bodyLarge: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w400, // Regular
        color: const Color(0xFF333333), // Dark Gray
        height: 1.5,
      ),
      
      // Body Medium - Secondary content
      bodyMedium: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: const Color(0xFF333333),
        height: 1.5,
      ),
      
      // Body Small - Captions, tags (e.g., "Exp: 2 days")
      bodySmall: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w300, // Light
        color: const Color(0xFF808080), // Light Gray
        height: 1.4,
      ),
      
      // Label Large - Button text, CTAs
      labelLarge: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w700, // Bold
        color: Colors.white,
        letterSpacing: 0.1,
      ),
      
      // Label Medium - Secondary buttons
      labelMedium: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: AppColors.primary,
        letterSpacing: 0.1,
      ),
      
      // Label Small - Small buttons, chips
      labelSmall: GoogleFonts.nunito(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: AppColors.primary,
        letterSpacing: 0.1,
      ),
    );
  }

  /// Get Nunito text theme for dark mode
  static TextTheme get darkTextTheme {
    return GoogleFonts.nunitoTextTheme(ThemeData.dark().textTheme).copyWith(
      // H1 - Screen titles
      headlineLarge: GoogleFonts.nunito(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: AppColors.primaryLight, // Lighter brown for dark mode
        letterSpacing: 0.5,
        height: 1.5,
      ),
      
      // H2 - Card titles, section headers
      headlineMedium: GoogleFonts.nunito(
        fontSize: 18,
        fontWeight: FontWeight.w500,
        color: const Color(0xFF90EE90), // Light green for dark mode
        letterSpacing: 0.5,
        height: 1.5,
      ),
      
      // Title Large
      titleLarge: GoogleFonts.nunito(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppColors.primaryLight,
        letterSpacing: -0.01,
        height: 1.3,
      ),
      
      // Title Medium
      titleMedium: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: AppColors.primaryLight,
        height: 1.4,
      ),
      
      // Body Large - Main content
      bodyLarge: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: AppColors.gray100,
        height: 1.5,
      ),
      
      // Body Medium
      bodyMedium: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: AppColors.gray200,
        height: 1.5,
      ),
      
      // Body Small - Captions, tags
      bodySmall: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w300,
        color: AppColors.gray400,
        height: 1.4,
      ),
      
      // Label Large - Button text
      labelLarge: GoogleFonts.nunito(
        fontSize: 16,
        fontWeight: FontWeight.w700,
        color: Colors.white,
        letterSpacing: 0.1,
      ),
      
      // Label Medium
      labelMedium: GoogleFonts.nunito(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: AppColors.primaryLight,
        letterSpacing: 0.1,
      ),
      
      // Label Small
      labelSmall: GoogleFonts.nunito(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: AppColors.primaryLight,
        letterSpacing: 0.1,
      ),
    );
  }

  /// Preload Nunito fonts for better performance
  static Future<void> preloadFonts() async {
    await GoogleFonts.pendingFonts([
      GoogleFonts.nunito(),
      GoogleFonts.nunito(fontWeight: FontWeight.w300),
      GoogleFonts.nunito(fontWeight: FontWeight.w400),
      GoogleFonts.nunito(fontWeight: FontWeight.w500),
      GoogleFonts.nunito(fontWeight: FontWeight.w600),
      GoogleFonts.nunito(fontWeight: FontWeight.w700),
    ]);
  }

  /// Get error/alert text style
  static TextStyle get errorTextStyle => GoogleFonts.nunito(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: const Color(0xFFFF4500), // Error Red
    height: 1.4,
  );

  /// Get success text style
  static TextStyle get successTextStyle => GoogleFonts.nunito(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: AppColors.success,
    height: 1.4,
  );

  /// Get input hint text style
  static TextStyle get hintTextStyle => GoogleFonts.nunito(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: const Color(0xFF808080),
  );

  /// Get app bar title style
  static TextStyle get appBarTitleStyle => GoogleFonts.nunito(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AppColors.primary,
  );

  /// Get navigation label style
  static TextStyle get navigationLabelStyle => GoogleFonts.nunito(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: AppColors.primary,
  );

  /// Dynamic text scaling support
  static TextStyle scaleText(TextStyle style, BuildContext context) {
    final textScaler = MediaQuery.textScalerOf(context);
    return style.copyWith(
      fontSize: style.fontSize != null 
          ? textScaler.scale(style.fontSize!) 
          : null,
    );
  }
}
