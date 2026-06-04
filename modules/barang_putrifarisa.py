from flask import render_template, request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp, pembeli_bp

@pembeli_bp.route('/pembeli')
def pembeli_home():
    if not session.get('user'):
        return redirect(url_for('pembeli.pembeli_login'))
    cart_count = sum(item['jumlah'] for item in db.cart.values())
    sorted_barang = sorted(db.data_barang, key=lambda b: (b['stok'] == 0, b['nama']))
    return render_template('14-kategorialattulis.html', barang=sorted_barang, cart_count=cart_count)

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

@pembeli_bp.route('/pembeli/pesanan')
def pembeli_pesanan():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    
    count_dikemas = len([p for p in pesanan_user if p["status"] == "Disiapkan"])
    count_siap = len([p for p in pesanan_user if p["status"] in ("Siap diambil", "Menunggu Pembayaran")])
    count_selesai = len([p for p in pesanan_user if p["status"] in ("Selesai", "Sudah diambil")])
    
    return render_template('8-lihatpesanan.html', 
                           count_dikemas=count_dikemas, 
                           count_siap=count_siap, 
                           count_selesai=count_selesai)

@pembeli_bp.route('/pembeli/pesanan/dikemas')
def pembeli_pesanan_dikemas():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] == "Disiapkan"]
    return render_template('8_1-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/pesanan/siapdiambil')
def pembeli_pesanan_siapdiambil():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] in ("Siap diambil", "Menunggu Pembayaran")]
    return render_template('8_2-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/pesanan/selesai')
def pembeli_pesanan_selesai():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] in ("Selesai", "Sudah diambil")]
    return render_template('8_3-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/status')
def pembeli_status():
    return redirect(url_for('pembeli.pembeli_pesanan_dikemas'))

@pembeli_bp.route("/siap-diambil")
def siap_diambil():
    return redirect(url_for('pembeli.pembeli_pesanan_siapdiambil'))

# Admin-side routes related to Putri Farisa's "stok-tersedia"
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
