@echo off
REM Alfredo AI - Setup Script para Windows

echo 🤖 Configurando Alfredo AI...

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate

REM Instalar dependências
echo 📥 Instalando dependências...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Instalar em modo desenvolvimento
echo 🔧 Instalando em modo desenvolvimento...
pip install -e .

REM Criar diretórios necessários
echo 📁 Criando diretórios...
if not exist "data\input\local" mkdir data\input\local
if not exist "data\input\youtube" mkdir data\input\youtube
if not exist "data\output" mkdir data\output
if not exist "data\logs" mkdir data\logs
if not exist "data\temp" mkdir data\temp

REM Copiar arquivo de configuração se não existir
if not exist ".env" (
    echo ⚙️ Criando arquivo de configuração...
    copy .env.example .env
)

echo ✅ Setup concluído!
echo.
echo 🚀 Para começar a usar:
echo    venv\Scripts\activate
echo    python -m src.main --help
echo.
echo 📖 Veja o README.md para mais informações.
pause
