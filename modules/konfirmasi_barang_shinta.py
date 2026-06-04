from flask import render_template, request, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/konfirmasi-barang')
def admin_konfirmasi_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    nama_barang = request.args.get('nama_barang', '-')
    kategori = request.args.get('kategori', '-')
    variasi = request.args.get('variasi', '-')
    ukuran = request.args.get('ukuran', '-')
    rasa = request.args.get('rasa', '-')
    expired = request.args.get('expired', '-')
    deskripsi = request.args.get('deskripsi', '-')
    harga_beli = request.args.get('harga_beli', '0')
    harga_jual = request.args.get('harga_jual', '0')
    jumlah = request.args.get('jumlah', '0')
    tanggal = request.args.get('tanggal', '-')
    
    return render_template('17.-konfirmasi-barang.html', 
        nama_barang=nama_barang, kategori=kategori, variasi=variasi,
        ukuran=ukuran, rasa=rasa, expired=expired, deskripsi=deskripsi,
        harga_beli=harga_beli, harga_jual=harga_jual, jumlah=jumlah, 
        tanggal=tanggal)
