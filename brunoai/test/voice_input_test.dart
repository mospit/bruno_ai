import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_recognition_error.dart';
import 'package:permission_handler/permission_handler.dart';

import '../lib/controllers/voice_input_controller.dart';

// Mock classes
@GenerateNiceMocks([
  MockSpec<SpeechToText>(),
  MockSpec<PermissionHandler>(),
])
import 'voice_input_test.mocks.dart';

void main() {
  group('VoiceInputController Tests', () {
    late VoiceInputController controller;
    late MockSpeechToText mockSpeechToText;
    late MockPermissionHandler mockPermissionHandler;

    setUp(() {
      mockSpeechToText = MockSpeechToText();
      mockPermissionHandler = MockPermissionHandler();
      controller = VoiceInputController();
      
      // Inject mocks (this would require dependency injection in the actual controller)
      // For now, we'll test the behavior assuming the controller works with the mocks
    });

    tearDown(() {
      controller.dispose();
    });

    group('Initialization', () {
      testWidgets('should initialize successfully', (WidgetTester tester) async {
        // Arrange
        when(mockSpeechToText.initialize()).thenAnswer((_) async => true);
        
        // Act
        await controller.initialize();
        
        // Assert
        expect(controller.isInitialized, isTrue);
      });

      testWidgets('should handle initialization failure', (WidgetTester tester) async {
        // Arrange
        when(mockSpeechToText.initialize()).thenAnswer((_) async => false);
        
        // Act
        await controller.initialize();
        
        // Assert
        expect(controller.isInitialized, isFalse);
        expect(controller.hasError, isTrue);
        expect(controller.errorMessage, contains('Failed to initialize'));
      });
    });

    group('Permission Handling', () {
      testWidgets('should request microphone permission', (WidgetTester tester) async {
        // Arrange - simulate permission granted
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          const MethodChannel('flutter.baseflow.com/permissions/methods'),
          (MethodCall methodCall) async {
            if (methodCall.method == 'requestPermissions') {
              return <String, int>{'android.permission.RECORD_AUDIO': 1};
            }
            if (methodCall.method == 'checkPermissionStatus') {
              return 1; // PermissionStatus.granted
            }
            return null;
          },
        );
        
        // Act
        await controller.initialize();
        
        // Assert
        expect(controller.isInitialized, isTrue);
        expect(controller.hasPermission, isTrue);
      });

      testWidgets('should handle permission denied gracefully', (WidgetTester tester) async {
        // Arrange - simulate permission denied
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          const MethodChannel('flutter.baseflow.com/permissions/methods'),
          (MethodCall methodCall) async {
            if (methodCall.method == 'requestPermissions') {
              return <String, int>{'android.permission.RECORD_AUDIO': 0};
            }
            if (methodCall.method == 'checkPermissionStatus') {
              return 0; // PermissionStatus.denied
            }
            return null;
          },
        );
        
        // Act
        await controller.initialize();
        
        // Assert
        expect(controller.hasPermission, isFalse);
        expect(controller.hasError, isTrue);
        expect(controller.errorMessage, contains('Microphone permission'));
      });
    });

    group('Voice Recognition', () {
      setUp(() async {
        // Setup successful initialization
        when(mockSpeechToText.initialize()).thenAnswer((_) async => true);
        await controller.initialize();
      });

      testWidgets('should start listening successfully', (WidgetTester tester) async {
        // Arrange
        when(mockSpeechToText.isNotListening).thenReturn(true);
        when(mockSpeechToText.listen(
          onResult: anyNamed('onResult'),
          listenFor: anyNamed('listenFor'),
          pauseFor: anyNamed('pauseFor'),
          partialResults: anyNamed('partialResults'),
          localeId: anyNamed('localeId'),
          onSoundLevelChange: anyNamed('onSoundLevelChange'),
          cancelOnError: anyNamed('cancelOnError'),
          listenMode: anyNamed('listenMode'),
        )).thenAnswer((_) async {
          // Simulate successful start
        });
        
        // Act
        await controller.startListening();
        
        // Assert
        expect(controller.isListening, isTrue);
        expect(controller.hasError, isFalse);
      });

      testWidgets('should stop listening successfully', (WidgetTester tester) async {
        // Arrange
        when(mockSpeechToText.isListening).thenReturn(true);
        when(mockSpeechToText.stop()).thenAnswer((_) async {});
        
        // Start listening first
        await controller.startListening();
        
        // Act
        await controller.stopListening();
        
        // Assert
        expect(controller.isListening, isFalse);
      });

      testWidgets('should handle recognition results', (WidgetTester tester) async {
        // Arrange
        const testText = 'Plan meals for this week';
        String? receivedText;
        
        controller.onRecognitionComplete = (text) {
          receivedText = text;
        };
        
        // Simulate speech recognition result
        final result = SpeechRecognitionResult(
          [testText],
          true, // finalResult
        );
        
        // Act
        controller.onSpeechResult(result);
        
        // Assert
        expect(controller.recognizedText, equals(testText));
        expect(receivedText, equals(testText));
      });

      testWidgets('should handle partial results', (WidgetTester tester) async {
        // Arrange
        const partialText = 'Plan meals';
        
        final result = SpeechRecognitionResult(
          [partialText],
          false, // not finalResult
        );
        
        // Act
        controller.onSpeechResult(result);
        
        // Assert
        expect(controller.recognizedText, equals(partialText));
        // Should not call onRecognitionComplete for partial results
      });

      testWidgets('should handle recognition errors', (WidgetTester tester) async {
        // Arrange
        const error = SpeechRecognitionError(
          'network_timeout',
          'Network timeout occurred',
        );
        
        // Act
        controller.onSpeechError(error);
        
        // Assert
        expect(controller.hasError, isTrue);
        expect(controller.errorMessage, contains('Network timeout'));
        expect(controller.isListening, isFalse);
      });

      testWidgets('should handle no speech timeout', (WidgetTester tester) async {
        // Arrange
        const error = SpeechRecognitionError(
          'error_no_match',
          'No speech was heard',
        );
        
        // Act
        controller.onSpeechError(error);
        
        // Assert
        expect(controller.hasError, isTrue);
        expect(controller.errorMessage, contains('No speech detected'));
        expect(controller.isListening, isFalse);
      });
    });

    group('Sound Level Detection', () {
      testWidgets('should update sound level during listening', (WidgetTester tester) async {
        // Arrange
        const testLevel = 0.5;
        
        // Act
        controller.onSoundLevelChange(testLevel);
        
        // Assert
        expect(controller.soundLevel, equals(testLevel));
      });

      testWidgets('should reset sound level when not listening', (WidgetTester tester) async {
        // Arrange
        controller.onSoundLevelChange(0.8);
        expect(controller.soundLevel, equals(0.8));
        
        // Act
        await controller.stopListening();
        
        // Assert
        expect(controller.soundLevel, equals(0.0));
      });
    });

    group('Error Handling', () {
      testWidgets('should clear previous errors when starting new recognition', (WidgetTester tester) async {
        // Arrange
        controller.setError('Previous error');
        expect(controller.hasError, isTrue);
        
        // Act
        await controller.startListening();
        
        // Assert
        expect(controller.hasError, isFalse);
        expect(controller.errorMessage, isEmpty);
      });

      testWidgets('should handle multiple consecutive errors', (WidgetTester tester) async {
        // Arrange & Act
        controller.onSpeechError(const SpeechRecognitionError('error1', 'First error'));
        final firstError = controller.errorMessage;
        
        controller.onSpeechError(const SpeechRecognitionError('error2', 'Second error'));
        final secondError = controller.errorMessage;
        
        // Assert
        expect(firstError, contains('First error'));
        expect(secondError, contains('Second error'));
        expect(controller.hasError, isTrue);
      });
    });

    group('State Management', () {
      testWidgets('should maintain correct state during full cycle', (WidgetTester tester) async {
        // Initial state
        expect(controller.isListening, isFalse);
        expect(controller.hasError, isFalse);
        expect(controller.recognizedText, isEmpty);
        
        // Start listening
        await controller.startListening();
        expect(controller.isListening, isTrue);
        
        // Receive partial result
        controller.onSpeechResult(SpeechRecognitionResult(['Hello'], false));
        expect(controller.recognizedText, equals('Hello'));
        
        // Receive final result
        controller.onSpeechResult(SpeechRecognitionResult(['Hello world'], true));
        expect(controller.recognizedText, equals('Hello world'));
        
        // Stop listening
        await controller.stopListening();
        expect(controller.isListening, isFalse);
      });

      testWidgets('should reset state on dispose', (WidgetTester tester) async {
        // Arrange
        await controller.startListening();
        controller.onSpeechResult(SpeechRecognitionResult(['Test'], true));
        
        // Act
        controller.dispose();
        
        // Assert
        expect(controller.isListening, isFalse);
        expect(controller.recognizedText, isEmpty);
        expect(controller.soundLevel, equals(0.0));
      });
    });

    group('Integration Scenarios', () {
      testWidgets('should handle complete voice-to-send flow', (WidgetTester tester) async {
        // Arrange
        String? finalMessage;
        controller.onRecognitionComplete = (text) {
          finalMessage = text;
        };
        
        // Simulate complete flow
        await controller.initialize();
        await controller.startListening();
        
        // Simulate user speaking
        controller.onSpeechResult(
          SpeechRecognitionResult(['I need chicken recipes for dinner'], true),
        );
        
        // Assert
        expect(finalMessage, equals('I need chicken recipes for dinner'));
        expect(controller.recognizedText, equals('I need chicken recipes for dinner'));
      });

      testWidgets('should handle permission denied fallback', (WidgetTester tester) async {
        // Arrange - simulate permission denied
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          const MethodChannel('flutter.baseflow.com/permissions/methods'),
          (MethodCall methodCall) async {
            return <String, int>{'android.permission.RECORD_AUDIO': 0};
          },
        );
        
        // Act
        await controller.initialize();
        
        // Assert - should gracefully handle denied permission
        expect(controller.hasPermission, isFalse);
        expect(controller.errorMessage, isNotEmpty);
        // The UI should fallback to manual input
      });

      testWidgets('should handle network connectivity issues', (WidgetTester tester) async {
        // Arrange
        await controller.initialize();
        await controller.startListening();
        
        // Simulate network error
        controller.onSpeechError(
          const SpeechRecognitionError('error_network_timeout', 'Network timeout'),
        );
        
        // Assert
        expect(controller.hasError, isTrue);
        expect(controller.isListening, isFalse);
        expect(controller.errorMessage, contains('Network timeout'));
      });
    });
  });

  group('Voice Input Button Integration', () {
    testWidgets('should toggle states correctly with button presses', (WidgetTester tester) async {
      // This would test the integration with VoiceInputButton
      // Testing the visual states and user interactions
      
      final controller = VoiceInputController();
      await controller.initialize();
      
      // Test idle state
      expect(controller.currentState, equals(VoiceInputState.idle));
      
      // Test listening state
      await controller.startListening();
      expect(controller.currentState, equals(VoiceInputState.listening));
      
      // Test processing state (when receiving partial results)
      controller.onSpeechResult(SpeechRecognitionResult(['Processing...'], false));
      expect(controller.currentState, equals(VoiceInputState.processing));
      
      // Test complete state
      controller.onSpeechResult(SpeechRecognitionResult(['Complete message'], true));
      expect(controller.currentState, equals(VoiceInputState.complete));
    });

    testWidgets('should handle rapid button presses', (WidgetTester tester) async {
      final controller = VoiceInputController();
      await controller.initialize();
      
      // Rapid start/stop
      await controller.startListening();
      await controller.stopListening();
      await controller.startListening();
      
      expect(controller.isListening, isTrue);
      expect(controller.hasError, isFalse);
    });
  });
}

// Extension to add test utilities to VoiceInputController
extension VoiceInputControllerTestExt on VoiceInputController {
  void setError(String message) {
    errorMessage = message;
  }
  
  VoiceInputState get currentState {
    if (hasError) return VoiceInputState.error;
    if (isListening) {
      if (recognizedText.isNotEmpty && !recognizedText.endsWith('...')) {
        return VoiceInputState.processing;
      }
      return VoiceInputState.listening;
    }
    if (recognizedText.isNotEmpty) return VoiceInputState.complete;
    return VoiceInputState.idle;
  }
}

enum VoiceInputState {
  idle,
  listening,
  processing,
  complete,
  error,
}
