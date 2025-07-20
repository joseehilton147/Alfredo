#!/usr/bin/env python3
"""
Demonstração do sistema de exceções customizadas do Alfredo AI.

Este script mostra como as exceções específicas funcionam e como
podem ser usadas para tratamento de erros mais preciso.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.exceptions import (
    AlfredoError,
    ProviderUnavailableError,
    DownloadFailedError,
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError,
)


def demonstrate_exception_hierarchy():
    """Demonstra a hierarquia de exceções."""
    print("🔍 Demonstração da Hierarquia de Exceções")
    print("=" * 50)
    
    exceptions = [
        AlfredoError("Erro base do sistema"),
        ProviderUnavailableError("whisper", "Modelo não encontrado"),
        DownloadFailedError("https://youtube.com/watch?v=test", "Vídeo privado", 403),
        TranscriptionError("/path/audio.wav", "Arquivo corrompido", "whisper"),
        InvalidVideoFormatError("duration", -10, "deve ser positiva"),
        ConfigurationError("api_key", "não pode ser vazia", "string não vazia"),
    ]
    
    for i, exception in enumerate(exceptions, 1):
        print(f"\n{i}. {exception.__class__.__name__}")
        print(f"   Mensagem: {exception.message}")
        print(f"   É AlfredoError: {isinstance(exception, AlfredoError)}")
        print(f"   Detalhes: {exception.details}")


def demonstrate_exception_serialization():
    """Demonstra serialização de exceções."""
    print("\n\n📄 Demonstração da Serialização de Exceções")
    print("=" * 50)
    
    # Criar exceção com causa
    original_error = FileNotFoundError("Arquivo não encontrado")
    transcription_error = TranscriptionError(
        "/path/audio.wav",
        "Erro ao processar arquivo",
        "whisper",
        details={"file_size": 1024, "duration": 120}
    )
    transcription_error.cause = original_error
    
    # Serializar
    serialized = transcription_error.to_dict()
    
    print("Exceção serializada:")
    for key, value in serialized.items():
        print(f"  {key}: {value}")


def demonstrate_specific_error_handling():
    """Demonstra tratamento específico de erros."""
    print("\n\n🎯 Demonstração do Tratamento Específico de Erros")
    print("=" * 50)
    
    def simulate_download(url: str):
        """Simula download que pode falhar."""
        if "private" in url:
            raise DownloadFailedError(url, "Vídeo privado", 403)
        elif "not-found" in url:
            raise DownloadFailedError(url, "Vídeo não encontrado", 404)
        else:
            return f"Download bem-sucedido: {url}"
    
    def simulate_transcription(audio_path: str):
        """Simula transcrição que pode falhar."""
        if "corrupted" in audio_path:
            raise TranscriptionError(audio_path, "Arquivo corrompido", "whisper")
        elif "unsupported" in audio_path:
            raise TranscriptionError(audio_path, "Formato não suportado", "whisper")
        else:
            return f"Transcrição bem-sucedida: {audio_path}"
    
    # Testar diferentes cenários
    test_cases = [
        ("download", "https://youtube.com/watch?v=private", simulate_download),
        ("download", "https://youtube.com/watch?v=not-found", simulate_download),
        ("download", "https://youtube.com/watch?v=valid", simulate_download),
        ("transcription", "/path/corrupted.wav", simulate_transcription),
        ("transcription", "/path/unsupported.mp3", simulate_transcription),
        ("transcription", "/path/valid.wav", simulate_transcription),
    ]
    
    for operation, input_data, func in test_cases:
        try:
            result = func(input_data)
            print(f"✅ {operation.title()}: {result}")
        except DownloadFailedError as e:
            print(f"❌ Erro de Download: {e.message}")
            print(f"   URL: {e.url}, HTTP: {e.http_code}")
        except TranscriptionError as e:
            print(f"❌ Erro de Transcrição: {e.message}")
            print(f"   Arquivo: {e.audio_path}, Provider: {e.provider}")
        except AlfredoError as e:
            print(f"❌ Erro Geral: {e.message}")


def demonstrate_error_context():
    """Demonstra como o contexto de erro é preservado."""
    print("\n\n🔗 Demonstração do Contexto de Erro")
    print("=" * 50)
    
    def process_video_with_context():
        """Simula processamento que preserva contexto de erro."""
        try:
            # Simular erro de configuração
            raise ValueError("API key inválida")
        except ValueError as e:
            # Converter para exceção específica preservando contexto
            raise ConfigurationError(
                "groq_api_key",
                "Chave de API inválida ou expirada",
                expected="chave válida da Groq",
                details={
                    "provided_key_length": 0,
                    "validation_error": str(e)
                }
            ) from e
    
    try:
        process_video_with_context()
    except ConfigurationError as e:
        print(f"Erro capturado: {e.message}")
        print(f"Configuração: {e.config_key}")
        print(f"Esperado: {e.expected}")
        print(f"Detalhes: {e.details}")
        print(f"Causa original: {e.__cause__}")
        
        # Mostrar serialização completa
        print("\nSerialização completa:")
        serialized = e.to_dict()
        for key, value in serialized.items():
            print(f"  {key}: {value}")


def main():
    """Função principal da demonstração."""
    print("🚀 Demonstração do Sistema de Exceções Customizadas - Alfredo AI")
    print("=" * 70)
    
    demonstrate_exception_hierarchy()
    demonstrate_exception_serialization()
    demonstrate_specific_error_handling()
    demonstrate_error_context()
    
    print("\n\n✨ Demonstração concluída!")
    print("\nVantagens do sistema de exceções customizadas:")
    print("• Tratamento de erros mais preciso e específico")
    print("• Preservação de contexto e detalhes estruturados")
    print("• Serialização automática para logging e debugging")
    print("• Hierarquia clara e extensível")
    print("• Mensagens de erro mais informativas para o usuário")


if __name__ == "__main__":
    main()