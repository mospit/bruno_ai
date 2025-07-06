#!/usr/bin/env dart

import 'dart:io';

/// Test runner script for Bruno AI Flutter project
/// Runs different categories of tests with proper reporting
void main(List<String> args) async {
  print('🐻 Bruno AI Test Runner');
  print('========================\n');

  if (args.isEmpty) {
    await runAllTests();
  } else {
    final command = args[0].toLowerCase();
    switch (command) {
      case 'unit':
        await runUnitTests();
        break;
      case 'widget':
        await runWidgetTests();
        break;
      case 'integration':
        await runIntegrationTests();
        break;
      case 'models':
        await runModelTests();
        break;
      case 'providers':
        await runProviderTests();
        break;
      case 'coverage':
        await runTestsWithCoverage();
        break;
      case 'help':
      case '-h':
      case '--help':
        showHelp();
        break;
      default:
        print('❌ Unknown command: $command');
        showHelp();
        exit(1);
    }
  }
}

Future<void> runAllTests() async {
  print('🧪 Running all tests...\n');
  
  final results = <String, bool>{};
  
  // Run unit tests
  print('📊 Running unit tests...');
  results['Unit Tests'] = await runTests('test/unit/');
  
  // Run widget tests
  print('\n🎨 Running widget tests...');
  results['Widget Tests'] = await runTests('test/widget/');
  
  // Run app test
  print('\n📱 Running app test...');
  results['App Test'] = await runTests('test/widget_test.dart');
  
  // Print summary
  printSummary(results);
}

Future<void> runUnitTests() async {
  print('📊 Running unit tests...\n');
  final success = await runTests('test/unit/');
  if (success) {
    print('\n✅ Unit tests passed!');
  } else {
    print('\n❌ Unit tests failed!');
    exit(1);
  }
}

Future<void> runWidgetTests() async {
  print('🎨 Running widget tests...\n');
  final success = await runTests('test/widget/');
  if (success) {
    print('\n✅ Widget tests passed!');
  } else {
    print('\n❌ Widget tests failed!');
    exit(1);
  }
}

Future<void> runIntegrationTests() async {
  print('🔄 Running integration tests...\n');
  final success = await runTests('test/integration/');
  if (success) {
    print('\n✅ Integration tests passed!');
  } else {
    print('\n❌ Integration tests failed!');
    exit(1);
  }
}

Future<void> runModelTests() async {
  print('📦 Running model tests...\n');
  final success = await runTests('test/unit/models/');
  if (success) {
    print('\n✅ Model tests passed!');
  } else {
    print('\n❌ Model tests failed!');
    exit(1);
  }
}

Future<void> runProviderTests() async {
  print('🏪 Running provider tests...\n');
  final success = await runTests('test/unit/providers/');
  if (success) {
    print('\n✅ Provider tests passed!');
  } else {
    print('\n❌ Provider tests failed!');
    exit(1);
  }
}

Future<void> runTestsWithCoverage() async {
  print('📈 Running tests with coverage...\n');
  
  final result = await Process.run(
    'flutter',
    ['test', '--coverage'],
    runInShell: true,
  );
  
  if (result.exitCode == 0) {
    print('✅ Tests with coverage completed!');
    print('📊 Coverage report generated in coverage/lcov.info');
    
    // Try to generate HTML coverage report if lcov is available
    final lcovResult = await Process.run(
      'genhtml',
      ['-o', 'coverage/html', 'coverage/lcov.info'],
      runInShell: true,
    );
    
    if (lcovResult.exitCode == 0) {
      print('🌐 HTML coverage report generated in coverage/html/');
    } else {
      print('ℹ️  Install lcov to generate HTML coverage reports');
    }
  } else {
    print('❌ Tests with coverage failed!');
    print(result.stderr);
    exit(1);
  }
}

Future<bool> runTests(String path) async {
  final result = await Process.run(
    'flutter',
    ['test', path],
    runInShell: true,
  );
  
  print(result.stdout);
  if (result.stderr.toString().isNotEmpty) {
    print(result.stderr);
  }
  
  return result.exitCode == 0;
}

void printSummary(Map<String, bool> results) {
  print('\n📋 Test Summary');
  print('================');
  
  int passed = 0;
  int total = results.length;
  
  for (final entry in results.entries) {
    final status = entry.value ? '✅' : '❌';
    print('$status ${entry.key}');
    if (entry.value) passed++;
  }
  
  print('\n📊 Overall: $passed/$total test suites passed');
  
  if (passed == total) {
    print('🎉 All tests passed! Great job! 🐻');
  } else {
    print('⚠️  Some tests failed. Please check the output above.');
    exit(1);
  }
}

void showHelp() {
  print('''
Usage: dart test_runner.dart [command]

Commands:
  (no command)  Run all tests
  unit          Run unit tests only
  widget        Run widget tests only
  integration   Run integration tests only
  models        Run model tests only
  providers     Run provider tests only
  coverage      Run tests with coverage report
  help          Show this help message

Examples:
  dart test_runner.dart           # Run all tests
  dart test_runner.dart unit      # Run only unit tests
  dart test_runner.dart coverage  # Run tests with coverage
''');
}
