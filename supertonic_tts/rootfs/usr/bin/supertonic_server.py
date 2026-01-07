#!/usr/bin/env python3
"""
Supertonic2 TTS Wyoming Server for Home Assistant
Provides text-to-speech via Wyoming protocol for automatic discovery
"""

import argparse
import asyncio
import logging
import os
import sys
import tempfile
from functools import partial
from pathlib import Path

import numpy as np
import soundfile as sf

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer, AsyncEventHandler
from wyoming.tts import Synthesize
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event

# Add supertonic to path
SUPERTONIC_PATH = "/opt/supertonic/py"
sys.path.insert(0, SUPERTONIC_PATH)

from helper import load_text_to_speech, load_voice_style

# Configure logging
_LOGGER = logging.getLogger(__name__)

# Available languages and voices
SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "ko": "Korean"
}

SUPPORTED_VOICES = {
    "M1": "Male Voice 1",
    "M2": "Male Voice 2",
    "M3": "Male Voice 3",
    "M4": "Male Voice 4",
    "M5": "Male Voice 5",
    "F1": "Female Voice 1",
    "F2": "Female Voice 2",
    "F3": "Female Voice 3",
    "F4": "Female Voice 4",
    "F5": "Female Voice 5"
}


class SupertonicEventHandler(AsyncEventHandler):
    """Handle Wyoming protocol events for Supertonic2 TTS"""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        tts_engine,
        voice_styles: dict,
        config: dict,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.wyoming_info = wyoming_info
        self.cli_args = cli_args
        self.tts_engine = tts_engine
        self.voice_styles = voice_styles
        self.config = config

    async def handle_event(self, event: Event) -> bool:
        """Handle a Wyoming protocol event"""
        if Synthesize.is_type(event.type):
            synthesize = Synthesize.from_event(event)
            await self._handle_synthesize(synthesize)
        else:
            _LOGGER.debug("Unexpected event: %s", event)

        return True

    async def _handle_synthesize(self, synthesize: Synthesize):
        """Handle a TTS synthesis request"""
        text = synthesize.text
        voice = synthesize.voice or self.config.get("default_voice", "M4")

        # Extract language from voice spec (e.g., "fr_M4" -> "fr", "M4")
        if "_" in voice:
            language, voice_name = voice.split("_", 1)
        else:
            # Default language if not specified
            language = self.config.get("default_language", "fr")
            voice_name = voice

        _LOGGER.info("Synthesizing: text='%s...', lang=%s, voice=%s",
                     text[:50], language, voice_name)

        try:
            # Get parameters
            speed = self.config.get("speed", 1.5)
            volume = self.config.get("volume_boost", 2.0)
            quality = self.config.get("quality", 5)

            # Get voice style
            if voice_name not in self.voice_styles:
                _LOGGER.warning("Voice %s not found, using default", voice_name)
                voice_name = self.config.get("default_voice", "M4")

            style = self.voice_styles[voice_name]

            # Generate speech
            wav, duration = self.tts_engine(
                text=text,
                lang=language,
                style=style,
                total_step=int(quality),
                speed=float(speed)
            )

            # Extract duration value
            duration_val = float(duration[0]) if hasattr(duration, '__len__') else float(duration)

            # Trim to actual duration
            trim_samples = int(self.tts_engine.sample_rate * duration_val)
            wav_trimmed = wav[0, :trim_samples]

            # Apply volume boost
            wav_boosted = wav_trimmed * float(volume)

            # Clip to prevent distortion
            wav_boosted = np.clip(wav_boosted, -1.0, 1.0)

            # Convert to int16 for Wyoming
            wav_int16 = (wav_boosted * 32767).astype(np.int16)

            _LOGGER.info("Generated audio: duration=%.2fs, samples=%d",
                        duration_val, len(wav_int16))

            # Send audio in chunks using AsyncEventHandler's write_event method
            chunk_size = 1024
            for i in range(0, len(wav_int16), chunk_size):
                chunk = wav_int16[i:i + chunk_size]
                chunk_bytes = chunk.tobytes()

                await self.write_event(
                    AudioChunk(
                        rate=self.tts_engine.sample_rate,
                        width=2,  # 16-bit
                        channels=1,  # mono
                        audio=chunk_bytes
                    ).event()
                )

            # Signal completion
            await self.write_event(AudioStop().event())

        except Exception as e:
            _LOGGER.error("TTS synthesis failed: %s", e, exc_info=True)
            # Send stop event to signal error
            await self.write_event(AudioStop().event())



async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Supertonic2 TTS Wyoming Server")
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:10300",
        help="URI to bind server (e.g. tcp://0.0.0.0:10300)",
    )
    parser.add_argument(
        "--data-dir",
        default="/data",
        help="Data directory for configuration",
    )
    parser.add_argument(
        "--models-dir",
        default="/opt/supertonic/models",
        help="Directory containing Supertonic2 models",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    _LOGGER.info("=== Supertonic2 TTS Wyoming Server Starting ===")

    # Load configuration
    config = {}
    options_file = Path(args.data_dir) / "options.json"
    if options_file.exists():
        import json
        with open(options_file, 'r') as f:
            config = json.load(f)
        _LOGGER.info("Loaded configuration: %s", config)
    else:
        # Default configuration
        config = {
            "default_language": "fr",
            "default_voice": "M4",
            "speed": 1.5,
            "volume_boost": 2.0,
            "quality": 5
        }
        _LOGGER.info("Using default configuration")

    # Initialize TTS engine
    onnx_dir = Path(args.models_dir) / "onnx"
    voices_dir = Path(args.models_dir) / "voice_styles"

    _LOGGER.info("Loading TTS engine from %s", onnx_dir)
    tts_engine = load_text_to_speech(onnx_dir=str(onnx_dir), use_gpu=False)
    _LOGGER.info("TTS engine loaded (sample rate: %d Hz)", tts_engine.sample_rate)

    # Pre-load all voice styles
    voice_styles = {}
    _LOGGER.info("Loading voice styles from %s", voices_dir)
    for voice_id in SUPPORTED_VOICES.keys():
        voice_path = voices_dir / f"{voice_id}.json"
        if voice_path.exists():
            voice_styles[voice_id] = load_voice_style([str(voice_path)])
            _LOGGER.info("  ✓ Loaded voice: %s", voice_id)
        else:
            _LOGGER.warning("  ✗ Voice file not found: %s", voice_path)

    _LOGGER.info("Loaded %d voice styles", len(voice_styles))

    # Create Wyoming Info with all voices for all languages
    voices = []
    for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
        for voice_id, voice_desc in SUPPORTED_VOICES.items():
            voices.append(
                TtsVoice(
                    name=f"{lang_code}_{voice_id}",
                    description=f"{lang_name} - {voice_desc}",
                    attribution=Attribution(
                        name="Supertone Inc.",
                        url="https://github.com/supertone-inc/supertonic",
                    ),
                    installed=True,
                    version="2.0.0",
                    languages=[lang_code],
                )
            )

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="supertonic2",
                description="Supertonic2 - Ultra-fast, on-device multilingual TTS",
                attribution=Attribution(
                    name="Supertone Inc.",
                    url="https://github.com/supertone-inc/supertonic",
                ),
                installed=True,
                version="2.0.0",
                voices=voices,
            )
        ],
    )

    # Start Wyoming server
    _LOGGER.info("Starting Wyoming server on %s", args.uri)

    server = AsyncServer.from_uri(args.uri)

    await server.run(
        partial(
            SupertonicEventHandler,
            wyoming_info,
            args,
            tts_engine,
            voice_styles,
            config,
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Server stopped by user")
    except Exception as e:
        _LOGGER.error("Server error: %s", e, exc_info=True)
        sys.exit(1)
