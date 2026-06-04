from flask import render_template, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli/detail-barang/<int:id>')
def pembeli_detail_barang(id):
    if not session.get('user'):
        return redirect(url_for('pembeli.pembeli_login'))
    barang = None
    for b in db.data_barang:
        if b['no'] == id:
            barang = {'id': b['no'], 'nama': b['nama'], 'harga': b['harga'], 'stok': b['stok'],
                      'gambar': b.get('gambar', ''), 'kategori': b['kategori'], 'rating': b.get('rating', 4),
                      'berat': b.get('berat', ''), 'deskripsi': f"{b['nama']} dari kategori {b['kategori']}."}
            break
    if not barang:
        return "Barang tidak ditemukan", 404
    return render_template('7-detailbarang.html', barang=barang, formatRp=formatRp)
