from flask import render_template, request, redirect, url_for
from database import db
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli/tambah-keranjang', methods=['POST'])
def pembeli_tambah_keranjang():
    nama = request.form.get('nama', '').strip()
    harga = int(request.form.get('harga', 0))
    jumlah = int(request.form.get('jumlah', 1))
    gambar = request.form.get('gambar', '')
    
    barang = next((b for b in db.data_barang if b['nama'] == nama), None)
    stok_tersedia = barang['stok'] if barang else 0

    if nama and jumlah > 0:
        current_qty = db.cart.get(nama, {}).get('jumlah', 0)
        if current_qty + jumlah <= stok_tersedia:
            if nama in db.cart:
                db.cart[nama]['jumlah'] += jumlah
            else:
                db.cart[nama] = {'harga': harga, 'jumlah': jumlah, 'gambar': gambar}
        else:
            if stok_tersedia > 0:
                db.cart[nama] = {'harga': harga, 'jumlah': stok_tersedia, 'gambar': gambar}
    return redirect('/pembeli?added=1')

@pembeli_bp.route('/pembeli/update-keranjang', methods=['POST'])
def pembeli_update_keranjang():
    nama = request.form.get('nama', '').strip()
    aksi = request.form.get('aksi', '')
    if nama in db.cart:
        if aksi == 'tambah':
            barang = next((b for b in db.data_barang if b['nama'] == nama), None)
            stok_tersedia = barang['stok'] if barang else 0
            if db.cart[nama]['jumlah'] < stok_tersedia:
                db.cart[nama]['jumlah'] += 1
        elif aksi == 'kurang':
            db.cart[nama]['jumlah'] -= 1
            if db.cart[nama]['jumlah'] <= 0:
                del db.cart[nama]
        elif aksi == 'hapus':
            del db.cart[nama]
    return redirect(url_for('pembeli.pembeli_keranjang'))

@pembeli_bp.route('/pembeli/keranjang')
def pembeli_keranjang():
    tambah_id = request.args.get('tambah')
    qty = request.args.get('qty', 1, type=int)
    if tambah_id:
        tambah_id = int(tambah_id)
        barang = None
        for b in db.data_barang:
            if b['no'] == tambah_id:
                barang = {'id': b['no'], 'nama': b['nama'], 'harga': b['harga'], 'stok': b['stok'],
                          'gambar': b.get('gambar', ''), 'kategori': b['kategori']}
                break
        
        if barang:
            stok_tersedia = barang.get('stok', 0)
            nama = barang['nama']
            gambar = barang.get('gambar', '')
            
            if stok_tersedia > 0:
                current_qty = db.cart.get(nama, {}).get('jumlah', 0)
                if current_qty + qty <= stok_tersedia:
                    if nama in db.cart:
                        db.cart[nama]['jumlah'] += qty
                    else:
                        db.cart[nama] = {'harga': barang['harga'], 'jumlah': qty, 'gambar': gambar}
                else:
                    db.cart[nama] = {'harga': barang['harga'], 'jumlah': stok_tersedia, 'gambar': gambar}
        
        return redirect(url_for('pembeli.pembeli_keranjang'))

    total = 0
    for nama in db.cart:
        total += db.cart[nama]['harga'] * db.cart[nama]['jumlah']
    return render_template('18-masukkankeranjang.html', cart=db.cart, total=total)
