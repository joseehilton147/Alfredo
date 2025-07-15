# Project Structure

## Clean Architecture Layers

### Domain Layer (`src/domain/`)
- **entities/** - Core business entities (Video, Transcription)
- **repositories/** - Abstract repository interfaces
- Contains business logic and rules, independent of external concerns

### Application Layer (`src/application/`)
- **use_cases/** - Application-specific business rules and orchestration
- **interfaces/** - Abstract interfaces for external dependencies
- Coordinates between domain and infrastructure layers

### Infrastructure Layer (`src/infrastructure/`)
- **providers/** - External service implementations (WhisperProvider)
- **repositories/** - Concrete repository implementations (JsonVideoRepository)
- Handles external dependencies and data persistence

### Configuration (`src/config/`)
- **settings.py** - Application configuration and environment variables

## Data Organization (`data/`)
```
data/
├── input/
│   ├── local/      # Local video files
│   └── youtube/    # Downloaded YouTube videos
├── output/         # Processed results and transcriptions
├── logs/           # Application logs
├── temp/           # Temporary processing files
└── cache/          # Cached data (if enabled)
```

## Testing Structure (`tests/`)
- Mirror the `src/` structure for easy navigation
- **conftest.py** - Shared test configuration and fixtures
- Separate test files for each module
- 100% test coverage target

## Key Files
- **src/main.py** - Application entry point and CLI interface
- **requirements.txt** - Production dependencies
- **requirements-dev.txt** - Development dependencies
- **Makefile** - Build and development commands
- **Dockerfile** - Container configuration
- **docker-compose.yml** - Multi-container setup
- **.env.example** - Environment configuration template

## Naming Conventions
- **Snake_case** for Python files, functions, and variables
- **PascalCase** for classes
- **UPPER_CASE** for constants and environment variables
- Descriptive names that reflect business domain

## Import Organization
- Standard library imports first
- Third-party imports second
- Local application imports last
- Use absolute imports from `src/` root

## File Organization Rules
- One class per file in most cases
- Group related functionality in modules
- Keep files focused and cohesive
- Use `__init__.py` files to control public interfaces
