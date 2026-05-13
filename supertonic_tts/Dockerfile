# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm
FROM $BUILD_FROM

WORKDIR /opt

# Runtime deps only — onnxruntime wheels ship precompiled, no compiler needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Pin SDK version: the migration relies on the current TTS(model_dir=...) API
# and the SDK's hardcoded ~/.cache/supertonic3 download path. A breaking SDK
# change would silently break rebuilds — re-test before bumping these.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      'supertonic>=1.2.1,<2.0' \
      'wyoming>=1.5.0' \
      'zeroconf>=0.132.0'

# Pre-download Supertonic-3 model at build time and relocate to a stable path.
# The SDK hardcodes ~/.cache/supertonic3 for downloads (SUPERTONIC_CACHE_DIR is
# only half-respected). We resolve the actual cache directory via the SDK itself
# (in case it changes in a future patch) and move it to /opt/supertonic-models.
RUN python3 -c "from supertonic import TTS; TTS(model='supertonic-3', auto_download=True)" && \
    SRC=$(python3 -c "from supertonic.loader import get_model_cache_dir; print(get_model_cache_dir('supertonic-3'))") && \
    test -d "$SRC/onnx" || (echo "ERROR: unexpected SDK cache layout at $SRC" && exit 1) && \
    mv "$SRC" /opt/supertonic-models && \
    ls -la /opt/supertonic-models/onnx && \
    ls -la /opt/supertonic-models/voice_styles

COPY rootfs /

LABEL \
    io.hass.name="Supertonic3 TTS" \
    io.hass.description="Ultra-fast, on-device multilingual text-to-speech (Supertonic-3)" \
    io.hass.type="addon" \
    io.hass.version="2.0.0"
