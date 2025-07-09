#!/usr/bin/env python3
"""
� COMANDO: INFO-PC
===================
Comando para exibir informações detalhadas do computador
"""

import os
import platform
import psutil
from datetime import datetime

# Informações do comando para o Alfredo
COMMAND_INFO = {
    "name": "info-pc",
    "description": "💻 Informações detalhadas do computador",
    "function": "main",
    "help": "Exibe CPU, memória, armazenamento e sistema operacional",
    "version": "0.0.1",
    "author": "Alfredo AI"
}

def main():
    """Exibe informações detalhadas do PC"""
    print("\n💻 ALFREDO - INFORMAÇÕES DO PC")
    print("=" * 40)
    print(f"🕐 Consultado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Informações básicas
    print("🖥️  SISTEMA OPERACIONAL:")
    print(f"   Sistema: {platform.system()}")
    print(f"   Versão: {platform.version()}")
    print(f"   Arquitetura: {platform.architecture()[0]}")
    print(f"   Hostname: {platform.node()}")
    print()
    
    # CPU
    print("🧮 PROCESSADOR:")
    print(f"   Modelo: {platform.processor()}")
    print(f"   Núcleos físicos: {psutil.cpu_count(logical=False)}")
    print(f"   Núcleos lógicos: {psutil.cpu_count(logical=True)}")
    print(f"   Uso atual: {psutil.cpu_percent(interval=1):.1f}%")
    print()
    
    # Memória
    memory = psutil.virtual_memory()
    print("🧠 MEMÓRIA:")
    print(f"   Total: {memory.total / (1024**3):.1f} GB")
    print(f"   Disponível: {memory.available / (1024**3):.1f} GB")
    print(f"   Em uso: {memory.percent:.1f}%")
    print()
    
    # Armazenamento
    print("💾 ARMAZENAMENTO:")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"   Drive {partition.device}")
            print(f"     Total: {usage.total / (1024**3):.1f} GB")
            print(f"     Livre: {usage.free / (1024**3):.1f} GB")
            print(f"     Uso: {(usage.used / usage.total) * 100:.1f}%")
        except PermissionError:
            print(f"   Drive {partition.device} - Acesso negado")
    
    print("\n🤖 Alfredo: Informações do PC coletadas com sucesso!")

if __name__ == "__main__":
    main()
