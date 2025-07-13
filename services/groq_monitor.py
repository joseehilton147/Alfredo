"""
Monitor de uso da API Groq
Controla rate limits e fornece informações sobre uso
"""

import time
import json
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

def safe_print(text, end="\n", flush=False):
    """Função para imprimir texto sem problemas de encoding no Windows"""
    try:
        print(text, end=end, flush=flush)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais, mantém apenas ASCII
        import re
        text = re.sub(r'[^\x20-\x7E]+', '', text)
        print(text, end=end, flush=flush)

class GroqAPIMonitor:
    """Monitor de uso da API Groq com controle de rate limits"""
    
    def __init__(self):
        self.usage_file = Path('data/cache/groq_usage.json')
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rate limits conforme documentação Groq (free tier)
        self.rate_limits = {
            'requests_per_minute': 30,
            'requests_per_day': 14400,
            'tokens_per_minute': 6000,
            'tokens_per_day': 8640000,
            'audio_seconds_per_hour': 1800,
            'audio_seconds_per_day': 43200
        }
        
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """Carrega dados de uso salvos"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'requests': [],
            'tokens': [],
            'audio_seconds': [],
            'last_reset': datetime.now().isoformat()
        }
    
    def _save_usage_data(self):
        """Salva dados de uso"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            safe_print(f"⚠️ Erro ao salvar dados de uso: {e}")
    
    def _cleanup_old_entries(self):
        """Remove entradas antigas (mais de 24h)"""
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        cutoff_iso = cutoff.isoformat()
        
        for key in ['requests', 'tokens', 'audio_seconds']:
            self.usage_data[key] = [
                entry for entry in self.usage_data[key]
                if entry['timestamp'] > cutoff_iso
            ]
    
    def _count_recent_usage(self, usage_type: str, minutes: int) -> int:
        """Conta uso recente em minutos"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=minutes)
        cutoff_iso = cutoff.isoformat()
        
        return sum(
            entry['count'] for entry in self.usage_data[usage_type]
            if entry['timestamp'] > cutoff_iso
        )
    
    def record_request(self, tokens_used: int = 0, audio_seconds: float = 0):
        """Registra uma requisição com faturamento correto conforme Groq"""
        now = datetime.now().isoformat()
        
        # Limpar entradas antigas
        self._cleanup_old_entries()
        
        # Registrar requisição
        self.usage_data['requests'].append({
            'timestamp': now,
            'count': 1
        })
        
        # Registrar tokens se fornecido
        if tokens_used > 0:
            self.usage_data['tokens'].append({
                'timestamp': now,
                'count': tokens_used
            })
        
        # Registrar segundos de áudio com faturamento mínimo
        if audio_seconds > 0:
            # Groq cobra mínimo de 10 segundos por requisição de áudio
            billed_seconds = max(audio_seconds, 10.0)
            
            self.usage_data['audio_seconds'].append({
                'timestamp': now,
                'count': billed_seconds
            })
            
            safe_print(f"📊 Áudio registrado: {audio_seconds:.1f}s solicitados, {billed_seconds:.1f}s faturados")
        
        self._save_usage_data()
    
    def check_rate_limits(self, tokens_needed: int = 0, audio_seconds: float = 0) -> Dict[str, bool]:
        """Verifica se pode fazer uma requisição sem violar rate limits com base na documentação Groq"""
        self._cleanup_old_entries()
        
        # Contadores atuais
        requests_last_minute = self._count_recent_usage('requests', 1)
        requests_last_day = self._count_recent_usage('requests', 24 * 60)
        tokens_last_minute = self._count_recent_usage('tokens', 1)
        tokens_last_day = self._count_recent_usage('tokens', 24 * 60)
        audio_last_hour = self._count_recent_usage('audio_seconds', 60)
        audio_last_day = self._count_recent_usage('audio_seconds', 24 * 60)
        
        # Verificações de limites com margem de segurança
        can_make_request = (
            requests_last_minute < self.rate_limits['requests_per_minute'] and
            requests_last_day < self.rate_limits['requests_per_day']
        )
        
        can_use_tokens = (
            tokens_last_minute + tokens_needed <= self.rate_limits['tokens_per_minute'] and
            tokens_last_day + tokens_needed <= self.rate_limits['tokens_per_day']
        )
        
        # Para áudio, aplicar faturamento mínimo do Groq
        if audio_seconds > 0:
            # Groq cobra mínimo de 10 segundos por requisição de áudio
            billed_audio_seconds = max(audio_seconds, 10.0)
        else:
            billed_audio_seconds = 0
            
        can_use_audio = (
            audio_last_hour + billed_audio_seconds <= self.rate_limits['audio_seconds_per_hour'] and
            audio_last_day + billed_audio_seconds <= self.rate_limits['audio_seconds_per_day']
        )
        
        # Debug info para análise
        if audio_seconds > 0:
            safe_print(f"📊 Verificação de áudio:")
            safe_print(f"   Duração solicitada: {audio_seconds:.1f}s")
            safe_print(f"   Duração faturada: {billed_audio_seconds:.1f}s")
            safe_print(f"   Uso atual/hora: {audio_last_hour:.1f}s / {self.rate_limits['audio_seconds_per_hour']}s")
            safe_print(f"   Uso atual/dia: {audio_last_day:.1f}s / {self.rate_limits['audio_seconds_per_day']}s")
            safe_print(f"   Pode usar áudio: {can_use_audio}")
        
        return {
            'can_make_request': can_make_request,
            'can_use_tokens': can_use_tokens,
            'can_use_audio': can_use_audio,
            'current_usage': {
                'requests_per_minute': requests_last_minute,
                'requests_per_day': requests_last_day,
                'tokens_per_minute': tokens_last_minute,
                'tokens_per_day': tokens_last_day,
                'audio_seconds_per_hour': audio_last_hour,
                'audio_seconds_per_day': audio_last_day
            },
            'billed_audio_seconds': billed_audio_seconds if audio_seconds > 0 else 0
        }
    
    def get_usage_summary(self) -> str:
        """Retorna resumo colorido do uso atual"""
        limits = self.check_rate_limits()
        usage = limits['current_usage']
        
        def format_number(num: int) -> str:
            """Formata número com pontuação brasileira"""
            return f"{num:,}".replace(",", ".")
        
        def format_percentage(current: int, limit: int) -> str:
            pct = (current / limit) * 100 if limit > 0 else 0
            if pct < 50:
                color = '\033[1;32m'  # Verde
            elif pct < 80:
                color = '\033[1;33m'  # Amarelo
            else:
                color = '\033[1;31m'  # Vermelho
            
            # Formatar números com pontuação
            current_formatted = format_number(current)
            limit_formatted = format_number(limit)
            
            return f'{color}{current_formatted}/{limit_formatted} ({pct:.1f}%)\033[0m'
        
        return f"""
📊 \033[1;36mStatus da API Groq\033[0m
\033[1;33m──────────────────────────────────────────────────────────────\033[0m
  🔄 Requisições/min  : {format_percentage(usage['requests_per_minute'], self.rate_limits['requests_per_minute'])}
  📅 Requisições/dia  : {format_percentage(usage['requests_per_day'], self.rate_limits['requests_per_day'])}
  🔤 Tokens/min       : {format_percentage(usage['tokens_per_minute'], self.rate_limits['tokens_per_minute'])}
  📊 Tokens/dia       : {format_percentage(usage['tokens_per_day'], self.rate_limits['tokens_per_day'])}
  🎧 Áudio/hora       : {format_percentage(int(usage['audio_seconds_per_hour']), self.rate_limits['audio_seconds_per_hour'])}
  🎵 Áudio/dia        : {format_percentage(int(usage['audio_seconds_per_day']), self.rate_limits['audio_seconds_per_day'])}
\033[1;33m──────────────────────────────────────────────────────────────\033[0m
"""
    
    def wait_for_rate_limit(self, required_type: str = 'request') -> float:
        """Calcula tempo de espera necessário para respeitar rate limits"""
        limits = self.check_rate_limits()
        
        if required_type == 'request' and not limits['can_make_request']:
            # Precisa esperar até o próximo minuto
            return 60 - datetime.now().second
        
        return 0

    def reset_usage_data(self):
        """Reseta todos os dados de uso - usar apenas para debug/testes"""
        self.usage_data = {
            'requests': [],
            'tokens': [],
            'audio_seconds': [],
            'last_reset': datetime.now().isoformat()
        }
        self._save_usage_data()
        safe_print("🔄 Dados de uso resetados com sucesso!")
    
    def diagnose_rate_limits(self) -> str:
        """Diagnóstico detalhado dos rate limits para debug"""
        self._cleanup_old_entries()
        
        # Contadores atuais
        req_min = self._count_recent_usage('requests', 1)
        req_day = self._count_recent_usage('requests', 24 * 60)
        tok_min = self._count_recent_usage('tokens', 1)
        tok_day = self._count_recent_usage('tokens', 24 * 60)
        audio_hour = self._count_recent_usage('audio_seconds', 60)
        audio_day = self._count_recent_usage('audio_seconds', 24 * 60)
        
        return f"""
🔍 DIAGNÓSTICO DETALHADO - API GROQ
──────────────────────────────────────────────────────────────
📊 Contadores de Uso:
   Requisições/min   : {req_min}/{self.rate_limits['requests_per_minute']} ({(req_min/self.rate_limits['requests_per_minute']*100):.1f}%)
   Requisições/dia   : {req_day}/{self.rate_limits['requests_per_day']} ({(req_day/self.rate_limits['requests_per_day']*100):.1f}%)
   Tokens/min        : {tok_min}/{self.rate_limits['tokens_per_minute']} ({(tok_min/self.rate_limits['tokens_per_minute']*100):.1f}%)
   Tokens/dia        : {tok_day}/{self.rate_limits['tokens_per_day']} ({(tok_day/self.rate_limits['tokens_per_day']*100):.1f}%)
   Áudio/hora        : {audio_hour:.1f}/{self.rate_limits['audio_seconds_per_hour']} ({(audio_hour/self.rate_limits['audio_seconds_per_hour']*100):.1f}%)
   Áudio/dia         : {audio_day:.1f}/{self.rate_limits['audio_seconds_per_day']} ({(audio_day/self.rate_limits['audio_seconds_per_day']*100):.1f}%)

📈 Histórico Recente:
   Total de requisições armazenadas: {len(self.usage_data['requests'])}
   Total de registros de tokens: {len(self.usage_data['tokens'])}
   Total de registros de áudio: {len(self.usage_data['audio_seconds'])}
   Último reset: {self.usage_data.get('last_reset', 'N/A')}

💡 Informações Importantes:
   • Groq cobra mínimo de 10s por requisição de áudio
   • Rate limits aplicam-se por organização, não por usuário
   • Arquivo de dados: {self.usage_file}
──────────────────────────────────────────────────────────────
"""

# Instância global do monitor
groq_monitor = GroqAPIMonitor()
