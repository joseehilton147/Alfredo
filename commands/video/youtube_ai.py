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

def save_transcription_cache(video_title: str, transcription: str):
    """Salva transcrição em cache para reuso"""
    cache_dir = Path('data/cache/transcriptions')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f'{video_title}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump({'transcription': transcription, 'timestamp': time.time()}, f, ensure_ascii=False)

def load_transcription_cache(video_title: str) -> str:
    """Carrega transcrição do cache se existir"""
    cache_dir = Path('data/cache/transcriptions')
    cache_file = cache_dir / f'{video_title}.json'
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['transcription']
        except:
            pass
    return None

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

    video_path = None
    audio_path = None
    spinner = ProgressSpinner()
    try:
        safe_print('\n===============================================================')
        safe_print(' Alfredo: Vou processar este video do YouTube para voce!')
        safe_print('===============================================================\n')
        
        from commands.video.youtube_downloader import download_youtube_video
        from commands.video.audio_analyzer import extract_audio

        # Caminho esperado do video
        from urllib.parse import urlparse, parse_qs
        import re
        video_id = None
        url_data = urlparse(args.url)
        if 'youtube' in url_data.netloc or 'youtu.be' in url_data.netloc:
            if 'v' in parse_qs(url_data.query):
                video_id = parse_qs(url_data.query)['v'][0]
            else:
                # Para links do tipo youtu.be/VIDEOID
                video_id = url_data.path.split('/')[-1]
        video_title = None
        video_dir = Path('data/input/youtube')
        if video_id:
            # Busca arquivo de video ja baixado
            for f in video_dir.glob(f'*{video_id}*.mp4'):
                video_path = f
                video_title = f.stem
                break
        
        # ETAPA 1: DOWNLOAD DO VIDEO
        safe_print('ETAPA 1: Download do Video')
        if not video_path or not video_path.exists():
            safe_print('Baixando video do YouTube...')
            spinner = ProgressSpinner('Baixando')
            spinner.start()
            try:
                async def download_operation():
                    with suppress_stdout():
                        return download_youtube_video(args.url)
                video_path = await retry_operation(download_operation, 3, 'Download do video')
                video_title = Path(video_path).stem
            finally:
                spinner.stop()
            safe_print('Download concluido!')
        else:
            safe_print('Reutilizando video ja baixado')
        safe_print('---------------------------------------------------------------\n')

        # ETAPA 2: EXTRACAO DE AUDIO
        safe_print('ETAPA 2: Extracao de Audio')
        audio_dir = Path('data/cache/audio')
        audio_path = audio_dir / f'{video_title}.wav'
        if not audio_path.exists():
            safe_print('Extraindo audio do video...')
            spinner = ProgressSpinner('Processando audio')
            spinner.start()
            try:
                async def extract_operation():
                    with suppress_stdout():
                        return extract_audio(video_path)
                audio_path = await retry_operation(extract_operation, 3, 'Extracao de audio')
            finally:
                spinner.stop()
            safe_print('Audio extraido com sucesso!')
        else:
            safe_print('Reutilizando audio ja extraido')
        safe_print('---------------------------------------------------------------\n')

        # ETAPA 3: TRANSCRICAO
        safe_print('ETAPA 3: Transcricao do Audio')
        transcription = load_transcription_cache(video_title)
        if transcription:
            safe_print('Reutilizando transcricao do cache')
        else:
            safe_print('Transcrevendo audio com IA...')
            
            # Tenta primeiro com o provider solicitado, depois fallback
            from core.provider_factory import get_ai_provider
            current_provider = args.provider or 'groq'
            fallback_provider = 'ollama' if current_provider == 'groq' else 'groq'
            
            transcription_success = False
            for provider_name in [current_provider, fallback_provider]:
                if transcription_success:
                    break
                
                safe_print(f'Usando provedor: {provider_name.title()}')
                try:
                    ai_provider = get_ai_provider(provider_name)
                    spinner = ProgressSpinner(f'Transcrevendo com {provider_name.title()}')
                    spinner.start()
                    try:
                        async def transcribe_operation():
                            with suppress_stdout():
                                return await ai_provider.transcribe(str(audio_path))
                        transcription = await retry_operation(transcribe_operation, 3, 'Transcricao')
                        save_transcription_cache(video_title, transcription)
                        transcription_success = True
                    finally:
                        spinner.stop()
                    safe_print('Transcricao concluida!')
                    break
                except Exception as e:
                    spinner.stop()
                    safe_print(f'Falha com {provider_name.title()}: {str(e)[:50]}...')
                    if provider_name != fallback_provider:
                        safe_print(f'Tentando com {fallback_provider.title()}...')
            if not transcription_success:
                raise Exception('Todos os provedores de IA falharam na transcricao')
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
        safe_print('Resumo criado com sucesso!')
        safe_print('---------------------------------------------------------------\n')

        # FINALIZACAO
        safe_print('FINALIZANDO')
        safe_print('Gerando HTML...')
        output_dir = Path('data/output/summaries/youtube')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from services.markdown_utils import create_html_directly
        html_path = create_html_directly(summary, video_title, output_dir)
        html_url = html_path.resolve().as_uri()

        safe_print('Abrindo no navegador...')
        from services.open_in_browser import open_in_browser
        open_in_browser(html_url)
        safe_print('---------------------------------------------------------------\n')

        safe_print('===============================================================')
        safe_print('Processo concluido com sucesso!')
        safe_print(f'O resumo foi aberto no seu navegador para leitura.')
        safe_print(f'Arquivo salvo: {html_path.name}')
        safe_print('===============================================================')

    except Exception as e:
        safe_print('\n===============================================================')
        safe_print('Processo interrompido')
        safe_print(f'Erro: {str(e)}')
        safe_print(f'Sugestao: Verifique sua conexao e tente novamente')
        safe_print('===============================================================')
    finally:
        import os
        # Remove apenas o arquivo de áudio temporário após sucesso COMPLETO
        # Mantém vídeo e transcrição para reuso futuro
        try:
            if audio_path and isinstance(audio_path, Path) and audio_path.exists():
                os.remove(audio_path)
        except Exception as e:
            safe_print(f'! Alfredo: Não consegui remover arquivo de áudio temporário {audio_path}: {e}')

if __name__ == "__main__":
    asyncio.run(main())
