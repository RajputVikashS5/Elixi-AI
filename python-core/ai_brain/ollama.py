import os
import requests
from typing import Optional


class OllamaAIBrain:
    """Ollama integration for offline AI brain."""

    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        self.timeout = self._get_timeout()

    def _get_timeout(self) -> int:
        value = os.getenv("OLLAMA_TIMEOUT", "8")
        try:
            parsed = int(value)
            return parsed if parsed > 0 else 8
        except ValueError:
            return 8

    def is_available(self):
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name", "").startswith(self.model) for m in models)
            return False
        except Exception as e:
            print(f"[Warning] Ollama not available: {e}")
            return False

    def generate_reply(self, prompt: str, context: str = "", timeout: Optional[int] = None) -> Optional[str]:
        """
        Generate a reply using Ollama.
        Args:
            prompt: User's input text
            context: Optional context from memories
        Returns:
            Generated reply text
        """
        try:
            full_prompt = f"{context}\n\nUser: {prompt}\nAssistant:"

            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=timeout or self.timeout,
            )

            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return None
        except Exception as e:
            print(f"[Error] Ollama generation failed: {e}")
            return None

    def summarize(self, text: str, max_length: int = 100) -> Optional[str]:
        """
        Summarize text using Ollama.
        Args:
            text: Text to summarize
            max_length: Max length of summary
        Returns:
            Summarized text
        """
        prompt = f"Summarize the following in {max_length} words: {text}"
        return self.generate_reply(prompt)
