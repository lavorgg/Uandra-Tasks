@echo off
title Uandra Tasks
echo.
echo  =========================================
echo    Iniciando Uandra Tasks...
echo  =========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERRO: Python nao encontrado!
    echo  Baixe em: https://python.org/downloads
    pause
    exit
)

echo  Instalando Django (aguarde)...
pip install django -q

if not exist db.sqlite3 (
    echo  Criando banco de dados...
    python manage.py migrate --run-syncdb -v 0
    echo  Criando dados de exemplo...
    python seed.py
)

echo.
echo  =========================================
echo   Acesse: http://localhost:8000
echo   Para fechar: pressione CTRL+C
echo  =========================================
echo.

start "" http://localhost:8000
python manage.py runserver
pause
