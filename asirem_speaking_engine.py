"""aSiReM Speaking Engine stub — uses pyttsx3 if available, else silent."""
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class SpeakingConfig:
    reference_audio: str = ""
    voice_model: str = "default"

class ASiREMSpeakingEngine:
    def __init__(self, config: SpeakingConfig):
        self.config = config
        self._callback: Optional[Callable] = None
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 165)
        except Exception:
            pass
    
    def set_callback(self, callback: Callable):
        self._callback = callback
    
    async def speak(self, text: str):
        print(f"[aSiReM TTS] {text}")
        if self._engine:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                print(f"[aSiReM TTS] Engine error: {e}")
