import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/widgets/meal_card.dart';
import 'package:brunoai/models/shopping_item.dart';

void main() {
  group('Meal', () {
    late Meal meal;

    setUp(() {
      meal = Meal(
        id: 'meal_1',
        name: 'Chicken Stir Fry',
        description: 'Delicious chicken stir fry with vegetables',
        cost: 15.99,
        servings: 4,
        prepTime: 30,
        imageUrl: 'https://example.com/meal.jpg',
        ingredients: ['2 lbs chicken breast', '1 cup broccoli', '2 cups rice'],
        instructions: ['Heat pan', 'Cook chicken', 'Add vegetables'],
        category: 'Main Course',
        nutrition: {'calories': 350.0, 'protein': 25.0, 'carbs': 30.0},
        isHealthy: true,
        isQuick: true,
        difficulty: 'Easy',
      );
    });

    test('should create Meal with all properties', () {
      expect(meal.id, equals('meal_1'));
      expect(meal.name, equals('Chicken Stir Fry'));
      expect(meal.description, equals('Delicious chicken stir fry with vegetables'));
      expect(meal.cost, equals(15.99));
      expect(meal.servings, equals(4));
      expect(meal.prepTime, equals(30));
      expect(meal.imageUrl, equals('https://example.com/meal.jpg'));
      expect(meal.ingredients, hasLength(3));
      expect(meal.instructions, hasLength(3));
      expect(meal.category, equals('Main Course'));
      expect(meal.nutrition['calories'], equals(350.0));
      expect(meal.isHealthy, isTrue);
      expect(meal.isQuick, isTrue);
      expect(meal.difficulty, equals('Easy'));
    });

    test('should calculate cost per serving correctly', () {
      expect(meal.costPerServing, equals(3.9975));
    });

    test('should create with default values', () {
      final simpleMeal = Meal(
        id: 'simple_meal',
        name: 'Simple Meal',
        description: 'A simple meal',
        cost: 10.0,
        servings: 2,
        prepTime: 15,
        ingredients: ['ingredient1', 'ingredient2'],
      );

      expect(simpleMeal.imageUrl, isNull);
      expect(simpleMeal.instructions, isEmpty);
      expect(simpleMeal.category, equals('Main Course'));
      expect(simpleMeal.nutrition, isEmpty);
      expect(simpleMeal.isHealthy, isFalse);
      expect(simpleMeal.isQuick, isFalse);
      expect(simpleMeal.difficulty, equals('Easy'));
    });

    test('should convert ingredients to shopping items', () {
      final shoppingItems = meal.shoppingItems;
      
      expect(shoppingItems, hasLength(3));
      expect(shoppingItems[0].name, equals('lbs chicken breast'));
      expect(shoppingItems[0].quantity, equals(2));
      expect(shoppingItems[0].notes, equals('For Chicken Stir Fry'));
      
      expect(shoppingItems[1].name, equals('cup broccoli'));
      expect(shoppingItems[1].quantity, equals(1));
      
      expect(shoppingItems[2].name, equals('cups rice'));
      expect(shoppingItems[2].quantity, equals(2));
    });

    test('should categorize ingredients correctly', () {
      final meatMeal = Meal(
        id: 'meat_meal',
        name: 'Meat Meal',
        description: 'Meat based meal',
        cost: 20.0,
        servings: 4,
        prepTime: 45,
        ingredients: ['1 lb chicken', '2 cups beef', '1 lb pork'],
      );

      final shoppingItems = meatMeal.shoppingItems;
      expect(shoppingItems[0].category, equals('Meat'));
      expect(shoppingItems[1].category, equals('Meat'));
      expect(shoppingItems[2].category, equals('Meat'));
    });

    test('should determine ingredient units correctly', () {
      final unitTestMeal = Meal(
        id: 'unit_test',
        name: 'Unit Test Meal',
        description: 'Testing units',
        cost: 15.0,
        servings: 2,
        prepTime: 20,
        ingredients: ['1 lb chicken', '2 cups rice', '1 tbsp oil', '1 tsp salt'],
      );

      final shoppingItems = unitTestMeal.shoppingItems;
      expect(shoppingItems[0].unit, equals('lbs'));
      expect(shoppingItems[1].unit, equals('cups'));
      expect(shoppingItems[2].unit, equals('tbsp'));
      expect(shoppingItems[3].unit, equals('tsp'));
    });

    test('should handle ingredients without quantities', () {
      final noQuantityMeal = Meal(
        id: 'no_quantity',
        name: 'No Quantity Meal',
        description: 'Meal without quantities',
        cost: 12.0,
        servings: 3,
        prepTime: 25,
        ingredients: ['chicken', 'rice', 'vegetables'],
      );

      final shoppingItems = noQuantityMeal.shoppingItems;
      expect(shoppingItems[0].quantity, equals(1));
      expect(shoppingItems[1].quantity, equals(1));
      expect(shoppingItems[2].quantity, equals(1));
    });

    test('should categorize dairy ingredients', () {
      final dairyMeal = Meal(
        id: 'dairy_meal',
        name: 'Dairy Meal',
        description: 'Dairy based meal',
        cost: 18.0,
        servings: 2,
        prepTime: 15,
        ingredients: ['1 cup milk', '2 oz cheese', '1 cup yogurt'],
      );

      final shoppingItems = dairyMeal.shoppingItems;
      expect(shoppingItems[0].category, equals('Dairy'));
      expect(shoppingItems[1].category, equals('Dairy'));
      expect(shoppingItems[2].category, equals('Dairy'));
    });

    test('should categorize vegetable ingredients', () {
      final vegMeal = Meal(
        id: 'veg_meal',
        name: 'Vegetable Meal',
        description: 'Vegetable based meal',
        cost: 10.0,
        servings: 2,
        prepTime: 20,
        ingredients: ['1 tomato', '1 onion', '1 bell pepper'],
      );

      final shoppingItems = vegMeal.shoppingItems;
      expect(shoppingItems[0].category, equals('Vegetables'));
      expect(shoppingItems[1].category, equals('Vegetables'));
      expect(shoppingItems[2].category, equals('Vegetables'));
    });

    test('should categorize grain ingredients', () {
      final grainMeal = Meal(
        id: 'grain_meal',
        name: 'Grain Meal',
        description: 'Grain based meal',
        cost: 8.0,
        servings: 4,
        prepTime: 30,
        ingredients: ['2 cups rice', '1 lb pasta', '2 slices bread'],
      );

      final shoppingItems = grainMeal.shoppingItems;
      expect(shoppingItems[0].category, equals('Grains'));
      expect(shoppingItems[1].category, equals('Grains'));
      expect(shoppingItems[2].category, equals('Grains'));
    });
  });
}
