# Alfredo AI - Simple Docker Setup
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./

# Install the package
RUN pip install -e .

# Create data directories
RUN mkdir -p /app/data/{input/{local,youtube},output,logs,temp}

# Default command
CMD ["python", "-m", "src.main", "--help"]

# Default command
CMD ["alfredo", "--help"]
