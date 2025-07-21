"""Implementação de extração de áudio usando FFmpeg."""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

from src.application.gateways.audio_extractor_gateway import AudioExtractorGateway, AudioFormat
from src.config.alfredo_config import AlfredoConfig
from src.domain.exceptions.alfredo_errors import (
    TranscriptionError,
    InvalidVideoFormatError,
    ConfigurationError
)


class FFmpegExtractor(AudioExtractorGateway):
    """Implementação de AudioExtractorGateway usando FFmpeg."""
    
    def __init__(self, config: AlfredoConfig):
        """
        Inicializa o extrator.
        
        Args:
            config: Configuração do Alfredo
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Verificar se FFmpeg está disponível
        self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self) -> None:
        """
        Verifica se FFmpeg está disponível no sistema.
        
        Raises:
            ConfigurationError: Se FFmpeg não está disponível
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                raise ConfigurationError(
                    "ffmpeg_availability",
                    "FFmpeg não está funcionando corretamente",
                    expected="FFmpeg instalado e funcionando",
                    details={"stderr": result.stderr}
                )
        except FileNotFoundError:
            raise ConfigurationError(
                "ffmpeg_dependency",
                "FFmpeg não está instalado ou não está no PATH",
                expected="FFmpeg instalado no sistema",
                details={"command": "ffmpeg"}
            )
        except subprocess.TimeoutExpired:
            raise ConfigurationError(
                "ffmpeg_timeout",
                "FFmpeg não respondeu em tempo hábil",
                expected="FFmpeg responsivo",
                details={"timeout": 10}
            )
    
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
        Extrai áudio do vídeo com configurações específicas.
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_path: Caminho de destino do áudio
            format: Formato de saída do áudio
            sample_rate: Taxa de amostragem
            channels: Número de canais (1=mono, 2=stereo)
            bitrate: Taxa de bits para formatos comprimidos
            
        Returns:
            Caminho do arquivo de áudio extraído
            
        Raises:
            TranscriptionError: Quando falha a extração
        """
        try:
            # Converter para Path se necessário
            video_path = Path(video_path)
            output_path = Path(output_path)
            
            # Verificar se arquivo de vídeo existe
            if not video_path.exists():
                raise TranscriptionError(
                    str(video_path),
                    "Arquivo de vídeo não encontrado",
                    details={"video_path": str(video_path), "output_path": str(output_path)}
                )
            
            # Garantir que diretório de saída existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Construir comando FFmpeg
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",  # Sem vídeo
                "-acodec", self._get_audio_codec(format),
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-y",  # Sobrescrever arquivo existente
            ]
            
            # Adicionar bitrate se especificado
            if bitrate and format in [AudioFormat.MP3, AudioFormat.AAC]:
                cmd.extend(["-b:a", bitrate])
            
            cmd.append(str(output_path))
            
            # Executar extração em thread separada
            def extract_sync():
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.config.transcription_timeout
                )
                return result
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, extract_sync)
            
            if result.returncode != 0:
                raise TranscriptionError(
                    str(video_path),
                    f"FFmpeg falhou: {result.stderr}",
                    details={
                        "command": " ".join(cmd),
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                )
            
            # Verificar se arquivo foi criado
            if not output_path.exists():
                raise TranscriptionError(
                    str(video_path),
                    "Arquivo de áudio não foi criado",
                    details={
                        "expected_output": str(output_path),
                        "command": " ".join(cmd)
                    }
                )
            
            self.logger.info(f"Áudio extraído: {output_path}")
            return str(output_path)
            
        except subprocess.TimeoutExpired:
            raise TranscriptionError(
                str(video_path),
                f"Timeout na extração de áudio ({self.config.transcription_timeout}s)",
                details={
                    "timeout": self.config.transcription_timeout,
                    "video_path": str(video_path),
                    "output_path": str(output_path)
                }
            )
        except TranscriptionError:
            # Re-raise exceções específicas
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado na extração: {str(e)}")
            raise TranscriptionError(
                str(video_path),
                f"Erro inesperado: {str(e)}",
                details={
                    "error": str(e),
                    "video_path": str(video_path),
                    "output_path": str(output_path),
                    "format": format.value,
                    "sample_rate": sample_rate
                }
            )
    
    async def get_audio_info(self, video_path: str | Path) -> Dict:
        """
        Obtém informações do áudio sem extrair.
        
        Args:
            video_path: Caminho do arquivo de vídeo
            
        Returns:
            Dicionário com informações do áudio
            
        Raises:
            InvalidVideoFormatError: Quando arquivo é inválido
        """
        try:
            # Converter para Path se necessário
            video_path = Path(video_path)
            
            # Verificar se arquivo existe
            if not video_path.exists():
                raise InvalidVideoFormatError(
                    "video_path",
                    str(video_path),
                    "Arquivo não encontrado"
                )
            
            # Comando para obter informações do áudio
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-select_streams", "a:0",  # Primeiro stream de áudio
                str(video_path)
            ]
            
            def probe_sync():
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, probe_sync)
            
            if result.returncode != 0:
                raise InvalidVideoFormatError(
                    "video_path",
                    str(video_path),
                    f"FFprobe falhou: {result.stderr}"
                )
            
            # Parse do JSON
            probe_data = json.loads(result.stdout)
            
            if not probe_data.get("streams"):
                return {
                    "has_audio": False,
                    "duration": 0.0,
                    "sample_rate": 0,
                    "channels": 0,
                    "codec": "none",
                    "bitrate": 0,
                    "format": "none"
                }
            
            audio_stream = probe_data["streams"][0]
            
            return {
                "has_audio": True,
                "duration": float(audio_stream.get("duration", 0)),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": int(audio_stream.get("channels", 0)),
                "codec": audio_stream.get("codec_name", "unknown"),
                "bitrate": int(audio_stream.get("bit_rate", 0)),
                "format": audio_stream.get("codec_name", "unknown"),
            }
            
        except subprocess.TimeoutExpired:
            raise InvalidVideoFormatError(
                "video_path",
                str(video_path),
                "Timeout ao analisar arquivo (30s)"
            )
        except json.JSONDecodeError as e:
            raise InvalidVideoFormatError(
                "video_path",
                str(video_path),
                f"Erro ao analisar resposta do FFprobe: {str(e)}"
            )
        except InvalidVideoFormatError:
            # Re-raise exceções específicas
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao obter info do áudio: {str(e)}")
            raise InvalidVideoFormatError(
                "video_path",
                str(video_path),
                f"Erro inesperado: {str(e)}"
            )
    
    def _get_audio_codec(self, format: AudioFormat) -> str:
        """
        Converte formato em codec de áudio para FFmpeg.
        
        Args:
            format: Formato desejado
            
        Returns:
            Nome do codec para FFmpeg
        """
        codec_map = {
            AudioFormat.WAV: "pcm_s16le",
            AudioFormat.MP3: "libmp3lame",
            AudioFormat.AAC: "aac",
            AudioFormat.FLAC: "flac",
            AudioFormat.OGG: "libvorbis",
        }
        
        return codec_map.get(format, "pcm_s16le")
    
    async def is_format_supported(self, format: AudioFormat) -> bool:
        """
        Verifica se um formato de áudio é suportado.
        
        Args:
            format: Formato de áudio a ser verificado
            
        Returns:
            bool: True se o formato é suportado, False caso contrário
        """
        supported_formats = await self.get_supported_formats()
        return format in supported_formats
    
    async def get_supported_formats(self) -> List[AudioFormat]:
        """
        Lista todos os formatos de áudio suportados.
        
        Returns:
            list[AudioFormat]: Lista de formatos suportados
        """
        return [
            AudioFormat.WAV,
            AudioFormat.MP3,
            AudioFormat.AAC,
            AudioFormat.FLAC,
            AudioFormat.OGG
        ]
    
    async def validate_video_file(self, video_path: str | Path) -> bool:
        """
        Valida se um arquivo é um vídeo válido e processável.
        
        Args:
            video_path: Caminho para o arquivo a ser validado
            
        Returns:
            bool: True se o arquivo é válido, False caso contrário
        """
        try:
            video_path = Path(video_path)
            
            # Verificar se arquivo existe
            if not video_path.exists():
                return False
            
            # Tentar obter informações do áudio
            await self.get_audio_info(video_path)
            return True
            
        except Exception:
            return False
    
    async def estimate_extraction_time(
        self, 
        video_path: str | Path,
        format: AudioFormat = AudioFormat.WAV
    ) -> float:
        """
        Estima o tempo necessário para extrair o áudio.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            format: Formato de áudio desejado
            
        Returns:
            float: Tempo estimado em segundos
            
        Raises:
            InvalidVideoFormatError: Quando o arquivo não é válido
        """
        try:
            audio_info = await self.get_audio_info(video_path)
            duration = audio_info.get("duration", 0)
            
            # Estimativa baseada no formato e duração
            # WAV é mais rápido, formatos comprimidos são mais lentos
            format_multiplier = {
                AudioFormat.WAV: 0.1,    # 10% da duração
                AudioFormat.MP3: 0.15,   # 15% da duração
                AudioFormat.AAC: 0.15,   # 15% da duração
                AudioFormat.FLAC: 0.2,   # 20% da duração
                AudioFormat.OGG: 0.18,   # 18% da duração
            }
            
            multiplier = format_multiplier.get(format, 0.1)
            estimated_time = duration * multiplier
            
            # Mínimo de 1 segundo, máximo baseado na duração
            return max(1.0, min(estimated_time, duration * 0.5))
            
        except Exception as e:
            raise InvalidVideoFormatError(
                "video_path",
                str(video_path),
                f"Erro ao estimar tempo: {str(e)}"
            )
    
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
        try:
            # Validar tempos
            if start_time < 0 or end_time <= start_time:
                raise InvalidVideoFormatError(
                    "time_range",
                    f"{start_time}-{end_time}",
                    "Tempos inválidos: start_time >= 0 e end_time > start_time"
                )
            
            # Converter para Path se necessário
            video_path = Path(video_path)
            output_path = Path(output_path)
            
            # Verificar se arquivo de vídeo existe
            if not video_path.exists():
                raise TranscriptionError(
                    str(video_path),
                    "Arquivo de vídeo não encontrado"
                )
            
            # Garantir que diretório de saída existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Calcular duração do segmento
            duration = end_time - start_time
            
            # Construir comando FFmpeg para segmento
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-ss", str(start_time),      # Tempo de início
                "-t", str(duration),         # Duração
                "-vn",                       # Sem vídeo
                "-acodec", self._get_audio_codec(format),
                "-ar", str(sample_rate),
                "-ac", "1",                  # Mono
                "-y",                        # Sobrescrever arquivo existente
                str(output_path)
            ]
            
            # Executar extração em thread separada
            def extract_sync():
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.config.transcription_timeout
                )
                return result
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, extract_sync)
            
            if result.returncode != 0:
                raise TranscriptionError(
                    str(video_path),
                    f"FFmpeg falhou na extração do segmento: {result.stderr}",
                    details={
                        "command": " ".join(cmd),
                        "stderr": result.stderr,
                        "start_time": start_time,
                        "end_time": end_time
                    }
                )
            
            # Verificar se arquivo foi criado
            if not output_path.exists():
                raise TranscriptionError(
                    str(video_path),
                    "Arquivo de segmento de áudio não foi criado",
                    details={
                        "expected_output": str(output_path),
                        "start_time": start_time,
                        "end_time": end_time
                    }
                )
            
            self.logger.info(f"Segmento de áudio extraído: {output_path}")
            return str(output_path)
            
        except subprocess.TimeoutExpired:
            raise TranscriptionError(
                str(video_path),
                f"Timeout na extração do segmento ({self.config.transcription_timeout}s)",
                details={
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
        except (TranscriptionError, InvalidVideoFormatError):
            # Re-raise exceções específicas
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado na extração do segmento: {str(e)}")
            raise TranscriptionError(
                str(video_path),
                f"Erro inesperado: {str(e)}",
                details={
                    "start_time": start_time,
                    "end_time": end_time,
                    "format": format.value
                }
            )