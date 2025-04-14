# Use Ubuntu as base image
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install python-dotenv so .env loading works
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt python-dotenv

# Copy the rest of the application code
COPY . .

# Expose app port
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
