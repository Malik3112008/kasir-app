#!/bin/bash
# Setup virtual environment untuk Kasir App di Linux/Mac
cd "$(dirname "$0")"

echo "========================================"
echo "  Setup Kasir App"
echo "========================================"
echo ""

# Cek apakah python tersedia
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 tidak ditemukan!"
    echo "Silakan install Python3 terlebih dahulu."
    exit 1
fi

# Buat virtual environment
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
    echo "Virtual environment berhasil dibuat!"
else
    echo "Virtual environment sudah ada."
fi

# Install dependencies
echo ""
echo "Menginstall Flask..."
./venv/bin/pip install flask --quiet

echo ""
echo "========================================"
echo "  Setup selesai!"
echo "  Jalankan ./run.sh untuk memulai aplikasi."
echo "  Buka browser: http://localhost:5000"
echo "========================================"
