import 'package:uuid/uuid.dart';

class ChatMessage {
  final String id;
  final String text;
  final String message; // For backward compatibility
  final bool isFromUser;
  final bool isUser; // For backward compatibility
  final DateTime timestamp;
  final List<String> suggestions;
  final bool hasShoppingAction;
  final MessageType type;
  final Map<String, dynamic>? metadata;

  ChatMessage({
    String? id,
    required this.text,
    required this.isFromUser,
    required this.timestamp,
    this.suggestions = const [],
    this.hasShoppingAction = false,
    this.type = MessageType.text,
    this.metadata,
  })  : id = id ?? const Uuid().v4(),
        message = text,
        isUser = isFromUser;

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String? ?? const Uuid().v4(),
      text: json['text'] as String? ?? json['message'] as String? ?? '',
      isFromUser: json['isFromUser'] as bool? ?? json['isUser'] as bool? ?? false,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      suggestions: (json['suggestions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      hasShoppingAction: json['hasShoppingAction'] as bool? ?? false,
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.text,
      ),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'message': message,
      'isFromUser': isFromUser,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'suggestions': suggestions,
      'hasShoppingAction': hasShoppingAction,
      'type': type.name,
      'metadata': metadata,
    };
  }

  ChatMessage copyWith({
    String? id,
    String? text,
    bool? isFromUser,
    DateTime? timestamp,
    List<String>? suggestions,
    bool? hasShoppingAction,
    MessageType? type,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      text: text ?? this.text,
      isFromUser: isFromUser ?? this.isFromUser,
      timestamp: timestamp ?? this.timestamp,
      suggestions: suggestions ?? this.suggestions,
      hasShoppingAction: hasShoppingAction ?? this.hasShoppingAction,
      type: type ?? this.type,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'ChatMessage(id: $id, text: $text, isFromUser: $isFromUser, timestamp: $timestamp)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ChatMessage && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

enum MessageType {
  text,
  mealPlan,
  shoppingList,
  suggestion,
  error,
  system,
  welcome,
  typing,
}

// Extension for Bruno-specific message helpers
extension BrunoMessageExtensions on ChatMessage {
  bool get isBrunoMessage => !isFromUser;
  bool get isUserMessage => isFromUser;
  
  bool get isWelcomeMessage => type == MessageType.welcome;
  bool get isMealPlanMessage => type == MessageType.mealPlan;
  bool get isShoppingMessage => type == MessageType.shoppingList;
  bool get isErrorMessage => type == MessageType.error;
  
  String get displayTime {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
  
  bool get hasMetadata => metadata != null && metadata!.isNotEmpty;
  
  T? getMetadata<T>(String key) {
    return metadata?[key] as T?;
  }
}
