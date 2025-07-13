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
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    video_path = Path(f'data/input/youtube/{video_id}.mp4')
    audio_path = Path(f'data/cache/audio/{video_id}.wav')
    spinner = ProgressSpinner()
    ai_provider = None
    transcription = None
    try:
        # ETAPA 1: DOWNLOAD DO VIDEO
        safe_print('ETAPA 1: Download do Video')
        if not video_path.exists():
            safe_print('Baixando video do YouTube...')
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
            safe_print('Download concluido!')
        else:
            safe_print('Reutilizando video ja baixado')
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
        safe_print('ETAPA 2: Extracao de Audio')
        if not audio_path.exists():
            safe_print('Extraindo audio do video...')
            spinner = ProgressSpinner('Processando audio')
            spinner.start()
            try:
                async def extract_operation():
                    with suppress_stdout():
                        from commands.video.audio_analyzer import extract_audio
                        return extract_audio(video_path)
                await retry_operation(extract_operation, 3, 'Extracao de audio')
            finally:
                spinner.stop()
            audio_size = audio_path.stat().st_size / (1024 * 1024) if audio_path.exists() else 0
            audio_duration = get_duration(audio_path)
            print(f'\033[1;36m\n🎵 Áudio extraído!\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
            print(f'  📁  Arquivo  : \033[1;37m{audio_path.name}\033[0m')
            print(f'  💾  Tamanho  : \033[1;34m{audio_size:.2f} MB\033[0m')
            print(f'  ⏱️  Duração  : \033[1;35m{audio_duration} min\033[0m')
            print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        else:
            safe_print('Reutilizando audio ja extraido')
        safe_print('---------------------------------------------------------------\n')

        # ETAPA 3: TRANSCRICAO
        safe_print('ETAPA 3: Transcricao do Audio')
        transcription = load_transcription_cache(video_id)
        if transcription:
            safe_print('Reutilizando transcricao do cache')
            ai_provider_name = args.provider or 'groq'
            from core.provider_factory import get_ai_provider
            ai_provider = get_ai_provider(ai_provider_name)
        else:
            safe_print('Transcrevendo audio com IA...')
            from core.provider_factory import get_ai_provider
            current_provider = args.provider or 'groq'
            fallback_provider = 'ollama' if current_provider == 'groq' else 'groq'
            providers = [current_provider, fallback_provider]
            for provider_name in providers:
                safe_print(f'Usando provedor: {provider_name.title()}')
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
                            safe_print('Transcricao concluida!')
                            break
                    finally:
                        spinner.stop()
                except Exception as e:
                    spinner.stop()
                    safe_print(f'Falha com {provider_name.title()}: {str(e)[:50]}...')
                    if provider_name != fallback_provider:
                        safe_print(f'Tentando com {fallback_provider.title()}...')
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
        safe_print('ETAPA 4: Geracao do Resumo')
        safe_print('Criando resumo inteligente...')
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
        safe_print('FINALIZANDO')
        safe_print('Gerando HTML...')
        output_dir = Path('data/output/summaries/youtube')
        output_dir.mkdir(parents=True, exist_ok=True)
        from services.markdown_utils import create_html_directly
        html_path = output_dir / f'{video_id}.html'
        html_path = create_html_directly(summary, video_title, output_dir, output_filename=f'{video_id}.html')
        html_size = html_path.stat().st_size / 1024 if html_path.exists() else 0
        html_url = html_path.resolve().as_uri()
        print(f'\033[1;36m\n🌐 HTML gerado!\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m')
        print(f'  📄  Arquivo  : \033[1;37m{html_path.name}\033[0m')
        print(f'  💾  Tamanho  : \033[1;34m{html_size:.2f} KB\033[0m')
        print(f'  🌍  Caminho  : \033[1;32m{html_url}\033[0m')
        print(f'\033[1;33m──────────────────────────────────────────────────────────────\033[0m\n')
        safe_print('Abrindo no navegador...')
        from services.open_in_browser import open_in_browser
        open_in_browser(html_url)
        safe_print('---------------------------------------------------------------\n')

        safe_print('===============================================================')
        safe_print('Processo concluido com sucesso!')
        safe_print(f'O resumo foi aberto no seu navegador para leitura.')
        safe_print(f'Arquivo salvo: {video_id}.html')
        safe_print('===============================================================')

    except Exception as e:
        safe_print('\n===============================================================')
        safe_print('Processo interrompido')
        safe_print(f'Erro: {str(e)}')
        safe_print('===============================================================')
    finally:
        import os
        try:
            if audio_path and isinstance(audio_path, Path) and audio_path.exists():
                os.remove(audio_path)
        except Exception as e:
            safe_print(f'! Alfredo: Não consegui remover arquivo de áudio temporário {audio_path}: {e}')

if __name__ == "__main__":
    asyncio.run(main())
