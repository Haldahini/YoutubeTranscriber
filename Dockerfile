FROM python:3.11-slim

# Force Python to be unbuffered for real-time output
ENV PYTHONUNBUFFERED=1

# Install yt-dlp + dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY youtube_playlist_to_text.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for volumes
RUN mkdir -p /app/downloads /app/transcriptions

# Entrypoint
ENTRYPOINT ["python", "-u", "youtube_playlist_to_text.py"]