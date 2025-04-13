# Use Ubuntu with Ollama support
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
  curl git python3 python3-pip python3-venv wget unzip && \
  rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Set up app
WORKDIR /app
COPY . .

# Install Python deps
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Download Ollama models beforehand (optional but recommended)
RUN ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf
RUN ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

# Expose Flask app port
EXPOSE 5000

CMD ["bash", "-c", "ollama serve & python3 server.py"]
