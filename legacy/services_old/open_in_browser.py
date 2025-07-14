import sys
import os
import subprocess
import webbrowser
from dotenv import load_dotenv

load_dotenv()

def open_in_browser(url: str):
    """Abre a URL no navegador padrão do sistema, ou no navegador definido em BROWSER."""
    browser_env = os.getenv('BROWSER')
    
    # Tenta navegador específico definido no .env
    if browser_env:
        if browser_env.lower() == 'chrome':
            # Tenta abrir no Chrome com diferentes estratégias
            chrome_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        subprocess.run([chrome_path, url], check=False)
                        return
                    except Exception:
                        pass
            
            # Fallback para webbrowser
            try:
                webbrowser.get('chrome').open_new_tab(url)
                return
            except Exception:
                pass
        else:
            try:
                webbrowser.get(browser_env).open_new_tab(url)
                return
            except Exception:
                pass
    
    # Usa o navegador padrão do sistema
    if sys.platform.startswith('win'):
        try:
            webbrowser.get('windows-default').open_new_tab(url)
            return
        except Exception:
            pass
    
    # Fallback universal
    webbrowser.open_new_tab(url)
