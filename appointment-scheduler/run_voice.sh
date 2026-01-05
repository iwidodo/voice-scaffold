#!/bin/bash
# Voice chat runner for appointment scheduler

echo "🎤 Voice Appointment Scheduler Setup"
echo "======================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo "Please start it in another terminal with: ./run_local.sh"
    exit 1
fi

echo "✓ Backend is running"
echo ""

# Check for required dependencies
if ! python -c "import pyaudio" 2>/dev/null; then
    echo "📦 Installing voice dependencies..."
    pip install pyaudio pydub simpleaudio 2>&1 | grep -v "Requirement already satisfied" || true
fi

echo ""
echo "🎤 Starting voice chat..."
echo ""

# Run voice chat
python voice_chat.py
