import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/models/shopping_item.dart';

void main() {
  group('FavoriteMeal', () {
    late FavoriteMeal favoriteMeal;
    late DateTime testDate;

    setUp(() {
      testDate = DateTime(2025, 1, 1);
      favoriteMeal = FavoriteMeal(
        id: 'meal_1',
        name: 'Chicken Stir Fry',
        description: 'Delicious chicken stir fry with vegetables',
        ingredients: ['2 lbs chicken breast', '1 cup broccoli', '2 cups rice'],
        estimatedCost: 15.99,
        servings: 4,
        cookingTime: 30,
        category: 'Main Course',
        dateAdded: testDate,
      );
    });

    test('should create FavoriteMeal with all properties', () {
      expect(favoriteMeal.id, equals('meal_1'));
      expect(favoriteMeal.name, equals('Chicken Stir Fry'));
      expect(favoriteMeal.description, equals('Delicious chicken stir fry with vegetables'));
      expect(favoriteMeal.ingredients, hasLength(3));
      expect(favoriteMeal.estimatedCost, equals(15.99));
      expect(favoriteMeal.servings, equals(4));
      expect(favoriteMeal.cookingTime, equals(30));
      expect(favoriteMeal.category, equals('Main Course'));
      expect(favoriteMeal.dateAdded, equals(testDate));
    });

    test('should contain expected ingredients', () {
      expect(favoriteMeal.ingredients, contains('2 lbs chicken breast'));
      expect(favoriteMeal.ingredients, contains('1 cup broccoli'));
      expect(favoriteMeal.ingredients, contains('2 cups rice'));
    });

    test('should have correct cost per serving calculation', () {
      final costPerServing = favoriteMeal.estimatedCost / favoriteMeal.servings;
      expect(costPerServing, equals(3.9975));
    });
  });
}
