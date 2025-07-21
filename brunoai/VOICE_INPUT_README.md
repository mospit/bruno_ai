# Voice Input Feature Implementation

## Overview
This document describes the implementation of voice input functionality in Bruno AI, allowing users to speak their meal planning requests instead of typing them.

## 🎤 Features Implemented

### 1. VoiceInputController (`lib/controllers/voice_input_controller.dart`)
- **Speech-to-Text Integration**: Uses `speech_to_text` package for voice recognition
- **Permission Management**: Handles microphone permissions with `permission_handler`
- **State Management**: Tracks listening, processing, and error states
- **Error Handling**: Graceful fallbacks for network issues, permission denied, etc.
- **Sound Level Monitoring**: Visual feedback during speech recognition

### 2. VoiceInputButton (`lib/widgets/voice_input_button.dart`)
- **Visual States**: Idle, listening, processing, error, and complete states
- **Animated UI**: Pulse animations and visual feedback
- **Sound Visualization**: Real-time sound level indicators
- **Touch Feedback**: Haptic feedback for better user experience

### 3. Chat Interface Integration (`lib/widgets/chat_interface.dart`)
- **Dynamic Button Switching**: Shows mic button when text field is empty, send button when text is present
- **Text Integration**: Appends voice transcription to existing text
- **Automatic Sending**: Option to auto-send after voice recognition
- **Fallback Support**: Manual input remains available when voice fails

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ChatInterface  │────│ VoiceInputButton │────│VoiceInputCtrl  │
│                 │    │                  │    │                 │
│ - Text input    │    │ - Visual states  │    │ - Speech-to-text│
│ - Send button   │    │ - Animations     │    │ - Permissions   │
│ - Voice button  │    │ - User feedback  │    │ - Error handling│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────────┐
                    │   Speech-to-Text    │
                    │   & Permissions     │
                    │     Packages        │
                    └─────────────────────┘
```

## 📱 User Experience Flow

1. **Initial State**: User sees text input with mic button (when empty)
2. **Voice Activation**: User taps mic button to start listening
3. **Permission Check**: App requests microphone permission if needed
4. **Listening**: Visual feedback shows recording state with sound levels
5. **Processing**: Transcription appears in real-time (partial results)
6. **Completion**: Final transcribed text appears in input field
7. **Send Options**: User can edit text or send immediately
8. **Fallback**: Manual typing always available if voice fails

## 🛠️ Implementation Details

### Dependencies Added
```yaml
dependencies:
  speech_to_text: ^6.6.2
  permission_handler: ^11.1.0

dev_dependencies:
  mockito: ^5.4.4
  build_runner: ^2.4.9
```

### Key Methods

#### VoiceInputController
- `initialize()`: Sets up speech recognition and checks permissions
- `startListening()`: Begins voice recognition
- `stopListening()`: Stops voice recognition
- `onSpeechResult()`: Handles transcription results
- `onSpeechError()`: Manages recognition errors

#### ChatInterface Integration
- `_onVoiceRecognitionComplete()`: Processes final voice transcription
- Dynamic button switching based on text field content
- Error feedback via SnackBar
- Seamless integration with existing send functionality

### Error Handling
- **Permission Denied**: Shows error state, falls back to manual input
- **Network Issues**: Timeout handling with retry options
- **No Speech Detected**: User feedback with instructions
- **Recognition Errors**: Clear error messages with fallback options

## 🧪 Testing

### Unit Tests (`test/voice_input_test.dart`)
- Controller initialization and lifecycle
- Permission handling (granted/denied scenarios)
- Speech recognition flow (start/stop/results/errors)
- Sound level monitoring
- State management during full cycles
- Error recovery and fallback scenarios

### Widget Tests (`test/widget/chat_interface_voice_test.dart`)
- Voice button visibility based on text content
- Button state changes during voice recognition
- Voice transcription integration with chat
- Permission denial fallback behavior
- Message sending with voice input
- Error recovery in UI

### Test Runner (`test/run_voice_tests.dart`)
- Automated test execution
- Comprehensive test coverage reporting
- Feature readiness verification

## 🚀 Usage Instructions

### For Developers
1. **Setup Dependencies**:
   ```bash
   flutter pub get
   flutter pub run build_runner build
   ```

2. **Run Tests**:
   ```bash
   dart test/run_voice_tests.dart
   # OR individual tests:
   flutter test test/voice_input_test.dart
   flutter test test/widget/chat_interface_voice_test.dart
   ```

3. **Integration**:
   - `VoiceInputController` is automatically initialized in `ChatInterface`
   - `VoiceInputButton` replaces send button when text field is empty
   - No additional setup required - works out of the box

### For Users
1. **First Time Use**: Grant microphone permission when prompted
2. **Voice Input**: Tap the microphone button to start speaking
3. **Visual Feedback**: Watch the button animation and sound level indicators
4. **Text Review**: Review and edit the transcribed text if needed
5. **Send Message**: Tap send button or continue with voice input

## ⚙️ Configuration

### Supported Languages
- Default: English (US)
- Configurable through `localeId` parameter in `VoiceInputController`

### Timeout Settings
- **Listen Duration**: 30 seconds (configurable)
- **Pause Detection**: 3 seconds of silence
- **Network Timeout**: Handled by speech-to-text package

### Permissions Required

#### Android (`android/app/src/main/AndroidManifest.xml`)
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
```

#### iOS (`ios/Runner/Info.plist`)
```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs access to the microphone for voice input in meal planning conversations.</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app uses speech recognition to convert your voice to text for easier meal planning.</string>
```

## 🔧 Customization Options

### Visual Styling
- Button colors and animations can be customized in `VoiceInputButton`
- Error states and feedback colors configurable via theme
- Sound level visualization style adjustable

### Behavior Settings
- Auto-send after voice recognition (currently manual)
- Partial results display (currently enabled)
- Error retry attempts and timeouts
- Language and locale settings

## 🐛 Troubleshooting

### Common Issues
1. **Permission Denied**: 
   - Check app permissions in device settings
   - Ensure proper permission declarations in manifests
   
2. **No Speech Detected**:
   - Check device microphone functionality
   - Test in quiet environment
   - Verify network connectivity for cloud speech recognition

3. **Recognition Errors**:
   - Ensure stable internet connection
   - Speak clearly and avoid background noise
   - Check if language/locale is supported

### Debugging
- Enable verbose logging in `VoiceInputController`
- Use Flutter Inspector to check widget states
- Monitor permission status in device settings

## 🎯 Future Enhancements
- [ ] Offline speech recognition support
- [ ] Multiple language support with language detection
- [ ] Custom wake words ("Hey Bruno")
- [ ] Voice commands for app navigation
- [ ] Voice-to-emoji conversion
- [ ] Background voice processing
- [ ] Voice training for better accuracy

## 📋 Requirements Met
✅ Integrate `speech_to_text` and wrap in `VoiceInputController`  
✅ Add mic button to chat composer that toggles listening state  
✅ Append transcribed text to message input  
✅ Handle permission prompts gracefully with fallback to manual input  
✅ Unit test transcription → send flow with mock recognition results  

## 📚 References
- [speech_to_text package](https://pub.dev/packages/speech_to_text)
- [permission_handler package](https://pub.dev/packages/permission_handler)
- [Flutter Speech Recognition Guide](https://flutter.dev/docs/development/data-and-backend/speech-recognition)
- [Material Design Voice Input Guidelines](https://material.io/design/communication/voice-and-speech.html)
