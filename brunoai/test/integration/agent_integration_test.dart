import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:brunoai/main.dart' as app;
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/widgets/chat_interface.dart';
import 'package:brunoai/services/api_service.dart';
import 'package:provider/provider.dart';

/// Comprehensive integration tests for Bruno AI agent functionality
/// Tests real agent responses, shopping list generation, budget tracking,
/// and meal planning capabilities through the chat interface.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Bruno AI Agent Integration Tests', () {
    late BrunoProvider provider;
    late ApiService apiService;

    setUp(() {
      apiService = ApiService();
    });

    testWidgets('Agent should respond to basic greeting', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send greeting message
      await _sendMessage(tester, 'Hello Bruno!');
      
      // Wait for agent response
      await tester.pumpAndSettle(const Duration(seconds: 5));
      
      // Verify Bruno responded with greeting
      expect(find.textContaining('Hi!'), findsOneWidget);
      expect(find.textContaining('Bruno'), findsOneWidget);
      
      // Verify message was processed by agent
      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.messages.length, greaterThanOrEqualTo(2));
      expect(provider.messages.last.isUser, isFalse);
    });

    testWidgets('Agent should handle budget setting and meal planning', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set budget
      await _sendMessage(tester, 'My weekly budget is \$80');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify budget was set
      expect(provider.currentBudget, equals('80'));
      
      // Verify agent acknowledged budget
      expect(find.textContaining('\$80'), findsAtLeastNWidgets(1));
      
      // Request meal plan
      await _sendMessage(tester, 'Plan meals for this week for 4 people');
      await tester.pumpAndSettle(const Duration(seconds: 8));
      
      // Verify meal plan response
      expect(find.textContaining('meal'), findsAtLeastNWidgets(1));
      expect(provider.messages.length, greaterThanOrEqualTo(4));
    });

    testWidgets('Agent should generate shopping list from meal requests', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request specific meal
      await _sendMessage(tester, 'I want to make chicken stir fry for dinner');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify shopping list was generated
      expect(provider.shoppingList.isNotEmpty, isTrue);
      expect(provider.totalCost, greaterThan(0));
      
      // Verify agent provided ingredients
      expect(find.textContaining('chicken'), findsAtLeastNWidgets(1));
      
      // Add to Instacart
      await _sendMessage(tester, 'Add everything to instacart');
      await tester.pumpAndSettle(const Duration(seconds: 5));
      
      // Verify instacart response
      expect(find.textContaining('cart'), findsAtLeastNWidgets(1));
    });

    testWidgets('Agent should handle dietary restrictions', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set dietary restrictions
      await _sendMessage(tester, 'I am vegetarian and gluten-free');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify dietary restrictions were noted
      expect(provider.dietaryRestrictions.isNotEmpty, isTrue);
      
      // Request meal suggestions
      await _sendMessage(tester, 'Suggest meals for \$60 budget');
      await tester.pumpAndSettle(const Duration(seconds: 8));
      
      // Verify vegetarian and gluten-free options
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('vegetarian') || lastMessage.contains('gluten'), isTrue);
    });

    testWidgets('Agent should handle budget constraints', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set low budget
      await _sendMessage(tester, 'My budget is only \$25 for the week');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.currentBudget, equals('25'));
      
      // Request expensive meal
      await _sendMessage(tester, 'I want lobster and steak dinners');
      await tester.pumpAndSettle(const Duration(seconds: 8));
      
      // Verify agent suggests budget-friendly alternatives
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('budget') || lastMessage.contains('affordable'), isTrue);
    });

    testWidgets('Agent should provide recipe details', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request recipe
      await _sendMessage(tester, 'Give me a recipe for spaghetti carbonara');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify recipe information is provided
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('recipe') || lastMessage.contains('ingredient'), isTrue);
      
      // Check if recipe card is shown
      expect(find.byType(Card), findsAtLeastNWidgets(1));
    });

    testWidgets('Agent should handle family size adjustments', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set family size
      await _sendMessage(tester, 'I need meals for 6 people');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.familySize, equals(6));
      
      // Request meal plan
      await _sendMessage(tester, 'Plan dinner for tonight');
      await tester.pumpAndSettle(const Duration(seconds: 8));
      
      // Verify serving size is adjusted
      expect(find.textContaining('6'), findsAtLeastNWidgets(1));
    });

    testWidgets('Agent should provide cost breakdowns', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request cost analysis
      await _sendMessage(tester, 'Show me the cheapest meals under \$15');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify cost information is provided
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('\$') || lastMessage.contains('cost'), isTrue);
      
      // Check if shopping list has pricing
      if (provider.shoppingList.isNotEmpty) {
        expect(provider.totalCost, greaterThan(0));
      }
    });

    testWidgets('Agent should handle store preferences', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set store preference
      await _sendMessage(tester, 'I prefer shopping at Whole Foods');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.selectedStore, equals('Whole Foods'));
      
      // Request shopping list
      await _sendMessage(tester, 'Create shopping list for pasta dinner');
      await tester.pumpAndSettle(const Duration(seconds: 8));
      
      // Verify store preference is acknowledged
      expect(find.textContaining('Whole Foods'), findsAtLeastNWidgets(1));
    });

    testWidgets('Agent should handle conversation context', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Start conversation
      await _sendMessage(tester, 'I want to cook Italian food');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Follow up question
      await _sendMessage(tester, 'What ingredients do I need?');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify agent maintains context
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('italian') || lastMessage.contains('ingredient'), isTrue);
    });

    testWidgets('Agent should handle error scenarios gracefully', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send invalid request
      await _sendMessage(tester, 'asdfghjkl qwertyuiop');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify agent handles gracefully
      expect(provider.messages.last.isUser, isFalse);
      expect(provider.messages.last.message.isNotEmpty, isTrue);
    });

    testWidgets('Agent should provide suggestions and quick actions', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send initial message
      await _sendMessage(tester, 'Help me plan meals');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Look for suggestion chips
      final suggestionChips = find.byType(Chip);
      if (suggestionChips.evaluate().isNotEmpty) {
        // Tap on suggestion
        await tester.tap(suggestionChips.first);
        await tester.pumpAndSettle(const Duration(seconds: 5));
        
        provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
        
        // Verify suggestion was processed
        expect(provider.messages.length, greaterThanOrEqualTo(3));
      }
    });

    testWidgets('Agent should handle reordering past meals', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request to reorder
      await _sendMessage(tester, 'Reorder my last meal');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify reorder functionality
      expect(provider.messages.last.isUser, isFalse);
      
      // Check if favorites are mentioned
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('favorite') || lastMessage.contains('last'), isTrue);
    });

    testWidgets('Agent should integrate with pantry management', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Ask about pantry items
      await _sendMessage(tester, 'What can I make with what I have?');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify pantry integration
      expect(provider.pantryList.isNotEmpty, isTrue);
      expect(provider.messages.last.isUser, isFalse);
    });

    testWidgets('Agent should handle multiple meal requests', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request multiple meals
      await _sendMessage(tester, 'Plan breakfast, lunch, and dinner for tomorrow');
      await tester.pumpAndSettle(const Duration(seconds: 10));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify comprehensive meal planning
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('breakfast') || 
             lastMessage.contains('lunch') || 
             lastMessage.contains('dinner'), isTrue);
    });

    testWidgets('Agent should provide nutritional information', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Request healthy options
      await _sendMessage(tester, 'Find healthy low-calorie meals');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Verify nutritional focus
      final lastMessage = provider.messages.last.message.toLowerCase();
      expect(lastMessage.contains('healthy') || 
             lastMessage.contains('calorie') || 
             lastMessage.contains('nutrition'), isTrue);
    });
  });

  group('Agent Performance Tests', () {
    testWidgets('Agent should respond within reasonable time', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      final stopwatch = Stopwatch()..start();
      
      await _sendMessage(tester, 'Quick meal suggestion');
      await tester.pumpAndSettle(const Duration(seconds: 10));
      
      stopwatch.stop();
      
      // Response should be within 10 seconds
      expect(stopwatch.elapsed.inSeconds, lessThan(10));
      
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      expect(provider.messages.last.isUser, isFalse);
    });

    testWidgets('Agent should handle concurrent requests', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Send multiple messages in sequence
      await _sendMessage(tester, 'First message');
      await _sendMessage(tester, 'Second message');
      await _sendMessage(tester, 'Third message');
      
      await tester.pumpAndSettle(const Duration(seconds: 15));
      
      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Should have all messages processed
      expect(provider.messages.length, greaterThanOrEqualTo(6)); // 3 user + 3 agent
    });
  });

  group('Agent State Management Tests', () {
    testWidgets('Agent should maintain state across app lifecycle', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Set initial state
      await _sendMessage(tester, 'My budget is \$100');
      await tester.pumpAndSettle(const Duration(seconds: 5));

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      final initialBudget = provider.currentBudget;
      final initialMessageCount = provider.messages.length;

      // Simulate app backgrounding and returning
      await tester.binding.defaultBinaryMessenger.handlePlatformMessage(
        'flutter/lifecycle',
        null,
        (data) {},
      );

      await tester.pumpAndSettle();

      // Verify state persisted
      expect(provider.currentBudget, equals(initialBudget));
      expect(provider.messages.length, equals(initialMessageCount));
    });

    testWidgets('Agent should handle provider updates correctly', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      final provider = tester.element(find.byType(ChatInterface)).read<BrunoProvider>();
      
      // Manually update provider state
      provider.setBudget('150');
      provider.setFamilySize(3);
      
      // Send message that uses this state
      await _sendMessage(tester, 'Plan meals based on my preferences');
      await tester.pumpAndSettle(const Duration(seconds: 8));

      // Verify agent uses updated state
      expect(provider.currentBudget, equals('150'));
      expect(provider.familySize, equals(3));
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
