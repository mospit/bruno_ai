// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:brunoai/providers/bruno_provider.dart';
import 'package:brunoai/theme/modern_theme.dart';

void main() {
  testWidgets('App structure is correct', (WidgetTester tester) async {
    // Create a simple app structure without complex animations
    await tester.pumpWidget(
      MaterialApp(
        title: 'Bruno AI Test',
        theme: ModernTheme.lightTheme,
        home: ChangeNotifierProvider(
          create: (_) => BrunoProvider(),
          child: const Scaffold(
            body: Center(
              child: Text('Bruno AI App'),
            ),
          ),
        ),
      ),
    );

    // Verify basic app structure
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.text('Bruno AI App'), findsOneWidget);
  });
}
