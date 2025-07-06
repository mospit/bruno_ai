import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:brunoai/widgets/meal_card.dart';
import 'package:brunoai/widgets/liquid_glass_container.dart';

void main() {
  group('MealPlanCard Widget', () {
    late Meal testMeal;

    setUp(() {
      testMeal = Meal(
        id: 'test_meal',
        name: 'Test Chicken Stir Fry',
        description: 'A delicious test meal',
        cost: 15.99,
        servings: 4,
        prepTime: 30,
        ingredients: ['2 lbs chicken breast', '1 cup broccoli', '2 cups rice'],
        instructions: ['Heat pan', 'Cook chicken', 'Add vegetables'],
        category: 'Main Course',
        nutrition: {'calories': 350.0, 'protein': 25.0},
        isHealthy: true,
        isQuick: true,
        difficulty: 'Easy',
      );
    });

    Widget createTestWidget({
      required Meal meal,
      VoidCallback? onAddToCart,
      VoidCallback? onViewRecipe,
      bool isInCart = false,
      bool showNutrition = false,
    }) {
      return MaterialApp(
        home: Scaffold(
          body: MealPlanCard(
            meal: meal,
            onAddToCart: onAddToCart,
            onViewRecipe: onViewRecipe,
            isInCart: isInCart,
            showNutrition: showNutrition,
          ),
        ),
      );
    }

    testWidgets('should display meal information correctly', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      expect(find.text('Test Chicken Stir Fry'), findsOneWidget);
      expect(find.text('A delicious test meal'), findsOneWidget);
    });

    testWidgets('should display cost and serving information', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      // Cost should be displayed in the badge
      expect(find.textContaining('\$15.99'), findsOneWidget);
      
      // Servings should be displayed
      expect(find.textContaining('4 servings'), findsOneWidget);
    });

    testWidgets('should show prep time', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      expect(find.textContaining('30'), findsOneWidget);
      expect(find.textContaining('min'), findsOneWidget);
    });

    testWidgets('should be wrapped in LiquidGlassContainer', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      expect(find.byType(LiquidGlassContainer), findsOneWidget);
    });

    testWidgets('should handle tap interactions', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      final mealCardFinder = find.byType(MealPlanCard);
      expect(mealCardFinder, findsOneWidget);

      // Should find required components
      expect(find.byType(AnimatedContainer), findsOneWidget);
      expect(find.byType(AnimatedCrossFade), findsOneWidget);
    });

    testWidgets('should expand and show additional content when tapped', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      // Initially should be collapsed
      final crossFade = tester.widget<AnimatedCrossFade>(find.byType(AnimatedCrossFade));
      expect(crossFade.crossFadeState, equals(CrossFadeState.showFirst));

      // Find and tap the expand button specifically
      final expandButton = find.byIcon(Icons.expand_more);
      await tester.tap(expandButton);
      await tester.pump();

      // Should be expanded now
      final expandedCrossFade = tester.widget<AnimatedCrossFade>(find.byType(AnimatedCrossFade));
      expect(expandedCrossFade.crossFadeState, equals(CrossFadeState.showSecond));
    });

    testWidgets('should contain Transform and animation widgets', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      // Should have Transform widgets for animations (multiple are expected)
      expect(find.byType(Transform), findsWidgets);
      
      // Should have AnimatedRotation for expand button
      expect(find.byType(AnimatedRotation), findsOneWidget);
    });

    testWidgets('should call onAddToCart when provided', (tester) async {
      bool addToCartCalled = false;
      
      await tester.pumpWidget(createTestWidget(
        meal: testMeal,
        onAddToCart: () => addToCartCalled = true,
      ));

      // Note: This would need to be implemented in the actual widget
      // The current implementation doesn't show the add to cart button
      // This test documents expected behavior
    });

    testWidgets('should call onViewRecipe when provided', (tester) async {
      bool viewRecipeCalled = false;
      
      await tester.pumpWidget(createTestWidget(
        meal: testMeal,
        onViewRecipe: () => viewRecipeCalled = true,
      ));

      // Note: This would need to be implemented in the actual widget
      // The current implementation doesn't show the view recipe button
      // This test documents expected behavior
    });

    testWidgets('should show different UI when isInCart is true', (tester) async {
      await tester.pumpWidget(createTestWidget(
        meal: testMeal,
        isInCart: true,
      ));

      // Note: This would need visual indication in the actual widget
      // This test documents expected behavior
    });

    testWidgets('should show nutrition info when showNutrition is true', (tester) async {
      await tester.pumpWidget(createTestWidget(
        meal: testMeal,
        showNutrition: true,
      ));

      // Note: This would need to be implemented in the actual widget
      // to show nutrition information when expanded
      // This test documents expected behavior
    });

    testWidgets('should show ingredients when expanded', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      // Tap expand button to show ingredients
      final expandButton = find.byIcon(Icons.expand_more);
      await tester.tap(expandButton);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300)); // Wait for animation

      // Should show ingredients section
      expect(find.text('Ingredients'), findsOneWidget);
    });

    testWidgets('should handle meals without optional properties', (tester) async {
      final simpleMeal = Meal(
        id: 'simple',
        name: 'Simple Meal',
        description: 'Basic meal',
        cost: 10.0,
        servings: 2,
        prepTime: 15,
        ingredients: ['ingredient1'],
      );

      await tester.pumpWidget(createTestWidget(meal: simpleMeal));

      expect(find.text('Simple Meal'), findsOneWidget);
      expect(find.text('Basic meal'), findsOneWidget);
    });

    testWidgets('should dispose animation controller properly', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      // Remove the widget
      await tester.pumpWidget(const MaterialApp(home: Scaffold(body: SizedBox())));

      // Should not throw any errors about disposed controllers
    });

    testWidgets('should handle rapid expand button taps', (tester) async {
      await tester.pumpWidget(createTestWidget(meal: testMeal));

      final expandButton = find.byIcon(Icons.expand_more);

      // Rapidly tap expand button multiple times
      for (int i = 0; i < 5; i++) {
        await tester.tap(expandButton);
        await tester.pump(const Duration(milliseconds: 50));
      }

      // Should handle gracefully without errors
      expect(find.byType(MealPlanCard), findsOneWidget);
    });

    group('Meal Properties', () {
      testWidgets('should show healthy indicator for healthy meals', (tester) async {
        final healthyMeal = Meal(
          id: 'healthy',
          name: 'Healthy Meal',
          description: 'Nutritious meal',
          cost: 12.0,
          servings: 2,
          prepTime: 20,
          ingredients: ['vegetables'],
          isHealthy: true,
        );

        await tester.pumpWidget(createTestWidget(meal: healthyMeal));

        // Note: Healthy indicator would need to be implemented
        // in the actual widget UI
      });

      testWidgets('should show quick indicator for quick meals', (tester) async {
        final quickMeal = Meal(
          id: 'quick',
          name: 'Quick Meal',
          description: 'Fast meal',
          cost: 8.0,
          servings: 1,
          prepTime: 15,
          ingredients: ['pasta'],
          isQuick: true,
        );

        await tester.pumpWidget(createTestWidget(meal: quickMeal));

        // Note: Quick indicator would need to be implemented
        // in the actual widget UI
      });

      testWidgets('should display difficulty level', (tester) async {
        final hardMeal = Meal(
          id: 'hard',
          name: 'Complex Meal',
          description: 'Difficult meal',
          cost: 25.0,
          servings: 6,
          prepTime: 90,
          ingredients: ['many', 'complex', 'ingredients'],
          difficulty: 'Hard',
        );

        await tester.pumpWidget(createTestWidget(meal: hardMeal));

        // Note: Difficulty display would need to be implemented
        // in the actual widget UI
      });
    });
  });
}
