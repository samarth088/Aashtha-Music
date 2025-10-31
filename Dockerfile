FROM python:3.11.9-slim

# Install FFmpeg + Build Tools
RUN apt-get update && \
    apt-get install -y ffmpeg libopus0 build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run bot
CMD ["python", "main.py"]
