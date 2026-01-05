# Voice-Enabled Appointment Scheduler 🎤

Voice integration for the appointment scheduling chatbot using Deepgram for Speech-to-Text and Text-to-Speech.

## Features

✅ **Speech-to-Text** - Speak naturally to describe your health issues  
✅ **Text-to-Speech** - Hear the assistant's responses  
✅ **Smart Recording** - Auto-detects when you stop speaking  
✅ **Full Integration** - Works with all appointment booking features  
✅ **Real-time Processing** - Fast transcription and responses  

## Quick Start

### 1. Prerequisites

Make sure you have:
- ✅ Backend server running (`./run_local.sh`)
- ✅ Deepgram API key set in environment

```bash
export DEEPGRAM_API_KEY="your-api-key-here"
```

### 2. Run Voice Chat

```bash
# From the voice-scaffold root directory
cd ..
./run_appointment_voice.sh
```

Or manually:

```bash
# From voice-scaffold root
pip install pyaudio pydub simpleaudio
python appointment_voice.py
```

## How It Works

```
┌──────────────────────────────────────────────────────────┐
│  1. Press Enter to Record                                 │
│     ↓                                                     │
│  2. Speak Your Request                                    │
│     "I need a dental cleaning tomorrow afternoon"        │
│     ↓                                                     │
│  3. Auto-Detect Silence → Stop Recording                 │
│     ↓                                                     │
│  4. Deepgram Transcribes (STT)                           │
│     ↓                                                     │
│  5. Send to Appointment API                              │
│     ↓                                                     │
│  6. Get Response from LLM                                │
│     ↓                                                     │
│  7. Deepgram Speaks Response (TTS)                       │
│     "Great! Dr. Amanda White has availability..."        │
│     ↓                                                     │
│  8. Press Enter to Continue or 'q' to Quit               │
└──────────────────────────────────────────────────────────┘
```

## Example Conversation

```
🎤 VOICE APPOINTMENT SCHEDULER
═══════════════════════════════════════════════════════════

▶ Press Enter to speak (or 'q' to quit): [Enter]

🎤 Listening... (speak now, will auto-detect silence)
✓ Recording complete
🔄 Transcribing...
📝 You said: "I need to schedule a dental cleaning for tomorrow afternoon"

💭 Processing...

🤖 Assistant: Hi! I can help you schedule a dental cleaning. I've found 
Dr. Amanda White, a dentist with 12 years of experience and a 4.9 rating. 
She has these afternoon slots available tomorrow, Tuesday, January 6, 2026:
- 1:00 PM
- 3:00 PM

Which time works best for you?

   (State: availability_checked)

💡 Suggestions:
   • Check availability
   • Ask about the provider

🔊 Speaking response...
✓ Done

▶ Press Enter to speak (or 'q' to quit):
```

## Voice Commands Examples

### Scheduling
- "I need a dental cleaning tomorrow afternoon"
- "Can I see a dermatologist for a rash?"
- "Book me with a general practitioner next week"

### Preferences
- "Morning times work better for me"
- "Do you have any afternoon slots?"
- "What about Friday?"

### Confirmation
- "Yes, 2 PM works great"
- "Book the 10 AM appointment"
- "My name is John Smith"

## Technical Details

### Audio Recording
- **Format**: 16-bit PCM WAV
- **Sample Rate**: 16kHz (optimized for speech)
- **Channels**: Mono
- **Detection**: Volume-based silence detection
- **Max Duration**: 5 seconds safety limit

### Transcription (STT)
- **Provider**: Deepgram Nova-3 model
- **Accuracy**: High accuracy for medical terms
- **Speed**: ~1-2 seconds processing time

### Speech Synthesis (TTS)
- **Provider**: Deepgram Aura-2 (Asteria voice)
- **Format**: MP3 output
- **Chunking**: Handles long responses (2000 char chunks)
- **Playback**: Real-time audio playback through speakers

## Architecture

```
voice-scaffold/                              <-- Run from here
├── appointment_voice.py                     <-- Voice interface
├── voice.py                                 <-- STT/TTS wrapper
└── appointment-scheduler/
    └── backend/                             <-- API at :8000

┌─────────────────────────────────────────────────────┐
│         appointment_voice.py (ROOT)                 │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │  VoiceAppointmentScheduler                 │   │
│  │                                            │   │
│  │  • record_audio()    → Audio bytes        │   │
│  │  • send_message()    → API call           │   │
│  │  • run()             → Main loop          │   │
│  └───────────┬────────────────────────────────┘   │
│              │                                     │
└──────────────┼─────────────────────────────────────┘
               │
               ├──────────────────┐
               │                  │
       ┌───────▼────────┐  ┌─────▼──────────────┐
       │  voice.py      │  │  Backend API       │
       │  (STT/TTS)     │  │  :8000/api/conv... │
       │                │  │                    │
       │  • listen()    │  │  • LLM Processing  │
       │  • speak()     │  │  • Tool Calls      │
       └────────┬───────┘  │  • State Mgmt      │
                │          └────────────────────┘
                │
       ┌────────▼─────────┐
       │  Deepgram API    │
       │  • Nova-3 (STT)  │
       │  • Aura-2 (TTS)  │
       └──────────────────┘
```

## Dependencies

### Python Packages
```
pyaudio          # Audio recording
pydub            # Audio processing
simpleaudio      # Audio playback
deepgram-sdk     # STT/TTS (already in requirements.txt)
requests         # API calls
```

### System Requirements
- **macOS**: Built-in support
- **Linux**: `sudo apt-get install portaudio19-dev python3-pyaudio`
- **Windows**: PyAudio wheels available via pip

## Troubleshooting

### "Backend is not running"
```bash
# Start backend in another terminal
cd appointment-scheduler
./run_local.sh
```

### "Cannot connect to Deepgram"
```bash
# Check API key
echo $DEEPGRAM_API_KEY

# Or set it
export DEEPGRAM_API_KEY="your-key"
```

### "No audio input detected"
- Check microphone permissions
- Test with: `python -c "import pyaudio; p=pyaudio.PyAudio(); print('Audio OK')"`
- Try speaking louder or closer to mic

### "Audio playback not working"
```bash
# Install audio dependencies
pip install pydub simpleaudio

# macOS may need ffmpeg
brew install ffmpeg
```

### "Import pyaudio error"
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

## Configuration

You can customize the voice chat behavior by editing `appointment_voice.py` (in the root voice-scaffold directory):

```python
# Recording settings
RECORD_SECONDS = 5      # Max recording duration
RATE = 16000           # Sample rate (Hz)
CHANNELS = 1           # Mono audio

# Voice selection
voice = "aura-2-asteria-en"  # Female voice
# Other options:
# - "aura-2-athena-en"    (Female, warm)
# - "aura-2-helios-en"    (Male, professional)
# - "aura-2-zeus-en"      (Male, authoritative)
```

## Advanced Usage

### Custom Voice Selection

```python
# In appointment_voice.py (root directory), modify the speak() call:
audio = self.voice.speak(
    assistant_text, 
    voice="aura-2-helios-en",  # Male voice
    play=True
)
```

### Save Audio Files

```python
# Save transcription audio
with open("recording.wav", "wb") as f:
    f.write(audio_bytes)

# Save response audio
audio = self.voice.speak(assistant_text, play=False)
with open("response.mp3", "wb") as f:
    f.write(audio)
```

### Integration with Streamlit

The voice features can be added to `streamlit_app.py` using:
- `streamlit-webrtc` for browser recording
- `audio-recorder-streamlit` widget
- Or file upload for pre-recorded audio

## Performance

- **Recording Latency**: Instant start
- **Transcription**: ~1-2 seconds
- **LLM Processing**: ~2-5 seconds (depends on complexity)
- **TTS Generation**: ~1-2 seconds
- **Total**: ~5-10 seconds per interaction

## Security

- ✅ API keys loaded from environment
- ✅ Audio never stored permanently
- ✅ Secure HTTPS communication with Deepgram
- ✅ No PHI (Protected Health Information) logging

## Future Enhancements

Possible improvements:
- [ ] Wake word detection ("Hey Assistant")
- [ ] Conversation history playback
- [ ] Multi-language support
- [ ] Voice biometrics for patient verification
- [ ] Streaming responses (incremental TTS)
- [ ] Background noise cancellation

## See Also

- [Main README](../README.md) - Project overview
- [Streamlit UI](STREAMLIT_README.md) - Web interface
- [API Documentation](../backend/api/) - Backend API
- [Voice Class](../voice.py) - Core voice functionality
