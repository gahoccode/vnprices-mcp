# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for wordcloud and vnstock3
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Make executable
RUN chmod +x server.py

# Metadata
LABEL org.opencontainers.image.title="VNStock MCP Server"
LABEL org.opencontainers.image.description="MCP server for Vietnamese financial data via vnstock3"
LABEL org.opencontainers.image.version="1.0.0"

# Run server
ENTRYPOINT ["python3", "server.py"]