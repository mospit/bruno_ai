import 'dart:io';

/// Test runner for voice input functionality
/// 
/// This script runs all voice input related tests and provides
/// comprehensive coverage of the voice input feature including:
/// - VoiceInputController functionality
/// - Permission handling
/// - Speech recognition flow
/// - UI integration
/// - Error handling and fallbacks
void main() async {
  print('🎤 Running Voice Input Tests...\n');
  
  final tests = [
    'test/voice_input_test.dart',
    'test/widget/chat_interface_voice_test.dart',
  ];
  
  var allTestsPassed = true;
  var totalTests = 0;
  var passedTests = 0;
  
  for (final testFile in tests) {
    print('📋 Running $testFile');
    
    final result = await Process.run(
      'flutter',
      ['test', testFile, '--reporter=expanded'],
      runInShell: true,
    );
    
    if (result.exitCode == 0) {
      print('✅ $testFile passed\n');
      
      // Parse test results (simplified)
      final output = result.stdout.toString();
      final testCount = _extractTestCount(output);
      totalTests += testCount;
      passedTests += testCount;
    } else {
      print('❌ $testFile failed');
      print('Error: ${result.stderr}');
      print('Output: ${result.stdout}\n');
      allTestsPassed = false;
      
      // Still count total tests even if some failed
      final output = result.stdout.toString();
      final testCount = _extractTestCount(output);
      totalTests += testCount;
    }
  }
  
  // Summary
  print('📊 Test Summary');
  print('=' * 50);
  
  if (allTestsPassed) {
    print('🎉 All voice input tests passed!');
    print('✅ $passedTests/$totalTests tests passed');
    print('\n🎤 Voice Input Feature Status: READY');
    print('The following features are tested and working:');
    print('  • VoiceInputController initialization and lifecycle');
    print('  • Microphone permission handling');
    print('  • Speech-to-text recognition flow');
    print('  • Voice input button UI states');
    print('  • Integration with chat composer');
    print('  • Transcription → send message flow');
    print('  • Error handling and graceful fallbacks');
    print('  • Manual input fallback when voice fails');
  } else {
    print('⚠️  Some tests failed');
    print('❌ ${totalTests - passedTests}/$totalTests tests failed');
    print('\n🔧 Please fix failing tests before deploying voice input feature');
  }
  
  print('\n🚀 Next Steps:');
  print('  1. Run: flutter pub get');
  print('  2. Run: flutter pub run build_runner build');
  print('  3. Test on physical device for microphone access');
  print('  4. Test in noisy environments');
  print('  5. Test with different languages/accents');
  
  exit(allTestsPassed ? 0 : 1);
}

int _extractTestCount(String output) {
  // Simple regex to extract test count from flutter test output
  final pattern = RegExp(r'All tests passed! \((\d+) passed\)|(\d+) tests? passed');
  final match = pattern.firstMatch(output);
  
  if (match != null) {
    return int.tryParse(match.group(1) ?? match.group(2) ?? '0') ?? 0;
  }
  
  // Fallback: count individual test case indicators
  final testCasePattern = RegExp(r'✓ ');
  return testCasePattern.allMatches(output).length;
}
