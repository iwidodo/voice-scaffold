# Voice-Enabled Appointment Scheduler 🎤🏥

An intelligent voice assistant for scheduling healthcare appointments. Speak naturally to book appointments with doctors, dentists, and other healthcare providers.

## Quick Start

### 1. Start the Backend
```bash
cd appointment-scheduler
./run_local.sh
```

### 2. Run Voice Interface (in another terminal)
```bash
# From the voice-scaffold root
./run_appointment_voice.sh
```

That's it! Start speaking to book appointments.

## What Can You Say?

- **"I need a dental cleaning tomorrow afternoon"**
- **"Can I see a dermatologist for a rash?"**
- **"Book me with a general practitioner next Wednesday morning"**
- **"Yes, 2 PM works for me. My name is John Smith"**

## Project Structure

```
voice-scaffold/
├── appointment_voice.py          # Voice interface (run this!)
├── run_appointment_voice.sh      # Launcher script
├── voice.py                      # STT/TTS wrapper (Deepgram)
├── cli.py                        # CLI utilities
└── appointment-scheduler/        # Backend system
    ├── backend/                  # FastAPI application
    │   ├── api/                  # Conversation endpoint
    │   ├── llm/                  # GPT-4o-mini integration
    │   ├── database/             # CSV-based storage
    │   └── services/             # Business logic
    ├── streamlit_app.py          # Text-based web UI
    └── tests/                    # Test suite
```

## How It Works

```
You speak → Deepgram STT → LLM Processing → Deepgram TTS → You hear response
              ↓                    ↓
         "I need a         Extract: specialty=dental
          dental cleaning   time=tomorrow afternoon
          tomorrow"              ↓
                          Search providers & slots
                                 ↓
                          "Dr. White has 1PM, 3PM..."
```

## Features

✅ **Natural Language Understanding** - Speak conversationally, no commands to memorize  
✅ **Smart Provider Matching** - Finds the best doctor based on specialty, location, ratings  
✅ **Temporal Awareness** - Understands "tomorrow", "next week", "Wednesday afternoon"  
✅ **Persistent Storage** - All appointments saved to CSV database  
✅ **Real-time Voice** - Fast transcription and response (~5-10 seconds)  
✅ **Dual Interface** - Use voice OR web chat (Streamlit)

## Requirements

### API Keys
- **Deepgram API Key** - For speech-to-text and text-to-speech
  ```bash
  export DEEPGRAM_API_KEY="your-key-here"
  ```

- **OpenAI API Key** - For LLM conversation (GPT-4o-mini)
  ```bash
  export OPENAI_API_KEY="your-key-here"
  ```

### Python Dependencies
```bash
# Voice dependencies (auto-installed by run script)
pip install pyaudio pydub simpleaudio

# Backend dependencies
cd appointment-scheduler
pip install -r requirements.txt
```

## Usage Examples

### Voice Interface
```bash
./run_appointment_voice.sh

🎤 VOICE APPOINTMENT SCHEDULER
═══════════════════════════════
▶ Press Enter to speak (or 'q' to quit): [Enter]

🎤 Listening...
📝 You said: "I need a dental cleaning tomorrow afternoon"
💭 Processing...
🤖 Assistant: Great! Dr. Amanda White has availability at 1 PM and 3 PM...
🔊 Speaking response...
```

### Web Chat Interface
```bash
cd appointment-scheduler
./run_streamlit.sh
# Opens browser at http://localhost:8501
```

## Architecture

### Voice Pipeline
```
┌──────────────────────────────────────────────────┐
│  appointment_voice.py                            │
│  ├── Record audio (PyAudio)                     │
│  ├── Transcribe (Deepgram Nova-3)               │
│  ├── Send to /api/conversation/                 │
│  └── Speak response (Deepgram Aura-2)           │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│  Backend (localhost:8000)                        │
│  ├── Conversation Manager (GPT-4o-mini)         │
│  ├── Function Calling (identify_provider, etc)  │
│  ├── CSV Database (providers.csv, schedules.csv)│
│  └── State Management (Redis-like)              │
└──────────────────────────────────────────────────┘
```

### Data Flow
1. **User speaks** → Audio recorded
2. **Deepgram STT** → Text transcription
3. **LLM Processing** → Intent extraction, function calls
4. **Database Query** → Find providers/slots
5. **Response Generation** → Natural language response
6. **Deepgram TTS** → Audio synthesis
7. **Playback** → User hears response

## Database

### Providers (12 healthcare professionals)
- **2 Dentists** - Dental cleanings, cavity fills
- **3 General Practitioners** - Check-ups, general health
- **2 Dermatologists** - Skin conditions, rashes
- **2 Cardiologists** - Heart health
- **2 Orthopedists** - Bone and joint issues
- **1 Psychiatrist** - Mental health

### Schedules
- **Sparse scheduling** - 3-5 slots per day per provider
- **Time preferences** - Morning (before 12 PM), Afternoon (12 PM+)
- **Auto-persistence** - Bookings immediately saved to CSV

## Configuration

### Voice Settings
Edit `appointment_voice.py`:
```python
# Recording duration
RECORD_SECONDS = 5      # Max duration

# Audio quality
RATE = 16000           # Sample rate (Hz)
CHANNELS = 1           # Mono

# Backend URL
API_BASE_URL = "http://localhost:8000"
```

### Voice Selection
Change TTS voice:
```python
# In appointment_voice.py
audio = self.voice.speak(
    assistant_text, 
    voice="aura-2-helios-en",  # Male voice
    play=True
)
```

Available voices:
- `aura-2-asteria-en` - Female, conversational (default)
- `aura-2-athena-en` - Female, warm
- `aura-2-helios-en` - Male, professional
- `aura-2-zeus-en` - Male, authoritative

### LLM Settings
Edit `appointment-scheduler/backend/llm/client.py`:
```python
model="gpt-4o-mini"     # Or gpt-4, gpt-3.5-turbo
temperature=0.7
```

## Troubleshooting

### "Backend is not running"
```bash
cd appointment-scheduler
./run_local.sh
```

### "Deepgram API key not found"
```bash
export DEEPGRAM_API_KEY="your-key"
```

### PyAudio installation issues
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### No audio input
- Check microphone permissions in System Preferences
- Test with: `python -c "import pyaudio; pyaudio.PyAudio()"`

### Audio playback issues
```bash
# Install ffmpeg (required for pydub)
brew install ffmpeg  # macOS
```

## Development

### Run Tests
```bash
cd appointment-scheduler
pytest tests/
```

### Run Backend Manually
```bash
cd appointment-scheduler
uvicorn backend.main:app --reload --port 8000
```

### View API Docs
Open http://localhost:8000/docs when backend is running

### Add New Providers
Edit `appointment-scheduler/backend/database/providers.csv`:
```csv
p013,Dr. New Provider,Cardiologist,15,4.9,New York
```

### Add New Specialties
Edit `appointment-scheduler/backend/models/constants.py`:
```python
SPECIALTIES = {
    "Neurologist": ["brain", "headache", "migraine", ...],
    # Add more...
}
```

## Testing Voice Integration

### Test STT
```python
from voice import Voice
voice = Voice()
# Record audio and save to file
with open("test.wav", "rb") as f:
    text = voice.listen(f.read())
    print(f"Transcribed: {text}")
```

### Test TTS
```python
from voice import Voice
voice = Voice()
audio = voice.speak("Hello! This is a test.", play=True)
```

### Test API
```bash
curl -X POST http://localhost:8000/api/conversation/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a dental cleaning"}'
```

## Documentation

- **[Appointment Scheduler README](appointment-scheduler/README.md)** - Backend details
- **[Voice Features](appointment-scheduler/VOICE_README.md)** - Detailed voice docs
- **[Streamlit UI](appointment-scheduler/STREAMLIT_README.md)** - Web interface guide
- **[Logging](appointment-scheduler/LOGGING_DOCUMENTATION.md)** - Debug logging

## Performance

- **Recording Latency**: Instant start
- **Transcription**: ~1-2 seconds (Deepgram Nova-3)
- **LLM Processing**: ~2-5 seconds (GPT-4o-mini)
- **TTS Generation**: ~1-2 seconds (Deepgram Aura-2)
- **Total**: ~5-10 seconds per interaction

## Security & Privacy

- ✅ API keys from environment (not hardcoded)
- ✅ Audio never stored permanently
- ✅ HTTPS communication with Deepgram
- ✅ No PHI logging (Protected Health Information)
- ✅ In-memory conversation state (cleared on exit)

## Limitations

- Single conversation at a time (no concurrent users)
- English language only (can be extended)
- Requires stable internet (for STT/TTS/LLM APIs)
- Mock data (not connected to real EHR systems)

## Future Enhancements

- [ ] Wake word detection ("Hey Assistant")
- [ ] Streaming responses (incremental TTS)
- [ ] Multi-language support
- [ ] Voice biometrics for patient verification
- [ ] WebSocket real-time streaming
- [ ] Integration with calendar systems
- [ ] SMS/Email confirmation

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review documentation in `appointment-scheduler/`
3. Open a GitHub issue with details

---

**Built with**: Python, FastAPI, OpenAI, Deepgram, Streamlit, PyAudio
