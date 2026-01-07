#!/usr/bin/env python3
"""
Supertonic2 TTS HTTP Server for Home Assistant
Provides text-to-speech API endpoint for HA TTS platform
"""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path
from flask import Flask, request, send_file, jsonify
import numpy as np
import soundfile as sf

# Add supertonic to path
SUPERTONIC_PATH = "/opt/supertonic/py"
sys.path.insert(0, SUPERTONIC_PATH)

from helper import load_text_to_speech, load_voice_style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global TTS engine and configuration
tts_engine = None
config = {}
voice_styles = {}

# Available languages and voices
SUPPORTED_LANGUAGES = ["en", "fr", "es", "pt", "ko"]
SUPPORTED_VOICES = ["M1", "M2", "M3", "M4", "M5", "F1", "F2", "F3", "F4", "F5"]


def load_configuration():
    """Load addon configuration from Home Assistant options"""
    global config

    config_file = "/data/options.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "default_language": "fr",
            "default_voice": "M4",
            "speed": 1.5,
            "volume_boost": 2.0,
            "quality": 5
        }

    logger.info(f"Loaded configuration: {config}")
    return config


def initialize_tts_engine():
    """Initialize the Supertonic2 TTS engine"""
    global tts_engine, voice_styles

    onnx_dir = "/opt/supertonic/models/onnx"
    voices_dir = "/opt/supertonic/models/voice_styles"

    logger.info(f"Loading TTS engine from {onnx_dir}")
    tts_engine = load_text_to_speech(onnx_dir=onnx_dir, use_gpu=False)
    logger.info(f"TTS engine loaded successfully (sample rate: {tts_engine.sample_rate} Hz)")

    # Pre-load all voice styles
    logger.info("Loading voice styles...")
    for voice in SUPPORTED_VOICES:
        voice_path = os.path.join(voices_dir, f"{voice}.json")
        if os.path.exists(voice_path):
            voice_styles[voice] = load_voice_style([voice_path])
            logger.info(f"  ✓ Loaded voice: {voice}")
        else:
            logger.warning(f"  ✗ Voice file not found: {voice_path}")

    logger.info(f"Loaded {len(voice_styles)} voice styles")


def synthesize_speech(text, language=None, voice=None, speed=None, volume=None, quality=None):
    """
    Synthesize speech from text using Supertonic2

    Args:
        text: Text to synthesize
        language: Language code (en, fr, es, pt, ko)
        voice: Voice ID (M1-M5, F1-F5)
        speed: Speech speed multiplier (0.5-2.0)
        volume: Volume boost multiplier (1.0-3.0)
        quality: Quality level / denoising steps (1-10)

    Returns:
        Path to generated audio file
    """
    # Use config defaults if not specified
    language = language or config.get("default_language", "fr")
    voice = voice or config.get("default_voice", "M4")
    speed = speed if speed is not None else config.get("speed", 1.5)
    volume = volume if volume is not None else config.get("volume_boost", 2.0)
    quality = quality if quality is not None else config.get("quality", 5)

    # Validate parameters
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    if voice not in voice_styles:
        raise ValueError(f"Unsupported or unavailable voice: {voice}")

    logger.info(f"Synthesizing: text='{text[:50]}...', lang={language}, voice={voice}, speed={speed}, volume={volume}, quality={quality}")

    # Get voice style
    style = voice_styles[voice]

    # Generate speech
    wav, duration = tts_engine(
        text=text,
        lang=language,
        style=style,
        total_step=int(quality),
        speed=float(speed)
    )

    # Extract duration value
    duration_val = float(duration[0]) if hasattr(duration, '__len__') else float(duration)
    logger.info(f"Generated audio: duration={duration_val:.2f}s")

    # Trim to actual duration
    trim_samples = int(tts_engine.sample_rate * duration_val)
    wav_trimmed = wav[0, :trim_samples]

    # Apply volume boost
    wav_boosted = wav_trimmed * float(volume)

    # Clip to prevent distortion
    wav_boosted = np.clip(wav_boosted, -1.0, 1.0)

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.wav',
        prefix='supertonic_'
    )
    temp_file.close()

    sf.write(temp_file.name, wav_boosted, tts_engine.sample_rate)
    logger.info(f"Audio saved to: {temp_file.name}")

    return temp_file.name


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Supertonic2 TTS",
        "languages": SUPPORTED_LANGUAGES,
        "voices": list(voice_styles.keys())
    })


@app.route('/api/tts', methods=['GET', 'POST'])
def tts_endpoint():
    """
    Main TTS endpoint compatible with Home Assistant TTS platform

    Query parameters (GET) or JSON body (POST):
        - text: Text to synthesize (required)
        - language: Language code (optional, defaults to config)
        - voice: Voice ID (optional, defaults to config)
        - speed: Speech speed (optional, defaults to config)
        - volume: Volume boost (optional, defaults to config)
        - quality: Quality level (optional, defaults to config)
    """
    try:
        # Get parameters from request
        if request.method == 'POST':
            data = request.get_json() or {}
            text = data.get('text') or request.args.get('text')
        else:
            text = request.args.get('text')
            data = request.args

        if not text:
            return jsonify({"error": "Missing 'text' parameter"}), 400

        # Extract optional parameters
        language = data.get('language')
        voice = data.get('voice')
        speed = data.get('speed')
        volume = data.get('volume')
        quality = data.get('quality')

        # Convert string numbers to appropriate types
        if speed is not None:
            speed = float(speed)
        if volume is not None:
            volume = float(volume)
        if quality is not None:
            quality = int(quality)

        # Synthesize speech
        audio_file = synthesize_speech(
            text=text,
            language=language,
            voice=voice,
            speed=speed,
            volume=volume,
            quality=quality
        )

        # Send audio file
        return send_file(
            audio_file,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='tts_output.wav'
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        return jsonify({"error": "TTS generation failed", "details": str(e)}), 500


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        "languages": SUPPORTED_LANGUAGES,
        "default": config.get("default_language", "fr")
    })


@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Get list of available voices"""
    language = request.args.get('language')
    return jsonify({
        "voices": list(voice_styles.keys()),
        "default": config.get("default_voice", "M4"),
        "note": "All voices support all languages"
    })


def main():
    """Main entry point"""
    logger.info("=== Supertonic2 TTS Server Starting ===")

    # Load configuration
    load_configuration()

    # Initialize TTS engine
    initialize_tts_engine()

    # Start Flask server
    port = int(os.environ.get('PORT', 8765))
    logger.info(f"Starting HTTP server on port {port}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
