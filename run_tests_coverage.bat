@echo off
echo Executando testes com cobertura...
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
echo.
echo Relatorio de cobertura gerado em: htmlcov/index.html
pause
