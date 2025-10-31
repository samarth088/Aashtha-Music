FROM python:3.11.9-slim

# Install FFmpeg + Build Tools + Git
RUN apt-get update && \
    apt-get install -y ffmpeg libopus0 build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pytgcalls from Git (latest)
RUN pip install --no-cache-dir git+https://github.com/pytgcalls/pytgcalls

# Install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
