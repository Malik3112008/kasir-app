from flask import render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from database import db
from helpers import format_kbbi_date, formatRp
from modules.blueprints import admin_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'gambar')

@admin_bp.route('/informasi')
def informasi():
    return render_template('informasi.html', koperasi=db.data_koperasi)

@admin_bp.route("/admin/notifikasi")
def admin_notifikasi():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.NotifikasiAdmin.html", notifikasi=db.notifikasi)

@admin_bp.route("/admin/riwayat")
def admin_riwayat():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.RiwayatTransaksi.html", pesanan=db.pesanan)

@admin_bp.route("/admin/detail-transaksi/<trx_id>")
def admin_detail_transaksi(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    trx = None
    for p in db.pesanan:
        if p['id'] == trx_id:
            trx = p
            break
    if not trx:
        return "Transaksi tidak ditemukan", 404
    items = []
    for b in trx['barang']:
        items.append({
            'nama': b['nama'],
            'harga': b['harga'],
            'jumlah': b['jumlah'],
            'id_transaksi': trx['id'],
            'gambar': b.get('gambar', '')
        })
    total = sum(b['harga'] * b['jumlah'] for b in trx['barang'])
    tanggal_fmt = format_kbbi_date(trx['tanggal'])
    return render_template("detail_transaksi.html", items=items, total=total, tanggal=tanggal_fmt)

@admin_bp.route("/admin/riwayat-notifikasi")
def admin_riwayat_notifikasi():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.RiwayatNotifikasi.html", riwayat=db.riwayat)

@admin_bp.route("/admin/riwayat-aktivitas")
def admin_riwayat_aktivitas():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    daftar_admin = list(set(d['admin'] for d in db.data_aktivitas))
    return render_template("24.RiwayatAktivitas.html", daftar_admin=daftar_admin)

@admin_bp.route("/admin/api/aktivitas")
def admin_api_aktivitas():
    search = request.args.get('search', '').lower()
    admin_filter = request.args.get('admin', 'Pilihan Admin')
    tanggal = request.args.get('tanggal', '')
    hasil = db.data_aktivitas
    if search:
        hasil = [d for d in hasil if search in d['catatan'].lower()]
    if admin_filter != 'Pilihan Admin':
        hasil = [d for d in hasil if admin_filter in d['admin']]
    if tanggal:
        hasil = [d for d in hasil if d['waktu'].startswith(tanggal)]
    return jsonify(hasil)

@admin_bp.route("/admin/hapus-semua", methods=["POST"])
def admin_hapus_semua():
    db.riwayat.extend(db.notifikasi)
    db.notifikasi.clear()
    db.save_notifikasi()
    return redirect(url_for('admin.admin_notifikasi'))

@admin_bp.route('/admin/hapus-notif/<int:index>', methods=['POST'])
def admin_hapus_notif(index):
    if index < len(db.notifikasi):
        db.riwayat.append(db.notifikasi[index])
        db.notifikasi.pop(index)
        db.save_notifikasi()
    return redirect(url_for('admin.admin_notifikasi'))

@admin_bp.route('/admin/hapus-riwayat-satuan/<int:index>', methods=['POST'])
def admin_hapus_riwayat_satuan(index):
    if index < len(db.riwayat):
        db.riwayat.pop(index)
        db.save_notifikasi()
    return redirect(url_for('admin.admin_riwayat'))

@admin_bp.route("/admin/hapus-riwayat", methods=["POST"])
def admin_hapus_riwayat():
    db.riwayat.clear()
    db.save_notifikasi()
    return redirect(url_for('admin.admin_riwayat'))

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))

    totalProduk = len(db.data_barang)
    stokMenipis = len([b for b in db.data_barang if b['stok'] <= 10])
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_trx = [p for p in db.pesanan if p['tanggal'] == today_str]
    transaksiHariIni = len(today_trx) if today_trx else len(db.pesanan)
    
    total_income = sum(p['total'] for p in db.pesanan)
    pendapatan = formatRp(total_income)

    hasil_penjualan = {
        "Senin": {"makanan": 0, "minuman": 0, "alat tulis": 0},
        "Selasa": {"makanan": 0, "minuman": 0, "alat tulis": 0},
        "Rabu": {"makanan": 0, "minuman": 0, "alat tulis": 0},
        "Kamis": {"makanan": 0, "minuman": 0, "alat tulis": 0},
        "Jumat": {"makanan": 0, "minuman": 0, "alat tulis": 0},
    }
    
    nama_kategori = {}
    for b in db.data_barang:
        nama_kategori[b['nama'].lower()] = b['kategori'].lower()
        
    hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat"}
    
    for p in db.pesanan:
        try:
            dt = datetime.strptime(p['tanggal'], "%Y-%m-%d")
            wday = dt.weekday()
            if wday in hari_map:
                hari = hari_map[wday]
                for item in p.get('barang', []):
                    item_nama = item.get('nama', '').lower()
                    qty = item.get('jumlah', 0)
                    
                    kat = nama_kategori.get(item_nama, "")
                    if not kat:
                        if "roti" in item_nama or "mie" in item_nama or "donat" in item_nama or "keripik" in item_nama or "cemilan" in item_nama or "makanan" in item_nama:
                            kat = "makanan"
                        elif "air" in item_nama or "teh" in item_nama or "milk" in item_nama or "botol" in item_nama or "minuman" in item_nama:
                            kat = "minuman"
                        else:
                            kat = "alat tulis"
                            
                    if "makan" in kat:
                        kat_key = "makanan"
                    elif "minum" in kat:
                        kat_key = "minuman"
                    else:
                        kat_key = "alat tulis"
                        
                    hasil_penjualan[hari][kat_key] += qty
        except:
            continue

    total_sales_count = sum(sum(day.values()) for day in hasil_penjualan.values())
    if total_sales_count == 0:
        hasil_penjualan = {
            "Senin": {"makanan": 5, "minuman": 2, "alat tulis": 2},
            "Selasa": {"makanan": 0, "minuman": 5, "alat tulis": 5},
            "Rabu": {"makanan": 5, "minuman": 5, "alat tulis": 5},
            "Kamis": {"makanan": 6, "minuman": 7, "alat tulis": 5},
            "Jumat": {"makanan": 10, "minuman": 5, "alat tulis": 7},
        }

    y_hasilPenjualan = []
    for hari in hasil_penjualan:
        hasil = sum(hasil_penjualan[hari].values())
        y_hasilPenjualan.append(hasil)

    return render_template('07.Beranda_admin.html',
                           data_penjualan=y_hasilPenjualan,
                           card_product=totalProduk,
                           card_stock=stokMenipis,
                           card_transaction=transaksiHariIni,
                           card_income=pendapatan,
                           grafik_penjualan=hasil_penjualan)

@admin_bp.route('/admin/kelola_akun_penjual')
def admin_kelola_akun_penjual():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    keyword = request.args.get('cari', '').lower()
    if keyword:
        filtered = [p for p in db.data_penjual if keyword in p['nama'].lower() or keyword in p['email'].lower()]
    else:
        filtered = db.data_penjual
        
    return render_template('08.pengelola_akun_penjual.html', penjual=filtered, keyword=keyword)

@admin_bp.route('/admin/tambah-akun', methods=['GET', 'POST'])
def admin_tambah_akun():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    if request.method == 'POST':
        max_id = max([p['id'] for p in db.data_penjual], default=0)
        akun_baru = {
            'id': max_id + 1,
            'nama': request.form['nama'],
            'email': request.form['email'],
            'status': request.form['status'],
            'foto': 'profile.png'
        }
        db.data_penjual.append(akun_baru)
        db.save_penjual()
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
    return render_template('08.tambah_akun.html')

@admin_bp.route('/admin/edit-akun/<int:id>', methods=['GET', 'POST'])
def admin_edit_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    akun = next((p for p in db.data_penjual if p['id'] == id), None)
    if not akun:
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
        
    if request.method == 'POST':
        akun['nama'] = request.form['nama']
        akun['email'] = request.form['email']
        akun['status'] = request.form['status']
        db.save_penjual()
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
    return render_template('08.edit_akun.html', akun=akun)

@admin_bp.route('/admin/hapus-akun/<int:id>')
def admin_hapus_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    db.data_penjual = [p for p in db.data_penjual if p['id'] != id]
    db.save_penjual()
    return redirect(url_for('admin.admin_kelola_akun_penjual'))

@admin_bp.route('/admin/manajemen-barang')
def admin_manajemen_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    keyword = request.args.get('cari', '').lower()
    if keyword:
        filtered = [b for b in db.data_barang if keyword in b['nama'].lower() or keyword in b['kategori'].lower()]
    else:
        filtered = db.data_barang
    return render_template('09.manajemen_barang.html', data=filtered, keyword=request.args.get('cari', ''))

@admin_bp.route('/admin/pengisian_barang')
def admin_pengisian_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template('10.pengisian_barang_.html')

@admin_bp.route('/admin/pengisian_barang/<int:id>')
def admin_pengisian_barang_restok(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    barang = None
    for b in db.data_barang:
        if b['no'] == id:
            barang = b
            break
    if not barang:
        return redirect(url_for('admin.admin_pengisian_barang'))
    return render_template('10.pengisian_barang_.html', barang=barang)

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

    return render_template('10.rekap_barang.html', kategori=kategori, nama_barang=nama_barang, tanggal=tanggal, jumlah=jumlah, harga=harga_jual, catatan=catatan)

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

@admin_bp.route('/admin/cek-pembayaran')
def admin_cek_pembayaran():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    cari = request.args.get('cari', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    if cari:
        hasil = [p for p in db.pesanan if cari in p['id'].lower() or cari in p['pelanggan'].lower()]
    else:
        hasil = list(db.pesanan)
    total = len(hasil)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    transaksi = hasil[start:end]
    return render_template('21.cek_pembayaran.html', pesanan=transaksi,
                           page=page, total_pages=total_pages, total=total,
                           keyword=cari)

@admin_bp.route('/admin/cek-pembayaran/detail/<trx_id>')
def admin_cek_pembayaran_detail(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    order = None
    for p in db.pesanan:
        if p['id'] == trx_id:
            order = p
            break
    if not order:
        return "Transaksi tidak ditemukan", 404
    return render_template('21.cek_pembayaran_detail.html', order=order)

@admin_bp.route('/admin/cek-pembayaran/update-status/<trx_id>', methods=['POST'])
def admin_update_status(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    new_status = request.form.get('status', '').strip()
    if not new_status:
        return "Status tidak boleh kosong", 400
        
    order = None
    for p in db.pesanan:
        if p['id'] == trx_id:
            order = p
            break
            
    if not order:
        return "Transaksi tidak ditemukan", 404
        
    old_status = order.get('status', '')
    if old_status != new_status:
        order['status'] = new_status
        db.save_pesanan()
        
        if new_status == "Siap diambil":
            db.tambah_notifikasi(
                "Pembayaran Dikonfirmasi",
                f"Pembayaran {order['metode']} oleh {order['pelanggan']} senilai {formatRp(order['total'])} telah divalidasi",
                "hijau"
            )
        elif new_status == "Selesai":
            db.tambah_notifikasi(
                "Transaksi Selesai",
                f"Transaksi #{trx_id} oleh {order['pelanggan']} senilai {formatRp(order['total'])} telah selesai",
                "hijau"
            )
            
        admin_name = session.get('user', 'Admin')
        db.tambah_aktivitas(
            "ubah", 
            f"Mengubah status transaksi #{trx_id}: {old_status} -> {new_status}", 
            "Berhasil", 
            admin_name
        )
        
    return redirect(url_for('admin.admin_cek_pembayaran_detail', trx_id=trx_id))

@admin_bp.route('/admin/pengaturan', methods=['GET'])
def admin_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    logo_path = db.data_koperasi.get('logo', '')
    if logo_path:
        full_path = os.path.join(BASE_DIR, 'static', logo_path)
        if not os.path.exists(full_path):
            logo_path = 'image/logo_3.png'
    else:
        logo_path = 'image/logo_3.png'
        
    data = dict(db.data_koperasi)
    data['logo'] = logo_path
    return render_template('22.pengaturan_umum.html', **data)

@admin_bp.route('/admin/simpan_pengaturan', methods=['POST'])
def admin_simpan_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    db.data_koperasi['nama'] = request.form.get('nama', db.data_koperasi['nama'])
    db.data_koperasi['deskripsi'] = request.form.get('deskripsi', db.data_koperasi['deskripsi'])
    db.data_koperasi['alamat'] = request.form.get('alamat', db.data_koperasi['alamat'])
    db.data_koperasi['telepon'] = request.form.get('telepon', db.data_koperasi['telepon'])
    db.data_koperasi['jam'] = request.form.get('jam', db.data_koperasi['jam'])
    db.data_koperasi['hari'] = request.form.get('hari', db.data_koperasi['hari'])

    file = request.files.get('gambar')
    if file and file.filename:
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        db.data_koperasi['logo'] = 'gambar/' + filename
        
        file.seek(0)
        file.save(os.path.join(BASE_DIR, 'static', 'image', 'logo_3.png'))

    db.save_koperasi()
    return redirect(url_for('admin.admin_pengaturan'))
