import 'package:uuid/uuid.dart';

class ShoppingItem {
  final String id;
  final String name;
  final double price;
  final int quantity;
  final String category;
  final String unit;
  final String notes;
  final String? imageUrl;
  final String? brandName;
  final bool isOnSale;
  final double? _originalPrice;
  final String? store;
  final DateTime? dateAdded;

  ShoppingItem({
    String? id,
    required this.name,
    required this.price,
    required this.quantity,
    this.category = 'General',
    this.unit = 'item',
    this.notes = '',
    this.imageUrl,
    this.brandName,
    bool? isOnSale,
    double? originalPrice,
    this.store,
    DateTime? dateAdded,
  })  : assert(name.isNotEmpty, 'Name cannot be empty'),
        assert(price >= 0, 'Price cannot be negative'),
        assert(quantity > 0, 'Quantity must be positive'),
        id = id ?? const Uuid().v4(),
        dateAdded = dateAdded ?? DateTime.now(),
        _originalPrice = originalPrice,
        isOnSale = isOnSale ?? (originalPrice != null && originalPrice > price);

  factory ShoppingItem.fromJson(Map<String, dynamic> json) {
    return ShoppingItem(
      id: json['id'] as String? ?? json['product_id'] as String? ?? const Uuid().v4(),
      name: json['name'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      quantity: json['quantity'] as int? ?? 1,
      category: json['category'] as String? ?? json['subcategory'] as String? ?? 'Other',
      unit: json['unit'] as String? ?? 'item',
      notes: json['notes'] as String? ?? json['description'] as String? ?? '',
      imageUrl: json['imageUrl'] as String? ?? json['image_url'] as String?,
      brandName: json['brandName'] as String? ?? json['brand'] as String?,
      isOnSale: json['isOnSale'] as bool? ?? (json['sale_price'] != null),
      originalPrice: (json['originalPrice'] as num?)?.toDouble(),
      store: json['store'] as String? ?? json['store_name'] as String?,
      dateAdded: json['dateAdded'] != null
          ? DateTime.parse(json['dateAdded'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'price': price,
      'quantity': quantity,
      'category': category,
      'unit': unit,
      'notes': notes,
      'imageUrl': imageUrl,
      'brandName': brandName,
      'isOnSale': isOnSale,
      'originalPrice': _originalPrice ?? price,
      'totalPrice': totalPrice,
      'store': store,
      'dateAdded': dateAdded?.toIso8601String(),
    };
  }

  ShoppingItem copyWith({
    String? id,
    String? name,
    double? price,
    int? quantity,
    String? category,
    String? unit,
    String? notes,
    String? imageUrl,
    String? brandName,
    bool? isOnSale,
    double? originalPrice,
    String? store,
    DateTime? dateAdded,
  }) {
    return ShoppingItem(
      id: id ?? this.id,
      name: name ?? this.name,
      price: price ?? this.price,
      quantity: quantity ?? this.quantity,
      category: category ?? this.category,
      unit: unit ?? this.unit,
      notes: notes ?? this.notes,
      imageUrl: imageUrl ?? this.imageUrl,
      brandName: brandName ?? this.brandName,
      isOnSale: isOnSale ?? this.isOnSale,
      originalPrice: originalPrice ?? this._originalPrice,
      store: store ?? this.store,
      dateAdded: dateAdded ?? this.dateAdded,
    );
  }

  /// Get original price, defaults to current price if not set
  double get originalPrice => _originalPrice ?? price;

  double get totalPrice => price * quantity;

  double get savings {
    if (_originalPrice != null && _originalPrice! > price) {
      return (_originalPrice! - price) * quantity;
    }
    return 0.0;
  }

  double get savingsPercentage {
    if (_originalPrice != null && _originalPrice! > 0) {
      return ((_originalPrice! - price) / _originalPrice!) * 100;
    }
    return 0.0;
  }

  String get displayPrice {
    if (_originalPrice != null && _originalPrice! > price) {
      return '\$${price.toStringAsFixed(2)} (was \$${_originalPrice!.toStringAsFixed(2)})';
    }
    return '\$${price.toStringAsFixed(2)}';
  }

  String get displayTotalPrice {
    return '\$${totalPrice.toStringAsFixed(2)}';
  }

  String get displayName {
    if (brandName != null && brandName!.isNotEmpty) {
      return '$brandName $name';
    }
    return name;
  }

  String get displayQuantity {
    if (quantity == 1 && unit == 'item') {
      return '1';
    }
    return '$quantity ${quantity == 1 ? unit : _pluralizeUnit(unit)}';
  }

  /// Alias for displayQuantity for test compatibility
  String get unitDisplay => displayQuantity;
  
  /// Computed discount amount
  double get discountAmount {
    if (_originalPrice != null && _originalPrice! > price) {
      return _originalPrice! - price;
    }
    return 0.0;
  }
  
  /// Computed discount percentage
  double get discountPercentage {
    if (_originalPrice != null && _originalPrice! > 0) {
      return ((_originalPrice! - price) / _originalPrice!) * 100;
    }
    return 0.0;
  }

  String _pluralizeUnit(String unit) {
    // Simple pluralization - could be made more sophisticated
    switch (unit.toLowerCase()) {
      case 'lb':
      case 'lbs':
        return 'lbs';
      case 'oz':
        return 'oz';
      case 'bunch':
        return 'bunches';
      case 'bag':
        return 'bags';
      case 'box':
        return 'boxes';
      case 'bottle':
        return 'bottles';
      case 'can':
        return 'cans';
      case 'jar':
        return 'jars';
      case 'pack':
        return 'packs';
      case 'item':
        return 'items';
      default:
        return '${unit}s';
    }
  }

  @override
  String toString() {
    return 'ShoppingItem(id: $id, name: $name, price: $price, quantity: $quantity, category: $category)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ShoppingItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Shopping item categories with icons
enum ShoppingCategory {
  meat('Meat', '🥩'),
  seafood('Seafood', '🐟'),
  dairy('Dairy', '🥛'),
  produce('Produce', '🥬'),
  vegetables('Vegetables', '🥕'),
  fruits('Fruits', '🍎'),
  grains('Grains', '🌾'),
  pantry('Pantry', '🏪'),
  beverages('Beverages', '🥤'),
  snacks('Snacks', '🍿'),
  frozen('Frozen', '🧊'),
  bakery('Bakery', '🍞'),
  spices('Spices', '🌶️'),
  condiments('Condiments', '🧂'),
  other('Other', '📦');

  const ShoppingCategory(this.displayName, this.emoji);

  final String displayName;
  final String emoji;

  static ShoppingCategory fromString(String category) {
    return ShoppingCategory.values.firstWhere(
      (c) => c.displayName.toLowerCase() == category.toLowerCase(),
      orElse: () => ShoppingCategory.other,
    );
  }
}

// Extension for shopping item helpers
extension ShoppingItemExtensions on ShoppingItem {
  ShoppingCategory get categoryEnum => ShoppingCategory.fromString(category);
  
  String get categoryEmoji => categoryEnum.emoji;
  
  bool get hasDiscount => _originalPrice != null && _originalPrice! > price;
  
  bool get isExpensive => price > 20.0;
  
  bool get isBulkItem => quantity > 3;
  
  Map<String, dynamic> get analyticsData => {
    'item_id': id,
    'item_name': name,
    'category': category,
    'price': price,
    'quantity': quantity,
    'is_on_sale': isOnSale,
    'store': store,
  };
}
