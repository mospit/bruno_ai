import 'package:uuid/uuid.dart';

class PantryItem {
  final String id;
  final String name;
  final double quantity;
  final String unit;
  final DateTime expirationDate;
  final String location;
  final String category;
  final String? brand;
  final String? imageUrl;
  final String notes;
  final DateTime dateAdded;
  final DateTime? dateOpened;
  final double? originalQuantity;
  final bool isOpened;
  final bool isExpired;

  PantryItem({
    String? id,
    required this.name,
    required this.quantity,
    this.unit = 'item',
    required this.expirationDate,
    required this.location,
    this.category = 'Other',
    this.brand,
    this.imageUrl,
    this.notes = '',
    DateTime? dateAdded,
    this.dateOpened,
    this.originalQuantity,
    this.isOpened = false,
  })  : id = id ?? const Uuid().v4(),
        dateAdded = dateAdded ?? DateTime.now(),
        isExpired = expirationDate.isBefore(DateTime.now());

  factory PantryItem.fromJson(Map<String, dynamic> json) {
    return PantryItem(
      id: json['id'] as String? ?? const Uuid().v4(),
      name: json['name'] as String? ?? '',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? 'item',
      expirationDate: json['expirationDate'] != null
          ? DateTime.parse(json['expirationDate'] as String)
          : DateTime.now().add(const Duration(days: 7)),
      location: json['location'] as String? ?? '',
      category: json['category'] as String? ?? 'Other',
      brand: json['brand'] as String?,
      imageUrl: json['imageUrl'] as String?,
      notes: json['notes'] as String? ?? '',
      dateAdded: json['dateAdded'] != null
          ? DateTime.parse(json['dateAdded'] as String)
          : DateTime.now(),
      dateOpened: json['dateOpened'] != null
          ? DateTime.parse(json['dateOpened'] as String)
          : null,
      originalQuantity: (json['originalQuantity'] as num?)?.toDouble(),
      isOpened: json['isOpened'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'quantity': quantity,
      'unit': unit,
      'expirationDate': expirationDate.toIso8601String(),
      'location': location,
      'category': category,
      'brand': brand,
      'imageUrl': imageUrl,
      'notes': notes,
      'dateAdded': dateAdded.toIso8601String(),
      'dateOpened': dateOpened?.toIso8601String(),
      'originalQuantity': originalQuantity,
      'isOpened': isOpened,
    };
  }

  PantryItem copyWith({
    String? id,
    String? name,
    double? quantity,
    String? unit,
    DateTime? expirationDate,
    String? location,
    String? category,
    String? brand,
    String? imageUrl,
    String? notes,
    DateTime? dateAdded,
    DateTime? dateOpened,
    double? originalQuantity,
    bool? isOpened,
  }) {
    return PantryItem(
      id: id ?? this.id,
      name: name ?? this.name,
      quantity: quantity ?? this.quantity,
      unit: unit ?? this.unit,
      expirationDate: expirationDate ?? this.expirationDate,
      location: location ?? this.location,
      category: category ?? this.category,
      brand: brand ?? this.brand,
      imageUrl: imageUrl ?? this.imageUrl,
      notes: notes ?? this.notes,
      dateAdded: dateAdded ?? this.dateAdded,
      dateOpened: dateOpened ?? this.dateOpened,
      originalQuantity: originalQuantity ?? this.originalQuantity,
      isOpened: isOpened ?? this.isOpened,
    );
  }

  // Computed properties
  int get daysUntilExpiration => expirationDate.difference(DateTime.now()).inDays;
  
  bool get isExpiringSoon => daysUntilExpiration <= 3 && daysUntilExpiration >= 0;
  
  bool get isLowStock => quantity <= (originalQuantity ?? quantity) * 0.2;
  
  String get displayName {
    if (brand != null && brand!.isNotEmpty) {
      return '$brand $name';
    }
    return name;
  }
  
  String get displayQuantity {
    if (quantity == quantity.toInt()) {
      return '${quantity.toInt()} $unit';
    }
    return '${quantity.toStringAsFixed(1)} $unit';
  }
  
  String get expirationStatus {
    if (isExpired) return 'Expired';
    if (isExpiringSoon) return 'Expires Soon';
    if (daysUntilExpiration <= 7) return 'Use This Week';
    return 'Fresh';
  }
  
  String get locationDisplay {
    return location.isEmpty ? 'Unknown Location' : location;
  }

  @override
  String toString() {
    return 'PantryItem(id: $id, name: $name, quantity: $quantity, location: $location, expires: $expirationDate)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is PantryItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Pantry item categories with icons
enum PantryCategory {
  meat('Meat', '🥩'),
  seafood('Seafood', '🐟'),
  dairy('Dairy', '🥛'),
  produce('Produce', '🥬'),
  vegetables('Vegetables', '🥕'),
  fruits('Fruits', '🍎'),
  grains('Grains', '🌾'),
  pantryStaples('Pantry Staples', '🏪'),
  beverages('Beverages', '🥤'),
  snacks('Snacks', '🍿'),
  frozen('Frozen', '🧊'),
  bakery('Bakery', '🍞'),
  spices('Spices', '🌶️'),
  condiments('Condiments', '🧂'),
  canned('Canned Goods', '🥫'),
  other('Other', '📦');

  const PantryCategory(this.displayName, this.emoji);

  final String displayName;
  final String emoji;

  static PantryCategory fromString(String category) {
    return PantryCategory.values.firstWhere(
      (c) => c.displayName.toLowerCase() == category.toLowerCase(),
      orElse: () => PantryCategory.other,
    );
  }
}

// Extension for pantry item helpers
extension PantryItemExtensions on PantryItem {
  PantryCategory get categoryEnum => PantryCategory.fromString(category);
  
  String get categoryEmoji => categoryEnum.emoji;
  
  bool get needsAttention => isExpired || isExpiringSoon || isLowStock;
  
  Map<String, dynamic> get analyticsData => {
    'item_id': id,
    'item_name': name,
    'category': category,
    'location': location,
    'quantity': quantity,
    'is_expired': isExpired,
    'is_expiring_soon': isExpiringSoon,
    'is_low_stock': isLowStock,
  };
}


