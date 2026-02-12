#!/usr/bin/env python3
"""Test ElevenLabs voice integration"""

import os
from voice_system.elevenlabs_voice import ElevenLabsVoice
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs():
    print("\n=== ElevenLabs Configuration Test ===\n")
    
    elevenlabs = ElevenLabsVoice()
    
    # Check configuration
    api_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"API Key Set: {bool(api_key)}")
    if api_key:
        print(f"  (First 20 chars: {api_key[:20]}...)")
    
    print(f"Voice ID: {elevenlabs.voice_id}")
    print(f"Model ID: {elevenlabs.model_id}")
    print(f"Is Configured: {elevenlabs.is_configured()}")
    
    # Try to get voices if configured
    if elevenlabs.is_configured():
        print("\nFetching available voices...")
        try:
            voices = elevenlabs.get_voices()
            print(f"✓ Found {len(voices)} voices")
            for voice in voices[:5]:
                print(f"  - {voice['name']} (ID: {voice['id']})")
            if len(voices) > 5:
                print(f"  ... and {len(voices) - 5} more")
        except Exception as e:
            print(f"✗ Error fetching voices: {e}")
        
        # Test TTS
        print("\nTesting Text-to-Speech...")
        try:
            text = "Hello. I am ELIXI, your personal AI assistant."
            audio = elevenlabs.text_to_speech(text)
            if audio:
                print(f"✓ TTS successful (audio length: {len(audio)} chars)")
            else:
                print("✗ TTS failed to generate audio")
        except Exception as e:
            print(f"✗ TTS error: {e}")
    else:
        print("\n✗ ElevenLabs not configured. Set ELEVENLABS_API_KEY in .env to use this service.")

if __name__ == "__main__":
    test_elevenlabs()
