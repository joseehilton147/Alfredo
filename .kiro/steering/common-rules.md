# Common Rules - Alfredo AI Project

Quando estiver executando as tarefas de uma spec, antes de marcar a tarefa principal como concluida, revise se toda as subtarefas foram implementadas corretamente, se sim, marque como concluido, se não, ajuste o que for necessário antes de marcar como concluida.

## 1. Language and Communication

### Responses and Documentation

- **ALWAYS** respond in Brazilian Portuguese
- Use appropriate but accessible technical language
- Explain complex concepts clearly
- Include practical examples when relevant

### Code Comments

- Comments in Brazilian Portuguese when necessary
- Prioritize self-explanatory code over excessive comments
- Document important architectural decisions
- Use Portuguese docstrings for public functions

```python
def processar_video_youtube(url: str) -> Summary:
    """
    Processa um vídeo do YouTube gerando transcrição e resumo.
    
    Args:
        url: URL válida do vídeo do YouTube
        
    Returns:
        Summary: Objeto contendo transcrição e resumo gerado
        
    Raises:
        DownloadFailedError: Quando falha o download do vídeo
        TranscriptionError: Quando falha a transcrição do áudio
    """
    pass
```

## 2. Naming Conventions

### Variables and Functions

- **snake_case** for variables, functions and methods
- English names to maintain international compatibility
- Use verbs for functions: `get_lista_usuarios()`, `create_video_summary()`
- Use nouns for variables: `video_duration`, `transcription_text`

```python
# ✅ Correct
def get_lista_videos() -> List[Video]:
    video_count = len(videos)
    return processed_videos

# ❌ Incorrect  
def getListaVideos() -> List[Video]:
    videoCount = len(videos)
    return processedVideos
```

### Classes and Types

- **PascalCase** for classes and types
- Descriptive names that reflect the business domain
- Use appropriate suffixes: `Gateway`, `Provider`, `UseCase`, `Error`

```python
# ✅ Correct
class VideoDownloaderGateway(ABC):
    pass

class SummarizeYoutubeVideoUseCase:
    pass

class TranscriptionError(AlfredoError):
    pass
```

### Constants and Configuration

- **UPPER_CASE** for constants
- Group in configuration classes when appropriate

```python
# ✅ Correct
MAX_VIDEO_DURATION = 3600
DEFAULT_WHISPER_MODEL = "base"

@dataclass
class AlfredoConfig:
    groq_model: str = "llama-3.3-70b-versatile"
    max_retries: int = 3
```

## 3. MCP Tools Usage

### Context7 for Documentation

- **ALWAYS** use MCP Context7 to search for library documentation
- Resolve library IDs before searching documentation
- Check official documentation before implementing
- Stay updated with latest library versions

```python
# Example: search FastAPI documentation
# 1. Resolve library ID: resolve_library_id("fastapi")
# 2. Get docs: get_library_docs("/tiangolo/fastapi")
```

### Memory Manager for Context and Tasks

- **ALWAYS** use to save important architectural decisions
- Register identified patterns and implemented solutions
- Maintain history of refactorings and improvements
- Create and manage project tasks
- Get memory context for work continuity

```python
# Memory Manager usage examples:
# - create_task("Implement Clean Architecture", "refactoring", "high")
# - get_memory_context("clean architecture")
# - get_project_summary() for project overview
```

### AWS Labs for AWS Documentation

- Use to consult official AWS documentation
- Get updated information about AWS services
- Consult best practices and implementation examples
- **IMPORTANT**: Do not discuss company implementation details on AWS

### Sequential Thinking for Complex Problems

- Use for complex architectural problem analysis
- Break large refactorings into smaller steps
- Plan implementations with multiple dependencies
- Review and adjust approaches during development

```python
# Example: use to plan Clean Architecture refactoring
# - Analyze current structure
# - Identify dependencies
# - Plan implementation order
# - Verify each step before proceeding
```

### Playwright Browser for E2E Testing

- Use for web interface testing (if applicable)
- Automate web page interactions
- Capture screenshots for documentation
- Validate web application behavior

### Serper Search for Research and Web Scraping

- Search for updated technical information
- Find implementation examples
- Check trends and best practices
- Scrape documentation when necessary

```python
# Example: search Clean Architecture patterns in Python
# google_search("Clean Architecture Python patterns", "us", "en")
```

### Fetch for API Access and Web Resources

- Fetch online documentation
- Access APIs to validate integrations
- Get external resources needed for the project
- Check external service status

## 3.1. MCP Usage Guidelines

### When to Use Each MCP

**Context7**:

- Whenever you need Python library documentation
- Before implementing integrations with external libraries
- To check available APIs and methods

**Memory Manager**:

- At the beginning of each session to get context
- When making important architectural decisions
- To create and track development tasks
- When finishing implementations to register learnings

**Sequential Thinking**:

- For complex refactoring problems
- When you need to plan multi-step implementations
- For architecture and design pattern analysis
- When there are multiple possible approaches

**Serper Search**:

- To search for current best practices
- When you need implementation examples
- To check trends and technological news
- To find solutions for specific problems

**AWS Labs**:

- Only when working with AWS services
- To consult official AWS documentation
- To check AWS configurations and best practices

**Playwright Browser**:

- For automated web interface testing
- To capture visual evidence of functionalities
- To automate complex page interactions

**Fetch**:

- To access documentation not available in Context7
- To check external APIs
- To get specific web resources

### Information Search Priority Order

1. **Memory Manager** - Check existing context and knowledge
2. **Context7** - For Python library documentation
3. **Sequential Thinking** - For complex problem analysis
4. **Serper Search** - For general information and examples
5. **Fetch** - For specific resources not found previously
6. **AWS Labs** - Only for AWS-specific questions

### MCP Integration

- Use **Memory Manager** to save insights obtained via other MCPs
- Combine **Sequential Thinking** with **Context7** to plan implementations
- Use **Serper Search** to validate approaches found in **Context7**
- Register best practices discovered in **Memory Manager**

### Practical Integration Examples - Alfredo Project

#### Scenario 1: Implementing new library integration

```python
# 1. Memory Manager - check existing context
get_memory_context("audio library integration")

# 2. Context7 - search documentation
resolve_library_id("pydub")
get_library_docs("/jiaaro/pydub", topic="audio processing")

# 3. Sequential Thinking - plan implementation
# Analyze: requirements → design → implementation → tests

# 4. Memory Manager - save decision
create_task("Implement AudioProcessor with pydub", "feature", "medium")
```

#### Scenario 2: Complex architectural refactoring

```python
# 1. Memory Manager - get project context
get_project_summary()

# 2. Sequential Thinking - break problem into steps
# Analyze current structure → identify dependencies → plan migration

# 3. Serper Search - search Clean Architecture examples
google_search("Clean Architecture Python examples", "us", "en")

# 4. Memory Manager - register action plan
create_task("Refactor to Clean Architecture - Phase 1", "refactoring", "high")
```

#### Scenario 3: Debugging and problem solving

```python
# 1. Memory Manager - check similar problems
get_memory_context("transcription timeout error")

# 2. Context7 - check library documentation
get_library_docs("/openai/whisper", topic="timeout configuration")

# 3. Serper Search - search community solutions
google_search("whisper timeout error python solution", "us", "en")

# 4. Sequential Thinking - analyze possible solutions
# Compare approaches → test solution → validate result

# 5. Memory Manager - document solution
create_task("Implement configurable timeout for Whisper", "bugfix", "high")
```

## 4. Alfredo-Specific Development Patterns

### Command Structure

- All commands must follow the `COMMAND_INFO` registration pattern
- Separate presentation logic from business logic
- Use dependency injection for external components

```python
COMMAND_INFO = {
    "name": "resumir-audio-local",
    "description": "🎧 Local audio quick analysis",
    "function": "main",
    "help": "Process only video audio for transcription and summary",
    "category": "video"
}

async def main():
    # Only presentation logic here
    args = parse_arguments()
    use_case = create_audio_analysis_use_case()
    result = await use_case.execute(args.file_path)
    display_result(result)
```

### Error Handling

- Use custom exception hierarchy
- Catch specific errors in presentation layer
- Display user-friendly messages

```python
try:
    summary = await use_case.execute(url)
    print(f"✅ Summary saved: {summary.file_path}")
except DownloadFailedError as e:
    print(f"❌ Download error: {e}")
except TranscriptionError as e:
    print(f"❌ Transcription error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    logger.error(f"Unhandled error: {e}", exc_info=True)
```

### Configuration and Paths

- Use `AlfredoPaths` class for path management
- Centralize configurations in typed classes
- Validate configurations at initialization

```python
# ✅ Use centralized paths
from config.paths import paths

output_path = paths.get_output_summary_path(video_name, "youtube")

# ✅ Use typed configuration
config = AlfredoConfig()
ai_provider = get_ai_provider(config.default_provider)
```

## 5. Quality and Testing

### Test Coverage

- Minimum 80% coverage for new code
- Unit tests for Use Cases are mandatory
- Use mocks for external dependencies
- Integration tests for complete flows

### Static Analysis

- Run `black` for formatting before commits
- Use `flake8` or `pylint` for code analysis
- Check types with `mypy` when possible
- Run `bandit` for security analysis

### Performance

- Monitor execution time of long operations
- Use progress bars for user feedback
- Implement appropriate timeouts for network operations
- Optimize memory usage for large videos

## 6. Security and Best Practices

### Input Validation

- Validate all URLs before processing
- Check supported file formats
- Sanitize file names to avoid path traversal
- Limit maximum size of processed files

### Resource Management

- Clean temporary files after processing
- Implement rate limiting for external APIs
- Use context managers for resources that need to be closed
- Monitor disk and memory usage

### Logging and Monitoring

- Use structured logging with appropriate levels
- Do not log sensitive information (API keys, full paths)
- Implement basic usage metrics
- Maintain error logs for debugging

```python
import logging

logger = logging.getLogger(__name__)

async def process_video(video_path: str) -> Summary:
    logger.info(f"Starting video processing: {Path(video_path).name}")
    
    try:
        # Processing
        result = await do_processing(video_path)
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        raise
```

## 7. Integration and Deployment

### Development Environment

- Use `.env` for local configurations
- Keep `.env.example` updated
- Document system dependencies (ffmpeg, etc.)
- Use virtual environments for isolation

### Versioning

- Follow Semantic Versioning (SemVer)
- Keep CHANGELOG.md updated
- Use tags for releases
- Document breaking changes

### Compatibility

- Support Python 3.8+ as specified
- Test on different operating systems
- Maintain compatibility with LTS versions of dependencies
- Document minimum system requirements
