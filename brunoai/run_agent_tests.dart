#!/usr/bin/env dart

import 'dart:io';
import 'dart:convert';

/// Test runner for Bruno AI agent integration tests
/// This script runs the agent tests and provides detailed output
void main(List<String> arguments) async {
  print('🐻 Bruno AI Agent Test Runner');
  print('================================');
  
  // Check if server is running
  print('Checking if Bruno AI server is running...');
  final serverRunning = await checkServer();
  
  if (!serverRunning) {
    print('❌ Bruno AI server is not running');
    print('Please start the server first:');
    print('  cd server && python main.py');
    exit(1);
  }
  
  print('✅ Bruno AI server is running');
  
  // Run the integration tests
  print('\n🧪 Running agent integration tests...');
  
  final testCommand = [
    'flutter',
    'test',
    'integration_test/agent_integration_test.dart',
    '--verbose'
  ];
  
  final result = await Process.run(
    testCommand.first,
    testCommand.skip(1).toList(),
    workingDirectory: Directory.current.path,
  );
  
  print('\n📊 Test Results:');
  print('================');
  print('Exit code: ${result.exitCode}');
  print('\nOutput:');
  print(result.stdout);
  
  if (result.stderr.toString().isNotEmpty) {
    print('\nErrors:');
    print(result.stderr);
  }
  
  if (result.exitCode == 0) {
    print('\n✅ All tests passed!');
  } else {
    print('\n❌ Some tests failed');
  }
  
  exit(result.exitCode);
}

/// Check if the Bruno AI server is running
Future<bool> checkServer() async {
  try {
    final client = HttpClient();
    final request = await client.getUrl(Uri.parse('http://localhost:3000/gateway/health'));
    final response = await request.close();
    
    final responseBody = await response.transform(utf8.decoder).join();
    client.close();
    
    if (response.statusCode == 200) {
      final data = jsonDecode(responseBody);
      return data['status'] == 'healthy';
    }
    
    return false;
  } catch (e) {
    return false;
  }
}
