# Supertonic2 TTS Add-on

Ultra-fast, on-device text-to-speech for Home Assistant powered by Supertonic2.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armv7 Architecture][armv7-shield]

## About

This add-on brings Supertonic2 TTS to Home Assistant, providing:

- **Lightning-fast** text-to-speech (up to 167× real-time)
- **Complete privacy** - 100% on-device processing
- **Multilingual support** - English, French, Spanish, Portuguese, Korean
- **10 voice options** - 5 male and 5 female voices
- **Zero latency** - No network dependency

Perfect for home automation announcements, notifications, and accessibility features.

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Supertonic2 TTS" add-on
3. Configure your preferences
4. Start the add-on
5. Add TTS platform configuration to `configuration.yaml`

## Configuration Example

```yaml
default_language: "fr"
default_voice: "M4"
speed: 1.5
volume_boost: 2.0
quality: 5
```
