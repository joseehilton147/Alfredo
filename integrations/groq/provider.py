import os
import asyncio
import time
import sys
import groq
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integrations.ai_provider import AIProvider
from legacy.services_old.prompt_service import get_summary_prompt
from integrations.groq.monitor import groq_monitor

def safe_print(text, end="\n", flush=False):
    """Função para imprimir texto sem problemas de encoding no Windows"""
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais, mantém apenas ASCII
        import re
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        print(text, end=end, flush=flush)

class GroqProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError('GROQ_API_KEY não encontrada nas variáveis de ambiente')
        self.client = groq.AsyncGroq(api_key=api_key)
        
        # Limites do Groq conforme documentação
        self.MAX_FILE_SIZE_FREE = 40 * 1024 * 1024  # 40MB free tier
        self.MAX_FILE_SIZE_DEV = 100 * 1024 * 1024  # 100MB dev tier
        self.SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.ogg', '.wav', '.webm', '.flac'}

    def _validate_audio_file(self, audio_path: str) -> tuple[bool, str]:
        """Valida o arquivo de áudio conforme limitações do Groq"""
        path = Path(audio_path)
        
        # Verificar se arquivo existe
        if not path.exists():
            return False, f"Arquivo não encontrado: {audio_path}"
        
        # Verificar formato
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"Formato não suportado: {path.suffix}. Formatos aceitos: {', '.join(self.SUPPORTED_FORMATS)}"
        
        # Verificar tamanho
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE_FREE:  # Assumindo free tier
            size_mb = file_size / (1024 * 1024)
            return False, f"Arquivo muito grande: {size_mb:.1f}MB. Máximo: 40MB (free tier) ou 100MB (dev tier)"
        
        return True, "OK"

    async def transcribe(self, audio_path: str) -> str:
        """Transcreve áudio usando Groq Whisper com tratamento de erros otimizado"""
        
        # Validar arquivo antes de enviar
        is_valid, validation_msg = self._validate_audio_file(audio_path)
        if not is_valid:
            raise RuntimeError(f'Erro de validação: {validation_msg}')
        
        # Verificar rate limits antes de fazer a requisição
        audio_duration = self._estimate_audio_duration(audio_path)
        limits_check = groq_monitor.check_rate_limits(audio_seconds=audio_duration)
        
        safe_print(f"📊 Verificação de limites para áudio de {audio_duration:.1f}s:")
        safe_print(f"   Pode fazer requisição: {limits_check['can_make_request']}")
        safe_print(f"   Pode usar áudio: {limits_check['can_use_audio']}")
        
        if not limits_check['can_make_request']:
            wait_time = groq_monitor.wait_for_rate_limit('request')
            raise RuntimeError(f'Rate limit de requisições atingido. Aguarde {wait_time:.0f} segundos.')
        
        if not limits_check['can_use_audio']:
            current_hour = limits_check["current_usage"]["audio_seconds_per_hour"]
            current_day = limits_check["current_usage"]["audio_seconds_per_day"]
            billed_seconds = limits_check.get('billed_audio_seconds', audio_duration)
            
            raise RuntimeError(
                f'Limite de áudio atingido!\n'
                f'Uso atual: {current_hour:.0f}s/hora ({groq_monitor.rate_limits["audio_seconds_per_hour"]}s máx)\n'
                f'Uso diário: {current_day:.0f}s/dia ({groq_monitor.rate_limits["audio_seconds_per_day"]}s máx)\n'
                f'Tentativa: {billed_seconds:.0f}s (incluindo faturamento mínimo de 10s)'
            )
        
        # Retry com backoff exponencial para rate limits
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                with open(audio_path, 'rb') as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model='whisper-large-v3-turbo',  # Modelo mais rápido conforme docs
                        file=audio_file,
                        language='pt',  # Especificar idioma melhora accuracy e latency
                        response_format='text',  # Formato simples para melhor performance
                        temperature=0.0  # Determinístico para transcrições
                    )
                
                # Registrar uso bem-sucedido
                groq_monitor.record_request(audio_seconds=audio_duration)
                
                return response
                
            except groq.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f'Rate limit atingido após {max_retries} tentativas: {e}')
                
                delay = base_delay * (2 ** attempt)
                safe_print(f'⏳ Rate limit atingido, aguardando {delay}s antes de tentar novamente...')
                await asyncio.sleep(delay)
                
            except groq.BadRequestError as e:
                # Erro 413 - Content Too Large
                if "413" in str(e) or "too large" in str(e).lower():
                    file_size = Path(audio_path).stat().st_size / (1024 * 1024)
                    raise RuntimeError(f'Arquivo muito grande para a API Groq ({file_size:.1f}MB). '
                                     f'Use arquivos menores que 40MB ou considere dividir o áudio em chunks.')
                else:
                    raise RuntimeError(f'Erro na requisição Groq: {e}')
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f'Erro na transcrição Groq após {max_retries} tentativas: {e}')
                
                delay = base_delay * (2 ** attempt)
                safe_print(f'🔄 Erro temporário, tentando novamente em {delay}s...')
                await asyncio.sleep(delay)
    
    def _estimate_audio_duration(self, audio_path: str) -> float:
        """Estima duração do áudio para controle de rate limits com base na documentação Groq"""
        try:
            import os
            
            # Obter informações do arquivo
            file_size = Path(audio_path).stat().st_size
            file_ext = Path(audio_path).suffix.lower()
            
            # Estimativas mais precisas baseadas na documentação Groq
            if file_ext in ['.flac']:
                # FLAC: ~1MB por minuto de áudio de alta qualidade
                estimated_duration = file_size / (1024 * 1024) * 60
            elif file_ext in ['.mp3', '.m4a']:
                # MP3/M4A: ~128kbps padrão
                estimated_duration = file_size / (128 * 1024 / 8)
            elif file_ext in ['.wav']:
                # WAV: ~10MB por minuto (sem compressão)
                estimated_duration = file_size / (10 * 1024 * 1024) * 60
            elif file_ext in ['.mp4', '.webm']:
                # Arquivos de vídeo: estimar apenas o áudio (~64kbps)
                estimated_duration = file_size / (64 * 1024 / 8)
            else:
                # Fallback genérico
                estimated_duration = file_size / (96 * 1024 / 8)  # 96kbps médio
            
            # Aplicar faturamento mínimo do Groq: 10 segundos
            estimated_duration = max(estimated_duration, 10.0)
            
            # Máximo razoável: 1 hora
            estimated_duration = min(estimated_duration, 3600.0)
            
            safe_print(f"📊 Duração estimada do áudio: {estimated_duration:.1f}s (arquivo: {file_size / (1024*1024):.1f}MB)")
            return estimated_duration
            
        except Exception as e:
            safe_print(f"⚠️ Erro ao estimar duração do áudio: {e}")
            # Fallback: 30 segundos (mais realista que 5 minutos)
            return 30.0

    async def summarize(self, transcription: str, video_title: str) -> str:
        """Sumariza transcrição usando Groq com configurações otimizadas"""
        final_prompt = get_summary_prompt(transcription, video_title)
        
        # Verificar rate limits antes de fazer a requisição
        estimated_tokens = len(final_prompt.split()) * 1.3  # Estimativa tokens de entrada + saída
        limits_check = groq_monitor.check_rate_limits(tokens_needed=estimated_tokens)
        
        if not limits_check['can_make_request']:
            wait_time = groq_monitor.wait_for_rate_limit('request')
            raise RuntimeError(f'Rate limit atingido. Aguarde {wait_time:.0f} segundos.')
        
        if not limits_check['can_use_tokens']:
            raise RuntimeError(f'Limite de tokens atingido. Uso atual: {limits_check["current_usage"]["tokens_per_minute"]}/minuto')
        
        # Retry com backoff exponencial
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model='llama-3.3-70b-versatile',  # Modelo mais moderno e capaz
                    messages=[
                        {
                            'role': 'system', 
                            'content': 'Você é o Alfredo, um assistente especializado em análise de conteúdo educativo e técnico. '
                                     'Crie resumos estruturados, claros e informativos em português brasileiro.'
                        },
                        {
                            'role': 'user', 
                            'content': final_prompt
                        }
                    ],
                    temperature=0.1,  # Baixa criatividade para consistência
                    max_tokens=4096,  # Limite adequado para resumos detalhados
                    top_p=0.9,  # Controle de diversidade
                    stream=False
                )
                
                # Registrar uso bem-sucedido
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else estimated_tokens
                groq_monitor.record_request(tokens_used=tokens_used)
                
                return response.choices[0].message.content
                
            except groq.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f'Rate limit atingido após {max_retries} tentativas: {e}')
                
                delay = base_delay * (2 ** attempt)
                safe_print(f'⏳ Rate limit atingido, aguardando {delay}s antes de tentar novamente...')
                await asyncio.sleep(delay)
                
            except groq.BadRequestError as e:
                # Prompt muito longo
                if "too long" in str(e).lower() or "token" in str(e).lower():
                    # Tentar com prompt mais curto
                    short_prompt = f"Resuma este conteúdo em português:\n\n{transcription[:8000]}..."
                    try:
                        response = await self.client.chat.completions.create(
                            model='llama-3.3-70b-versatile',
                            messages=[{'role': 'user', 'content': short_prompt}],
                            temperature=0.1,
                            max_tokens=2048
                        )
                        
                        # Registrar uso
                        groq_monitor.record_request(tokens_used=estimated_tokens//2)
                        
                        return response.choices[0].message.content + "\n\n⚠️ Nota: Resumo baseado em parte do conteúdo devido a limitações de tamanho."
                    except Exception:
                        raise RuntimeError(f'Conteúdo muito longo para processamento: {e}')
                else:
                    raise RuntimeError(f'Erro na requisição Groq: {e}')
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f'Erro na sumarização Groq após {max_retries} tentativas: {e}')
                
                delay = base_delay * (2 ** attempt)
                safe_print(f'🔄 Erro temporário, tentando novamente em {delay}s...')
                await asyncio.sleep(delay)
