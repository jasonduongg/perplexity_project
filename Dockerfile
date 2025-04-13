# Use Ubuntu as base image
FROM ubuntu:22.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Start Ollama and download models
RUN ollama serve & \
    sleep 10 && \
    ollama pull nomic-embed-text && \
    ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["bash", "-c", "echo 'Starting Ollama...' && ollama serve & sleep 10 && echo 'Starting server.py...' && python server.py & wait -n"]
