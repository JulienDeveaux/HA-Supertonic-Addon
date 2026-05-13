# Home Assistant Supertonic3 TTS Add-on

Ultra-fast, on-device multilingual text-to-speech powered by Supertonic-3 for Home Assistant.

## About

This repository contains a Home Assistant add-on that brings **Supertonic-3 TTS** to your
home automation setup. Supertonic-3 is a fast, privacy-focused text-to-speech system that
runs entirely on your device.

### Why Supertonic-3?

- **⚡ Blazingly Fast**: several times faster than real-time on consumer CPUs
- **🔒 100% Private**: All processing happens on your device — no cloud, no API calls, no data sent anywhere
- **🌍 Multilingual**: native support for **31 languages**
- **🎤 Multiple Voices**: choose from **10 different voices** (5 male, 5 female)
- **🎛️ Highly Configurable**: control speed, volume, quality, and voice
- **💪 Works Offline**: zero network dependency after install

## Features

| Feature | Details |
|---------|---------|
| **Languages** | 31 languages — see [list below](#supported-languages) |
| **Voices** | M1, M2, M3, M4, M5 (male) • F1, F2, F3, F4, F5 (female) |
| **Speed Control** | 0.5× to 2.0× (50 % slower to 2× faster) |
| **Volume Control** | 1.0× to 3.0× amplification |
| **Quality (`total_steps`)** | 2 - 16 |
| **Audio Format** | WAV, 44.1 kHz, mono |
| **Protocol** | Wyoming protocol with automatic discovery |

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
5. Find "Supertonic3 TTS" in the add-on list
6. Click **Install**

### Method 2: Manual Installation (Development/Testing)

1. Clone this repository:
   ```bash
   git clone https://github.com/JulienDeveaux/HA-Supertonic-Addon.git
   cd HA-Supertonic-Addon
   ```

2. Copy the `supertonic_tts` directory to your Home Assistant Apps folder:
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
default_language: "fr"      # one of 31 supported languages (or "na" fallback)
default_voice: "M4"         # M1-M5, F1-F5
speed: 1.5                  # 0.5 - 2.0
volume_boost: 2.0           # 1.0 - 3.0
quality: 5                  # 2 - 16 (diffusion steps)
```

### 2. Start the Add-on

- Click **Start**
- Enable **Start on boot** (optional)
- Enable **Watchdog** (optional)

> ⏱️ **Note**: first start loads ~385 MB of models into memory; the image itself is pre-bundled with the weights, so no network round-trip is required at runtime.

### 3. Automatic Discovery

**That's it!** Home Assistant will automatically discover the TTS service via Wyoming protocol.

- The integration appears automatically in **Settings → Devices & Services**
- Click **Configure** when you see the Wyoming Protocol notification
- A single Supertonic3 TTS entity is created; the **310 voice variants** (31 languages × 10 timbres) are selectable via the `voice` option on `tts.speak`

## Staying on Supertonic-2

Supertonic-3 is larger than v2 (~99 M params vs ~66 M) and uses more memory and CPU.
On low-end hardware, v2 may give a better latency
profile. The previous v2 implementation is kept on the
[`v2-legacy`](https://github.com/JulienDeveaux/HA-Supertonic-Addon/tree/v2-legacy) branch
— install from that branch via the manual method above to stay on v2.

## Architecture Support

| Architecture | Supported | Notes |
|--------------|-----------|-------|
| aarch64 | ✅ Yes | ARM 64-bit (Raspberry Pi 3/4/5, etc.) |
| amd64 | ✅ Yes | Intel/AMD 64-bit (most PCs) |
| armv7 | ❌ No | onnxruntime does not ship armv7 wheels — use the [`v2-legacy`](https://github.com/JulienDeveaux/HA-Supertonic-Addon/tree/v2-legacy) branch on 32-bit ARM |
| armhf | ❌ No | Not supported |
| i386 | ❌ No | 32-bit x86 not supported |

## Wyoming Protocol

This add-on uses the **Wyoming protocol** for communication with Home Assistant:
- **Port**: 10300 (TCP)
- **Protocol**: Wyoming (binary protocol for voice services)
- **Discovery**: Automatic via Zeroconf/mDNS (`_wyoming._tcp.local.`)
- **Communication**: Event-based (Describe, Synthesize, AudioChunk, AudioStop)

No REST API or HTTP endpoints are exposed. All communication happens through the Wyoming protocol.

## Performance

Generation speed depends mainly on the `quality` (= number of diffusion steps) and on
your CPU. Measured locally on Apple M-series silicon:

| `quality` | Real-Time Factor | Use Case |
|---------|------------------|----------|
| 2 | ~14× | Quick notifications |
| 5 | ~6× | General use |
| 10 | ~3× | High-quality audio |

> **Real-Time Factor (RTF)**: 1× means generation takes the same time as playback. Higher is faster. Values on ARM SBCs (e.g. Raspberry Pi 5) will be significantly lower.

## Supported Languages

31 languages plus a `na` fallback. Grouped by region for readability:

| Region | Languages |
|---|---|
| **Western European** | `en` English · `fr` French · `de` German · `es` Spanish · `pt` Portuguese · `it` Italian · `nl` Dutch |
| **Nordic & Baltic** | `sv` Swedish · `da` Danish · `fi` Finnish · `et` Estonian · `lv` Latvian · `lt` Lithuanian |
| **Slavic** | `pl` Polish · `cs` Czech · `sk` Slovak · `sl` Slovenian · `hr` Croatian · `bg` Bulgarian · `ru` Russian · `uk` Ukrainian |
| **Other European** | `el` Greek · `hu` Hungarian · `ro` Romanian |
| **Asian & Middle Eastern** | `ko` Korean · `ja` Japanese · `hi` Hindi · `id` Indonesian · `vi` Vietnamese · `tr` Turkish · `ar` Arabic |
| **Fallback** | `na` — no language-specific cues (useful for code-switched or unknown-language text) |

Voices are named `<lang>_<voice>` (e.g. `fr_M4`, `de_F1`) and passed as `options.voice`
to `tts.speak`. With 10 timbres (M1-M5 male, F1-F5 female) × 31 languages, that's
310 voice variants accessible from the single Supertonic3 TTS entity.

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **RAM** | 1 GB | 2 GB+ |
| **Disk Space** | 1 GB | 2 GB+ |
| **CPU** | ARM/x86 dual-core | Quad-core+ |
| **Network** | Required for the initial add-on install only | - |

## Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For bugs or feature requests, please [open an issue](https://github.com/JulienDeveaux/HA-Supertonic-Addon/issues).

## Credits

- **Supertonic-3** by [Supertone Inc.](https://www.supertone.ai/)
  - GitHub: [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic)
  - HuggingFace: [Supertone/supertonic-3](https://huggingface.co/Supertone/supertonic-3)
  - SDK: [`supertonic`](https://pypi.org/project/supertonic/) on PyPI
