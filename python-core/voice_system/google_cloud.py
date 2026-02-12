import os
from io import BytesIO
from google.cloud import speech_v1
from google.cloud import texttospeech_v1
import base64


class GoogleCloudVoice:
    """Google Cloud Speech-to-Text and Text-to-Speech integration."""

    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        self.stt_client = None
        self.tts_client = None

        if self.credentials_path and os.path.exists(self.credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            try:
                self.stt_client = speech_v1.SpeechClient()
                self.tts_client = texttospeech_v1.TextToSpeechClient()
            except Exception as e:
                print(f"[Warning] Google Cloud voice not available: {e}")

    def is_configured(self):
        """Check if Google Cloud voice is properly configured."""
        return self.stt_client is not None and self.tts_client is not None

    def speech_to_text(self, audio_bytes, language_code="en-US"):
        """
        Convert audio bytes to text using Google Cloud STT.
        Args:
            audio_bytes: Raw audio data
            language_code: Language code (default: en-US)
        Returns:
            Transcribed text string
        """
        if not self.is_configured():
            return None

        try:
            audio = speech_v1.RecognitionAudio(content=audio_bytes)
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
            )

            response = self.stt_client.recognize(config=config, audio=audio)

            if response.results:
                return response.results[0].alternatives[0].transcript
            return None
        except Exception as e:
            print(f"[Error] STT failed: {e}")
            return None

    def text_to_speech(self, text, language_code="en-US", voice_name="en-US-Neural2-C"):
        """
        Convert text to speech using Google Cloud TTS.
        Args:
            text: Text to convert
            language_code: Language code (default: en-US)
            voice_name: Voice name (default: en-US-Neural2-C)
        Returns:
            Base64-encoded audio bytes
        """
        if not self.is_configured():
            return None

        try:
            synthesis_input = texttospeech_v1.SynthesisInput(text=text)
            voice = texttospeech_v1.VoiceSelectionParams(
                language_code=language_code, name=voice_name
            )
            audio_config = texttospeech_v1.AudioConfig(
                audio_encoding=texttospeech_v1.AudioEncoding.MP3
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            return base64.b64encode(response.audio_content).decode("utf-8")
        except Exception as e:
            print(f"[Error] TTS failed: {e}")
            return None
