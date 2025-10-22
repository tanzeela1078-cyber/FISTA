#!/usr/bin/env python3
"""
client.py — Live bilingual voice translator using translator.py Agent
Uses speech recognition + TTS and the modern 2025 agents MCP connection.
"""

import asyncio
import sys
import os
import speech_recognition as sr
from gtts import gTTS
import tempfile

# Import the translator agent runner
from translator import run_agent_interaction

def speak_text(text: str, lang: str = "en"):
    """Speak text using gTTS"""
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        filename = fp.name + ".mp3"
        tts.save(filename)
        if sys.platform.startswith("win"):
            os.system(f"start {filename}")
        elif sys.platform.startswith("darwin"):
            os.system(f"afplay {filename}")
        else:
            os.system(f"mpg123 {filename}")

async def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Live bilingual translator started. Say 'exit' to quit.")

    # Launch the translator Agent in background
    agent_task = asyncio.create_task(run_agent_interaction())

    await asyncio.sleep(1)  # Give the Agent time to start MCP server

    while True:
        with mic as source:
            print("\n🎙 Speak now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio, try again.")
            continue

        text = text.strip()
        if text.lower() == "exit":
            print("👋 Exiting translator.")
            agent_task.cancel()
            break

        # Detect language (rough heuristic)
        is_english = all(ord(c) < 128 for c in text)
        source_lang = "English" if is_english else "Japanese"
        target_lang = "Japanese" if is_english else "English"
        tts_lang = "ja" if is_english else "en"

        # Prepare instruction for Agent
        instruction = f"Translate '{text}' from {source_lang} to {target_lang}."

        print(f"🔄 Sending to Agent: {instruction}")

        # Run agent interaction for this single input
        # `run_agent_interaction` in translator.py can accept initial_input dynamically
        from translator import run_agent_interaction as agent_runner

        async def single_run():
            # Monkey-patch initial_input
            from translator import run_agent_interaction as base_runner
            # we override initial_input temporarily
            base_runner_initial_input = instruction
            return await base_runner()  # it will use the dynamic input

        # Actually, simplest: just call translator.py via subprocess for live demo
        # Or modify translator.py to accept `initial_input` as argument (recommended)
        # For now, we'll simulate:
        print(f"💬 Translated (simulated call): {text[::-1]}")  # replace with actual Agent call
        speak_text(text[::-1], lang=tts_lang)  # replace with actual translation output

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
