import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:brunoai/main.dart' as app;
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/widgets/chat_interface.dart';
import 'package:provider/provider.dart';

/// Simple agent integration tests that work with fallback responses
/// These tests verify the chat interface works and can handle agent responses
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Bruno AI Agent Simple Tests', () {
    testWidgets('Chat interface should load and display welcome message', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Verify welcome screen is shown
      expect(find.textContaining('Hi there! I\'m Bruno'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('User can send messages and get responses', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send a greeting message
      await _sendMessage(tester, 'Hello Bruno!');
      
      // Wait for response (uses fallback if server unavailable)
      await tester.pumpAndSettle(const Duration(seconds: 3));
      
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify message was sent and response received
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.messages.first.isUser, isTrue);
      expect(provider.messages.first.message, equals('Hello Bruno!'));
      expect(provider.messages.last.isUser, isFalse);
    });

    testWidgets('Agent responds to budget setting', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send budget message
      await _sendMessage(tester, 'My weekly budget is \$100');
      await tester.pumpAndSettle(const Duration(seconds: 3));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify budget was processed (either by server or fallback)
      expect(provider.currentBudget, equals('100'));
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      
      // Verify response mentions budget
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('budget') || lastMessage.contains('\$100'), isTrue);
    });

    testWidgets('Agent can handle recipe requests', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send recipe request
      await _sendMessage(tester, 'I want a chicken recipe');
      await tester.pumpAndSettle(const Duration(seconds: 3));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify response contains recipe information
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('recipe') || lastMessage.contains('chicken'), isTrue);
    });

    testWidgets('Agent can handle shopping requests', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send shopping request
      await _sendMessage(tester, 'Add to instacart');
      await tester.pumpAndSettle(const Duration(seconds: 3));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify shopping list was updated
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.shoppingList.isNotEmpty, isTrue);
      
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('cart') || lastMessage.contains('shopping'), isTrue);
    });

    testWidgets('Typing indicator shows during response', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send message and immediately check typing indicator
      await _sendMessage(tester, 'Quick test');
      await tester.pump(const Duration(milliseconds: 100));
      
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Typing indicator should be shown during processing
      expect(provider.isTyping, isTrue);
      
      // Wait for response and verify typing indicator is hidden
      await tester.pumpAndSettle(const Duration(seconds: 3));
      expect(provider.isTyping, isFalse);
    });

    testWidgets('Multiple messages maintain conversation context', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send first message
      await _sendMessage(tester, 'Hello');
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Send second message
      await _sendMessage(tester, 'My budget is \$50');
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Send third message
      await _sendMessage(tester, 'Plan meals');
      await tester.pumpAndSettle(const Duration(seconds: 2));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify conversation flow
      expect(provider.messages.length, greaterThanOrEqualTo(6)); // 3 user + 3 agent
      expect(provider.currentBudget, equals('50'));
    });

    testWidgets('Quick action buttons work', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Look for quick action buttons in welcome screen
      final quickActionButtons = find.textContaining('Set Budget');
      
      if (quickActionButtons.evaluate().isNotEmpty) {
        await tester.tap(quickActionButtons.first);
        await tester.pumpAndSettle(const Duration(seconds: 2));
        
        final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
        
        // Verify quick action triggered message
        expect(provider.messages.isNotEmpty, isTrue);
      }
    });

    testWidgets('App handles network errors gracefully', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send message that might fail network request
      await _sendMessage(tester, 'Test network failure');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Should still get a response (fallback mode)
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.messages.last.isUser, isFalse);
    });
  });
}

/// Helper function to send a message in the chat interface
Future<void> _sendMessage(WidgetTester tester, String message) async {
  final textField = find.byType(TextField);
  expect(textField, findsOneWidget);

  await tester.enterText(textField, message);
  await tester.testTextInput.receiveAction(TextInputAction.send);
  await tester.pump();
}
