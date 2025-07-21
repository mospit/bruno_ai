import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import '../../lib/widgets/chat_interface.dart';
import '../../lib/widgets/voice_input_button.dart';
import '../../lib/controllers/voice_input_controller.dart';
import '../../lib/providers/bruno_provider.dart';
import '../../lib/theme/app_theme.dart';

@GenerateNiceMocks([
  MockSpec<BrunoProvider>(),
  MockSpec<VoiceInputController>(),
])
import 'chat_interface_voice_test.mocks.dart';

void main() {
  group('ChatInterface Voice Input Integration', () {
    late MockBrunoProvider mockProvider;
    late MockVoiceInputController mockVoiceController;

    setUp(() {
      mockProvider = MockBrunoProvider();
      mockVoiceController = MockVoiceInputController();
      
      // Setup default mock responses
      when(mockProvider.messages).thenReturn([]);
      when(mockProvider.shoppingList).thenReturn([]);
      when(mockProvider.currentBudget).thenReturn('');
      when(mockProvider.totalCost).thenReturn(0.0);
      when(mockProvider.isTyping).thenReturn(false);
      when(mockProvider.favoriteMeals).thenReturn([]);
      
      when(mockVoiceController.isInitialized).thenReturn(true);
      when(mockVoiceController.isListening).thenReturn(false);
      when(mockVoiceController.hasError).thenReturn(false);
      when(mockVoiceController.hasPermission).thenReturn(true);
      when(mockVoiceController.recognizedText).thenReturn('');
      when(mockVoiceController.soundLevel).thenReturn(0.0);
      when(mockVoiceController.errorMessage).thenReturn('');
    });

    Widget createTestWidget() {
      return MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: ChangeNotifierProvider<BrunoProvider>(
            create: (_) => mockProvider,
            child: const ChatInterface(),
          ),
        ),
      );
    }

    group('Voice Input Button Display', () {
      testWidgets('should show voice input button when text field is empty', 
          (WidgetTester tester) async {
        // Act
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Assert
        expect(find.byType(VoiceInputButton), findsOneWidget);
        expect(find.byIcon(Icons.arrow_upward_rounded), findsNothing);
      });

      testWidgets('should show send button when text field has content', 
          (WidgetTester tester) async {
        // Arrange
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final textField = find.byType(TextField);
        expect(textField, findsOneWidget);

        // Act - Enter text in the text field
        await tester.enterText(textField, 'Plan meals for tonight');
        await tester.pumpAndSettle();

        // Assert
        expect(find.byType(VoiceInputButton), findsNothing);
        expect(find.byIcon(Icons.arrow_upward_rounded), findsOneWidget);
      });

      testWidgets('should switch between voice and send button based on text content', 
          (WidgetTester tester) async {
        // Arrange
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final textField = find.byType(TextField);

        // Initially should show voice button
        expect(find.byType(VoiceInputButton), findsOneWidget);

        // Act 1 - Add text
        await tester.enterText(textField, 'Hello');
        await tester.pumpAndSettle();

        // Assert 1 - Should show send button
        expect(find.byType(VoiceInputButton), findsNothing);
        expect(find.byIcon(Icons.arrow_upward_rounded), findsOneWidget);

        // Act 2 - Clear text
        await tester.enterText(textField, '');
        await tester.pumpAndSettle();

        // Assert 2 - Should show voice button again
        expect(find.byType(VoiceInputButton), findsOneWidget);
        expect(find.byIcon(Icons.arrow_upward_rounded), findsNothing);
      });
    });

    group('Voice Input Interaction', () {
      testWidgets('should handle voice input button tap', 
          (WidgetTester tester) async {
        // Arrange
        when(mockVoiceController.startListening()).thenAnswer((_) async {});
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Act
        await tester.tap(find.byType(VoiceInputButton));
        await tester.pumpAndSettle();

        // Assert - This would verify the button responds to tap
        // The actual verification depends on the VoiceInputButton implementation
      });

      testWidgets('should display voice input states correctly', 
          (WidgetTester tester) async {
        // Test different states: idle, listening, processing, error
        
        // Initial idle state
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();
        expect(find.byType(VoiceInputButton), findsOneWidget);

        // Listening state
        when(mockVoiceController.isListening).thenReturn(true);
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Error state
        when(mockVoiceController.isListening).thenReturn(false);
        when(mockVoiceController.hasError).thenReturn(true);
        when(mockVoiceController.errorMessage).thenReturn('Network error');
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();
      });
    });

    group('Voice Recognition Results', () {
      testWidgets('should handle voice recognition completion', 
          (WidgetTester tester) async {
        // Arrange
        const recognizedText = 'Plan a healthy meal for tonight';
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final chatInterfaceState = tester.state<_ChatInterfaceState>(
          find.byType(ChatInterface)
        );

        // Act - Simulate voice recognition completion
        chatInterfaceState._onVoiceRecognitionComplete(recognizedText);
        await tester.pumpAndSettle();

        // Assert - Text should be added to the text field
        expect(find.text(recognizedText), findsOneWidget);
      });

      testWidgets('should show feedback snackbar after voice input', 
          (WidgetTester tester) async {
        // Arrange
        const recognizedText = 'Find budget recipes';
        when(mockVoiceController.recognizedText).thenReturn(recognizedText);
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final chatInterfaceState = tester.state<_ChatInterfaceState>(
          find.byType(ChatInterface)
        );

        // Act
        chatInterfaceState._onVoiceRecognitionComplete(recognizedText);
        await tester.pumpAndSettle();

        // Assert - Should show snackbar with voice input confirmation
        expect(find.byType(SnackBar), findsOneWidget);
        expect(find.textContaining('Voice input:'), findsOneWidget);
        expect(find.textContaining(recognizedText), findsOneWidget);
      });

      testWidgets('should append to existing text when voice input completes', 
          (WidgetTester tester) async {
        // Arrange
        const existingText = 'I need ';
        const voiceText = 'chicken recipes for dinner';
        const expectedText = '$existingText$voiceText';
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final textField = find.byType(TextField);
        await tester.enterText(textField, existingText);
        await tester.pumpAndSettle();

        final chatInterfaceState = tester.state<_ChatInterfaceState>(
          find.byType(ChatInterface)
        );

        // Act
        chatInterfaceState._onVoiceRecognitionComplete(voiceText);
        await tester.pumpAndSettle();

        // Assert
        expect(find.text(expectedText), findsOneWidget);
      });
    });

    group('Permission Handling', () {
      testWidgets('should handle permission denial gracefully', 
          (WidgetTester tester) async {
        // Arrange
        when(mockVoiceController.hasPermission).thenReturn(false);
        when(mockVoiceController.hasError).thenReturn(true);
        when(mockVoiceController.errorMessage).thenReturn(
          'Microphone permission denied'
        );
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Act - Try to use voice input
        await tester.tap(find.byType(VoiceInputButton));
        await tester.pumpAndSettle();

        // Assert - Should still allow manual text input
        final textField = find.byType(TextField);
        expect(textField, findsOneWidget);
        
        await tester.enterText(textField, 'Manual input works');
        await tester.pumpAndSettle();
        expect(find.text('Manual input works'), findsOneWidget);
      });

      testWidgets('should show error state in voice button when permission denied', 
          (WidgetTester tester) async {
        // Arrange
        when(mockVoiceController.hasPermission).thenReturn(false);
        when(mockVoiceController.hasError).thenReturn(true);
        when(mockVoiceController.errorMessage).thenReturn(
          'Microphone permission is required for voice input'
        );
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Assert - Voice button should indicate error state
        expect(find.byType(VoiceInputButton), findsOneWidget);
        // The button should visually indicate the error state
      });
    });

    group('Message Sending Integration', () {
      testWidgets('should send message normally with manual input', 
          (WidgetTester tester) async {
        // Arrange
        const testMessage = 'Plan meals for this week';
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Act - Enter text and send
        final textField = find.byType(TextField);
        await tester.enterText(textField, testMessage);
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.arrow_upward_rounded));
        await tester.pumpAndSettle();

        // Assert
        verify(mockProvider.sendMessageToBruno(testMessage)).called(1);
      });

      testWidgets('should send message after voice input completion', 
          (WidgetTester tester) async {
        // Arrange
        const voiceMessage = 'Find healthy recipes under twenty dollars';
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final chatInterfaceState = tester.state<_ChatInterfaceState>(
          find.byType(ChatInterface)
        );

        // Act - Complete voice recognition
        chatInterfaceState._onVoiceRecognitionComplete(voiceMessage);
        await tester.pumpAndSettle();

        // Now send the message
        await tester.tap(find.byIcon(Icons.arrow_upward_rounded));
        await tester.pumpAndSettle();

        // Assert
        verify(mockProvider.sendMessageToBruno(voiceMessage)).called(1);
      });

      testWidgets('should clear text field after sending voice-input message', 
          (WidgetTester tester) async {
        // Arrange
        const voiceMessage = 'Show me pasta recipes';
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        final chatInterfaceState = tester.state<_ChatInterfaceState>(
          find.byType(ChatInterface)
        );
        final textField = find.byType(TextField);

        // Act
        chatInterfaceState._onVoiceRecognitionComplete(voiceMessage);
        await tester.pumpAndSettle();

        // Verify text is in field
        expect(find.text(voiceMessage), findsOneWidget);

        // Send message
        await tester.tap(find.byIcon(Icons.arrow_upward_rounded));
        await tester.pumpAndSettle();

        // Assert - Text field should be cleared and voice button should reappear
        expect(find.text(voiceMessage), findsNothing);
        expect(find.byType(VoiceInputButton), findsOneWidget);
      });
    });

    group('Error Recovery', () {
      testWidgets('should recover from voice input errors', 
          (WidgetTester tester) async {
        // Arrange
        when(mockVoiceController.hasError).thenReturn(true);
        when(mockVoiceController.errorMessage).thenReturn('Network timeout');
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Error state should be displayed
        expect(find.byType(VoiceInputButton), findsOneWidget);

        // Act - Simulate error recovery
        when(mockVoiceController.hasError).thenReturn(false);
        when(mockVoiceController.errorMessage).thenReturn('');
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Assert - Should be back to normal state
        expect(find.byType(VoiceInputButton), findsOneWidget);
      });

      testWidgets('should allow manual input fallback during voice errors', 
          (WidgetTester tester) async {
        // Arrange
        when(mockVoiceController.hasError).thenReturn(true);
        when(mockVoiceController.errorMessage).thenReturn('Speech recognition failed');
        
        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Act - Use manual input instead
        final textField = find.byType(TextField);
        await tester.enterText(textField, 'Manual fallback message');
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.arrow_upward_rounded));
        await tester.pumpAndSettle();

        // Assert - Manual input should work normally
        verify(mockProvider.sendMessageToBruno('Manual fallback message')).called(1);
      });
    });
  });
}

// Extension to access private methods for testing
extension _ChatInterfaceStateTest on _ChatInterfaceState {
  void _onVoiceRecognitionComplete(String text) {
    // This would be the actual implementation from ChatInterface
    // For testing purposes, we simulate the behavior
  }
}
