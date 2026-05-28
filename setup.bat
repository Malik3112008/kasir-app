@echo off
REM Setup virtual environment untuk Kasir App di Windows
cd /d "%~dp0"

echo ========================================
echo   Setup Kasir App
echo ========================================
echo.

REM Cek apakah python tersedia
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python dari https://python.org
    echo Pastikan centang "Add Python to PATH" saat install.
    pause
    exit /b 1
)

REM Buat virtual environment
if not exist "venv" (
    echo Membuat virtual environment...
    python -m venv venv
    echo Virtual environment berhasil dibuat!
) else (
    echo Virtual environment sudah ada.
)

REM Install dependencies
echo.
echo Menginstall Flask...
"venv\Scripts\pip.exe" install flask --quiet

echo.
echo ========================================
echo   Setup selesai!
echo   Jalankan run.bat untuk memulai aplikasi.
echo   Buka browser: http://localhost:5000
echo ========================================
echo.
pause
