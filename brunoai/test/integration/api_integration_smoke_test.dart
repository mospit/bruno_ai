import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:brunoai/repositories/auth_repository.dart';
import 'package:brunoai/repositories/chat_repository.dart';
import 'package:brunoai/repositories/pantry_repository.dart';
import 'package:brunoai/models/pantry_item.dart';
import 'package:brunoai/models/chat_message.dart';
import 'package:brunoai/services/api_service.dart';

void main() {
  group('API Integration Smoke Tests', () {
    late AuthRepository authRepository;
    late ChatRepository chatRepository;
    late PantryRepository pantryRepository;

    setUpAll(() async {
      // Initialize Flutter testing environment
      TestWidgetsFlutterBinding.ensureInitialized();
      
      // Initialize sqflite_ffi for testing
      databaseFactory = databaseFactoryFfi;
      
      // Initialize repositories
      authRepository = AuthRepository();
      chatRepository = ChatRepository();
      pantryRepository = PantryRepository();
    });

    group('Authentication Integration Tests', () {
      test('should handle login request gracefully', () async {
        // Test with mock credentials - this should handle both success and failure gracefully
        final result = await authRepository.login(
          email: 'test@example.com',
          password: 'testpassword123',
        );

        expect(result, isA<AuthResult>());
        expect(result.isSuccess, isA<bool>());
        expect(result.message, isNotEmpty);
        
        // If successful, should have user data
        if (result.isSuccess) {
          expect(result.user, isNotNull);
          expect(result.user!.id, isNotEmpty);
          expect(result.user!.email, contains('@'));
        } else {
          expect(result.user, isNull);
        }
      });

      test('should handle signup request gracefully', () async {
        final result = await authRepository.signup(
          email: 'newuser@example.com',
          password: 'newpassword123',
          name: 'Test User',
        );

        expect(result, isA<AuthResult>());
        expect(result.isSuccess, isA<bool>());
        expect(result.message, isNotEmpty);
        
        if (result.isSuccess) {
          expect(result.user, isNotNull);
          expect(result.user!.name, equals('Test User'));
          expect(result.user!.email, equals('newuser@example.com'));
        }
      });

      test('should check authentication state', () async {
        final isAuthenticated = await authRepository.isAuthenticated();
        expect(isAuthenticated, isA<bool>());
      });
    });

    group('Chat Integration Tests', () {
      test('should send message and return expected response structure', () async {
        const testMessage = 'Hello Bruno, what can you help me with?';
        
        final result = await chatRepository.sendMessage(
          message: testMessage,
          userId: 'test_user_123',
          budgetLimit: 100.0,
          familySize: 4,
          dietaryRestrictions: ['vegetarian'],
        );

        expect(result, isA<ChatResult>());
        expect(result.isSuccess, isTrue);
        expect(result.userMessage, isNotNull);
        expect(result.botMessage, isNotNull);
        
        // Validate user message structure
        expect(result.userMessage!.text, equals(testMessage));
        expect(result.userMessage!.isFromUser, isTrue);
        expect(result.userMessage!.timestamp, isA<DateTime>());
        
        // Validate bot message structure
        expect(result.botMessage!.text, isNotEmpty);
        expect(result.botMessage!.isFromUser, isFalse);
        expect(result.botMessage!.timestamp, isA<DateTime>());
        expect(result.botMessage!.type, isA<MessageType>());
      });

      test('should retrieve chat history', () async {
        final history = await chatRepository.getChatHistory(limit: 50);
        
        expect(history, isA<List<ChatMessage>>());
        expect(history.length, lessThanOrEqualTo(50));
        
        for (final message in history) {
          expect(message.id, isNotEmpty);
          expect(message.text, isNotEmpty);
          expect(message.timestamp, isA<DateTime>());
          expect(message.isFromUser, isA<bool>());
        }
      });

      test('should handle offline message generation gracefully', () async {
        const offlineMessage = 'What meals can you suggest for this week?';
        
        final result = await chatRepository.sendMessage(
          message: offlineMessage,
        );

        expect(result, isA<ChatResult>());
        expect(result.isSuccess, isTrue);
        expect(result.userMessage, isNotNull);
        expect(result.botMessage, isNotNull);
        
        // Should work regardless of network status
        expect(result.botMessage!.text, isNotEmpty);
        
        if (result.isFromCache) {
          expect(result.botMessage!.text, contains('offline'));
          expect(result.botMessage!.metadata?['offline_mode'], isTrue);
        }
      });
    });

    group('Pantry Integration Tests', () {
      test('should retrieve pantry items list', () async {
        final items = await pantryRepository.getPantryItems();
        
        expect(items, isA<List<PantryItem>>());
        
        for (final item in items) {
          expect(item.id, isNotEmpty);
          expect(item.name, isNotEmpty);
          expect(item.quantity, greaterThanOrEqualTo(0));
          expect(item.unit, isNotEmpty);
          expect(item.expirationDate, isA<DateTime>());
          expect(item.location, isNotEmpty);
          expect(item.category, isNotEmpty);
          expect(item.dateAdded, isA<DateTime>());
        }
      });

      test('should add pantry item successfully', () async {
        final testItem = PantryItem(
          name: 'Test Apple',
          quantity: 5.0,
          unit: 'pieces',
          expirationDate: DateTime.now().add(const Duration(days: 7)),
          location: 'Refrigerator',
          category: 'Fruits',
          notes: 'Test item for integration test',
        );

        final result = await pantryRepository.addPantryItem(testItem);
        
        expect(result, isA<PantryResult<PantryItem>>());
        expect(result.isSuccess, isTrue);
        expect(result.data, isNotNull);
        expect(result.message, isNotEmpty);
        
        // Validate returned item structure
        expect(result.data!.name, equals(testItem.name));
        expect(result.data!.quantity, equals(testItem.quantity));
        expect(result.data!.category, equals(testItem.category));
      });

      test('should update pantry item quantity', () async {
        // First get an item to update
        final items = await pantryRepository.getPantryItems();
        if (items.isNotEmpty) {
          final itemToUpdate = items.first;
          final newQuantity = itemToUpdate.quantity + 1;
          
          final result = await pantryRepository.updateItemQuantity(
            itemToUpdate.id, 
            newQuantity,
          );
          
          expect(result, isA<PantryResult<PantryItem>>());
          expect(result.isSuccess, isTrue);
          expect(result.data!.quantity, equals(newQuantity));
        }
      });

      test('should get expiring items with proper filtering', () async {
        final expiringItems = await pantryRepository.getExpiringItems(daysAhead: 7);
        
        expect(expiringItems, isA<List<PantryItem>>());
        
        final now = DateTime.now();
        final cutoffDate = now.add(const Duration(days: 7));
        
        for (final item in expiringItems) {
          expect(
            item.expirationDate.isBefore(cutoffDate) || item.isExpiringSoon,
            isTrue,
            reason: 'Item ${item.name} should be expiring within 7 days',
          );
        }
      });
    });

    group('Data Structure Validation Tests', () {
      test('should validate ChatMessage JSON serialization', () {
        final message = ChatMessage(
          text: 'Test message',
          isFromUser: true,
          timestamp: DateTime.now(),
          type: MessageType.text,
          suggestions: ['suggestion1', 'suggestion2'],
          hasShoppingAction: false,
          metadata: {'test_key': 'test_value'},
        );

        final json = message.toJson();
        final reconstructed = ChatMessage.fromJson(json);

        expect(reconstructed.text, equals(message.text));
        expect(reconstructed.isFromUser, equals(message.isFromUser));
        expect(reconstructed.type, equals(message.type));
        expect(reconstructed.suggestions, equals(message.suggestions));
        expect(reconstructed.hasShoppingAction, equals(message.hasShoppingAction));
      });

      test('should validate PantryItem JSON serialization', () {
        final item = PantryItem(
          name: 'Test Item',
          quantity: 2.5,
          unit: 'kg',
          expirationDate: DateTime.now().add(const Duration(days: 5)),
          location: 'Pantry',
          category: 'Grains',
          brand: 'Test Brand',
          notes: 'Test notes',
        );

        final json = item.toJson();
        final reconstructed = PantryItem.fromJson(json);

        expect(reconstructed.name, equals(item.name));
        expect(reconstructed.quantity, equals(item.quantity));
        expect(reconstructed.unit, equals(item.unit));
        expect(reconstructed.location, equals(item.location));
        expect(reconstructed.category, equals(item.category));
        expect(reconstructed.brand, equals(item.brand));
        expect(reconstructed.notes, equals(item.notes));
      });

      test('should validate API response wrapper structure', () {
        final successResponse = ApiResponse.success('test data');
        expect(successResponse.isSuccess, isTrue);
        expect(successResponse.data, equals('test data'));
        expect(successResponse.error, isNull);
        expect(successResponse.hasError, isFalse);

        final errorResponse = ApiResponse.error('test error');
        expect(errorResponse.isSuccess, isFalse);
        expect(errorResponse.data, isNull);
        expect(errorResponse.error, equals('test error'));
        expect(errorResponse.hasError, isTrue);
      });
    });

    group('Offline Functionality Tests', () {
      test('should handle offline chat gracefully', () async {
        final result = await chatRepository.sendMessage(
          message: 'Test offline message',
        );

        expect(result, isA<ChatResult>());
        expect(result.isSuccess, isTrue);
        
        // Should work regardless of network status
        expect(result.userMessage, isNotNull);
        expect(result.botMessage, isNotNull);
      });

      test('should handle offline pantry operations', () async {
        final testItem = PantryItem(
          name: 'Offline Test Item',
          quantity: 1.0,
          unit: 'piece',
          expirationDate: DateTime.now().add(const Duration(days: 3)),
          location: 'Test Location',
          category: 'Test',
        );

        final result = await pantryRepository.addPantryItem(testItem);
        
        expect(result, isA<PantryResult<PantryItem>>());
        expect(result.isSuccess, isTrue);
        
        // Should indicate if operation was cached/offline
        if (result.isFromCache) {
          expect(result.message, contains('offline'));
        }
      });
    });
  });
}
