# Bruno AI Unified Color System - 2025 Design

This document outlines the unified color palette used across both the website and Flutter app to ensure perfect consistency.

## 🎨 Primary Brand Colors

### Main Accent Colors
- **Primary**: `#6366F1` (Indigo 500) - The beautiful purple/indigo from the website
- **Primary Light**: `#8B5CF6` (Purple 500) - Lighter variant for hover states
- **Primary Dark**: `#4F46E5` (Indigo 600) - Darker variant for pressed states

### Legacy Bruno Colors (Still Available)
- **Bruno Brown**: `#8B4513` - Original brown color
- **Bruno Warm**: `#D2691E` - Warm orange brown
- **Bruno Light**: `#DEB887` - Light tan

## 🎯 System Colors

### Success & Feedback
- **Success**: `#10B981` (Emerald 500)
- **Warning**: `#F59E0B` (Amber 500)  
- **Error**: `#EF4444` (Red 500)

### Neutral Scale (Tailwind-based)
- **White**: `#FFFFFF`
- **Gray 50**: `#FAFAFA`
- **Gray 100**: `#F5F5F5`
- **Gray 200**: `#E5E5E5`
- **Gray 300**: `#D4D4D4`
- **Gray 400**: `#A3A3A3`
- **Gray 500**: `#737373`
- **Gray 600**: `#525252`
- **Gray 700**: `#404040`
- **Gray 800**: `#262626`
- **Gray 900**: `#171717`

## 🌐 Website Implementation (CSS)

```css
:root {
    /* Primary Brand Colors */
    --primary: #6366f1;
    --primary-light: #8b5cf6;
    --primary-dark: #4f46e5;
    --accent: #6366f1;
    --accent-light: #8b5cf6;
    --accent-dark: #4f46e5;
    
    /* Neutrals */
    --white: #ffffff;
    --gray-50: #fafafa;
    --gray-100: #f5f5f5;
    --gray-200: #e5e5e5;
    --gray-300: #d4d4d4;
    --gray-400: #a3a3a3;
    --gray-500: #737373;
    --gray-600: #525252;
    --gray-700: #404040;
    --gray-800: #262626;
    --gray-900: #171717;
    
    /* System Colors */
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
}
```

## 📱 Flutter Implementation (Dart)

```dart
// lib/theme/app_colors.dart
class AppColors {
  // Primary Brand Colors
  static const Color primary = Color(0xFF6366F1);
  static const Color primaryLight = Color(0xFF8B5CF6);
  static const Color primaryDark = Color(0xFF4F46E5);
  
  // Neutrals
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
  
  // System Colors
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
}
```

## 🎭 Usage Guidelines

### Primary Actions
- Use `primary` (#6366F1) for main CTAs, buttons, and interactive elements
- Use `primary-light` (#8B5CF6) for hover states
- Use `primary-dark` (#4F46E5) for pressed/active states

### Text Hierarchy
- **Primary Text**: Gray 900 (#171717) for headings and important content
- **Secondary Text**: Gray 600 (#525252) for body text
- **Tertiary Text**: Gray 500 (#737373) for captions and less important text

### Backgrounds
- **Main Background**: White (#FFFFFF) with subtle gradients
- **Surface**: Gray 50 (#FAFAFA) for cards and elevated surfaces
- **Section Backgrounds**: Gray 100 (#F5F5F5) for subtle sections

### Borders & Dividers
- **Subtle Borders**: Gray 200 (#E5E5E5)
- **Strong Borders**: Gray 300 (#D4D4D4)

## 🔄 Conversion Reference

| Color Name | Hex | RGB | Flutter Hex |
|------------|-----|-----|-------------|
| Primary | #6366F1 | rgb(99, 102, 241) | 0xFF6366F1 |
| Primary Light | #8B5CF6 | rgb(139, 92, 246) | 0xFF8B5CF6 |
| Primary Dark | #4F46E5 | rgb(79, 70, 229) | 0xFF4F46E5 |
| Gray 900 | #171717 | rgb(23, 23, 23) | 0xFF171717 |
| Gray 600 | #525252 | rgb(82, 82, 82) | 0xFF525252 |
| Success | #10B981 | rgb(16, 185, 129) | 0xFF10B981 |

## 🎨 Design Tokens

The color system is designed to work seamlessly across:
- ✅ Website (CSS custom properties)
- ✅ Flutter app (Dart constants)
- ✅ Design tools (Figma, Adobe XD)
- ✅ Brand guidelines
- ✅ Marketing materials

## 🚀 Implementation Status

- [x] Website updated with unified colors
- [x] Flutter app colors defined
- [x] Modern theme created
- [x] Perfect color consistency achieved
- [x] Documentation completed

This unified color system ensures that Bruno AI maintains a cohesive visual identity across all platforms while embracing a modern, professional aesthetic that users will love! 🎉
