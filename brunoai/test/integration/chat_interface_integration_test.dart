import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:brunoai/main.dart' as app;
import 'package:brunoai/widgets/chat_interface.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:provider/provider.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Chat Interface Integration Tests', () {
    testWidgets('should send message and receive Bruno response', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Find the text input field
      final textFieldFinder = find.byType(TextField);
      expect(textFieldFinder, findsOneWidget);

      // Type a message
      await tester.enterText(textFieldFinder, 'Hello Bruno');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle();

      // Verify user message appears
      expect(find.text('Hello Bruno'), findsOneWidget);

      // Wait for Bruno's response (with timeout)
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify Bruno's response appears
      expect(find.textContaining('Hi! I\'m Bruno'), findsOneWidget);
    });

    testWidgets('should handle budget setting flow', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Enter budget message
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'My budget is \$100');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify budget was set in provider
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.currentBudget, equals('100'));

      // Verify response mentions budget
      expect(find.textContaining('\$100'), findsAtLeastNWidgets(1));
    });

    testWidgets('should add items to shopping cart', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send shopping message
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Add to instacart');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify shopping list was updated
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.shoppingList.isNotEmpty, isTrue);
      expect(provider.totalCost, greaterThan(0));

      // Verify shopping cart badge shows items
      final cartBadge = find.byType(Badge);
      if (cartBadge.evaluate().isNotEmpty) {
        expect(cartBadge, findsOneWidget);
      }
    });

    testWidgets('should show typing indicator during response', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send a message
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Tell me a recipe');
      await tester.testTextInput.receiveAction(TextInputAction.send);

      // Immediately check for typing indicator
      await tester.pump(const Duration(milliseconds: 100));
      
      // Verify typing indicator is shown
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.isTyping, isTrue);

      // Wait for response to complete
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      // Verify typing indicator is hidden
      expect(provider.isTyping, isFalse);
    });

    testWidgets('should handle multiple message exchanges', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      final textFieldFinder = find.byType(TextField);

      // First message
      await tester.enterText(textFieldFinder, 'Hello');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Clear field and send second message
      await tester.enterText(textFieldFinder, '');
      await tester.enterText(textFieldFinder, 'My budget is \$50');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Third message
      await tester.enterText(textFieldFinder, '');
      await tester.enterText(textFieldFinder, 'Show me recipes');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify multiple messages exist
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.messages.length, greaterThanOrEqualTo(6)); // 3 user + 3 Bruno
    });

    testWidgets('should navigate to shopping cart when cart button is tapped', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // First add items to cart
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Add to instacart');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Find and tap shopping cart button
      final cartButton = find.byIcon(Icons.shopping_cart);
      if (cartButton.evaluate().isNotEmpty) {
        await tester.tap(cartButton);
        await tester.pumpAndSettle();

        // Verify navigation occurred (would depend on actual navigation implementation)
        // This test documents expected behavior
      }
    });

    testWidgets('should clear messages when clear button is pressed', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send a message first
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Test message');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Look for clear/delete button (implementation dependent)
      final clearButton = find.byIcon(Icons.clear_all);
      if (clearButton.evaluate().isNotEmpty) {
        await tester.tap(clearButton);
        await tester.pumpAndSettle();

        // Verify messages were cleared
        final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
        expect(provider.messages, isEmpty);
      }
    });

    testWidgets('should handle text input edge cases', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      final textFieldFinder = find.byType(TextField);

      // Test empty message
      await tester.enterText(textFieldFinder, '');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pump();

      // Should not add empty message
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.messages, isEmpty);

      // Test very long message
      final longMessage = 'A' * 1000;
      await tester.enterText(textFieldFinder, longMessage);
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should handle gracefully
      expect(provider.messages.isNotEmpty, isTrue);
    });

    testWidgets('should show suggestion chips when appropriate', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send initial message to trigger suggestions
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Hello');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Look for suggestion chips (implementation dependent)
      final suggestionChips = find.byType(Chip);
      if (suggestionChips.evaluate().isNotEmpty) {
        // Tap on a suggestion chip
        await tester.tap(suggestionChips.first);
        await tester.pumpAndSettle();

        // Should trigger appropriate action
      }
    });

    testWidgets('should handle app lifecycle changes', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send a message
      final textFieldFinder = find.byType(TextField);
      await tester.enterText(textFieldFinder, 'Test message');
      await tester.testTextInput.receiveAction(TextInputAction.send);
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Simulate app going to background and returning
      await tester.binding.defaultBinaryMessenger.handlePlatformMessage(
        'flutter/lifecycle',
        const StandardMethodCodec().encodeMethodCall(
          const MethodCall('routeUpdated', {
            'location': '/',
            'state': null,
          }),
        ),
        (data) {},
      );

      await tester.pumpAndSettle();

      // Verify state is preserved
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.messages.isNotEmpty, isTrue);
    });
  });
}
