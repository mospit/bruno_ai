# Bruno AI Testing Guide 🐻

This document provides comprehensive information about the testing setup for the Bruno AI Flutter application.

## 📋 Overview

Our testing strategy includes:
- **Unit Tests**: Testing individual classes and functions
- **Widget Tests**: Testing UI components and interactions
- **Integration Tests**: Testing complete user flows (setup for future implementation)

## 🧪 Test Structure

```
test/
├── unit/
│   ├── models/          # Data model tests
│   └── providers/       # State management tests
├── widget/              # Widget and UI tests
├── integration/         # End-to-end tests (framework ready)
├── test_utils.dart      # Test utilities and helpers
└── widget_test.dart     # Basic app structure test
```

## 🚀 Running Tests

### Using the Test Runner (Recommended)

We provide a custom test runner that makes testing easier:

```bash
# Run all tests
dart test_runner.dart

# Run specific test suites
dart test_runner.dart unit          # Unit tests only
dart test_runner.dart widget        # Widget tests only
dart test_runner.dart models        # Model tests only
dart test_runner.dart providers     # Provider tests only

# Run tests with coverage
dart test_runner.dart coverage

# Show help
dart test_runner.dart help
```

### Using Flutter Test Commands

```bash
# Run all tests
flutter test

# Run specific test directories
flutter test test/unit/
flutter test test/widget/

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/unit/models/meal_test.dart
```

## 📊 Test Coverage

Our tests cover the following components:

### Unit Tests (45 tests)

#### Models
- **FavoriteMeal** (3 tests)
  - Property creation and validation
  - Ingredient handling
  - Cost calculations

- **PastOrder** (4 tests)
  - Order data structure
  - Item collection management
  - Status tracking

- **Meal** (10 tests)
  - Complete meal data modeling
  - Ingredient categorization and parsing
  - Shopping item conversion
  - Cost per serving calculations
  - Unit detection and handling

#### Providers
- **BrunoProvider** (28 tests)
  - Chat message management
  - Typing state handling
  - Shopping list operations
  - Budget management
  - User preferences
  - AI response generation
  - Shopping actions

### Widget Tests (18 tests)

#### MealPlanCard Widget
- UI rendering and display
- User interactions and animations
- State management integration
- Edge case handling
- Accessibility features

### App Tests (1 test)
- Basic application structure validation
- Theme and provider setup

## 🛠 Test Utilities

The `test_utils.dart` file provides helpful utilities:

### TestUtils Class
```dart
// Create test app wrapper
TestUtils.createTestApp(child: widget, provider: mockProvider)

// Create mock data
TestUtils.createMockChatMessage(text: 'Hello', isFromUser: true)
TestUtils.createMockShoppingItem(name: 'Chicken', price: 8.99)
TestUtils.createMockMeal(name: 'Stir Fry', cost: 15.99)

// Create mock provider with data
TestUtils.createMockProvider(messages: [...], shoppingList: [...])

// Animation helpers
TestUtils.waitForAnimations(tester)
TestUtils.pumpUntilNoMoreFrames(tester)

// Interaction helpers
TestUtils.tapAndWait(tester, finder)
TestUtils.enterTextAndSend(tester, textField, 'message')
```

### Custom Matchers
```dart
// Shopping item matcher
expect(item, CustomMatchers.isShoppingItemWith(name: 'Chicken', price: 8.99))

// Chat message matcher
expect(message, CustomMatchers.isChatMessageWith(text: 'Hello', isFromUser: true))

// Meal matcher
expect(meal, CustomMatchers.isMealWith(name: 'Stir Fry', isHealthy: true))
```

## 🔧 Test Configuration

### Dependencies
The following test dependencies are configured in `pubspec.yaml`:

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  mockito: ^5.4.2
  build_runner: ^2.4.7
  test: ^1.24.6
  integration_test:
    sdk: flutter
  fake_async: ^1.3.1
  clock: ^1.1.1
```

### Mock Generation
For complex mocking scenarios, we can use mockito:

```bash
# Generate mocks
flutter packages pub run build_runner build
```

## 📈 Coverage Reports

Generate and view coverage reports:

```bash
# Generate coverage
dart test_runner.dart coverage

# View coverage (if lcov is installed)
genhtml -o coverage/html coverage/lcov.info
open coverage/html/index.html
```

## 🎯 Testing Best Practices

### Unit Tests
- Test one thing at a time
- Use descriptive test names
- Mock external dependencies
- Test edge cases and error conditions
- Verify both positive and negative scenarios

### Widget Tests
- Test user interactions
- Verify UI state changes
- Test accessibility features
- Mock providers and services
- Test responsive behavior

### Integration Tests
- Test complete user workflows
- Verify data persistence
- Test cross-screen navigation
- Validate real API interactions

## 🐛 Debugging Tests

### Common Issues

1. **Timer-related failures**: Use `fakeAsync` for controlling time
2. **Animation issues**: Use `pumpAndSettle()` or `pump()` with durations
3. **Provider state issues**: Ensure proper provider setup in test widgets
4. **Widget not found**: Use `finder.evaluate().isNotEmpty` to check existence

### Debug Output
```dart
// Print widget tree
debugDumpApp();

// Print render tree
debugDumpRenderTree();

// Print semantics
debugDumpSemanticsTree();
```

## 🚀 Future Enhancements

### Planned Test Additions
- **Integration Tests**: Complete user flows
- **Golden Tests**: UI regression testing
- **Performance Tests**: Load and stress testing
- **Accessibility Tests**: Screen reader and navigation testing

### CI/CD Integration
Tests are ready for integration with:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: dart test_runner.dart
      - run: dart test_runner.dart coverage
```

## 📚 Additional Resources

- [Flutter Testing Documentation](https://docs.flutter.dev/testing)
- [Widget Testing Guide](https://docs.flutter.dev/cookbook/testing/widget)
- [Integration Testing](https://docs.flutter.dev/testing/integration-tests)
- [Mockito Documentation](https://pub.dev/packages/mockito)

---

## 🤝 Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure all tests pass** before submitting
3. **Maintain test coverage** above 80%
4. **Update test documentation** for new patterns
5. **Follow naming conventions** for test files and descriptions

Happy testing! 🧪✨
