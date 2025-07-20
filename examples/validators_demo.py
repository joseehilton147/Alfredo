#!/usr/bin/env python3
"""
Demonstração dos validadores de domínio do Alfredo AI.

Este exemplo mostra como usar os validadores para garantir
que dados atendam às regras de negócio antes de criar entidades.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.domain.validators import (
    # Validadores de vídeo
    validate_video_id,
    validate_video_title,
    validate_video_duration,
    validate_video_sources,
    # Validadores de URL
    validate_url_format,
    is_youtube_url,
    is_supported_video_url,
    extract_youtube_video_id,
    validate_youtube_url,
)
from src.domain.exceptions import InvalidVideoFormatError


def demonstrate_video_validators():
    """Demonstra validadores específicos para vídeos."""
    print("🎬 Demonstração dos Validadores de Vídeo")
    print("=" * 50)
    
    # Teste de IDs de vídeo
    print("\n1. Validação de ID de Vídeo:")
    test_ids = [
        ("video_123", True),
        ("my-video-2024", True),
        ("", False),  # Vazio
        ("video with spaces", False),  # Espaços
        ("a" * 256, False),  # Muito longo
    ]
    
    for video_id, should_pass in test_ids:
        try:
            validate_video_id(video_id)
            result = "✅ VÁLIDO" if should_pass else "❌ DEVERIA FALHAR"
            print(f"   '{video_id}' -> {result}")
        except InvalidVideoFormatError as e:
            result = "❌ INVÁLIDO" if not should_pass else "✅ DEVERIA PASSAR"
            print(f"   '{video_id}' -> {result} ({e.constraint})")
    
    # Teste de títulos
    print("\n2. Validação de Título:")
    test_titles = [
        ("Meu Vídeo Incrível", True),
        ("Tutorial: Python 🐍", True),
        ("", False),  # Vazio
        ("   ", False),  # Apenas espaços
        ("a" * 501, False),  # Muito longo
    ]
    
    for title, should_pass in test_titles:
        try:
            validate_video_title(title)
            result = "✅ VÁLIDO" if should_pass else "❌ DEVERIA FALHAR"
            display_title = title[:30] + "..." if len(title) > 30 else title
            print(f"   '{display_title}' -> {result}")
        except InvalidVideoFormatError as e:
            result = "❌ INVÁLIDO" if not should_pass else "✅ DEVERIA PASSAR"
            display_title = title[:30] + "..." if len(title) > 30 else title
            print(f"   '{display_title}' -> {result} ({e.constraint})")
    
    # Teste de duração
    print("\n3. Validação de Duração:")
    test_durations = [
        (0, True),      # Zero permitido
        (120.5, True),  # Normal
        (3600, True),   # 1 hora
        (-10, False),   # Negativa
        (90000, False), # Mais de 24 horas
    ]
    
    for duration, should_pass in test_durations:
        try:
            validate_video_duration(duration)
            result = "✅ VÁLIDO" if should_pass else "❌ DEVERIA FALHAR"
            print(f"   {duration}s -> {result}")
        except InvalidVideoFormatError as e:
            result = "❌ INVÁLIDO" if not should_pass else "✅ DEVERIA PASSAR"
            print(f"   {duration}s -> {result} ({e.constraint})")


def demonstrate_url_validators():
    """Demonstra validadores específicos para URLs."""
    print("\n\n🌐 Demonstração dos Validadores de URL")
    print("=" * 50)
    
    # Teste de formato de URL
    print("\n1. Validação de Formato de URL:")
    test_urls = [
        ("https://youtube.com/watch?v=123", True),
        ("http://example.com/video", True),
        ("youtube.com", False),  # Sem protocolo
        ("ftp://example.com", False),  # Protocolo não suportado
        ("https://", False),  # Sem domínio
    ]
    
    for url, should_pass in test_urls:
        try:
            validate_url_format(url)
            result = "✅ VÁLIDO" if should_pass else "❌ DEVERIA FALHAR"
            print(f"   '{url}' -> {result}")
        except InvalidVideoFormatError as e:
            result = "❌ INVÁLIDO" if not should_pass else "✅ DEVERIA PASSAR"
            print(f"   '{url}' -> {result} ({e.constraint})")
    
    # Teste de detecção do YouTube
    print("\n2. Detecção de URLs do YouTube:")
    youtube_urls = [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://vimeo.com/123456",  # Não YouTube
        "https://example.com",  # Não YouTube
    ]
    
    for url in youtube_urls:
        is_yt = is_youtube_url(url)
        icon = "✅" if is_yt else "❌"
        print(f"   {icon} '{url}' -> {'YouTube' if is_yt else 'Não YouTube'}")
    
    # Teste de extração de ID
    print("\n3. Extração de ID do YouTube:")
    for url in youtube_urls[:4]:  # Apenas URLs do YouTube
        video_id = extract_youtube_video_id(url)
        if video_id:
            print(f"   ✅ '{url}' -> ID: {video_id}")
        else:
            print(f"   ❌ '{url}' -> Não conseguiu extrair ID")
    
    # Teste de plataformas suportadas
    print("\n4. Verificação de Plataformas Suportadas:")
    platform_urls = [
        "https://youtube.com/watch?v=123",
        "https://youtu.be/123",
        "https://vimeo.com/123",
        "https://dailymotion.com/123",
    ]
    
    for url in platform_urls:
        is_supported = is_supported_video_url(url)
        icon = "✅" if is_supported else "❌"
        status = "Suportada" if is_supported else "Não suportada"
        print(f"   {icon} '{url}' -> {status}")


def demonstrate_video_sources_validation():
    """Demonstra validação de fontes de vídeo."""
    print("\n\n📁 Demonstração da Validação de Fontes")
    print("=" * 50)
    
    # Criar arquivo de exemplo para teste
    example_file = Path("examples/sample_video.mp4")
    if not example_file.exists():
        example_file.touch()  # Criar arquivo vazio para teste
        print(f"   📝 Arquivo de exemplo criado: {example_file}")
    
    test_cases = [
        # (file_path, url, should_pass, description)
        (str(example_file), None, True, "Apenas arquivo válido"),
        (None, "https://youtube.com/watch?v=123", True, "Apenas URL válida"),
        (str(example_file), "https://youtube.com/watch?v=123", True, "Ambos válidos"),
        (None, None, False, "Nenhuma fonte"),
        ("inexistente.mp4", None, False, "Arquivo não existe"),
        (None, "url-inválida", False, "URL inválida"),
    ]
    
    for file_path, url, should_pass, description in test_cases:
        try:
            validate_video_sources(file_path, url)
            result = "✅ VÁLIDO" if should_pass else "❌ DEVERIA FALHAR"
            print(f"   {description} -> {result}")
        except InvalidVideoFormatError as e:
            result = "❌ INVÁLIDO" if not should_pass else "✅ DEVERIA PASSAR"
            print(f"   {description} -> {result} ({e.constraint})")
    
    # Limpar arquivo de exemplo
    if example_file.exists():
        example_file.unlink()
        print(f"   🗑️ Arquivo de exemplo removido")


def demonstrate_practical_usage():
    """Demonstra uso prático dos validadores."""
    print("\n\n💡 Demonstração de Uso Prático")
    print("=" * 50)
    
    # Simular criação de entidade Video
    print("\n1. Criação de Entidade Video com Validação:")
    
    video_data = {
        "id": "tutorial_python_2024",
        "title": "Tutorial Completo de Python",
        "duration": 3600.0,  # 1 hora
        "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
    }
    
    try:
        # Validar todos os campos
        validate_video_id(video_data["id"])
        print("   ✅ ID válido")
        
        validate_video_title(video_data["title"])
        print("   ✅ Título válido")
        
        validate_video_duration(video_data["duration"])
        print("   ✅ Duração válida")
        
        validate_url_format(video_data["url"])
        print("   ✅ URL válida")
        
        if is_youtube_url(video_data["url"]):
            print("   ✅ URL do YouTube detectada")
            video_id = extract_youtube_video_id(video_data["url"])
            print(f"   ✅ ID extraído: {video_id}")
        
        print("   🎉 Todos os dados são válidos! Entidade pode ser criada.")
        
    except InvalidVideoFormatError as e:
        print(f"   ❌ Erro de validação: {e.message}")
        print(f"   📋 Campo: {e.field}")
        print(f"   📋 Valor: {e.value}")
        print(f"   📋 Restrição: {e.constraint}")
    
    # Demonstrar tratamento de erro
    print("\n2. Tratamento de Erro de Validação:")
    
    invalid_data = {
        "id": "",  # ID inválido
        "title": "a" * 501,  # Título muito longo
        "duration": -10,  # Duração negativa
    }
    
    for field, value in invalid_data.items():
        try:
            if field == "id":
                validate_video_id(value)
            elif field == "title":
                validate_video_title(value)
            elif field == "duration":
                validate_video_duration(value)
        except InvalidVideoFormatError as e:
            print(f"   ❌ {field}: {e.constraint}")
            
            # Mostrar serialização para logging
            error_dict = e.to_dict()
            print(f"   📊 Dados para log: {error_dict}")


def main():
    """Função principal da demonstração."""
    print("🔍 Demonstração dos Validadores de Domínio - Alfredo AI")
    print("=" * 70)
    
    demonstrate_video_validators()
    demonstrate_url_validators()
    demonstrate_video_sources_validation()
    demonstrate_practical_usage()
    
    print("\n\n✨ Demonstração concluída!")
    print("\nBenefícios dos validadores de domínio:")
    print("• Garantem integridade dos dados desde a criação")
    print("• Fornecem mensagens de erro específicas e úteis")
    print("• São reutilizáveis em diferentes contextos")
    print("• Facilitam testes e debugging")
    print("• Mantêm regras de negócio centralizadas")


if __name__ == "__main__":
    main()