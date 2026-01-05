#!/usr/bin/env python3
"""
Voice-enabled appointment scheduler.
Uses Voice class for STT/TTS with the appointment booking chatbot.
Run from the voice-scaffold root directory.
"""
import sys
import os
import requests
import pyaudio
import wave
from pathlib import Path

from voice import Voice

# Configuration
API_BASE_URL = "http://localhost:8000"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5  # Max recording duration


class VoiceAppointmentScheduler:
    """Voice-enabled appointment scheduler."""
    
    def __init__(self):
        """Initialize voice scheduler."""
        print("🎤 Initializing voice appointment scheduler...")
        self.voice = Voice()
        self.audio = pyaudio.PyAudio()
        self.conversation_id = None
        print("✓ Ready! Press Ctrl+C to exit.\n")
    
    def record_audio(self) -> bytes:
        """
        Record audio from microphone.
        
        Returns:
            WAV audio bytes
        """
        print("🎤 Listening... (speak now, will auto-detect silence)")
        
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        silent_chunks = 0
        started_speaking = False
        
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Simple volume detection
                volume = sum(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) 
                           for i in range(0, len(data), 2)) / (len(data) / 2)
                
                if volume > 300:  # Speaking detected (lowered from 500 for more sensitivity)
                    started_speaking = True
                    silent_chunks = 0
                elif started_speaking:
                    silent_chunks += 1
                    if silent_chunks > 100:  # About 5 seconds of silence for longer pauses
                        break
                
                # Max recording time safety
                if len(frames) > (RATE * RECORD_SECONDS) / CHUNK:
                    break
        
        finally:
            stream.stop_stream()
            stream.close()
        
        print("✓ Recording complete")
        
        # Convert to WAV bytes
        import io
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        return wav_buffer.getvalue()
    
    def send_message(self, message: str) -> dict:
        """
        Send message to appointment API.
        
        Args:
            message: User message text
            
        Returns:
            API response dictionary
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/conversation/",
                json={
                    "message": message,
                    "conversation_id": self.conversation_id
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend. Is it running on http://localhost:8000?"}
        except Exception as e:
            return {"error": str(e)}
    
    def run(self):
        """Run the voice conversation loop."""
        print("=" * 60)
        print("🏥 VOICE APPOINTMENT SCHEDULER")
        print("=" * 60)
        print("\nHow it works:")
        print("1. Press Enter to start recording")
        print("2. Speak your request")
        print("3. System will transcribe and respond")
        print("4. Listen to the response")
        print("5. Type 'q' to quit, or press Enter to continue")
        print("=" * 60 + "\n")
        
        try:
            while True:
                # Wait for user to start
                user_input = input("\n▶ Press Enter to speak (or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("\n👋 Goodbye!")
                    break
                
                # Record audio
                audio_bytes = self.record_audio()
                
                # Transcribe
                print("🔄 Transcribing...")
                user_text = self.voice.listen(audio_bytes)
                
                if not user_text:
                    print("❌ Couldn't understand. Please try again.")
                    continue
                
                print(f"📝 You said: \"{user_text}\"")
                
                # Send to API
                print("💭 Processing...")
                response_data = self.send_message(user_text)
                
                if "error" in response_data:
                    print(f"❌ Error: {response_data['error']}")
                    continue
                
                # Update conversation ID
                if response_data.get("conversation_id"):
                    self.conversation_id = response_data["conversation_id"]
                
                # Get assistant response
                assistant_text = response_data.get("response", "I'm sorry, I couldn't process that.")
                print(f"\n🤖 Assistant: {assistant_text}")
                
                # Show state and suggestions
                if response_data.get("state"):
                    print(f"   (State: {response_data['state']})")
                
                if response_data.get("suggested_actions"):
                    print("\n💡 Suggestions:")
                    for action in response_data["suggested_actions"]:
                        print(f"   • {action}")
                
                # Speak response
                print("\n🔊 Speaking response...")
                audio = self.voice.speak(assistant_text, play=True)
                print("✓ Done")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up audio resources."""
        print("\n🧹 Cleaning up...")
        self.audio.terminate()
        print("✓ Goodbye!")


def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Main entry point."""
    # Check backend
    if not check_backend():
        print("❌ Backend server is not running!")
        print("Please start it with: cd appointment-scheduler && ./run_local.sh")
        sys.exit(1)
    
    # Run voice scheduler
    scheduler = VoiceAppointmentScheduler()
    scheduler.run()


if __name__ == "__main__":
    main()
