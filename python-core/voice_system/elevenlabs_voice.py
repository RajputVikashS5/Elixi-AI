import os
import base64
from elevenlabs import ElevenLabs, VoiceSettings
from elevenlabs.client import ElevenLabs as ElevenLabsClient


class ElevenLabsVoice:
    """ElevenLabs Speech-to-Text and Text-to-Speech integration."""

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")
        
        self.client = None
        if self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] ElevenLabs client init failed: {e}")

    def is_configured(self):
        """Check if ElevenLabs is properly configured."""
        return self.client is not None and self.api_key is not None

    def text_to_speech(self, text, voice_id=None, model_id=None):
        """
        Convert text to speech using ElevenLabs.
        Args:
            text: Text to convert
            voice_id: Optional override voice ID
            model_id: Optional override model ID
        Returns:
            Base64-encoded MP3 audio bytes
        """
        if not self.is_configured():
            return None

        try:
            voice_id = voice_id or self.voice_id
            model_id = model_id or self.model_id

            response = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id=model_id,
                text=text,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.7,
                    use_speaker_boost=True
                ),
            )

            # Convert generator response to bytes
            audio_bytes = b""
            for chunk in response:
                audio_bytes += chunk

            return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            print(f"[Error] TTS failed: {e}")
            return None

    def get_voices(self):
        """
        Fetch available voices from ElevenLabs.
        Returns:
            List of voice configurations
        """
        if not self.is_configured():
            return []

        try:
            response = self.client.voices.get_all()
            voices = []
            for voice in response.voices:
                voices.append({
                    "id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "preview_url": voice.preview_url if hasattr(voice, 'preview_url') else None
                })
            return voices
        except Exception as e:
            print(f"[Error] Fetching voices failed: {e}")
            return []

    def generate_speech(self, text, voice_id=None, model_id=None):
        """
        Alias for text_to_speech() - Generate speech from text.
        Args:
            text: Text to convert to speech
            voice_id: Optional override voice ID
            model_id: Optional override model ID
        Returns:
            Base64-encoded audio or None if failed
        """
        return self.text_to_speech(text, voice_id, model_id)

    def get_voice_settings(self):
        """Get current voice settings."""
        return {
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "api_key_set": bool(self.api_key)
        }
