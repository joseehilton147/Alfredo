# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash alfredo

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py pyproject.toml ./

# Install the package
RUN pip install -e .

# Change ownership to non-root user
RUN chown -R alfredo:alfredo /app

# Switch to non-root user
USER alfredo

# Create necessary directories
RUN mkdir -p /app/data/input /app/data/output /app/data/logs /app/data/temp

# Expose port (if needed for web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import alfredo_ai; print('OK')"

# Default command
CMD ["alfredo", "--help"]
