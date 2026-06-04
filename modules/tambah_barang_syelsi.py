from flask import render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from database import db
from modules.blueprints import admin_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'gambar')

@admin_bp.route('/admin/tambah-data-barang')
def admin_tambah_data_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template('25.tambah_data_barang.html')

@admin_bp.route('/admin/simpan-barang-baru', methods=['POST'])
def admin_simpan_barang_baru():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    kategori = request.form.get('kategori', '')
    nama_barang = request.form.get('nama_barang', '')
    harga_beli = int(request.form.get('harga_beli', 0))
    harga_jual = int(request.form.get('harga_jual', 0))
    jumlah = int(request.form.get('jumlah', 0))
    tanggal = request.form.get('tanggal', '')
    variasi = request.form.get('variasi', '')
    volume = request.form.get('volume', '')
    rasa = request.form.get('rasa', '')
    expired = request.form.get('expired', '')
    deskripsi = request.form.get('deskripsi', '')
    gambar_path = ''
    file = request.files.get('gambar')
    if file and file.filename:
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        gambar_path = 'gambar/' + filename

    no_baru = max([b['no'] for b in db.data_barang], default=0) + 1
    db.data_barang.append({
        'no': no_baru, 'nama': nama_barang, 'berat': volume or '-',
        'stok': jumlah, 'harga': harga_jual, 'kategori': kategori,
        'tanggal': tanggal, 'gambar': gambar_path, 'rating': 0, 'emoji': '📦'
    })
    db.save_data_barang()
    
    admin_name = session.get('user', 'Admin')
    db.tambah_aktivitas("tambah", f"Menambahkan pilihan barang: {nama_barang}", "Berhasil", admin_name)
    
    return render_template('17.-konfirmasi-barang.html',
        nama_barang=nama_barang, kategori=kategori,
        harga_beli=harga_beli, harga_jual=harga_jual, 
        jumlah=jumlah, tanggal=tanggal, variasi=variasi,
        ukuran=volume, rasa=rasa, expired=expired,
        deskripsi=deskripsi, gambar=gambar_path)
