import 'package:flutter/material.dart';

/// Bruno AI Unified Color System - 2025 Design
/// Bear-themed warm earth tones following the Bruno AI Style Guide
class AppColors {
  // Private constructor to prevent instantiation
  AppColors._();

  // === PRIMARY BRAND COLORS ===
  /// Bruno's signature brown - main brand color
  static const Color primary = Color(0xFF8B4513); // Warm Brown
  static const Color primaryLight = Color(0xFFD2691E); // Light brown
  static const Color primaryDark = Color(0xFF5A3A1F); // Dark brown (dark mode)
  
  /// Instacart Integration - keep brand consistency
  static const Color instacartGreen = Color(0xFF43B02A); // Instacart Green
  static const Color instacartGreenLight = Color(0xFF5CBF41); // Light green
  static const Color instacartGreenDark = Color(0xFF2E7D1C); // Dark green

  // === SUCCESS & FEEDBACK COLORS ===
  static const Color success = Color(0xFF10B981); // emerald-500
  static const Color successLight = Color(0xFF34D399); // emerald-400
  static const Color successDark = Color(0xFF059669); // emerald-600
  
  static const Color warning = Color(0xFFF59E0B); // amber-500
  static const Color warningLight = Color(0xFFFBBF24); // amber-400
  static const Color warningDark = Color(0xFFD97706); // amber-600
  
  static const Color error = Color(0xFFEF4444); // red-500
  static const Color errorLight = Color(0xFFF87171); // red-400
  static const Color errorDark = Color(0xFFDC2626); // red-600

  // === NEUTRAL SCALE ===
  static const Color white = Color(0xFFFFFFFF);
  static const Color gray50 = Color(0xFFFAFAFA);
  static const Color gray100 = Color(0xFFF5F5F5);
  static const Color gray200 = Color(0xFFE5E5E5);
  static const Color gray300 = Color(0xFFD4D4D4);
  static const Color gray400 = Color(0xFFA3A3A3);
  static const Color gray500 = Color(0xFF737373);
  static const Color gray600 = Color(0xFF525252);
  static const Color gray700 = Color(0xFF404040);
  static const Color gray800 = Color(0xFF262626);
  static const Color gray900 = Color(0xFF171717);

  // === SURFACE COLORS ===
  static const Color background = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF0F0F0F);
  static const Color surface = Color(0xFFFAFAFA);
  static const Color surfaceDark = Color(0xFF1C1C1C);

  // === GLASS/BLUR EFFECTS ===
  static const Color glassLight = Color(0x08FFFFFF);
  static const Color glassMedium = Color(0x12FFFFFF);
  static const Color glassDark = Color(0x20FFFFFF);
  static const Color glassAccent = Color(0x15FFFFFF);
  static const Color glassBorder = Color(0x20FFFFFF);

  // === SHADOW COLORS ===
  static const Color shadowLight = Color(0x0A000000);
  static const Color shadowMedium = Color(0x15000000);
  static const Color shadowDark = Color(0x25000000);

  // === BRUNO AI STYLE GUIDE COLORS ===
  /// Secondary colors from style guide
  static const Color softBeige = Color(0xFFD2B48C); // Soft Beige
  static const Color deepForestGreen = Color(0xFF228B22); // Deep Forest Green
  static const Color lightGray = Color(0xFFF5F5F5); // Light Gray
  
  /// Accent colors from style guide
  static const Color goldenYellow = Color(0xFFFFD700); // Golden Yellow
  static const Color errorRed = Color(0xFFFF4500); // Error Red (softened)
  static const Color successBlueGreen = Color(0xFF20B2AA); // Success Blue-Green
  
  /// Food and meal related colors
  static const Color foodAccent = Color(0xFFFF8C42); // warm orange
  
  /// Interactive states
  static const Color hover = Color(0x08000000);
  static const Color pressed = Color(0x12000000);
  static const Color focus = Color(0x12000000);
  static const Color disabled = Color(0x60000000);

  // === GRADIENT DEFINITIONS ===
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, primaryLight],
  );

  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [white, gray50],
  );

  static const LinearGradient glassGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [glassLight, glassMedium],
  );

  // === OPACITY HELPERS ===
  static Color withOpacity(Color color, double opacity) {
    return color.withValues(alpha: opacity);
  }

  // === COLOR SCHEME GENERATORS ===
  static ColorScheme get lightColorScheme => ColorScheme.light(
    primary: primary, // Bruno brown
    primaryContainer: primaryLight.withValues(alpha: 0.1),
    secondary: instacartGreen, // Instacart green for buttons
    secondaryContainer: instacartGreen.withValues(alpha: 0.1),
    tertiary: foodAccent,
    tertiaryContainer: foodAccent.withValues(alpha: 0.1),
    surface: background,
    surfaceContainerHighest: gray100,
    error: error,
    errorContainer: error.withValues(alpha: 0.1),
    onPrimary: white,
    onPrimaryContainer: primaryDark,
    onSecondary: white,
    onSecondaryContainer: instacartGreenDark,
    onTertiary: white,
    onTertiaryContainer: Color(0xFFB8460C),
    onSurface: gray900,
    onSurfaceVariant: gray600,
    onError: white,
    onErrorContainer: errorDark,
    outline: gray300,
    outlineVariant: gray200,
    shadow: shadowMedium,
    scrim: Color(0x80000000),
    inverseSurface: gray800,
    onInverseSurface: gray100,
    inversePrimary: primaryLight,
    surfaceTint: primary,
  );

  static ColorScheme get darkColorScheme => ColorScheme.dark(
    primary: primaryLight, // Light brown for dark mode
    primaryContainer: primaryDark,
    secondary: instacartGreenLight, // Light green for buttons
    secondaryContainer: instacartGreenDark,
    tertiary: foodAccent,
    tertiaryContainer: Color(0xFF9F3A00),
    surface: backgroundDark,
    surfaceContainerHighest: gray800,
    error: error,
    errorContainer: errorDark,
    onPrimary: gray900,
    onPrimaryContainer: primaryLight,
    onSecondary: gray900,
    onSecondaryContainer: instacartGreenLight,
    onTertiary: gray900,
    onTertiaryContainer: foodAccent,
    onSurface: gray100,
    onSurfaceVariant: gray400,
    onError: gray900,
    onErrorContainer: error,
    outline: gray600,
    outlineVariant: gray700,
    shadow: shadowDark,
    scrim: Color(0x80000000),
    inverseSurface: gray200,
    onInverseSurface: gray800,
    inversePrimary: primary,
    surfaceTint: primaryLight,
  );

  // === TEXT COLOR HELPERS ===
  static Color textPrimary(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray100 : gray900;
  }

  static Color textSecondary(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray400 : gray600;
  }

  static Color textTertiary(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray500 : gray500;
  }

  // === SURFACE COLOR HELPERS ===
  static Color surfacePrimary(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? surfaceDark : surface;
  }

  static Color surfaceSecondary(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray800 : gray100;
  }

  // === BORDER COLOR HELPERS ===
  static Color border(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray700 : gray200;
  }

  static Color borderStrong(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark ? gray600 : gray300;
  }
}

/// Extension to add convenience methods to Color class
extension ColorExtensions on Color {
  /// Create a MaterialColor swatch from this color
  MaterialColor toMaterialColor() {
    final int red = this.red;
    final int green = this.green;
    final int blue = this.blue;

    final Map<int, Color> shades = {
      50: Color.fromRGBO(red, green, blue, .1),
      100: Color.fromRGBO(red, green, blue, .2),
      200: Color.fromRGBO(red, green, blue, .3),
      300: Color.fromRGBO(red, green, blue, .4),
      400: Color.fromRGBO(red, green, blue, .5),
      500: Color.fromRGBO(red, green, blue, .6),
      600: Color.fromRGBO(red, green, blue, .7),
      700: Color.fromRGBO(red, green, blue, .8),
      800: Color.fromRGBO(red, green, blue, .9),
      900: Color.fromRGBO(red, green, blue, 1),
    };

    return MaterialColor(value, shades);
  }

  /// Get a lighter version of this color
  Color lighten([double factor = 0.1]) {
    assert(factor >= 0 && factor <= 1);
    final hsl = HSLColor.fromColor(this);
    final lightness = (hsl.lightness + factor).clamp(0.0, 1.0);
    return hsl.withLightness(lightness).toColor();
  }

  /// Get a darker version of this color
  Color darken([double factor = 0.1]) {
    assert(factor >= 0 && factor <= 1);
    final hsl = HSLColor.fromColor(this);
    final lightness = (hsl.lightness - factor).clamp(0.0, 1.0);
    return hsl.withLightness(lightness).toColor();
  }
}
