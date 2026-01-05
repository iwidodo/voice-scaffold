# Voice Scaffold

Minimal voice I/O wrapper for agent engineering interviews. Add voice to any agent in minutes.

## What's Included

### 1. Voice Scaffold (Root)
Simple voice I/O wrapper for adding speech-to-text and text-to-speech to any agent.

### 2. Appointment Scheduler ([`appointment-scheduler/`](appointment-scheduler/))
**Complete LLM-powered appointment scheduling system** - a reference implementation showing:
- Multi-turn conversation with OpenAI function calling
- Provider matching based on health issues
- Schedule management and availability checking
- Appointment creation with .ics calendar file generation
- RESTful API with FastAPI
- Comprehensive test suite

See [`appointment-scheduler/README.md`](appointment-scheduler/README.md) for full documentation.

---

## What This Does

```
[You speak] → STT → [Your Agent] → TTS → [You hear response]
```

You provide the agent logic (the middle part). We handle the voice.

## Setup

```bash
uv sync
export DEEPGRAM_API_KEY="your-key"      # Required - for STT/TTS
export OPENAI_API_KEY="your-key"        # Optional - only for --llm mode
```

Or add to `.env`:
```
DEEPGRAM_API_KEY="your-deepgram-key"
OPENAI_API_KEY="your-openai-key"
```

## Quick Start

```bash
# Echo mode - just test the voice pipeline
uv run python cli.py

# With OpenAI - test a real conversation
export OPENAI_API_KEY="your-key"
uv run python cli.py --llm

# With your custom agent
uv run python cli.py --agent my_agent:chat
```

**How it works:**
1. Hold **SPACEBAR** → speak
2. Release → your agent receives the transcript
3. Agent responds → you hear it
4. Repeat

---

## Wire Up Your Agent

### Option 1: Pass a function to `run_ptt_loop`

Create any file (e.g., `my_agent.py`):

```python
from cli import run_ptt_loop

def my_agent(user_input: str) -> str:
    """
    Your agent logic here.

    Args:
        user_input: What the user said (transcribed)

    Returns:
        What your agent says back (will be spoken)
    """
    # Example: call your LLM
    response = your_llm.chat(user_input)
    return response

if __name__ == "__main__":
    run_ptt_loop(my_agent)
```

Then run:
```bash
uv run python my_agent.py
```

### Option 2: Use the CLI with `--agent`

```python
# my_agent.py
def chat(text: str) -> str:
    return your_llm.respond(text)
```

```bash
uv run python cli.py --agent my_agent:chat
```

### Option 3: Use the Voice class directly

For full control (custom interfaces, web apps, etc.):

```python
from voice import Voice

voice = Voice()

# Speech-to-Text
transcript = voice.listen(audio_bytes)

# Text-to-Speech
audio = voice.speak("Hello!")

# Or play directly
voice.speak("Hello!", play=True)
```

---

## How `run_ptt_loop` Works

```python
def run_ptt_loop(agent_fn):
    """
    Main loop:
    1. Wait for spacebar press
    2. Record audio while held
    3. Transcribe (STT)
    4. Call your agent_fn(transcript)
    5. Speak the response (TTS)
    6. Repeat
    """
```

Your agent function just needs this signature:

```python
def my_agent(text: str) -> str:
    # text = what user said
    # return = what to say back
```

That's it. The scaffold handles everything else.

---

## Multi-turn Conversations

The scaffold is stateless - each turn is independent. Your agent manages conversation history:

```python
from cli import run_ptt_loop

history = []

def my_agent(text: str) -> str:
    history.append({"role": "user", "content": text})

    response = your_llm.chat(messages=history)

    history.append({"role": "assistant", "content": response})
    return response

run_ptt_loop(my_agent)
```

Or use OpenAI's Responses API which handles state automatically:

```python
from openai import OpenAI

client = OpenAI()
prev_id = None

def my_agent(text: str) -> str:
    global prev_id
    response = client.responses.create(
        model="gpt-4o-mini",
        input=text,
        previous_response_id=prev_id,
    )
    prev_id = response.id
    return response.output_text
```

---

## Built-in Agents

### Echo Agent (default)
```bash
uv run python cli.py
```
Just repeats back what you said. Good for testing the voice pipeline.

### OpenAI Agent
```bash
export OPENAI_API_KEY="your-key"
uv run python cli.py --llm
uv run python cli.py --llm --model gpt-4o  # different model
```
Uses OpenAI Responses API with automatic conversation history.

---

## Other Integration Examples

### FastAPI Server

```python
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from voice import Voice

app = FastAPI()
voice = Voice()

@app.post("/chat")
async def chat(audio: UploadFile):
    transcript = voice.listen(await audio.read())
    response = my_agent(transcript)
    return Response(content=voice.speak(response), media_type="audio/mpeg")
```

### WebSocket

```python
from voice import Voice

voice = Voice()

async def handle_audio(websocket, data):
    text = voice.listen(data)
    response = my_agent(text)
    await websocket.send(voice.speak(response))
```

---

## API Reference

### Voice Class

| Method | Input | Output |
|--------|-------|--------|
| `Voice(api_key=None)` | Optional Deepgram key | Voice instance |
| `voice.listen(audio_bytes)` | WAV/MP3/WebM bytes | Transcribed text |
| `voice.speak(text)` | String | MP3 audio bytes |
| `voice.speak(text, play=True)` | String | Plays through speakers |

### CLI

| Command | Description |
|---------|-------------|
| `python cli.py` | Echo mode |
| `python cli.py --llm` | OpenAI agent |
| `python cli.py --agent module:func` | Custom agent |
| `python cli.py --model gpt-4o` | Specify model for --llm |

---

## Voices

Default: `aura-2-asteria-en`

```python
voice.speak("Hello!", voice="aura-2-apollo-en")  # masculine
voice.speak("Hello!", voice="aura-2-thalia-en")  # different style
```

See [Deepgram TTS Models](https://developers.deepgram.com/docs/tts-models) for full list.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPGRAM_API_KEY` | Yes | For STT/TTS |
| `OPENAI_API_KEY` | Only for --llm | For built-in OpenAI agent |

---

## Troubleshooting

### macOS Accessibility Warning
If you see "This process is not trusted", grant Terminal accessibility permissions:
**System Settings → Privacy & Security → Accessibility → Add Terminal**

### No audio captured
Make sure your microphone is working and permissions are granted.

### TTS not playing
Install ffmpeg for pydub: `brew install ffmpeg` (macOS)

---

## Appointment Scheduler Example

The [`appointment-scheduler/`](appointment-scheduler/) directory contains a complete reference implementation of an LLM-powered appointment scheduling system.

### Features

- **LLM-Powered Conversations**: Multi-turn conversations using OpenAI function calling
- **Smart Provider Matching**: Automatically matches health issues to appropriate medical specialists
- **Schedule Management**: Real-time availability checking and booking
- **Calendar Integration**: Generates .ics files for calendar imports
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Full Test Coverage**: 39+ tests covering all components

### Quick Start

```bash
cd appointment-scheduler

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run examples
python example_usage.py

# Start the API server
./run_local.sh
# API docs at http://localhost:8000/docs
```

### Example Usage

```python
# Provider matching
from backend.llm.provider_matcher import match_provider_for_issue

match = match_provider_for_issue("I have a rash")
# → Dr. Sarah Johnson (Dermatologist)

# Create appointment
appointment_data = {
    "patient_name": "John Doe",
    "provider_id": "p001",
    "date": "2026-01-20",
    "time": "10:00",
    "reason": "Skin checkup"
}
# Returns appointment with .ics calendar file
```

### Architecture

- **Backend**: FastAPI with Pydantic validation
- **LLM**: OpenAI GPT-4o-mini with function calling
- **Data**: Mock providers and schedules (easily replaceable)
- **Testing**: pytest with comprehensive coverage

See the [full documentation](appointment-scheduler/README.md) for detailed API reference, conversation flows, and integration examples.

---

## Future Integration

The appointment scheduler is designed as a standalone API that can be integrated with the voice scaffold:

```python
from cli import run_ptt_loop
from appointment_scheduler_agent import chat  # Your integration

run_ptt_loop(chat)  # Voice-enabled appointment booking!
```

This demonstrates the full stack: voice I/O → LLM agent → business logic → structured output.
