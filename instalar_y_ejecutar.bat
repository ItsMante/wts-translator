@echo off
title WTS Translator - Instalador
echo.
echo  ============================================
echo   WTS Translator - Warcraft III ES-LA
echo   Verificando dependencias...
echo  ============================================
echo.

python -m pip install --upgrade customtkinter ollama tkinterdnd2 2>nul
if errorlevel 1 (
    py -m pip install --upgrade customtkinter ollama tkinterdnd2
)

echo.
echo  ============================================
echo   Instalacion completada.
echo   Iniciando aplicacion...
echo  ============================================
echo.

python app.py 2>nul
if errorlevel 1 (
    py app.py
)

pause
