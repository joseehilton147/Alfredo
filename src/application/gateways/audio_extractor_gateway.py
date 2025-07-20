"""
Gateway para extração de áudio de vídeos.

Este módulo define a interface abstrata para extração de áudio de arquivos de vídeo,
seguindo os princípios da Clean Architecture onde a camada de aplicação define
contratos que a infraestrutura deve implementar.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path
from enum import Enum


class AudioFormat(Enum):
    """Formatos de áudio suportados para extração."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"


class AudioExtractorGateway(ABC):
    """
    Interface abstrata para extração de áudio de vídeos.
    
    Esta interface define os contratos que implementações concretas de extração
    de áudio devem seguir, permitindo isolamento da infraestrutura e facilitando
    testes através de mocks.
    """

    @abstractmethod
    async def extract_audio(
        self,
        video_path: str | Path,
        output_path: str | Path,
        format: AudioFormat = AudioFormat.WAV,
        sample_rate: int = 16000,
        channels: int = 1,
        bitrate: Optional[str] = None
    ) -> str:
        """
        Extrai áudio de um arquivo de vídeo.
        
        Args:
            video_path: Caminho para o arquivo de vídeo de origem
            output_path: Caminho onde o arquivo de áudio será salvo
            format: Formato do áudio de saída (padrão: WAV)
            sample_rate: Taxa de amostragem em Hz (padrão: 16000)
            channels: Número de canais de áudio (1=mono, 2=stereo)
            bitrate: Taxa de bits para formatos comprimidos (ex: "128k")
            
        Returns:
            str: Caminho completo do arquivo de áudio extraído
            
        Raises:
            TranscriptionError: Quando a extração de áudio falha
            InvalidVideoFormatError: Quando o arquivo de vídeo não é válido
            ConfigurationError: Quando há problemas de configuração
        """
        pass

    @abstractmethod
    async def get_audio_info(self, video_path: str | Path) -> Dict:
        """
        Obtém informações sobre o áudio do vídeo sem extrair.
        
        Útil para validar se o vídeo tem áudio e obter metadados
        antes de decidir fazer a extração.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            Dict: Dicionário com informações do áudio:
                - has_audio: bool - Se o vídeo tem áudio
                - duration: float - Duração do áudio em segundos
                - sample_rate: int - Taxa de amostragem original
                - channels: int - Número de canais
                - codec: str - Codec de áudio usado
                - bitrate: int - Taxa de bits em bps
                - format: str - Formato do container de áudio
                
        Raises:
            InvalidVideoFormatError: Quando o arquivo não é um vídeo válido
            TranscriptionError: Quando não é possível acessar o arquivo
        """
        pass

    @abstractmethod
    async def is_format_supported(self, format: AudioFormat) -> bool:
        """
        Verifica se um formato de áudio é suportado.
        
        Args:
            format: Formato de áudio a ser verificado
            
        Returns:
            bool: True se o formato é suportado, False caso contrário
        """
        pass

    @abstractmethod
    async def get_supported_formats(self) -> list[AudioFormat]:
        """
        Lista todos os formatos de áudio suportados.
        
        Returns:
            list[AudioFormat]: Lista de formatos suportados
        """
        pass

    @abstractmethod
    async def validate_video_file(self, video_path: str | Path) -> bool:
        """
        Valida se um arquivo é um vídeo válido e processável.
        
        Args:
            video_path: Caminho para o arquivo a ser validado
            
        Returns:
            bool: True se o arquivo é válido, False caso contrário
        """
        pass

    @abstractmethod
    async def estimate_extraction_time(
        self, 
        video_path: str | Path,
        format: AudioFormat = AudioFormat.WAV
    ) -> float:
        """
        Estima o tempo necessário para extrair o áudio.
        
        Útil para mostrar progresso estimado ao usuário.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            format: Formato de áudio desejado
            
        Returns:
            float: Tempo estimado em segundos
            
        Raises:
            InvalidVideoFormatError: Quando o arquivo não é válido
        """
        pass

    @abstractmethod
    async def extract_audio_segment(
        self,
        video_path: str | Path,
        output_path: str | Path,
        start_time: float,
        end_time: float,
        format: AudioFormat = AudioFormat.WAV,
        sample_rate: int = 16000
    ) -> str:
        """
        Extrai um segmento específico do áudio.
        
        Útil para processar vídeos longos em partes ou extrair
        apenas trechos específicos.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            output_path: Caminho onde o segmento será salvo
            start_time: Tempo de início em segundos
            end_time: Tempo de fim em segundos
            format: Formato do áudio de saída
            sample_rate: Taxa de amostragem
            
        Returns:
            str: Caminho do arquivo de áudio do segmento
            
        Raises:
            TranscriptionError: Quando a extração falha
            InvalidVideoFormatError: Quando os tempos são inválidos
        """
        pass