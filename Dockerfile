FROM python:3.11-slim

# Install system dependencies (git is required for plugin management and version resolution)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-privileged user and setup directories
RUN useradd -m -u 1000 abot && \
    mkdir -p /app/data /app/log /app/plugins && \
    chown -R abot:abot /app

COPY . /app

RUN pip install --no-cache-dir .

USER abot

ENV NAME="abot" \
    PREFIX="./" \
    SUDO="0" \
    INSTALL=""

CMD ["sh", "-c", "python -m abot \"$NAME\" ${SESSION_STRING:+--session=\"$SESSION_STRING\"} --sudo=\"$SUDO\" --prefix=\"$PREFIX\" --install=\"$INSTALL\""]
