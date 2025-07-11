# Bruno AI - Smart Meal Planning Assistant

Bruno AI is a comprehensive Flutter application that revolutionizes meal planning and grocery shopping through AI-powered assistance. Built with a warm, bear-themed design system, Bruno helps users manage their pantry, plan meals, and shop efficiently while providing personalized recommendations.

## 🐻 About Bruno

Bruno is your friendly AI meal planning companion that combines the power of artificial intelligence with a delightful, bear-themed user experience. The app focuses on reducing food waste, saving money, and making meal planning enjoyable.

## ✨ Key Features

### 🏠 Smart Dashboard
- Real-time pantry status and expiration alerts
- Budget tracking and savings insights
- Personalized meal recommendations
- Quick action shortcuts

### 🗣️ AI Chat Interface
- Natural conversation with Bruno AI
- Recipe suggestions based on available ingredients
- Meal planning assistance
- Dietary preference understanding

### 🥫 Pantry Management
- Barcode scanning for quick item addition
- Expiration date tracking
- Smart categorization
- Usage recommendations

### 🛒 Smart Shopping
- AI-generated shopping lists
- Budget optimization
- Store integration (Instacart)
- Deal and discount detection

### 👨‍🍳 Meal Preparation
- Step-by-step cooking instructions
- Timer integration
- Ingredient substitution suggestions
- Nutritional information

## 🎨 Design System

### Color Palette
Bruno AI uses a warm, bear-themed color system:
- **Primary**: Warm Brown (#8B4513) - Bruno's signature color
- **Secondary**: Instacart Green (#43B02A) - For shopping integration
- **Accent**: Soft Beige (#D2B48C) and Deep Forest Green (#228B22)
- **Neutrals**: Comprehensive gray scale for UI elements

### Typography
- **Font Family**: Nunito - Warm and friendly bear-inspired typography
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semi-bold), 700 (Bold), 800 (Extra-bold)
- **Responsive scaling** for accessibility

### Animation System
Bruno AI features a comprehensive animation system following strict standards:

#### Animation Standards
- **Duration Range**: 200-500ms for all animations
  - 200ms: Micro-interactions (button press)
  - 300ms: Standard transitions
  - 400ms: Screen changes
  - 500ms: Complex animations

- **Curves**: 
  - `Curves.easeInOut`: Smooth transitions
  - `Curves.bounceIn`: Playful elements (Bruno's nods)

- **Performance**: 60fps target with smart fallbacks
- **Accessibility**: Respects reduced motion settings
- **Haptic Feedback**: Light impact on interactions

#### Animation Components
1. **AnimatedCard**: Fade-in cards with optional slide
2. **BounceButton**: Playful bounce for positive feedback
3. **AnimatedCheckbox**: Scale and fill animation
4. **AnimatedProgressBar**: Smooth progress transitions
5. **BrunoPageTransition**: Custom page transitions

#### Animation Colors
- **Green**: Success states
- **Brown**: Loading states (Bruno's signature)
- **Orange/Red**: Error states
- **Gray**: Neutral states

## 🏗️ Architecture

### State Management
- **Provider Pattern**: Centralized state management
- **BrunoProvider**: Main application state
- **Reactive UI**: Real-time updates across screens

### Project Structure
```
lib/
├── animations/          # Animation system
│   └── bruno_animations.dart
├── models/             # Data models
├── providers/          # State management
├── screens/            # App screens
├── services/           # API and external services
├── theme/              # Design system
│   ├── app_colors.dart
│   ├── bruno_typography.dart
│   └── modern_theme.dart
├── utils/              # Utility functions
└── widgets/            # Reusable components
```

### Key Components
- **BrunoAvatar**: Animated bear avatar with mood states
- **ChatInterface**: AI conversation UI
- **SmartDashboard**: Home screen with insights
- **ShoppingCart**: Integrated shopping experience
- **MealCard**: Interactive meal planning cards

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (^3.19.0)
- Dart SDK (^3.3.0)
- Android Studio / VS Code
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bruno-ai.git
   cd bruno-ai
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

### Development Setup

1. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Configure API keys for external services

2. **Code Generation**
   ```bash
   flutter packages pub run build_runner build
   ```

3. **Testing**
   ```bash
   flutter test
   ```

## 📱 Screens Overview

### Home Screen
- Smart dashboard with pantry insights
- Budget tracking visualization
- Quick action buttons
- Bruno AI avatar with contextual moods

### Chat Screen
- Natural language interface with Bruno
- Recipe suggestions and meal planning
- Contextual responses based on pantry
- Voice input support

### Pantry Screen
- Grid/List view toggle
- Category filtering
- Expiration tracking with color coding
- Barcode scanning integration

### Shopping Screen
- AI-generated shopping lists
- Budget progress tracking
- Store integration (Instacart)
- Deal optimization

### Meal Prep Screen
- Recipe browsing and search
- Step-by-step cooking instructions
- Timer integration
- Ingredient substitutions

## 🔧 Configuration

### Theme Customization
The app supports extensive theming through the `ModernTheme` class:
- Light and dark mode support
- Bruno-specific color palette
- Nunito typography system
- Custom animation transitions

### Animation Settings
Animations can be configured in `BrunoAnimations`:
- Duration customization
- Curve modifications
- Accessibility overrides
- Performance optimizations

## 🧪 Testing

### Test Categories
- **Unit Tests**: Model and provider logic
- **Widget Tests**: Component behavior
- **Integration Tests**: End-to-end workflows

### Running Tests
```bash
# All tests
flutter test

# Specific test files
flutter test test/unit/providers/bruno_provider_test.dart

# Integration tests
flutter test integration_test/
```

## 📚 Key Dependencies

### Core
- `flutter`: Framework
- `provider`: State management
- `http`: API communication

### UI/UX
- `google_fonts`: Nunito typography
- `lottie`: Complex animations
- `cached_network_image`: Image optimization

### Functionality
- `shared_preferences`: Local storage
- `path_provider`: File system access
- `barcode_scan2`: Barcode scanning

### Development
- `flutter_test`: Testing framework
- `build_runner`: Code generation
- `json_annotation`: JSON serialization

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Follow the coding standards
4. Add tests for new features
5. Update documentation
6. Submit a pull request

### Coding Standards
- Follow Dart/Flutter style guide
- Use meaningful variable names
- Document public APIs
- Maintain test coverage >80%

### Animation Guidelines
- All animations must be 200-500ms
- Use appropriate curves for context
- Include haptic feedback
- Respect accessibility settings
- Test on various devices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bruno AI design inspired by friendly bear aesthetics
- Animation system following Flutter best practices
- Typography system using Google Fonts (Nunito)
- State management patterns from Flutter community

## 📞 Support

For support, email support@bruno-ai.com or join our community Discord.

---

**Built with ❤️ and 🐻 by the Bruno AI team**
