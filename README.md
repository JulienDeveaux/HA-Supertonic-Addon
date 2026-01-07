# Home Assistant Supertonic2 TTS Add-on

Ultra-fast, on-device multilingual text-to-speech powered by Supertonic2 for Home Assistant.

## About

This repository contains a Home Assistant add-on that brings **Supertonic2 TTS** to your home automation setup. Supertonic2 is a lightning-fast, privacy-focused text-to-speech system that runs entirely on your device.

### Why Supertonic2?

- **⚡ Blazingly Fast**: Generates speech up to **167× faster than real-time**
- **🔒 100% Private**: All processing happens on your device - no cloud, no API calls, no data sent anywhere
- **🌍 Multilingual**: Native support for **English, French, Spanish, Portuguese, and Korean**
- **🎤 Multiple Voices**: Choose from **10 different voices** (5 male, 5 female)
- **🎛️ Highly Configurable**: Control speed, volume, quality, and voice selection
- **💪 Works Offline**: Zero network dependency after initial setup

## Features

| Feature | Details |
|---------|---------|
| **Languages** | English (en), French (fr), Spanish (es), Portuguese (pt), Korean (ko) |
| **Voices** | M1, M2, M3, M4, M5 (male) • F1, F2, F3, F4, F5 (female) |
| **Speed Control** | 0.5× to 2.0× (50% slower to 2× faster) |
| **Volume Control** | 1.0× to 3.0× amplification |
| **Quality Levels** | 1-10 (higher = better quality, slightly slower) |
| **Audio Format** | WAV, 44.1kHz, mono |
| **API** | REST API compatible with Home Assistant TTS platform |

## Installation

### Method 1: Add Repository to Home Assistant (Recommended)

**Quick Add (One Click):**

[![Open your Home Assistant instance and show the add add-on repository dialog with this repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FJulienDeveaux%2FHA-Supertonic-Addon)

**Or manually:**

1. In Home Assistant, navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** menu (three dots) in the top right corner
3. Select **Repositories**
4. Add this repository URL:
   ```
   https://github.com/JulienDeveaux/HA-Supertonic-Addon
   ```
5. Find "Supertonic2 TTS" in the add-on list
6. Click **Install**

### Method 2: Manual Installation (Development/Testing)

1. Clone this repository:
   ```bash
   git clone https://github.com/JulienDeveaux/HA-Supertonic-Addon.git
   cd HA-Supertonic-Addon
   ```

2. Copy the `supertonic_tts` directory to your Home Assistant addons folder:
   ```bash
   # For Home Assistant OS:
   cp -r supertonic_tts /addons/

   # For Supervised:
   cp -r supertonic_tts /usr/share/hassio/addons/local/
   ```

3. Restart the Supervisor:
   ```bash
   ha supervisor reload
   ```

4. The add-on will appear in your add-on store

## Quick Start

### 1. Configure the Add-on

After installation, configure your preferences:

```yaml
default_language: "fr"      # en, fr, es, pt, ko
default_voice: "M4"         # M1-M5, F1-F5
speed: 1.5                  # 0.5 - 2.0
volume_boost: 2.0           # 1.0 - 3.0
quality: 5                  # 1 - 10
```

### 2. Start the Add-on

- Click **Start**
- Enable **Start on boot** (optional)
- Enable **Watchdog** (optional)

> ⏱️ **Note**: First start takes 2-5 minutes to download models (~250MB)

### 3. Configure Home Assistant

Add to your `configuration.yaml`:

```yaml
tts:
  - platform: rest
    name: "Supertonic2"
    base_url: "http://localhost:8765"
    endpoint: "/api/tts"
    message_param: "text"
    language_param: "language"
```

Restart Home Assistant.

### 4. Test It!

```yaml
service: tts.speak
target:
  entity_id: media_player.living_room
data:
  message: "Bonjour, bienvenue à la maison!"
  language: "fr"
```

## Usage Examples

### Basic Announcement (French)

```yaml
automation:
  - alias: "Welcome Home"
    trigger:
      - platform: state
        entity_id: person.julien
        to: "home"
    action:
      - service: tts.speak
        target:
          entity_id: media_player.living_room
        data:
          message: "Bienvenue à la maison!"
          language: "fr"
```

### Advanced with Custom Settings

```yaml
service: tts.speak
target:
  entity_id: media_player.bedroom
data:
  message: "Good morning! It's time to wake up."
  language: "en"
  options:
    voice: "F2"        # Female voice 2
    speed: 1.3         # 30% faster
    volume: 2.5        # 2.5× volume
    quality: 8         # High quality
```

### Multi-language Household

```yaml
script:
  announce_english:
    sequence:
      - service: tts.speak
        data:
          message: "{{ message }}"
          language: "en"
          entity_id: media_player.living_room

  announce_french:
    sequence:
      - service: tts.speak
        data:
          message: "{{ message }}"
          language: "fr"
          entity_id: media_player.living_room
```

## Architecture Support

| Architecture | Supported | Notes |
|--------------|-----------|-------|
| aarch64 | ✅ Yes | ARM 64-bit (Raspberry Pi 3/4/5, etc.) |
| amd64 | ✅ Yes | Intel/AMD 64-bit (most PCs) |
| armv7 | ✅ Yes | ARM 32-bit v7 |
| armhf | ❌ No | Use armv7 instead |
| i386 | ❌ No | 32-bit x86 not supported |

## Performance Benchmarks

Generation speed examples (Apple M4 Pro):

| Quality | Real-Time Factor | Use Case |
|---------|------------------|----------|
| 2 | 167× | Quick notifications |
| 5 | 51× | General use (recommended) |
| 10 | 17× | High-quality audio |

> **Real-Time Factor (RTF)**: 1× means generation takes the same time as playback. Higher is faster.

## API Endpoints

The add-on exposes a REST API on port 8765:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and service info |
| `/api/tts` | GET/POST | Generate TTS audio |
| `/api/languages` | GET | List supported languages |
| `/api/voices` | GET | List available voices |

### Example API Call

```bash
# Generate French TTS
curl "http://localhost:8765/api/tts?text=Bonjour&language=fr&voice=M4" -o output.wav

# Check health
curl http://localhost:8765/health
```

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **RAM** | 512MB | 1GB+ |
| **Disk Space** | 500MB | 1GB+ |
| **CPU** | ARM/x86 dual-core | Quad-core+ |
| **Network** | Required for setup only | - |

## Supported Languages

| Language | Code | Native Accent | Status |
|----------|------|---------------|--------|
| English | `en` | ✅ Yes | Fully supported |
| French | `fr` | ✅ Yes | Fully supported |
| Spanish | `es` | ✅ Yes | Fully supported |
| Portuguese | `pt` | ✅ Yes | Fully supported |
| Korean | `ko` | ✅ Yes | Fully supported |

## Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For bugs or feature requests, please [open an issue](https://github.com/JulienDeveaux/HA-Supertonic-Addon/issues).

## Credits

- **Supertonic2** - Created by [Supertone Inc.](https://www.supertone.ai/)
  - GitHub: [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic)
  - HuggingFace: [Supertone/supertonic-2](https://huggingface.co/Supertone/supertonic-2)