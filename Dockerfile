# Use Ubuntu as base image
FROM ubuntu:22.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
RUN service ollama start

# Wait for Ollama to be ready
RUN sleep 10

# Download Ollama models beforehand (optional but recommended)
RUN ollama pull nomic-embed-text
RUN ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "server.py"]
