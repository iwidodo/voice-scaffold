#!/bin/bash
# Voice Appointment Scheduler Launcher
# Run from voice-scaffold root directory

set -e

echo "🎤 Voice Appointment Scheduler"
echo "================================"

# Check if backend is running
echo "Checking backend server..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend server is not running!"
    echo ""
    echo "Please start it in another terminal:"
    echo "  cd appointment-scheduler"
    echo "  ./run_local.sh"
    exit 1
fi
echo "✓ Backend is running"

# Check for required dependencies
echo "Checking dependencies..."
MISSING_DEPS=()

if ! python3 -c "import pyaudio" 2>/dev/null; then
    MISSING_DEPS+=("pyaudio")
fi

if ! python3 -c "import pydub" 2>/dev/null; then
    MISSING_DEPS+=("pydub")
fi

if ! python3 -c "import simpleaudio" 2>/dev/null; then
    MISSING_DEPS+=("simpleaudio")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Missing dependencies: ${MISSING_DEPS[*]}"
    echo "Installing..."
    pip install "${MISSING_DEPS[@]}"
fi
echo "✓ All dependencies installed"

# Load .env file if it exists (try both locations)
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✓ Loaded .env from root directory"
elif [ -f "appointment-scheduler/.env" ]; then
    export $(grep -v '^#' appointment-scheduler/.env | xargs)
    echo "✓ Loaded .env from appointment-scheduler directory"
fi

# Check for Deepgram API key
if [ -z "$DEEPGRAM_API_KEY" ]; then
    echo "⚠️  DEEPGRAM_API_KEY not set"
    echo "Please add it to appointment-scheduler/.env or export it:"
    echo "  export DEEPGRAM_API_KEY='your-key'"
    exit 1
fi
echo "✓ Deepgram API key found"

echo ""
echo "Starting voice appointment scheduler..."
echo "Press Ctrl+C to exit"
echo ""

# Run the voice chat
python3 appointment_voice.py
