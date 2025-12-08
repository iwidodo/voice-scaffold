"""
Voice - A minimal STT/TTS wrapper for voice-enabled agents.

Usage:
    from voice import Voice

    voice = Voice()  # Uses DEEPGRAM_API_KEY from environment

    # Speech-to-Text
    text = voice.listen(audio_bytes)

    # Text-to-Speech
    audio = voice.speak("Hello!")
    voice.speak("Hello!", play=True)  # Play through speakers
"""

import os
import io
from typing import Optional

from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()


class Voice:
    """
    Simple voice I/O wrapper using Deepgram.

    Two methods:
        - listen(audio_bytes) -> str  (STT)
        - speak(text) -> bytes         (TTS)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Voice with Deepgram API key.

        Args:
            api_key: Deepgram API key. If not provided, uses DEEPGRAM_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Deepgram API key required. Set DEEPGRAM_API_KEY environment variable "
                "or pass api_key to Voice()."
            )
        # SDK v5 auto-discovers DEEPGRAM_API_KEY from env, but we pass explicitly
        self._client = DeepgramClient(api_key=self._api_key)

    def listen(self, audio_bytes: bytes, mimetype: str = "audio/wav") -> str:
        """
        Transcribe audio to text (Speech-to-Text).

        Args:
            audio_bytes: Raw audio data.
            mimetype: Audio format - audio/wav, audio/webm, audio/mp3, etc.

        Returns:
            Transcribed text string.
        """
        if not audio_bytes:
            return ""

        # SDK v5 API: client.listen.v1.media.transcribe_file()
        response = self._client.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3",
        )

        try:
            return response.results.channels[0].alternatives[0].transcript
        except (AttributeError, IndexError):
            return ""

    def speak(
        self,
        text: str,
        voice: str = "aura-2-asteria-en",
        play: bool = False,
    ) -> bytes:
        """
        Convert text to speech (Text-to-Speech).

        Args:
            text: Text to synthesize.
            voice: Deepgram voice model (default: aura-2-asteria-en).
            play: If True, play audio through speakers.

        Returns:
            MP3 audio bytes.
        """
        if not text:
            return b""

        # Deepgram TTS has 2000 char limit - chunk if needed
        chunks = self._chunk_text(text, max_chars=2000)
        audio_parts = []

        # SDK v5 API: client.speak.v1.audio.generate()
        for chunk in chunks:
            response = self._client.speak.v1.audio.generate(
                text=chunk,
                model=voice,
            )
            # Handle both stream object and generator responses
            if hasattr(response, 'stream') and hasattr(response.stream, 'getvalue'):
                audio_parts.append(response.stream.getvalue())
            elif hasattr(response, 'stream'):
                # If stream is a generator, collect all bytes
                audio_parts.append(b"".join(response.stream))
            else:
                # Response itself might be iterable
                audio_parts.append(b"".join(response))

        audio_bytes = b"".join(audio_parts)

        if play:
            self._play_audio(audio_bytes)

        return audio_bytes

    def _chunk_text(self, text: str, max_chars: int = 2000) -> list[str]:
        """Split text into chunks at sentence boundaries."""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        current = ""

        # Split by sentences (rough heuristic)
        sentences = text.replace("! ", ".|").replace("? ", ".|").replace(". ", ".|").split("|")

        for sentence in sentences:
            if len(current) + len(sentence) <= max_chars:
                current += sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence

        if current:
            chunks.append(current.strip())

        return chunks if chunks else [text[:max_chars]]

    def _play_audio(self, audio_bytes: bytes) -> None:
        """Play MP3 audio through speakers."""
        try:
            from pydub import AudioSegment
            import simpleaudio as sa

            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            play_obj = sa.play_buffer(
                audio.raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate,
            )
            play_obj.wait_done()
        except ImportError:
            raise ImportError(
                "Audio playback requires pydub and simpleaudio. "
                "Install with: pip install pydub simpleaudio"
            )
