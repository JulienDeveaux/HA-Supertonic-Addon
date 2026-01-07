# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Set working directory
WORKDIR /opt

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    git \
    git-lfs \
    libsndfile \
    libsndfile-dev \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    linux-headers

# Create python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
# Note: Using compatible versions for Alpine Linux (musllinux)
RUN pip install --no-cache-dir \
    onnxruntime \
    numpy \
    soundfile \
    librosa \
    pyyaml \
    wyoming

# Clone Supertonic repository (for helper code)
RUN git clone --depth 1 https://github.com/supertone-inc/supertonic.git /opt/supertonic

# Initialize Git LFS and download Supertonic2 models
RUN git lfs install && \
    git clone https://huggingface.co/Supertone/supertonic-2 /opt/supertonic/models

# Clean up git files to save space (keep only models)
RUN cd /opt/supertonic/models && \
    rm -rf .git && \
    cd /opt && \
    cd /opt/supertonic && \
    rm -rf .git cpp csharp flutter go img ios java nodejs rust swift web && \
    rm -rf py/.git py/__pycache__ py/results

# Verify models are present
RUN ls -la /opt/supertonic/models/onnx && \
    ls -la /opt/supertonic/models/voice_styles

# Copy root filesystem
COPY rootfs /

# Labels
LABEL \
    io.hass.name="Supertonic2 TTS" \
    io.hass.description="Ultra-fast, on-device multilingual text-to-speech" \
    io.hass.type="addon" \
    io.hass.version="1.0.0"
