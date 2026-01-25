"""
Transcription Service for Demerzel
Primary: Deepgram (cloud, high accuracy, real-time)
Fallback: Vosk (offline, always available)

January 19, 2026: Initial implementation
"""

import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

# Vosk is the existing dependency - always available
from vosk import Model, KaldiRecognizer

# Try Deepgram (SDK v5.x has different API)
try:
    from deepgram import DeepgramClient
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False
    DeepgramClient = None
    print("[TRANSCRIPTION] deepgram-sdk not installed - using Vosk only")


@dataclass
class TranscriptionResult:
    """Result of a transcription operation"""
    text: str
    is_final: bool
    confidence: float
    backend: str  # "deepgram" or "vosk"


class TranscriptionService:
    """
    Multi-backend transcription service for Demerzel

    Deepgram provides:
    - High accuracy cloud transcription
    - Support for multiple languages
    - Better handling of noisy audio

    Vosk provides:
    - Offline transcription (no internet needed)
    - Always available fallback
    - Lower latency for local processing

    Usage:
        service = get_transcription_service()
        result = service.transcribe_chunk(audio_bytes)
        if result and result.is_final:
            print(f"Transcription: {result.text}")
    """

    VOSK_MODEL_PATH = str(Path.home() / "vosk-model-en-us-0.22")
    SAMPLE_RATE = 16000

    def __init__(self):
        self.deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        self.deepgram_available = bool(self.deepgram_key) and DEEPGRAM_AVAILABLE

        # Initialize Deepgram (SDK v5.x reads DEEPGRAM_API_KEY from env automatically)
        if self.deepgram_available:
            try:
                self.deepgram_client = DeepgramClient()  # Uses env var
                print("[TRANSCRIPTION] Deepgram initialized (SDK v5.x)")
            except Exception as e:
                print(f"[TRANSCRIPTION] Deepgram init failed: {e}")
                self.deepgram_available = False
                self.deepgram_client = None
        else:
            self.deepgram_client = None
            if not DEEPGRAM_AVAILABLE:
                print("[TRANSCRIPTION] Using Vosk only (Deepgram not installed)")
            elif not self.deepgram_key:
                print("[TRANSCRIPTION] Using Vosk only (DEEPGRAM_API_KEY not set)")

        # Always initialize Vosk as fallback
        self.vosk_model = None
        self.vosk_recognizer = None
        self._init_vosk()

        # Backend preference
        self.prefer_deepgram = self.deepgram_available

    def _init_vosk(self):
        """Initialize Vosk model"""
        if Path(self.VOSK_MODEL_PATH).exists():
            try:
                self.vosk_model = Model(self.VOSK_MODEL_PATH)
                self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.SAMPLE_RATE)
                self.vosk_recognizer.SetMaxAlternatives(0)
                self.vosk_recognizer.SetWords(False)
                print(f"[TRANSCRIPTION] Vosk initialized from {self.VOSK_MODEL_PATH}")
            except Exception as e:
                print(f"[TRANSCRIPTION] Vosk init failed: {e}")
                self.vosk_model = None
                self.vosk_recognizer = None
        else:
            print(f"[TRANSCRIPTION] WARNING: Vosk model not found at {self.VOSK_MODEL_PATH}")

    def transcribe_chunk(self, audio_chunk: bytes) -> Optional[TranscriptionResult]:
        """
        Process a single audio chunk.
        Returns TranscriptionResult if speech detected, None otherwise.

        Uses Vosk for real-time streaming (Deepgram is better for complete audio files).
        """
        # For streaming, always use Vosk (lower latency, local processing)
        return self._vosk_chunk(audio_chunk)

    def _vosk_chunk(self, audio_chunk: bytes) -> Optional[TranscriptionResult]:
        """Process chunk with Vosk"""
        if not self.vosk_recognizer:
            return None

        try:
            if self.vosk_recognizer.AcceptWaveform(audio_chunk):
                result = json.loads(self.vosk_recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    return TranscriptionResult(
                        text=text,
                        is_final=True,
                        confidence=1.0,  # Vosk doesn't provide confidence
                        backend="vosk"
                    )
            else:
                # Check partial
                partial = json.loads(self.vosk_recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    return TranscriptionResult(
                        text=partial_text,
                        is_final=False,
                        confidence=0.5,
                        backend="vosk"
                    )
        except Exception as e:
            print(f"[TRANSCRIPTION] Vosk error: {e}")

        return None

    def transcribe_audio_file(self, audio_data: bytes, mimetype: str = "audio/wav") -> Optional[TranscriptionResult]:
        """
        Transcribe a complete audio file using Deepgram (if available).

        Args:
            audio_data: Raw audio bytes
            mimetype: Audio format (audio/wav, audio/mp3, etc.)

        Returns:
            TranscriptionResult or None
        """
        if self.prefer_deepgram and self.deepgram_available:
            return self._deepgram_transcribe(audio_data, mimetype)

        # Fallback: can't easily transcribe file with Vosk without streaming
        print("[TRANSCRIPTION] File transcription requires Deepgram")
        return None

    def _deepgram_transcribe(self, audio_data: bytes, mimetype: str) -> Optional[TranscriptionResult]:
        """Transcribe using Deepgram prerecorded API (SDK v5.x)"""
        try:
            # SDK v5.x API
            source = {"buffer": audio_data, "mimetype": mimetype}
            options = {"model": "nova-2", "language": "en", "smart_format": True, "punctuate": True}

            response = self.deepgram_client.listen.rest.v("1").transcribe_file(source, options)

            # Extract transcript from response
            if hasattr(response, 'results'):
                channels = response.results.channels
                if channels and channels[0].alternatives:
                    alt = channels[0].alternatives[0]
                    return TranscriptionResult(
                        text=alt.transcript,
                        is_final=True,
                        confidence=getattr(alt, 'confidence', 0.9),
                        backend="deepgram"
                    )

        except Exception as e:
            print(f"[TRANSCRIPTION] Deepgram error: {e}")
            # Disable to avoid repeated errors
            self.prefer_deepgram = False

        return None

    def reset(self):
        """Reset recognizer state (call after processing complete utterance)"""
        if self.vosk_recognizer:
            try:
                self.vosk_recognizer.Reset()
            except Exception:
                pass

    def get_vosk_recognizer(self) -> Optional[KaldiRecognizer]:
        """Get raw Vosk recognizer for backward compatibility with brain_controller.py"""
        return self.vosk_recognizer

    def get_vosk_model(self) -> Optional[Model]:
        """Get raw Vosk model"""
        return self.vosk_model

    def recreate_vosk_recognizer(self) -> Optional[KaldiRecognizer]:
        """Recreate Vosk recognizer (useful after long pauses or errors)"""
        if self.vosk_model:
            try:
                self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.SAMPLE_RATE)
                self.vosk_recognizer.SetMaxAlternatives(0)
                self.vosk_recognizer.SetWords(False)
                print("[TRANSCRIPTION] Vosk recognizer recreated")
                return self.vosk_recognizer
            except Exception as e:
                print(f"[TRANSCRIPTION] Failed to recreate recognizer: {e}")
        return None

    def set_deepgram_enabled(self, enabled: bool) -> None:
        """Enable/disable Deepgram (force Vosk fallback)"""
        if enabled and self.deepgram_available:
            self.prefer_deepgram = True
            print("[TRANSCRIPTION] Deepgram enabled")
        else:
            self.prefer_deepgram = False
            print("[TRANSCRIPTION] Deepgram disabled, using Vosk")


# Singleton
_transcription_service = None

def get_transcription_service() -> TranscriptionService:
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
