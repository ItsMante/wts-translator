@echo off
python app.py 2>nul
if errorlevel 1 py app.py
