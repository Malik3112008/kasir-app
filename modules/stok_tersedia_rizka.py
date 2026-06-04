from flask import render_template, request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp

@admin_bp.route('/admin/stok-tersedia')
def admin_stok_tersedia():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    keyword = request.args.get('cari', '').lower()
    kategori = request.args.get('kategori', '')
    page = int(request.args.get('page', 1))
    per_page = 5

    filtered = db.data_barang
    if keyword:
        filtered = [b for b in filtered if keyword in b['nama'].lower()]
    if kategori:
        filtered = [b for b in filtered if b['kategori'] == kategori]

    total_halaman = max(1, (len(filtered) + per_page - 1) // per_page)
    start = (page - 1) * per_page
    data_page = filtered[start:start + per_page]

    return render_template('14.-stoktersedia.html',
        data=data_page, page=page, total_halaman=total_halaman,
        keyword=request.args.get('cari', ''), kategori=kategori)

@admin_bp.route('/admin/stok-tersedia/edit/<int:id>', methods=['GET', 'POST'])
def admin_stok_tersedia_edit(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    barang = None
    for b in db.data_barang:
        if b['no'] == id:
            barang = b
            break
    if not barang:
        return "Barang tidak ditemukan", 404
    if request.method == 'POST':
        old_price = barang['harga']
        new_price = int(request.form.get('harga', barang['harga']))
        barang['nama'] = request.form.get('nama', barang['nama'])
        barang['berat'] = request.form.get('berat', barang['berat'])
        barang['kategori'] = request.form.get('kategori', barang['kategori'])
        barang['stok'] = int(request.form.get('stok', barang['stok']))
        barang['harga'] = new_price
        barang['satuan'] = request.form.get('satuan', barang.get('satuan', ''))
        barang['tanggal_restok'] = request.form.get('tanggal_restok', barang.get('tanggal_restok', ''))
        barang['expired'] = request.form.get('expired', barang.get('expired', ''))
        barang['alasan'] = request.form.get('alasan', barang.get('alasan', ''))
        db.save_data_barang()
        
        admin_name = session.get('user', 'Admin')
        if old_price != new_price:
            catatan = f"Mengubah harga: {barang['nama']} ({formatRp(old_price)} -> {formatRp(new_price)})"
        else:
            catatan = f"Mengubah data barang: {barang['nama']}"
        db.tambah_aktivitas("ubah", catatan, "Berhasil", admin_name)
        
        return redirect(url_for('admin.admin_stok_tersedia'))
    return render_template('14.-stoktersedia_edit.html', barang=barang)
 
@admin_bp.route('/admin/stok-tersedia/hapus/<int:id>', methods=['POST'])
def admin_stok_tersedia_hapus(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    barang = None
    for b in db.data_barang:
        if b['no'] == id:
            barang = b
            break
            
    if barang:
        admin_name = session.get('user', 'Admin')
        db.tambah_aktivitas("hapus", f"Menghapus pilihan barang: {barang['nama']}", "Berhasil", admin_name)
        
    db.data_barang = [b for b in db.data_barang if b['no'] != id]
    db.save_data_barang()
    return redirect(url_for('admin.admin_stok_tersedia'))
