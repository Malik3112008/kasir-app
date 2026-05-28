#!/usr/bin/env fish
# Script untuk menjalankan aplikasi kasir
cd (dirname (status -f))
./venv/bin/python app.py
