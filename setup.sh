#!/bin/bash
# Alfredo AI - Setup Script

echo "🤖 Configurando Alfredo AI..."

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar em modo desenvolvimento
echo "🔧 Instalando em modo desenvolvimento..."
pip install -e .

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p data/{input/{local,youtube},output,logs,temp}

# Copiar arquivo de configuração se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo de configuração..."
    cp .env.example .env
fi

echo "✅ Setup concluído!"
echo ""
echo "🚀 Para começar a usar:"
echo "   source venv/bin/activate  # ou venv\\Scripts\\activate no Windows"
echo "   python -m src.main --help"
echo ""
echo "📖 Veja o README.md para mais informações."
