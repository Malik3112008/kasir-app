@echo off
REM Script untuk menjalankan aplikasi kasir di Windows
cd /d "%~dp0"

REM Cek apakah venv ada
if exist "venv\Scripts\python.exe" (
    echo Menjalankan Kasir App...
    "venv\Scripts\python.exe" app.py
) else if exist "venv\bin\python" (
    echo Menjalankan Kasir App (Linux/Mac)...
    "venv\bin\python" app.py
) else (
    echo Virtual environment tidak ditemukan!
    echo Silakan jalankan setup.bat terlebih dahulu.
    pause
    exit /b 1
)

pause
