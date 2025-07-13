#!/usr/bin/env python3
"""
COMANDO: RESUMIR-YOUTUBE
========================
Comando para baixar vídeos do YouTube e gerar resumo automático com IA
"""

import sys
from pathlib import Path
import argparse
import asyncio
import webbrowser
import threading
import time
import json
import contextlib
import io
import re
import subprocess

# Força encoding utf-8 no Windows para suportar emojis
if sys.platform == 'win32':
    try:
        import os
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except Exception:
        pass

def safe_print(text, end="\n", flush=False):
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Remove emojis e imprime só texto (apenas ASCII)
        import re
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        print(text, end=end, flush=flush)

# Informações do comando para o Alfredo Core
COMMAND_INFO = {
    "name": "resumir-youtube",
    "description": "Baixar do YouTube e resumir com IA",
    "function": "main",
    "help": "Download automático de vídeo do YouTube seguido de análise e resumo com IA",
    "version": "0.0.1",
    "author": "Alfredo AI",
    "category": "video"
}

class ProgressSpinner:
    """Spinner simples para mostrar progresso durante operações longas"""
    def __init__(self, message="Processando"):
        self.message = message
        self.running = False
        self.thread = None
        self.chars = "|/-\\"  # Usa caracteres ASCII seguros
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        # Limpa a linha completamente
        try:
            print(f"\r{' ' * 80}\r", end="", flush=True)
        except UnicodeEncodeError:
            print(f"\r{' ' * 80}\r", end="", flush=True)
    
    def _spin(self):
        i = 0
        while self.running:
            try:
                print(f"\r{self.chars[i % len(self.chars)]} {self.message}...", end="", flush=True)
            except UnicodeEncodeError:
                print(f"\r{self.chars[i % len(self.chars)]} {self.message}...", end="", flush=True)
            time.sleep(0.1)
            i += 1

async def retry_operation(operation, max_retries=3, operation_name="Operação"):
    """Executa uma operação com retry automático"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt < max_retries - 1:
                safe_print(f'   !  Tentativa {attempt + 1} falhou')
                safe_print(f'   -> Tentando novamente... ({attempt + 2}/{max_retries})')
                await asyncio.sleep(2)
            else:
                raise e

def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError('Não foi possível extrair o video_id da URL.')

def save_transcription_cache(video_id: str, transcription: str):
    cache_dir = Path('data/cache/transcriptions')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f'{video_id}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({'transcription': transcription, 'timestamp': time.time()}, f, ensure_ascii=False)

def load_transcription_cache(video_id: str) -> str:
    cache_dir = Path('data/cache/transcriptions')
    cache_file = cache_dir / f'{video_id}.json'
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['transcription']
        except:
            pass
    return None

def get_video_title(url: str) -> str:
    try:
        result = subprocess.run(
            ['yt-dlp', '--get-title', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        title = result.stdout.strip()
        if title:
            return title
    except Exception:
        pass
    return 'video'

@contextlib.contextmanager
def suppress_stdout():
    """Context manager para silenciar stdout temporariamente"""
    import os
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

async def main():
    parser = argparse.ArgumentParser(description='Resumir vídeo do YouTube com IA')
    parser.add_argument('url', help='URL do vídeo do YouTube')
    parser.add_argument('--provider', help='Especifica o provedor de IA a ser usado (groq ou ollama)', default=None)
    parser.add_argument('--show-groq-status', action='store_true', help='Mostrar status da API Groq')
    args = parser.parse_args()
    
    # Mostrar status do Groq se solicitado ou se for o provider padrão
    if args.show_groq_status or (not args.provider or args.provider == 'groq'):
        try:
            from services.groq_monitor import groq_monitor
            print(groq_monitor.get_usage_summary())
        except Exception:
            pass  # Falha silenciosa se houver problemas com o monitor

    video_id = extract_video_id(args.url)
    video_path = Path(f'data/input/youtube/{video_id}.mp4')
    
    # Determinar formato de áudio disponível (FLAC tem prioridade por ser lossless)
    audio_flac_path = Path(f'data/cache/audio/{video_id}.flac')
    audio_mp3_path = Path(f'data/cache/audio/{video_id}.mp3')
    
    # Usar FLAC se disponível e no tamanho adequado, senão MP3
    if audio_flac_path.exists() and audio_flac_path.stat().st_size <= 40 * 1024 * 1024:
        audio_path = audio_flac_path
    else:
        audio_path = audio_mp3_path
    spinner = ProgressSpinner()
    ai_provider = None
    transcription = None
    try:
        # ETAPA 1: DOWNLOAD DO VIDEO
        safe_print('🤖 Alfredo: Iniciando primeira etapa, baixando o vídeo do YouTube')
        if not video_path.exists():
            safe_print('🤖 Alfredo: Vou baixar o vídeo para você agora...')
            spinner = ProgressSpinner('Baixando')
            spinner.start()
            try:
                async def download_operation():
                    with suppress_stdout():
                        from commands.video.youtube_downloader import download_youtube_video
                        return download_youtube_video(args.url, output_dir=video_path.parent, output_filename=f'{video_id}.mp4')
                await retry_operation(download_operation, 3, 'Download do video')
            finally:
                spinner.stop()
            safe_print('🤖 Alfredo: Ótimo! Download concluído com sucesso!')
        else:
            safe_print('🤖 Alfredo: Ah, já encontrei o vídeo aqui nos meus arquivos, irei reutilizar.')
        safe_print('---------------------------------------------------------------\n')

        # Obter informações do vídeo
        video_title = get_video_title(args.url)
        video_size = video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0
        # Duração via ffprobe
        def get_duration(path):
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', str(path)
                ], capture_output=True, text=True, timeout=20)
                if result.returncode == 0:
                    seconds = float(result.stdout.strip())
                    m = int(seconds // 60)
                    s = int(seconds % 60)
                    return f'{m}:{s:02d}'
            except Exception:
                pass
            return 'N/A'
        video_duration = get_duration(video_path)

        # Output informativo e colorido
        print(f'\033[1;36m\n🎬 Alfredo: Pronto para processar seu vídeo!\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
        print(f'  📺  Título   : \033[1;37m{video_title}\033[0m')
        print(f'  🆔  ID       : \033[1;32m{video_id}\033[0m')
        print(f'  ⏱️  Duração  : \033[1;35m{video_duration} min\033[0m')
        print(f'  💾  Tamanho  : \033[1;34m{video_size:.2f} MB\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')

        # ETAPA 2: EXTRACAO DE AUDIO
        safe_print('🤖 Alfredo: Agora vou extrair o áudio do vídeo para análise')
        if not audio_path.exists():
            safe_print('🤖 Alfredo: Processando o áudio em alta qualidade...')
            spinner = ProgressSpinner('Processando audio')
            spinner.start()
            try:
                async def extract_operation():
                    with suppress_stdout():
                        from commands.video.audio_analyzer import extract_audio
                        return extract_audio(video_path)
                result_path = await retry_operation(extract_operation, 3, 'Extracao de audio')
                if result_path:
                    # Atualizar audio_path para o formato retornado (pode ser FLAC ou MP3)
                    audio_path = result_path
            finally:
                spinner.stop()
        else:
            safe_print('🤖 Alfredo: Perfeito! Já tenho o áudio extraído, vou reutilizar.')
            
        # Verificar se o arquivo existe e seu tamanho
        if not audio_path.exists():
            raise Exception('Falha na extração de áudio - arquivo não foi criado')
            
        audio_size = audio_path.stat().st_size / (1024 * 1024)
        audio_duration = get_duration(audio_path)
        
        # Verificar limites do Groq antes de prosseguir
        max_size_mb = 40  # Free tier limit
        if audio_size > max_size_mb:
            print(f'\033[1;31m\n⚠️  AVISO: Arquivo de áudio muito grande!\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
            print(f'  📁  Arquivo  : \033[1;37m{audio_path.name}\033[0m')
            print(f'  💾  Tamanho  : \033[1;31m{audio_size:.2f} MB (limite: {max_size_mb}MB)\033[0m')
            print(f'  ⏱️  Duração  : \033[1;35m{audio_duration} min\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
            print(f'\033[1;33m💡 Dica: Para arquivos grandes, considere usar o Ollama local\033[0m')
            print(f'\033[1;33m   ou divida o vídeo em partes menores.\033[0m\n')
            # Perguntar se deseja prosseguir mesmo assim
            try:
                response = input('🤔 Deseja tentar processar mesmo assim? (s/N): ').strip().lower()
                if response not in ['s', 'sim', 'y', 'yes']:
                    print('📋 Processamento cancelado pelo usuário.')
                    return
            except KeyboardInterrupt:
                print('\n📋 Processamento cancelado.')
                return
                
        # Exibir informações do áudio processado
        print(f'\033[1;36m\n🎵 Áudio extraído!\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
        print(f'  📁  Arquivo  : \033[1;37m{audio_path.name}\033[0m')
        print(f'  💾  Tamanho  : \033[1;34m{audio_size:.2f} MB\033[0m')
        print(f'  ⏱️  Duração  : \033[1;35m{audio_duration} min\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        safe_print('---------------------------------------------------------------\n')

        # ETAPA 3: TRANSCRICAO
        safe_print('🤖 Alfredo: Terceira etapa - vou transcrever todo o áudio para texto')
        
        # Definir provedores no início
        from core.provider_factory import get_ai_provider
        current_provider = args.provider or 'groq'
        fallback_provider = 'ollama' if current_provider == 'groq' else 'groq'
        providers = [current_provider, fallback_provider]
        
        transcription = load_transcription_cache(video_id)
        if transcription:
            safe_print('🤖 Alfredo: Que sorte! Já tenho a transcrição salva, vou reutilizar.')
            ai_provider = get_ai_provider(current_provider)
        else:
            safe_print('🤖 Alfredo: Vou usar minha IA para transcrever o áudio completo...')
            for provider_name in providers:
                safe_print(f'🤖 Alfredo: Usando o {provider_name.title()} para transcrever')
                try:
                    temp_provider = get_ai_provider(provider_name)
                    spinner = ProgressSpinner(f'Transcrevendo com {provider_name.title()}')
                    spinner.start()
                    try:
                        async def transcribe_operation():
                            with suppress_stdout():
                                return await temp_provider.transcribe(str(audio_path))
                        result = await retry_operation(transcribe_operation, 3, 'Transcricao')
                        if result:
                            transcription = result
                            ai_provider = temp_provider
                            save_transcription_cache(video_id, transcription)
                            safe_print('🤖 Alfredo: Excelente! Transcrição concluída com sucesso!')
                            break
                    finally:
                        spinner.stop()
                except Exception as e:
                    spinner.stop()
                    error_msg = str(e)
                    
                    # Tratamento específico para erro 413 (Content Too Large)
                    if "413" in error_msg or "too large" in error_msg.lower() or "content too large" in error_msg.lower():
                        safe_print(f'🤖 Alfredo: Ops! Arquivo muito grande para {provider_name.title()}')
                        safe_print(f'   📦 Tamanho atual: {audio_size:.1f}MB (limite Groq: 40MB)')
                        
                        if provider_name == 'groq':
                            safe_print('🤖 Alfredo: Sem problemas! Vou tentar com Ollama local...')
                        else:
                            safe_print('🤖 Alfredo: Considere usar um arquivo menor ou dividir o vídeo.')
                            
                    # Tratamento para rate limit
                    elif "rate limit" in error_msg.lower():
                        safe_print(f'🤖 Alfredo: Atingi o limite de requisições em {provider_name.title()}')
                        if provider_name != fallback_provider:
                            safe_print(f'🤖 Alfredo: Vou tentar com {fallback_provider.title()}...')
                    
                    # Outros erros
                    else:
                        safe_print(f'🤖 Alfredo: Tive um problema com {provider_name.title()}: {error_msg[:50]}...')
                        
                    if provider_name != fallback_provider:
                        safe_print(f'🤖 Alfredo: Tentando com {fallback_provider.title()}...')
        if not transcription or not ai_provider:
            raise Exception('Todos os provedores de IA falharam na transcricao. Não é possível prosseguir para a sumarização.')
        
        # Painel informativo da transcrição
        if transcription:
            word_count = len(transcription.split())
            char_count = len(transcription)
            print(f'\033[1;36m\n📝 Transcrição pronta!\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
            print(f'  🤖  Provedor : \033[1;32m{ai_provider.__class__.__name__}\033[0m')
            print(f'  🔤  Caracteres: \033[1;37m{char_count}\033[0m')
            print(f'  📄  Palavras : \033[1;34m{word_count}\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        safe_print('---------------------------------------------------------------\n')

        # ETAPA 4: GERACAO DO RESUMO
        safe_print('🤖 Alfredo: Última etapa - vou criar um resumo inteligente do conteúdo')
        safe_print('🤖 Alfredo: Analisando todo o conteúdo para fazer um resumo completo...')
        spinner = ProgressSpinner('Analisando e resumindo')
        spinner.start()
        try:
            async def summarize_operation():
                with suppress_stdout():
                    return await ai_provider.summarize(transcription, video_title)
            summary = await retry_operation(summarize_operation, 3, 'Geracao de resumo')
        finally:
            spinner.stop()
            
        # Painel informativo do resumo
        if summary:
            summary_lines = summary.strip().splitlines()
            preview = '\n'.join(summary_lines[:5])
            print(f'\033[1;36m\n📚 Resumo gerado!\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
            print(f'  🔤  Linhas   : \033[1;37m{len(summary_lines)}\033[0m')
            print(f'  📄  Preview  :')
            print(f'\033[1;37m{preview}\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        safe_print('---------------------------------------------------------------\n')

        # FINALIZACAO
        safe_print('🤖 Alfredo: Quase pronto! Vou gerar a página para você')
        safe_print('🤖 Alfredo: Criando uma página web bonita com seu resumo...')
        output_dir = Path('data/output/summaries/youtube')
        output_dir.mkdir(parents=True, exist_ok=True)
        from services.markdown_utils import create_html_directly
        html_path = output_dir / f'{video_id}.html'
        html_path = create_html_directly(summary, video_title, output_dir, output_filename=f'{video_id}.html')
        html_size = html_path.stat().st_size / 1024 if html_path.exists() else 0
        html_url = html_path.resolve().as_uri()
        print(f'\033[1;36m\n🌐 Página gerada!\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
        print(f'  📄  Arquivo  : \033[1;37m{html_path.name}\033[0m')
        print(f'  💾  Tamanho  : \033[1;34m{html_size:.2f} KB\033[0m')
        print(f'  🌍  Caminho  : \033[1;32m{html_url}\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        safe_print('🤖 Alfredo: Abrindo no seu navegador para você conferir...')
        from services.open_in_browser import open_in_browser
        open_in_browser(html_url)
        safe_print('---------------------------------------------------------------\n')

        safe_print('===============================================================')
        safe_print('🤖 Alfredo: Missão cumprida! Processo concluído com sucesso!')
        safe_print('🤖 Alfredo: Seu resumo está pronto e foi aberto no navegador.')
        safe_print('===============================================================')

    except Exception as e:
        safe_print('\n===============================================================')
        safe_print('🤖 Alfredo: Ops! Tive que interromper o processo')
        safe_print(f'🤖 Alfredo: Encontrei este problema: {str(e)}')
        safe_print('===============================================================')
    finally:
        import os
        try:
            if audio_path and isinstance(audio_path, Path) and audio_path.exists():
                os.remove(audio_path)
        except Exception as e:
            pass  # Limpeza silenciosa - não queremos interromper o usuário

if __name__ == "__main__":
    asyncio.run(main())
