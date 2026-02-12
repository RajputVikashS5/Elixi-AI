import os
import re
from difflib import SequenceMatcher


class WakeWordDetector:
    """Simple wake word detector using text matching."""

    def __init__(self):
        self.wake_word = os.getenv("WAKE_WORD", "hey elixi").lower()
        self.sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.7"))

    def detect(self, text):
        """
        Detect if text contains the wake word.
        Returns True if wake word is detected with sufficient similarity.
        """
        if not text:
            return False

        text_lower = text.lower()
        cleaned = re.sub(r"[^\w\s]", "", text_lower)
        cleaned_wake_word = re.sub(r"[^\w\s]", "", self.wake_word)

        # First check: exact substring match
        if cleaned_wake_word in cleaned:
            return True

        # Second check: word-by-word matching
        text_words = cleaned.split()
        wake_words = cleaned_wake_word.split()

        # Check if all wake word parts are in the text
        if len(wake_words) > 0:
            # Match consecutive words or with some tolerance
            for i in range(len(text_words) - len(wake_words) + 1):
                window = " ".join(text_words[i:i + len(wake_words)])
                ratio = SequenceMatcher(None, window, cleaned_wake_word).ratio()
                if ratio >= self.sensitivity:
                    return True

        # Third check: overall similarity on cleaned text
        ratio = SequenceMatcher(None, cleaned, cleaned_wake_word).ratio()
        return ratio >= self.sensitivity

    def extract_command(self, text):
        """
        Extract the command after the wake word.
        Returns the text after the wake word.
        """
        text_lower = text.lower()
        if self.wake_word in text_lower:
            start_idx = text_lower.find(self.wake_word) + len(self.wake_word)
            return text[start_idx:].strip()
        return text.strip()
