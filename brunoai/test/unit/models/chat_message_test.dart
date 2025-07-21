import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/models/chat_message.dart';

void main() {
  group('ChatMessage Model', () {
    test('should create ChatMessage with required parameters', () {
      final timestamp = DateTime.now();
      final message = ChatMessage(
        text: 'Hello, Bruno!',
        isFromUser: true,
        timestamp: timestamp,
      );

      expect(message.text, equals('Hello, Bruno!'));
      expect(message.isFromUser, isTrue);
      expect(message.timestamp, equals(timestamp));
      expect(message.suggestions, isEmpty);
      expect(message.hasShoppingAction, isFalse);
      expect(message.type, equals(MessageType.text));
      expect(message.metadata, isNull);
    });

    test('should create ChatMessage with optional parameters', () {
      final timestamp = DateTime.now();
      final metadata = {'test': 'data'};
      
      final message = ChatMessage(
        text: 'Test message',
        isFromUser: false,
        timestamp: timestamp,
        suggestions: ['suggestion1', 'suggestion2'],
        hasShoppingAction: true,
        type: MessageType.mealPlan,
        metadata: metadata,
      );

      expect(message.suggestions, hasLength(2));
      expect(message.suggestions, contains('suggestion1'));
      expect(message.hasShoppingAction, isTrue);
      expect(message.type, equals(MessageType.mealPlan));
      expect(message.metadata, equals(metadata));
    });

    test('should create ChatMessage from JSON', () {
      final json = {
        'id': 'test-id',
        'text': 'Test from JSON',
        'isFromUser': false,
        'timestamp': '2025-01-21T12:00:00.000Z',
        'suggestions': ['test'],
        'hasShoppingAction': true,
        'type': 'mealPlan',
        'metadata': {'key': 'value'}
      };

      final message = ChatMessage.fromJson(json);

      expect(message.id, equals('test-id'));
      expect(message.text, equals('Test from JSON'));
      expect(message.isFromUser, isFalse);
      expect(message.suggestions, contains('test'));
      expect(message.hasShoppingAction, isTrue);
      expect(message.type, equals(MessageType.mealPlan));
      expect(message.metadata?['key'], equals('value'));
    });

    test('should convert ChatMessage to JSON', () {
      final timestamp = DateTime.parse('2025-01-21T12:00:00.000Z');
      final message = ChatMessage(
        text: 'Test to JSON',
        isFromUser: true,
        timestamp: timestamp,
        suggestions: ['test'],
        hasShoppingAction: false,
        type: MessageType.text,
      );

      final json = message.toJson();

      expect(json['text'], equals('Test to JSON'));
      expect(json['isFromUser'], isTrue);
      expect(json['timestamp'], equals('2025-01-21T12:00:00.000Z'));
      expect(json['suggestions'], contains('test'));
      expect(json['hasShoppingAction'], isFalse);
      expect(json['type'], equals('text'));
    });

    test('should create copy with updated values', () {
      final original = ChatMessage(
        text: 'Original',
        isFromUser: true,
        timestamp: DateTime.now(),
      );

      final updated = original.copyWith(
        text: 'Updated',
        hasShoppingAction: true,
      );

      expect(updated.text, equals('Updated'));
      expect(updated.isFromUser, equals(original.isFromUser));
      expect(updated.hasShoppingAction, isTrue);
    });

    test('should have correct display time', () {
      final now = DateTime.now();
      
      // Test "Just now"
      final recentMessage = ChatMessage(
        text: 'Recent',
        isFromUser: true,
        timestamp: now.subtract(const Duration(seconds: 30)),
      );
      expect(recentMessage.displayTime, equals('Just now'));

      // Test minutes ago
      final minutesMessage = ChatMessage(
        text: 'Minutes',
        isFromUser: true,
        timestamp: now.subtract(const Duration(minutes: 5)),
      );
      expect(minutesMessage.displayTime, contains('m ago'));

      // Test hours ago
      final hoursMessage = ChatMessage(
        text: 'Hours',
        isFromUser: true,
        timestamp: now.subtract(const Duration(hours: 2)),
      );
      expect(hoursMessage.displayTime, contains('h ago'));

      // Test days ago
      final daysMessage = ChatMessage(
        text: 'Days',
        isFromUser: true,
        timestamp: now.subtract(const Duration(days: 3)),
      );
      expect(daysMessage.displayTime, contains('d ago'));
    });

    test('should check if message is from Bruno', () {
      final userMessage = ChatMessage(
        text: 'From user',
        isFromUser: true,
        timestamp: DateTime.now(),
      );

      final brunoMessage = ChatMessage(
        text: 'From Bruno',
        isFromUser: false,
        timestamp: DateTime.now(),
      );

      expect(userMessage.isBrunoMessage, isFalse);
      expect(userMessage.isUserMessage, isTrue);
      expect(brunoMessage.isBrunoMessage, isTrue);
      expect(brunoMessage.isUserMessage, isFalse);
    });

    test('should check message types correctly', () {
      final welcomeMessage = ChatMessage(
        text: 'Welcome',
        isFromUser: false,
        timestamp: DateTime.now(),
        type: MessageType.welcome,
      );

      final mealPlanMessage = ChatMessage(
        text: 'Meal plan',
        isFromUser: false,
        timestamp: DateTime.now(),
        type: MessageType.mealPlan,
      );

      expect(welcomeMessage.isWelcomeMessage, isTrue);
      expect(welcomeMessage.isMealPlanMessage, isFalse);
      expect(mealPlanMessage.isMealPlanMessage, isTrue);
      expect(mealPlanMessage.isWelcomeMessage, isFalse);
    });

    test('should handle metadata correctly', () {
      final messageWithMetadata = ChatMessage(
        text: 'With metadata',
        isFromUser: false,
        timestamp: DateTime.now(),
        metadata: {'count': 5, 'name': 'test'},
      );

      final messageWithoutMetadata = ChatMessage(
        text: 'Without metadata',
        isFromUser: false,
        timestamp: DateTime.now(),
      );

      expect(messageWithMetadata.hasMetadata, isTrue);
      expect(messageWithMetadata.getMetadata<int>('count'), equals(5));
      expect(messageWithMetadata.getMetadata<String>('name'), equals('test'));
      expect(messageWithMetadata.getMetadata<String>('nonexistent'), isNull);
      
      expect(messageWithoutMetadata.hasMetadata, isFalse);
      expect(messageWithoutMetadata.getMetadata<String>('any'), isNull);
    });

    test('should maintain equality based on id', () {
      final message1 = ChatMessage(
        id: 'same-id',
        text: 'Message 1',
        isFromUser: true,
        timestamp: DateTime.now(),
      );

      final message2 = ChatMessage(
        id: 'same-id',
        text: 'Message 2',
        isFromUser: false,
        timestamp: DateTime.now(),
      );

      final message3 = ChatMessage(
        id: 'different-id',
        text: 'Message 1',
        isFromUser: true,
        timestamp: DateTime.now(),
      );

      expect(message1, equals(message2));
      expect(message1.hashCode, equals(message2.hashCode));
      expect(message1, isNot(equals(message3)));
    });
  });
}
