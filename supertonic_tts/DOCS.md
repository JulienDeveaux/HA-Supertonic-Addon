# Supertonic2 TTS Add-on Documentation

Ultra-fast, on-device text-to-speech powered by Supertonic2 with full multilingual support.

## About

This add-on provides a local, privacy-focused text-to-speech service using Supertonic2, which generates speech up to 167× faster than real-time on consumer hardware. All processing happens on your device with zero network dependency.

**No configuration.yaml changes needed!** This add-on uses the Wyoming protocol for automatic discovery by Home Assistant.

## Features

- **🚀 Ultra-fast**: Generates speech up to 167× faster than real-time
- **🔒 100% Private**: Completely on-device, no cloud, no API calls
- **🌍 Multilingual**: Supports English, French, Spanish, Portuguese, and Korean
- **🎤 Multiple Voices**: 10 voice options (5 male, 5 female)
- **⚡ Low Latency**: Zero network latency
- **🎛️ Highly Configurable**: Adjust speed, volume, quality, and voice
- **🔌 Auto-Discovery**: Automatically detected by Home Assistant via Wyoming protocol

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Supertonic2 TTS" add-on
3. Configure your preferences (see below)
4. Start the add-on
5. **That's it!** Home Assistant will automatically discover the TTS service

No need to edit `configuration.yaml`!

## Configuration

### Add-on Configuration

Configure the default TTS settings in the add-on configuration:

```yaml
default_language: "fr"      # Default language (en, fr, es, pt, ko)
default_voice: "M4"         # Default voice (M1-M5, F1-F5)
speed: 1.5                  # Speech speed (0.5 - 2.0)
volume_boost: 2.0           # Volume amplification (1.0 - 3.0)
quality: 5                  # Quality level (1-10, higher = better quality)
debug_logging: false        # Enable debug logs
```

## Usage

### Basic Usage

After starting the add-on, Home Assistant will automatically create TTS entities for each voice/language combination.

**In the UI:**
1. Go to **Developer Tools** → **Services**
2. Search for "tts.speak"
3. Select a Supertonic2 TTS entity (e.g., `tts.supertonic2_fr_m4`)
4. Enter your message and call the service

**In Automations:**

```yaml
service: tts.speak
target:
  entity_id: tts.supertonic2_fr_m4
data:
  message: "Bonjour, bienvenue à la maison!"
  media_player_entity_id: media_player.living_room
```

### Voice Selection

Voices are named with the format: `language_voice` (e.g., `fr_M4`, `en_F2`)

**Available Languages:**
- `en` - English
- `fr` - French
- `es` - Spanish
- `pt` - Portuguese
- `ko` - Korean

**Available Voices:**
- `M1`, `M2`, `M3`, `M4`, `M5` - Male voices
- `F1`, `F2`, `F3`, `F4`, `F5` - Female voices

## Parameters

### speed (0.5 - 2.0)
- `0.5` - Half speed (very slow)
- `1.0` - Normal speed
- `1.5` - 50% faster (recommended)
- `2.0` - Double speed (very fast)

### volume_boost (1.0 - 3.0)
- `1.0` - No amplification
- `2.0` - 2x amplification (recommended)
- `3.0` - 3x amplification (maximum)

### quality (1 - 10)
- `1-3` - Lower quality, faster generation
- `5` - Balanced quality/speed (recommended)
- `8-10` - Highest quality, slower generation

## Backup Configuration

This add-on is configured to **exclude model files from Home Assistant backups** to prevent backup bloat. The models (~250MB) will be automatically re-downloaded if needed after restoring from backup.

Files excluded from backup:
- ONNX model files (`*.onnx`)
- All files in `/opt/supertonic/models/`
- PyTorch model files (`*.pt`, `*.pth`)

This is configured in `backup.json` and happens automatically.

## Support

For issues, feature requests, or questions:
- GitHub: [Repository Issues](https://github.com/JulienDeveaux/HA-Supertonic-Addon/issues)
- Home Assistant Community: [Forum](https://community.home-assistant.io/)

## Credits

Powered by [Supertonic2](https://github.com/supertone-inc/supertonic) by Supertone Inc.

## License

This add-on is licensed under the Apache 2.0 License.
Supertonic2 is licensed under the OpenRAIL License.
