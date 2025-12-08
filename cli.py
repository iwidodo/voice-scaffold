"""
Push-to-Talk CLI for Voice.

Hold SPACEBAR to record, release to process and hear response.

Usage:
    python cli.py              # Uses echo agent (default)
    python cli.py --llm        # Uses built-in OpenAI agent
    python cli.py --agent my_module:my_agent  # Uses your custom agent
"""

import argparse
import io
import os
import wave
import threading
from typing import Callable

import numpy as np
import sounddevice as sd
from pynput import keyboard

from voice import Voice


# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = np.int16


def record_audio_ptt() -> bytes:
    """
    Record audio while spacebar is held.
    Returns WAV bytes.
    """
    print("\n[Hold SPACEBAR to speak...]", end="", flush=True)

    recording = []
    is_recording = False
    stop_event = threading.Event()

    def on_press(key):
        nonlocal is_recording
        if key == keyboard.Key.space and not is_recording:
            is_recording = True
            print("\r[Recording... release to stop]", end="", flush=True)

    def on_release(key):
        nonlocal is_recording
        if key == keyboard.Key.space and is_recording:
            is_recording = False
            stop_event.set()
            return False  # Stop listener

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while not is_recording and not stop_event.is_set():
        sd.sleep(50)

    def audio_callback(indata, _frames, _time, _status):
        if is_recording:
            recording.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=audio_callback,
    ):
        stop_event.wait()

    listener.stop()

    if not recording:
        return b""

    audio_data = np.concatenate(recording)
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    return wav_buffer.getvalue()


def run_ptt_loop(agent_fn: Callable[[str], str]) -> None:
    """
    Run push-to-talk loop with any agent function.

    This is the main entry point for wiring up your agent to voice.

    Args:
        agent_fn: Any function with signature (text: str) -> str
                  Receives transcribed user speech, returns response to speak.

    Example:
        def my_agent(user_input: str) -> str:
            # Your LLM logic here
            return "Hello!"

        run_ptt_loop(my_agent)
    """
    voice = Voice()

    print("=" * 50)
    print("VOICE CLI - Push-to-Talk")
    print("=" * 50)
    print("Hold SPACEBAR to speak, release to get response.")
    print("Press Ctrl+C to exit.")
    print("=" * 50)

    while True:
        try:
            audio = record_audio_ptt()
            if not audio:
                print("\r[No audio captured]")
                continue

            print("\r[Transcribing...]       ", end="", flush=True)
            transcript = voice.listen(audio)

            if not transcript.strip():
                print("\r[No speech detected]    ")
                continue

            print(f"\r[You]: {transcript}")

            print("[Agent thinking...]", end="", flush=True)
            response = agent_fn(transcript)
            print(f"\r[Agent]: {response}")

            voice.speak(response, play=True)

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


# =============================================================================
# BUILT-IN AGENTS
# =============================================================================

def echo_agent(text: str) -> str:
    """Simple echo - repeats back what you said."""
    return f"You said: {text}"


def create_openai_agent(model: str = "gpt-4o-mini") -> Callable[[str], str]:
    """
    Create an OpenAI agent using the Responses API.

    The Responses API is stateful - it automatically maintains
    conversation history via previous_response_id.

    Requires: OPENAI_API_KEY environment variable
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI agent requires: uv add openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")

    client = OpenAI(api_key=api_key)
    state = {"previous_response_id": None}

    def agent(text: str) -> str:
        response = client.responses.create(
            model=model,
            input=text,
            previous_response_id=state["previous_response_id"],
        )
        state["previous_response_id"] = response.id
        return response.output_text

    return agent


def load_custom_agent(agent_path: str) -> Callable[[str], str]:
    """
    Load a custom agent from module:function path.

    Example: "my_agent:chat" loads chat() from my_agent.py
    """
    import importlib

    if ":" not in agent_path:
        raise ValueError(f"Use format module:function, got: {agent_path}")

    module_path, func_name = agent_path.rsplit(":", 1)
    module = importlib.import_module(module_path)

    if not hasattr(module, func_name):
        raise AttributeError(f"No function '{func_name}' in '{module_path}'")

    return getattr(module, func_name)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Voice CLI - Push-to-talk for agents")
    parser.add_argument("--llm", action="store_true", help="Use OpenAI agent")
    parser.add_argument("--agent", type=str, help="Custom agent as module:function")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model")

    args = parser.parse_args()

    if args.agent:
        print(f"Loading: {args.agent}")
        agent_fn = load_custom_agent(args.agent)
    elif args.llm:
        print(f"Using OpenAI ({args.model})")
        agent_fn = create_openai_agent(model=args.model)
    else:
        print("Echo mode (use --llm for OpenAI, --agent for custom)")
        agent_fn = echo_agent

    run_ptt_loop(agent_fn)


if __name__ == "__main__":
    main()
