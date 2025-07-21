"""Utilitários reutilizáveis para testes."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from unittest.mock import Mock, AsyncMock, patch
import pytest

from src.domain.entities.video import Video
from src.domain.exceptions.alfredo_errors import AlfredoError


class TestFileManager:
    """Gerenciador de arquivos para testes."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(tempfile.mkdtemp())
        self.created_files: List[Path] = []
        self.created_dirs: List[Path] = []
    
    def create_test_file(self, filename: str, content: str = "test content") -> Path:
        """Cria arquivo de teste."""
        file_path = self.base_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        self.created_files.append(file_path)
        return file_path
    
    def create_test_video_file(self, filename: str, duration: float = 120.0) -> Path:
        """Cria arquivo de vídeo de teste (fake)."""
        content = f"FAKE_VIDEO_FILE_DURATION_{duration}"
        return self.create_test_file(filename, content)
    
    def create_test_audio_file(self, filename: str, duration: float = 120.0) -> Path:
        """Cria arquivo de áudio de teste (fake)."""
        content = f"FAKE_AUDIO_FILE_DURATION_{duration}"
        return self.create_test_file(filename, content)
    
    def create_test_json_file(self, filename: str, data: Dict[str, Any]) -> Path:
        """Cria arquivo JSON de teste."""
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return self.create_test_file(filename, content)
    
    def create_test_directory(self, dirname: str) -> Path:
        """Cria diretório de teste."""
        dir_path = self.base_dir / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(dir_path)
        return dir_path
    
    def cleanup(self):
        """Remove todos os arquivos e diretórios criados."""
        for file_path in self.created_files:
            if file_path.exists():
                file_path.unlink()
        
        for dir_path in sorted(self.created_dirs, reverse=True):
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class AsyncTestHelper:
    """Helper para testes assíncronos."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Executa corrotina com timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"Operação assíncrona excedeu timeout de {timeout}s")
    
    @staticmethod
    def create_async_mock(return_value=None, side_effect=None):
        """Cria mock assíncrono."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
    
    @staticmethod
    async def collect_async_calls(mock_obj, expected_calls: int, timeout: float = 1.0):
        """Coleta chamadas assíncronas de um mock."""
        start_time = asyncio.get_event_loop().time()
        while len(mock_obj.call_args_list) < expected_calls:
            if asyncio.get_event_loop().time() - start_time > timeout:
                break
            await asyncio.sleep(0.01)
        return mock_obj.call_args_list


class MockBuilder:
    """Builder para criar mocks complexos."""
    
    def __init__(self):
        self.mock = Mock()
        self.async_methods = set()
    
    def add_method(self, name: str, return_value=None, side_effect=None, is_async=False):
        """Adiciona método ao mock."""
        if is_async:
            method_mock = AsyncMock()
            self.async_methods.add(name)
        else:
            method_mock = Mock()
        
        if return_value is not None:
            method_mock.return_value = return_value
        if side_effect is not None:
            method_mock.side_effect = side_effect
        
        setattr(self.mock, name, method_mock)
        return self
    
    def add_property(self, name: str, value):
        """Adiciona propriedade ao mock."""
        type(self.mock).name = Mock(return_value=value)
        return self
    
    def build(self):
        """Constrói o mock final."""
        return self.mock


class TestDataGenerator:
    """Gerador de dados de teste."""
    
    @staticmethod
    def create_video_data(
        id_suffix: str = "123",
        title: str = "Vídeo de Teste",
        duration: float = 120.0,
        **kwargs
    ) -> Dict[str, Any]:
        """Cria dados de vídeo para teste."""
        data = {
            'id': f'test_video_{id_suffix}',
            'title': title,
            'duration': duration,
            'created_at': None,
            'metadata': {}
        }
        data.update(kwargs)
        return data
    
    @staticmethod
    def create_transcription_data(
        text: str = "Transcrição de teste",
        language: str = "pt",
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """Cria dados de transcrição para teste."""
        return {
            'text': text,
            'language': language,
            'confidence': confidence,
            'segments': [
                {'start': 0.0, 'end': 5.0, 'text': text[:20]},
                {'start': 5.0, 'end': 10.0, 'text': text[20:]}
            ]
        }
    
    @staticmethod
    def create_summary_data(
        title: str = "Resumo de Teste",
        summary: str = "Este é um resumo de teste."
    ) -> Dict[str, Any]:
        """Cria dados de resumo para teste."""
        return {
            'title': title,
            'summary': summary,
            'key_points': ['Ponto 1', 'Ponto 2', 'Ponto 3'],
            'language': 'pt'
        }
    
    @staticmethod
    def create_error_scenarios() -> Dict[str, Exception]:
        """Cria cenários de erro para teste."""
        return {
            'generic_error': Exception("Erro genérico"),
            'alfredo_error': AlfredoError("Erro do Alfredo"),
            'file_not_found': FileNotFoundError("Arquivo não encontrado"),
            'connection_error': ConnectionError("Erro de conexão"),
            'timeout_error': TimeoutError("Timeout"),
            'value_error': ValueError("Valor inválido"),
            'type_error': TypeError("Tipo inválido")
        }


class AssertionHelper:
    """Helper para assertions customizadas."""
    
    @staticmethod
    def assert_video_equal(video1: Video, video2: Video, ignore_fields: Optional[List[str]] = None):
        """Compara dois objetos Video ignorando campos específicos."""
        ignore_fields = ignore_fields or []
        
        if 'id' not in ignore_fields:
            assert video1.id == video2.id
        if 'title' not in ignore_fields:
            assert video1.title == video2.title
        if 'duration' not in ignore_fields:
            assert video1.duration == video2.duration
        if 'file_path' not in ignore_fields:
            assert video1.file_path == video2.file_path
        if 'url' not in ignore_fields:
            assert video1.url == video2.url
    
    @staticmethod
    def assert_mock_called_with_video(mock_obj, expected_video: Video):
        """Verifica se mock foi chamado com vídeo específico."""
        mock_obj.assert_called()
        call_args = mock_obj.call_args[0]
        assert len(call_args) > 0
        actual_video = call_args[0]
        AssertionHelper.assert_video_equal(actual_video, expected_video)
    
    @staticmethod
    def assert_file_exists_and_not_empty(file_path: Union[str, Path]):
        """Verifica se arquivo existe e não está vazio."""
        path = Path(file_path)
        assert path.exists(), f"Arquivo não existe: {path}"
        assert path.stat().st_size > 0, f"Arquivo está vazio: {path}"
    
    @staticmethod
    def assert_directory_structure(base_dir: Path, expected_structure: Dict[str, Any]):
        """Verifica estrutura de diretórios."""
        for name, content in expected_structure.items():
            path = base_dir / name
            if isinstance(content, dict):
                assert path.is_dir(), f"Diretório esperado: {path}"
                AssertionHelper.assert_directory_structure(path, content)
            else:
                assert path.is_file(), f"Arquivo esperado: {path}"
                if content is not None:
                    assert path.read_text() == content


class PerformanceTestHelper:
    """Helper para testes de performance."""
    
    @staticmethod
    def measure_execution_time(func: Callable, *args, **kwargs) -> tuple:
        """Mede tempo de execução de função."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    async def measure_async_execution_time(coro) -> tuple:
        """Mede tempo de execução de corrotina."""
        import time
        start_time = time.time()
        result = await coro
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def assert_execution_time_under(execution_time: float, max_time: float):
        """Verifica se tempo de execução está abaixo do limite."""
        assert execution_time < max_time, f"Execução demorou {execution_time:.2f}s, limite: {max_time}s"


class SecurityTestHelper:
    """Helper para testes de segurança."""
    
    @staticmethod
    def get_malicious_inputs() -> Dict[str, List[str]]:
        """Retorna inputs maliciosos para testes."""
        return {
            'sql_injection': [
                "'; DROP TABLE videos; --",
                "1' OR '1'='1",
                "admin'/*"
            ],
            'xss': [
                '<script>alert("xss")</script>',
                'javascript:alert("xss")',
                '<img src="x" onerror="alert(1)">'
            ],
            'path_traversal': [
                '../../../etc/passwd',
                '..\\..\\..\\windows\\system32\\config\\sam',
                '/etc/passwd'
            ],
            'command_injection': [
                '; rm -rf /',
                '| cat /etc/passwd',
                '&& del /f /q C:\\*'
            ]
        }
    
    @staticmethod
    def assert_input_sanitized(original_input: str, sanitized_input: str):
        """Verifica se input foi sanitizado corretamente."""
        malicious_patterns = ['<script', 'javascript:', '../', 'DROP TABLE', 'rm -rf']
        for pattern in malicious_patterns:
            if pattern.lower() in original_input.lower():
                assert pattern.lower() not in sanitized_input.lower(), \
                    f"Padrão malicioso '{pattern}' não foi removido"


# Decorators para testes

def skip_if_no_network():
    """Decorator para pular teste se não há conexão de rede."""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return lambda func: func
    except OSError:
        return pytest.mark.skip(reason="Sem conexão de rede")


def timeout(seconds: float):
    """Decorator para adicionar timeout a testes."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                return await AsyncTestHelper.run_with_timeout(
                    func(*args, **kwargs), 
                    timeout=seconds
                )
        else:
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Teste excedeu timeout de {seconds}s")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(seconds))
                try:
                    return func(*args, **kwargs)
                finally:
                    signal.alarm(0)
        
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 0.1):
    """Decorator para retry em testes flaky."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        import time
                        time.sleep(delay)
                    continue
            raise last_exception
        return wrapper
    return decorator


# Context managers para testes

class MockEnvironment:
    """Context manager para mockar variáveis de ambiente."""
    
    def __init__(self, **env_vars):
        self.env_vars = env_vars
        self.original_values = {}
    
    def __enter__(self):
        import os
        for key, value in self.env_vars.items():
            self.original_values[key] = os.environ.get(key)
            os.environ[key] = value
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import os
        for key, original_value in self.original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


class TemporaryConfig:
    """Context manager para configuração temporária."""
    
    def __init__(self, config_obj, **config_changes):
        self.config_obj = config_obj
        self.config_changes = config_changes
        self.original_values = {}
    
    def __enter__(self):
        for key, value in self.config_changes.items():
            self.original_values[key] = getattr(self.config_obj, key)
            setattr(self.config_obj, key, value)
        return self.config_obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, original_value in self.original_values.items():
            setattr(self.config_obj, key, original_value)