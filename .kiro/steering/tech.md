# Technology Stack

## Core Technologies
- **Python 3.8+** - Primary programming language
- **OpenAI Whisper** - AI transcription engine
- **yt-dlp** - YouTube video downloading
- **FFmpeg** - Audio/video processing (system dependency)

## Architecture Pattern
- **Clean Architecture** with clear separation of concerns:
  - Domain layer (entities, business rules)
  - Application layer (use cases, interfaces)
  - Infrastructure layer (external providers, repositories)

## Development Tools
- **pytest** - Testing framework with async support
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pre-commit** - Git hooks for code quality

## Build & Deployment
- **setuptools** - Package management
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **Makefile** - Build automation

## Common Commands

### Development Setup
```bash
make setup          # Complete project setup
make install-dev    # Install dev dependencies
make format         # Format code (black + isort)
make lint           # Run all linters
```

### Testing
```bash
make test           # Run tests with coverage
pytest              # Direct pytest execution
pytest --cov=src    # Coverage report
```

### Running the Application
```bash
# Local video processing
python -m src.main -i path/to/video.mp4

# YouTube video processing
python -m src.main -u "https://youtube.com/watch?v=VIDEO_ID"

# Batch processing
python -m src.main -b directory/with/videos/

# With language specification
python -m src.main -i video.mp4 -l en
```

### Docker Usage
```bash
make docker-build   # Build Docker image
make docker-run     # Run in container
docker-compose up   # Start services
```

## Configuration
- Environment variables via `.env` file
- Default language: Portuguese (`pt`)
- Whisper model: `base` (configurable)
- Data directories auto-created under `data/`
