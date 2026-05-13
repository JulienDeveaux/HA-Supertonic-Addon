# Supertonic3 TTS Add-on Documentation

Ultra-fast, on-device text-to-speech powered by Supertonic-3 with full multilingual support.

## About

This add-on provides a local, privacy-focused text-to-speech service using Supertonic-3,
which generates speech several times faster than real-time on consumer hardware. All
processing happens on your device with zero network dependency after the first model
download.

**No configuration.yaml changes needed!** This add-on uses the Wyoming protocol for
automatic discovery by Home Assistant.

## Features

- **🚀 Ultra-Fast**: ~2×–14× real-time depending on quality (`total_steps`); ~6× at the default `quality: 5`
- **🔒 100% Private**: completely on-device, no cloud, no API calls
- **🌍 Multilingual**: 31 languages supported (see list below)
- **🎤 Multiple Voices**: 10 voice options (5 male, 5 female)
- **⚡ Streaming**: audio playback starts as soon as the first sentence is ready, reducing perceived latency on long texts
- **🗣️ Smart abbreviations**: common abbreviations (FR/EN) are automatically expanded to their spoken form before synthesis (e.g. `Dr.` → `Docteur`, `Mme.` → `Madame`)
- **🔌 Auto-Discovery**: automatically detected by Home Assistant via Wyoming protocol

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Supertonic3 TTS" add-on
3. Configure your preferences (see below)
4. Start the add-on
5. **That's it!** Home Assistant will automatically discover the TTS service

## Configuration

```yaml
default_language: "fr"      # one of 31 languages (see below) or "na" for fallback
default_voice: "M4"         # M1-M5 (male), F1-F5 (female)
speed: 1.5                  # 0.5 - 2.0
volume_boost: 2.0           # 1.0 - 3.0
quality: 5                  # 2 - 16 (number of diffusion steps)
debug_logging: false        # enable verbose logs
```

## Usage

### Basic Usage

After starting the add-on, Home Assistant creates a TTS entity for the
Supertonic3 service. The 310 voice variants (31 languages × 10 timbres) are exposed as
selectable options on that entity — pick one via the `voice` parameter when calling
`tts.speak`. The `default_language` / `default_voice` from the addon config are used
when no `voice` is passed.

**In the UI:**
1. Go to **Developer Tools** → **Services**
2. Search for `tts.speak`
3. Pick the Supertonic3 TTS entity
4. Optionally choose a `voice` (e.g. `fr_M4`, `en_F2`, `de_M1`)
5. Enter your message and call the service

**In Automations:**

```yaml
service: tts.speak
data:
  entity_id: tts.supertonic3
  message: "Bonjour, bienvenue à la maison !"
  options:
    voice: "fr_M4"
  media_player_entity_id: media_player.living_room
```

If `options.voice` is omitted, the addon falls back to the configured `default_language`
+ `default_voice`.

### Voice Selection

Voices are named with the format `language_voice` (e.g., `fr_M4`, `en_F2`, `de_M1`).

**Available Voices:**

- `M1`, `M2`, `M3`, `M4`, `M5` — Male voices
- `F1`, `F2`, `F3`, `F4`, `F5` — Female voices

**Available Languages (31):**

| Region | Languages |
|---|---|
| Western European | `en` English · `fr` French · `de` German · `es` Spanish · `pt` Portuguese · `it` Italian · `nl` Dutch |
| Nordic & Baltic | `sv` Swedish · `da` Danish · `fi` Finnish · `et` Estonian · `lv` Latvian · `lt` Lithuanian |
| Slavic | `pl` Polish · `cs` Czech · `sk` Slovak · `sl` Slovenian · `hr` Croatian · `bg` Bulgarian · `ru` Russian · `uk` Ukrainian |
| Other European | `el` Greek · `hu` Hungarian · `ro` Romanian |
| Asian & Middle Eastern | `ko` Korean · `ja` Japanese · `hi` Hindi · `id` Indonesian · `vi` Vietnamese · `tr` Turkish · `ar` Arabic |

**Fallback:** `na` is also accepted as `default_language` — it tells the model to
synthesize without language-specific cues (useful for code-switched or
unknown-language text).

## Parameters

### speed (0.5 - 2.0)

- `0.5` — Half speed (very slow)
- `1.0` — Normal speed
- `1.5` — 50 % faster (recommended)
- `2.0` — Double speed (very fast)

### volume_boost (1.0 - 3.0)

- `1.0` — No amplification
- `2.0` — 2× amplification (recommended)
- `3.0` — 3× amplification (maximum, may clip)

### quality (2 - 16)

`quality` maps to the SDK's `total_steps` — the number of diffusion steps used during
synthesis. Higher = better quality but slower.

- `2-3` — Fastest, occasional artefacts
- `5` — Balanced quality/speed (recommended)
- `10-16` — Highest quality, slower generation

## How Streaming Works

Long texts are automatically split into sentences before synthesis. Each sentence is
synthesized and streamed to Home Assistant immediately — playback begins as soon as the
first sentence is ready, while subsequent sentences are generated in parallel. This
significantly reduces the perceived response time on announcements longer than one
sentence.

Abbreviation expansion (FR/EN only) happens before splitting, so
`"M. Dupont est Dr. en médecine."` is synthesized as
`"Monsieur Dupont est Docteur en médecine."`.

## Backup Configuration

This add-on is configured to **exclude model files from Home Assistant backups** to
prevent backup bloat. The models (~385 MB) are baked into the add-on image and will be
restored automatically on re-install.

Files excluded from backup:
- ONNX model files (`*.onnx`)
- All files in `/opt/supertonic-models/`
- PyTorch model files (`*.pt`, `*.pth`)

This is configured in `backup.json` and happens automatically.

## Support

For issues, feature requests, or questions:
- GitHub: [Repository Issues](https://github.com/JulienDeveaux/HA-Supertonic-Addon/issues)
- Home Assistant Community: [Forum](https://community.home-assistant.io/)

## Credits

Powered by [Supertonic-3](https://github.com/supertone-inc/supertonic) by Supertone Inc.

- SDK: [`supertonic`](https://pypi.org/project/supertonic/) on PyPI
- Model weights: [Supertone/supertonic-3](https://huggingface.co/Supertone/supertonic-3) on HuggingFace
