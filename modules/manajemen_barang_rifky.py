from flask import render_template, request, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/manajemen-barang')
def admin_manajemen_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    keyword = request.args.get('cari', '').lower()
    if keyword:
        filtered = [b for b in db.data_barang if keyword in b['nama'].lower() or keyword in b['kategori'].lower()]
    else:
        filtered = db.data_barang
    return render_template('09.manajemen_barang.html', data=filtered, keyword=request.args.get('cari', ''), all_barang=db.data_barang)

@admin_bp.route('/admin/simpan', methods=['POST'])
def admin_simpan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    kategori = request.form['kategori']
    nama_barang = request.form['nama_barang']
    tanggal = request.form.get('tanggal', '')
    jumlah = request.form['jumlah']
    harga_jual = request.form.get('harga_jual', request.form.get('harga', '0'))
    catatan = request.form.get('catatan', '')
    restok_id = request.form.get('restok_id')

    if restok_id:
        for b in db.data_barang:
            if str(b['no']) == str(restok_id):
                b['stok'] = b.get('stok', 0) + int(jumlah)
                db.save_data_barang()
                admin_name = session.get('user', 'Admin')
                db.tambah_aktivitas("restok", f"Melakukan restok produk: {b['nama']} (+{jumlah} unit)", "Berhasil", admin_name)
                break

    return render_template('10.rekap_barang.html', kategori=kategori, nama_barang=nama_barang, tanggal=tanggal, jumlah=jumlah, harga=harga_jual, catatan=catatan, restok_id=restok_id)

@admin_bp.route('/admin/manajemen-barang/tambah-stok', methods=['POST'])
def admin_manajemen_barang_tambah_stok():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    restok_id = request.form.get('restok_id')
    jumlah = request.form.get('jumlah')
    
    if restok_id and jumlah:
        try:
            jumlah = int(jumlah)
            for b in db.data_barang:
                if str(b['no']) == str(restok_id):
                    b['stok'] = b.get('stok', 0) + jumlah
                    db.save_data_barang()
                    admin_name = session.get('user', 'Admin')
                    db.tambah_aktivitas("restok", f"Melakukan restok cepat: {b['nama']} (+{jumlah} unit)", "Berhasil", admin_name)
                    break
        except ValueError:
            pass
            
    return redirect(url_for('admin.admin_manajemen_barang'))

