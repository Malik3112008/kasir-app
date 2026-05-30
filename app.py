from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify
from werkzeug.utils import secure_filename
from jinja2 import ChoiceLoader, FileSystemLoader
import os
import secrets
import json
import csv
import io
import random
from datetime import datetime

# ============================================================
# APP SETUP
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev_secret_key')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # No caching during dev, change to 300 for prod

# Load templates dari kasir-admin dan kasir-pembeli
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'kasir-admin', 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'kasir-pembeli', 'templates')),
])

# ============================================================
# 404 NOT FOUND
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return '''
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Halaman Tidak Ditemukan</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { text-align: center; background: white; padding: 60px 50px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { font-size: 100px; color: #e74c3c; margin-bottom: 10px; }
            h2 { font-size: 24px; color: #333; margin-bottom: 15px; }
            p { color: #666; margin-bottom: 30px; font-size: 16px; }
            a { display: inline-block; padding: 12px 30px; background: #3498db; color: white; border-radius: 8px; text-decoration: none; font-size: 16px; margin: 5px; }
            a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>404</h1>
            <h2>Halaman Tidak Ditemukan</h2>
            <p>URL yang Anda cari tidak tersedia.</p>
            <a href="/admin/login">Admin</a>
            <a href="/pembeli/login">Pembeli</a>
        </div>
    </body>
    </html>
    ''', 404

# ============================================================
# ADMIN: BERANDA AWAL
# ============================================================

@app.route('/admin')
def admin_beranda_awal():
    return render_template('03.Beranda_awal.html')

# ============================================================
# ADMIN: DENAH
# ============================================================

CARDS_DATA = [
    {"id": 1, "text": "Rak Makanan Ringan", "icon": "fa-solid fa-cookie-bite", "href": "/admin/denah/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 130, "image": "images/makanan_ringan/gambar1.jpg"},
    {"id": 2, "text": "Rak Snack", "icon": "fa-solid fa-candy-cane", "href": "/admin/denah/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 300, "image": "images/makanan_ringan/gambar1.jpg"},
    {"id": 3, "text": "Rak Cemilan", "icon": "fa-solid fa-pizza-slice", "href": "/admin/denah/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 470, "image": "images/makanan_ringan/gambar1.jpg"},
    {"id": 4, "text": "Meja Kasir", "icon": "fa-solid fa-cash-register", "href": "/admin/denah/meja_kasir", "width": 220, "height": 180, "left": 520, "top": 140, "image": "images/meja_kasir/gambar1.jpg"},
    {"id": 5, "text": "Rak Alat Tulis", "icon": "fa-solid fa-book-open", "href": "/admin/denah/alat_tulis", "width": 180, "height": 230, "left": 870, "top": 130, "image": "images/alat_tulis/gambar1.jpg"},
    {"id": 6, "text": "Rak Makanan", "icon": "fa-solid fa-burger", "href": "/admin/denah/makanan", "width": 180, "height": 230, "left": 870, "top": 430, "image": "images/makanan/gambar1.jpg"},
    {"id": 7, "text": "Rak Minuman", "icon": "fa-solid fa-bottle-water", "href": "/admin/denah/minuman", "width": 180, "height": 430, "left": 1160, "top": 120, "image": "images/minuman/gambar1.jpg"},
    {"id": 8, "text": "Pintu Masuk/Keluar", "icon": "fa-solid fa-door-open", "href": "/admin/denah/pintu", "width": 420, "height": 120, "left": 430, "top": 640, "image": "images/pintu/gambar1.jpg"},
]

def load_cards():
    return CARDS_DATA

def save_cards(cards):
    global CARDS_DATA
    CARDS_DATA = cards

@app.route('/admin/denah')
def admin_denah():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    cards = load_cards()
    is_admin = True  # Always admin if logged in
    edit_mode = request.args.get('edit') == '1'
    edit_card_id = request.args.get('edit_card', type=int) if edit_mode else None
    edit_card = None
    if edit_card_id is not None:
        for card in cards:
            if card['id'] == edit_card_id:
                edit_card = card
                break
    return render_template('04.Denah.html', cards=cards, edit_mode=edit_mode, edit_card=edit_card, is_admin=is_admin, page='home')

@app.route('/admin/delete/<int:card_id>', methods=['POST'])
def admin_delete_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    cards = load_cards()
    cards = [c for c in cards if c['id'] != card_id]
    save_cards(cards)
    return redirect('/admin/denah?edit=1')

@app.route('/admin/update/<int:card_id>', methods=['POST'])
def admin_update_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    cards = load_cards()
    for card in cards:
        if card['id'] == card_id:
            card['text'] = request.form.get('text', card['text'])
            card['icon'] = request.form.get('icon', card['icon'])
            card['width'] = int(request.form.get('width', card['width']))
            card['height'] = int(request.form.get('height', card['height']))
            break
    save_cards(cards)
    return redirect('/admin/denah?edit=1')

@app.route('/admin/move/<int:card_id>', methods=['POST'])
def admin_move_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    data = request.get_json()
    cards = load_cards()
    for card in cards:
        if card['id'] == card_id:
            card['left'] = int(data.get('left', card['left']))
            card['top'] = int(data.get('top', card['top']))
            break
    save_cards(cards)
    return jsonify({'ok': True})

@app.route('/dynamic_cards.css')
def dynamic_cards_css():
    cards = load_cards()
    css_content = ""
    for card in cards:
        css_content += f".card-id-{card['id']} {{ width: {card['width']}px; height: {card['height']}px; left: {card['left']}px; top: {card['top']}px; }}\n"
    response = make_response(css_content)
    response.headers['Content-Type'] = 'text/css'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/admin/denah/<folder>')
def admin_detail(folder):
    title = folder.replace('-', ' ').replace('_', ' ').title()
    return render_template('04.Denah.html', title=title, folder=folder, page='detail')

# ============================================================
# ADMIN: LOGIN, REGISTER, FORGOT PASSWORD
# ============================================================

USERS = {'admin': 'admin123', 'pembeli': 'beli123'}
EMAIL_TO_USER = {}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        error = 'Nama akun atau kata sandi tidak cocok.'
    return render_template('05.1.login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not username or not email or not password:
            error = 'Lengkapi semua bidang.'
        elif password != confirm:
            error = 'Kata sandi dan konfirmasi tidak cocok.'
        elif username in USERS:
            error = 'Nama pengguna sudah terdaftar.'
        else:
            USERS[username] = password
            EMAIL_TO_USER[email] = username
            return redirect(url_for('admin_login'))
    return render_template('05.2.register.html', error=error)

@app.route('/admin/forgot', methods=['GET', 'POST'])
def admin_forgot():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['reset_email'] = email
        session['reset_user'] = EMAIL_TO_USER.get(email)
        otp = f"{secrets.randbelow(900000) + 100000}"
        session['otp'] = otp
        print(f"[DEBUG] OTP for {email}: {otp}")
        return redirect(url_for('admin_verify'))
    return render_template('05.3.forgot.html', error=error)

@app.route('/admin/verify', methods=['GET', 'POST'])
def admin_verify():
    error = None
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if otp and otp == session.get('otp'):
            return redirect(url_for('admin_reset'))
        error = 'Kode OTP tidak valid.'
    return render_template('05.4.verify_otp.html', error=error, email=session.get('reset_email'))

@app.route('/admin/reset', methods=['GET', 'POST'])
def admin_reset():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password:
            error = 'Masukkan kata sandi baru.'
        elif password != confirm:
            error = 'Konfirmasi kata sandi tidak cocok.'
        else:
            user = session.get('reset_user')
            if user:
                USERS[user] = password
            session.pop('otp', None)
            session.pop('reset_email', None)
            session.pop('reset_user', None)
            return redirect(url_for('admin_login'))
    return render_template('05.5.reset.html', error=error)

# ============================================================
# ADMIN: NOTIFIKASI
# ============================================================

notifikasi = [
    {"judul": "Pembelian Baru", "isi": "Transaksi #TRX005 oleh Ahmad Rizki senilai 18.000", "waktu": "10 menit lalu", "warna": "biru"},
    {"judul": "Stok Menipis", "isi": "Keripik singkong tersisa 3 unit", "waktu": "15 menit lalu", "warna": "orange"},
    {"judul": "Pembayaran Dikonfirmasi", "isi": "Pembayaran QRIS oleh Putri Amel senilai 10.000 telah divalidasi", "waktu": "20 menit lalu", "warna": "hijau"},
    {"judul": "Pembelian Dibatalkan", "isi": "Pembelian oleh Putri Amel senilai 10.000 telah dibatalkan", "waktu": "30 menit lalu", "warna": "merah"},
]

riwayat = []

@app.route("/admin/notifikasi")
def admin_notifikasi():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template("06.NotifikasiAdmin.html", notifikasi=notifikasi)

@app.route("/admin/riwayat")
def admin_riwayat():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template("06.RiwayatTransaksi.html", pesanan=pesanan)

@app.route("/admin/detail-transaksi/<trx_id>")
def admin_detail_transaksi(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    trx = None
    for p in pesanan:
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
    from datetime import datetime
    try:
        tgl_obj = datetime.strptime(trx['tanggal'], '%Y-%m-%d')
        bulan_id = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
        tanggal_fmt = f"{tgl_obj.day} {bulan_id[tgl_obj.month-1]} {tgl_obj.year}"
    except:
        tanggal_fmt = trx['tanggal']
    return render_template("detail_transaksi.html", items=items, total=total, tanggal=tanggal_fmt)

# ============================================================
# ADMIN: RIWAYAT AKTIVITAS
# ============================================================

data_aktivitas = [
    {"tipe": "login", "catatan": "Log in system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-28 08:00"},
    {"tipe": "tambah", "catatan": "Menambahkan pilihan barang: Roti Aoka", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-28 07:30"},
    {"tipe": "restok", "catatan": "Melakukan restok produk: Air Mineral (+50 unit)", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-28 07:00"},
    {"tipe": "logout", "catatan": "Log out system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-27 17:00"},
    {"tipe": "ubah", "catatan": "Mengubah harga: Bolpoin (Rp 3.500 -> Rp 4.000)", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-27 14:30"},
    {"tipe": "hapus", "catatan": "Menghapus pilihan barang: Kerupuk Bawang", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-27 11:20"},
    {"tipe": "login", "catatan": "Log in system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-27 08:00"},
]

@app.route("/admin/riwayat-aktivitas")
def admin_riwayat_aktivitas():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    daftar_admin = list(set(d['admin'] for d in data_aktivitas))
    return render_template("24.RiwayatAktivitas.html", daftar_admin=daftar_admin)

@app.route("/admin/api/aktivitas")
def admin_api_aktivitas():
    search = request.args.get('search', '').lower()
    admin_filter = request.args.get('admin', 'Pilihan Admin')
    tanggal = request.args.get('tanggal', '')
    hasil = data_aktivitas
    if search:
        hasil = [d for d in hasil if search in d['catatan'].lower()]
    if admin_filter != 'Pilihan Admin':
        hasil = [d for d in hasil if admin_filter in d['admin']]
    if tanggal:
        hasil = [d for d in hasil if d['waktu'].startswith(tanggal)]
    return jsonify(hasil)

@app.route("/admin/hapus-semua", methods=["POST"])
def admin_hapus_semua():
    global notifikasi, riwayat
    riwayat.extend(notifikasi)
    notifikasi.clear()
    return redirect("/admin/notifikasi")

@app.route('/admin/hapus-notif/<int:index>', methods=['POST'])
def admin_hapus_notif(index):
    if index < len(notifikasi):
        riwayat.append(notifikasi[index])
        notifikasi.pop(index)
    return redirect('/admin/notifikasi')

@app.route('/admin/hapus-riwayat-satuan/<int:index>', methods=['POST'])
def admin_hapus_riwayat_satuan(index):
    if index < len(riwayat):
        riwayat.pop(index)
    return redirect('/admin/riwayat')

@app.route("/admin/hapus-riwayat", methods=["POST"])
def admin_hapus_riwayat():
    global riwayat
    riwayat.clear()
    return redirect("/admin/riwayat")

# ============================================================
# ADMIN: DASHBOARD
# ============================================================

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user'):
        return redirect(url_for('admin_login'))

    totalProduk = 10
    stokMenipis = 2
    transaksiHariIni = 7
    pendapatan = 1000000

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

# ============================================================
# ADMIN: KELOLA AKUN PENJUAL
# ============================================================

data_penjual = [
    {"nama": "Zulfikar Aril", "email": "aril_10@gmail.com", "status": "Aktif", "foto": "profile.png"},
    {"nama": "Nafilah Yasmin", "email": "yasmin18@gmail.com", "status": "Tidak aktif", "foto": "profile.png"},
    {"nama": "Febriyanto", "email": "febri1711@gmail.com", "status": "Aktif", "foto": "profile.png"},
    {"nama": "Shafira Amelia", "email": "shafiramel@gmail.com", "status": "Aktif", "foto": "profile.png"},
]

@app.route('/admin/kelola_akun_penjual')
def admin_kelola_akun_penjual():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template('08.pengelola_akun_penjual.html', penjual=data_penjual)

@app.route('/admin/tambah-akun', methods=['GET', 'POST'])
def admin_tambah_akun():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        akun_baru = {
            'nama': request.form['nama'],
            'email': request.form['email'],
            'status': request.form['status'],
            'foto': 'profile.png'
        }
        data_penjual.append(akun_baru)
        return redirect(url_for('admin_kelola_akun_penjual'))
    return render_template('08.tambah_akun.html')

@app.route('/admin/edit-akun/<int:id>', methods=['GET', 'POST'])
def admin_edit_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    if id < 0 or id >= len(data_penjual):
        return redirect(url_for('admin_kelola_akun_penjual'))
    akun = data_penjual[id]
    if request.method == 'POST':
        akun['nama'] = request.form['nama']
        akun['email'] = request.form['email']
        akun['status'] = request.form['status']
        return redirect(url_for('admin_kelola_akun_penjual'))
    return render_template('08.edit_akun.html', akun=akun)

@app.route('/admin/hapus-akun/<int:id>')
def admin_hapus_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    global data_penjual
    if 0 <= id < len(data_penjual):
        data_penjual.pop(id)
    return redirect(url_for('admin_kelola_akun_penjual'))

# ============================================================
# ADMIN: MANAJEMEN BARANG
# ============================================================

@app.route('/admin/manajemen-barang')
def admin_manajemen_barang():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    keyword = request.args.get('cari', '').lower()
    if keyword:
        filtered = [b for b in data_barang if keyword in b['nama'].lower() or keyword in b['kategori'].lower()]
    else:
        filtered = data_barang
    return render_template('09.manajemen_barang.html', data=filtered, keyword=request.args.get('cari', ''))

# ============================================================
# ADMIN: PENGISIAN BARANG
# ============================================================

@app.route('/admin/pengisian_barang')
def admin_pengisian_barang():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template('10.pengisian_barang_.html')

@app.route('/admin/pengisian_barang/<int:id>')
def admin_pengisian_barang_restok(id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    barang = None
    for b in data_barang:
        if b['no'] == id:
            barang = b
            break
    if not barang:
        return redirect(url_for('admin_pengisian_barang'))
    return render_template('10.pengisian_barang_.html', barang=barang)

@app.route('/admin/simpan', methods=['POST'])
def admin_simpan():
    kategori = request.form['kategori']
    nama_barang = request.form['nama_barang']
    tanggal = request.form['tanggal']
    jumlah = request.form['jumlah']
    harga_beli = request.form.get('harga_beli', '0')
    harga_jual = request.form.get('harga_jual', request.form.get('harga', '0'))
    catatan = request.form.get('catatan', '')
    restok_id = request.form.get('restok_id')

    # If restok, update existing item stock
    if restok_id:
        for b in data_barang:
            if str(b['no']) == str(restok_id):
                b['stok'] = b.get('stok', 0) + int(jumlah)
                break

    return render_template('10.rekap_barang.html', kategori=kategori, nama_barang=nama_barang, tanggal=tanggal, jumlah=jumlah, harga=harga_jual, catatan=catatan)

@app.route('/admin/konfirmasi-barang')
def admin_konfirmasi_barang():
    nama_barang = request.args.get('nama_barang', '-')
    kategori = request.args.get('kategori', '-')
    harga = request.args.get('harga', '0')
    jumlah = request.args.get('jumlah', '0')
    return render_template('17. konfirmasi barang.html', nama_barang=nama_barang, kategori=kategori, harga=harga, jumlah=jumlah)

# ============================================================
# ADMIN: STOK TERSEDIA
# ============================================================

@app.route('/admin/stok-tersedia')
def admin_stok_tersedia():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    keyword = request.args.get('cari', '').lower()
    kategori = request.args.get('kategori', '')
    page = int(request.args.get('page', 1))
    per_page = 5

    filtered = data_barang
    if keyword:
        filtered = [b for b in filtered if keyword in b['nama'].lower()]
    if kategori:
        filtered = [b for b in filtered if b['kategori'] == kategori]

    total_halaman = max(1, (len(filtered) + per_page - 1) // per_page)
    start = (page - 1) * per_page
    data_page = filtered[start:start + per_page]

    return render_template('14. stoktersedia.html',
        data=data_page, page=page, total_halaman=total_halaman,
        keyword=request.args.get('cari', ''), kategori=kategori)

@app.route('/admin/stok-tersedia/edit/<int:id>', methods=['GET', 'POST'])
def admin_stok_tersedia_edit(id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    barang = None
    for b in data_barang:
        if b['no'] == id:
            barang = b
            break
    if not barang:
        return "Barang tidak ditemukan", 404
    if request.method == 'POST':
        barang['nama'] = request.form.get('nama', barang['nama'])
        barang['berat'] = request.form.get('berat', barang['berat'])
        barang['kategori'] = request.form.get('kategori', barang['kategori'])
        barang['stok'] = int(request.form.get('stok', barang['stok']))
        barang['harga'] = int(request.form.get('harga', barang['harga']))
        return redirect(url_for('admin_stok_tersedia'))
    return render_template('14. stoktersedia.html',
        data=[barang], page=1, total_halaman=1,
        keyword='', kategori='', edit_item=barang)

@app.route('/admin/stok-tersedia/hapus/<int:id>', methods=['POST'])
def admin_stok_tersedia_hapus(id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    global data_barang
    data_barang = [b for b in data_barang if b['no'] != id]
    return redirect(url_for('admin_stok_tersedia'))

# ============================================================
# ADMIN: CETAK LAPORAN
# ============================================================

data_barang = [
    {"no": 1, "nama": "Roti Aoka", "berat": "100 gram", "stok": 15, "harga": 3000, "kategori": "Makanan", "tanggal": "2026-05-03", "gambar": "gambar dan icon/gambar roti aoka.jpeg", "rating": 5, "emoji": "🍞"},
    {"no": 2, "nama": "Donat", "berat": "80 gram", "stok": 10, "harga": 5000, "kategori": "Makanan", "tanggal": "2026-05-03", "gambar": "gambar dan icon/roti.jpg", "rating": 4, "emoji": "🍩"},
    {"no": 3, "nama": "Mie Instan", "berat": "75 gram", "stok": 50, "harga": 4000, "kategori": "Makanan", "tanggal": "2026-05-08", "gambar": "gambar dan icon/roti.jpg", "rating": 4, "emoji": "🍜"},
    {"no": 4, "nama": "Keripik Kentang", "berat": "50 gram", "stok": 22, "harga": 10000, "kategori": "Makanan", "tanggal": "2026-05-11", "gambar": "gambar dan icon/roti.jpg", "rating": 4, "emoji": "🥔"},
    {"no": 5, "nama": "Sosis", "berat": "60 gram", "stok": 20, "harga": 2000, "kategori": "Makanan", "tanggal": "2026-05-12", "gambar": "gambar dan icon/roti.jpg", "rating": 3, "emoji": "🌭"},
    {"no": 6, "nama": "Air Mineral", "berat": "500 ml", "stok": 35, "harga": 3000, "kategori": "Minuman", "tanggal": "2026-05-06", "gambar": "gambar dan icon/ades.jpg", "rating": 5, "emoji": "💧"},
    {"no": 7, "nama": "Teh Botol", "berat": "350 ml", "stok": 18, "harga": 5000, "kategori": "Minuman", "tanggal": "2026-05-07", "gambar": "gambar dan icon/gambar le mineral.jpeg", "rating": 3, "emoji": "🍵"},
    {"no": 8, "nama": "Susu Kotak", "berat": "250 ml", "stok": 12, "harga": 7000, "kategori": "Minuman", "tanggal": "2026-05-10", "gambar": "gambar dan icon/gambar le mineral.jpeg", "rating": 4, "emoji": "🥛"},
    {"no": 9, "nama": "Kopi Sachet", "berat": "20 gram", "stok": 30, "harga": 4000, "kategori": "Minuman", "tanggal": "2026-05-13", "gambar": "gambar dan icon/ades.jpg", "rating": 3, "emoji": "☕"},
    {"no": 10, "nama": "Es Krim", "berat": "100 ml", "stok": 15, "harga": 4500, "kategori": "Minuman", "tanggal": "2026-05-14", "gambar": "gambar dan icon/gambar le mineral.jpeg", "rating": 4, "emoji": "🍦"},
    {"no": 11, "nama": "Pensil", "berat": "10 gram", "stok": 30, "harga": 2000, "kategori": "Alat Tulis", "tanggal": "2026-05-03", "gambar": "gambar dan icon/gambar pensil.jpeg", "rating": 4, "emoji": "✏️"},
    {"no": 12, "nama": "Bolpoin", "berat": "15 gram", "stok": 25, "harga": 4000, "kategori": "Alat Tulis", "tanggal": "2026-05-04", "gambar": "gambar dan icon/bulpoin.jpg", "rating": 3, "emoji": "🖊️"},
    {"no": 13, "nama": "Buku Tulis", "berat": "200 gram", "stok": 40, "harga": 6000, "kategori": "Alat Tulis", "tanggal": "2026-05-05", "gambar": "gambar dan icon/gambar pensil.jpeg", "rating": 4, "emoji": "📓"},
    {"no": 14, "nama": "Penghapus", "berat": "20 gram", "stok": 15, "harga": 2000, "kategori": "Alat Tulis", "tanggal": "2026-05-09", "gambar": "gambar dan icon/gambar penghapus.jpeg", "rating": 5, "emoji": "🧽"},
    {"no": 15, "nama": "Spidol", "berat": "25 gram", "stok": 14, "harga": 8000, "kategori": "Alat Tulis", "tanggal": "2026-05-12", "gambar": "gambar dan icon/gambar pulpen.jpeg", "rating": 4, "emoji": "🖍️"},
    {"no": 16, "nama": "Tipe X", "berat": "30 gram", "stok": 25, "harga": 5000, "kategori": "Alat Tulis", "tanggal": "2026-05-15", "gambar": "gambar dan icon/gambar tipe ex.jpeg", "rating": 5, "emoji": "📝"},
]

@app.route('/admin/cetak_laporan', methods=['GET', 'POST'])
def admin_cetak_laporan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))

    # Data transaksi sample (bisa diganti dari pesanan[])
    data_transaksi = []
    for p in pesanan:
        total_barang = sum(b['harga'] * b['jumlah'] for b in p['barang'])
        data_transaksi.append({
            'tanggal': p['tanggal'],
            'id': p['id'],
            'jumlah': sum(b['jumlah'] for b in p['barang']),
            'total': total_barang
        })

    # Tambah data sample jika pesanan kosong
    if not data_transaksi:
        data_transaksi = [
            {'tanggal': '2026-05-01', 'id': 'TRX001', 'jumlah': 3, 'total': 15000},
            {'tanggal': '2026-05-02', 'id': 'TRX002', 'jumlah': 5, 'total': 25000},
            {'tanggal': '2026-05-03', 'id': 'TRX003', 'jumlah': 2, 'total': 10000},
        ]

    total_pendapatan = sum(t['total'] for t in data_transaksi)
    modal_barang = int(total_pendapatan * 0.7)
    untung_rugi = total_pendapatan - modal_barang

    return render_template('12. cetaklaporan.html',
        barang=data_barang, formatRp=formatRp,
        total_pendapatan=total_pendapatan,
        modal_barang=modal_barang,
        untung_rugi=untung_rugi,
        data_transaksi=data_transaksi)

@app.route('/admin/cetak_laporan_barang')
def admin_cetak_laporan_barang():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    total_nilai = sum(b['harga'] * b['stok'] for b in data_barang)
    return render_template('12. cetaklaporan_barang.html',
        data_barang=data_barang,
        total_nilai=total_nilai)

@app.route('/admin/laporan_penjualan', methods=['GET', 'POST'])
def admin_laporan_penjualan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))

    # Kalender
    tanggal_awal = "2026-01-01"
    tanggal_akhir = "2026-12-31"

    if request.method == "POST":
        tanggal_awal = request.form.get("tanggal_awal", "2026-01-01")
        tanggal_akhir = request.form.get("tanggal_akhir", "2026-12-31")
        if tanggal_akhir < tanggal_awal:
            tanggal_akhir = tanggal_awal

    def Rupiah(angka):
        return "Rp{:,.2f}".format(angka).replace(",", "X").replace(".", ",").replace("X", ".")

    # Data harian
    data_harian = {
        "2026-04-06": {"hari": "Senin", "totalTransaksi": 35, "totalPendapatan": 98000, "modalBarang": 74000},
        "2026-04-07": {"hari": "Selasa", "totalTransaksi": 38, "totalPendapatan": 110000, "modalBarang": 83000},
        "2026-04-08": {"hari": "Rabu", "totalTransaksi": 48, "totalPendapatan": 200000, "modalBarang": 150000},
        "2026-04-09": {"hari": "Kamis", "totalTransaksi": 37, "totalPendapatan": 104000, "modalBarang": 78000},
        "2026-04-10": {"hari": "Jumat", "totalTransaksi": 39, "totalPendapatan": 110000, "modalBarang": 83000},
        "2026-05-01": {"hari": "Jumat", "totalTransaksi": 35, "totalPendapatan": 100000, "modalBarang": 75000},
        "2026-05-04": {"hari": "Senin", "totalTransaksi": 35, "totalPendapatan": 100000, "modalBarang": 75000},
        "2026-05-05": {"hari": "Selasa", "totalTransaksi": 35, "totalPendapatan": 100000, "modalBarang": 75000},
        "2026-05-06": {"hari": "Rabu", "totalTransaksi": 34, "totalPendapatan": 98000, "modalBarang": 74000},
        "2026-05-07": {"hari": "Kamis", "totalTransaksi": 44, "totalPendapatan": 118000, "modalBarang": 89000},
        "2026-05-08": {"hari": "Jumat", "totalTransaksi": 34, "totalPendapatan": 98000, "modalBarang": 74000},
        "2026-05-11": {"hari": "Senin", "totalTransaksi": 33, "totalPendapatan": 94000, "modalBarang": 71000},
        "2026-05-12": {"hari": "Selasa", "totalTransaksi": 35, "totalPendapatan": 101000, "modalBarang": 76000},
        "2026-05-13": {"hari": "Rabu", "totalTransaksi": 33, "totalPendapatan": 95000, "modalBarang": 71000},
        "2026-05-14": {"hari": "Kamis", "totalTransaksi": 34, "totalPendapatan": 98000, "modalBarang": 74000},
        "2026-05-15": {"hari": "Jumat", "totalTransaksi": 33, "totalPendapatan": 96000, "modalBarang": 72000},
    }

    # kolom informasi penting
    totalTransaksi = 0
    totalPendapatan = 0
    modalBarang = 0
    for tanggal, data in data_harian.items():
        if tanggal_awal <= tanggal <= tanggal_akhir:
            totalTransaksi += data["totalTransaksi"]
            totalPendapatan += data["totalPendapatan"]
            modalBarang += data["modalBarang"]
    untungRugi = totalPendapatan - modalBarang
    totalPendapatan = Rupiah(totalPendapatan)
    modalBarang = Rupiah(modalBarang)
    if untungRugi >= 0:
        untungRugi = "+" + Rupiah(untungRugi)
    else:
        untungRugi = "-" + Rupiah(abs(untungRugi))

    # Data diagram produk terlaris
    data_chart_produk_terlaris_perhari = {
        "2026-04-06": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [10, 5, 10, 7, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-04-07": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [12, 6, 8, 8, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-04-08": {"namaProduk": ["Air mineral","Aoka","Pensil","Pulpen","Buku","Pop mie"], "jumlahProduk": [11, 6, 9, 7, 3, 12], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple", "Green"]},
        "2026-04-09": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [10, 7, 10, 7, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-04-10": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [12, 6, 9, 8, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-01": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 9, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-04": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 9, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-05": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 9, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-06": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 8, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-07": {"namaProduk": ["Air mineral","Aoka","Pensil","Pulpen","Buku","Penghapus"], "jumlahProduk": [7, 8, 8, 7, 4, 10], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple", "Pink"]},
        "2026-05-08": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 8, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-11": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 8, 7, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-12": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [8, 7, 9, 7, 4], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-13": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 7, 8, 8, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-14": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [7, 8, 9, 7, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
        "2026-05-15": {"namaProduk": ["Air mineral", "Aoka", "Pensil", "Pulpen", "Buku"], "jumlahProduk": [8, 7, 8, 7, 3], "warnadiagramPT": ["Blue", "Orange", "Red", "Yellow", "Purple"]},
    }

    # Diagram produk terlaris
    total_produk = {}
    for tanggal, chart in data_chart_produk_terlaris_perhari.items():
        if tanggal_awal <= tanggal <= tanggal_akhir:
            for i in range(len(chart["namaProduk"])):
                nama = chart["namaProduk"][i]
                jumlah = chart["jumlahProduk"][i]
                if nama not in total_produk:
                    total_produk[nama] = 0
                total_produk[nama] += jumlah
    namaProduk = list(total_produk.keys())
    jumlahProduk = list(total_produk.values())
    warna_produk = {"Air mineral": "blue", "Aoka": "orange", "Pensil": "red", "Pulpen": "yellow", "Buku": "purple", "Pop mie": "green", "Penghapus": "pink"}
    warnadiagramPT = [warna_produk.get(produk, "gray") for produk in namaProduk]

    # Data Diagram pendapatan perkategori
    data_chart_pendapatan_perkategori_perhari = {
        "2026-04-06": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [30000, 53000, 15000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-04-07": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [36000, 56000, 18000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-04-08": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [33000, 53000, 114000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-04-09": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [30000, 53000, 21000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-04-10": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [36000, 56000, 18000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-01": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 55000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-04": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 55000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-05": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 55000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-06": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 53000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-07": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 73000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-08": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 53000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-11": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 49000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-12": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [24000, 56000, 21000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-13": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 53000, 21000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-14": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [21000, 53000, 24000], "warnadiagramPP": ["Blue", "Red", "Green"]},
        "2026-05-15": {"kategori": ["Minuman", "Alat tulis", "Makanan"], "pendapatanPerkategori": [24000, 51000, 21000], "warnadiagramPP": ["Blue", "Red", "Green"]},
    }

    # Diagram pendapatan perkategori
    total_kategori = {}
    for tanggal, chart in data_chart_pendapatan_perkategori_perhari.items():
        if tanggal_awal <= tanggal <= tanggal_akhir:
            for i in range(len(chart["kategori"])):
                nama = chart["kategori"][i]
                jumlah = chart["pendapatanPerkategori"][i]
                if nama not in total_kategori:
                    total_kategori[nama] = 0
                total_kategori[nama] += jumlah
    kategori = list(total_kategori.keys())
    pendapatanPerkategori = list(total_kategori.values())
    warna_kategori = {"Minuman": "blue", "Alat tulis": "red", "Makanan": "green"}
    warnadiagramPP = [warna_kategori.get(k, "gray") for k in kategori]

    # Diagram perbandingan pendapatan tiap bulan
    pendapatanbulan = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
    pendapatanPerbulan = []
    for bulan in range(1, 13):
        total = 0
        hasData = False
        for tanggal, data in data_harian.items():
            tahun, bln, hari = map(int, tanggal.split("-"))
            if tanggal_awal <= tanggal <= tanggal_akhir and bln == bulan:
                total += data["totalPendapatan"]
                hasData = True
        pendapatanPerbulan.append(total if hasData else None)

    # Diagram perbandingan jumlah transaksi tiap bulan
    transaksiperbulan = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
    jumlahtransaksiPerbulan = []
    for bulan in range(1, 13):
        total = 0
        hasData = False
        for tanggal, data in data_harian.items():
            tahun, bln, hari = map(int, tanggal.split("-"))
            if tanggal_awal <= tanggal <= tanggal_akhir and bln == bulan:
                total += data["totalTransaksi"]
                hasData = True
        jumlahtransaksiPerbulan.append(total if hasData else None)

    return render_template('15.Laporan_Penjualan.html',
        tanggal_awal=tanggal_awal, tanggal_akhir=tanggal_akhir,
        TT=totalTransaksi, TP=totalPendapatan, MB=modalBarang, UG=untungRugi,
        NP=namaProduk, JP=jumlahProduk, WPT=warnadiagramPT,
        KT=kategori, PPK=pendapatanPerkategori, WPP=warnadiagramPP,
        PL=pendapatanbulan, PPB=pendapatanPerbulan,
        TSP=transaksiperbulan, JTP=jumlahtransaksiPerbulan)

# ============================================================
# ADMIN: SIAPKAN PESANAN
# ============================================================

status_tunai = ["Disiapkan", "Siap diambil", "Menunggu Pembayaran", "Sudah diambil"]
status_qris  = ["Disiapkan", "Siap diambil", "Sudah diambil"]

pesanan = [
    {"id": "TRX001", "tanggal": "2025-11-15", "pelanggan": "Ahmad Rizki", "metode": "Tunai", "status": "Disiapkan",
     "barang": [{"nama": "Roti Tawar", "jumlah": 2, "harga": 8000, "gambar": "gambar dan icon/gambar roti aoka.jpeg"}, {"nama": "Air Mineral", "jumlah": 1, "harga": 3000, "gambar": "gambar dan icon/ades.jpg"}]},
    {"id": "TRX002", "tanggal": "2025-11-15", "pelanggan": "Siti Nurhazila", "metode": "QRIS", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar dan icon/gambar pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar dan icon/gambar penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar dan icon/gambar pensil.jpeg"}]},
    {"id": "TRX003", "tanggal": "2025-11-15", "pelanggan": "Diki Nurhazila", "metode": "Tunai", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar dan icon/gambar pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar dan icon/gambar penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar dan icon/gambar pensil.jpeg"}]},
    {"id": "TRX004", "tanggal": "2025-11-15", "pelanggan": "Siti riki", "metode": "QRIS", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar dan icon/gambar pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar dan icon/gambar penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar dan icon/gambar pensil.jpeg"}]},
]

def hitung_total_barang(barang):
    total = 0
    for b in barang:
        total += b["jumlah"] * b["harga"]
    return total

for p in pesanan:
    p["total_awal"] = hitung_total_barang(p["barang"])
    p["total"] = p["total_awal"]
    p["refund"] = 0

def formatRp(rupiah):
    return "Rp {:,.0f}".format(rupiah).replace(",", ".")

def get_status_list(pesan):
    return status_qris if pesan['metode'].lower() == 'qris' else status_tunai

@app.route('/admin/siapkan-pesanan', methods=['GET', 'POST'])
def admin_siapkan_pesanan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        trx_id = request.form["trx_id"]
        new_status = request.form.get("status")
        for i in pesanan:
            if i['id'] == trx_id:
                if new_status:
                    i['status'] = new_status
                else:
                    ganti = get_status_list(i)
                    ubah = ganti.index(i['status'])
                    if ubah + 1 < len(ganti):
                        i['status'] = ganti[ubah + 1]
                break
        return redirect('/admin/siapkan-pesanan')
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(pesanan)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    pesanan_page = pesanan[start:end]
    return render_template('19.SiapkanPesanan.html', pesanan=pesanan_page, formatRp=formatRp,
                           status=get_status_list, page=page, total_pages=total_pages, total=total)

@app.route("/admin/hapus-barang", methods=["POST"])
def admin_hapus_barang():
    trx_id = request.form["trx_id"]
    nama_barang = request.form["nama_barang"]
    for p in pesanan:
        if p["id"] == trx_id:
            dihapus = None
            for b in p["barang"]:
                if b["nama"] == nama_barang:
                    dihapus = b
                    break
            if dihapus:
                dihapus["jumlah"] -= 1
                if dihapus["jumlah"] <= 0:
                    p["barang"].remove(dihapus)
                p["total"] = hitung_total_barang(p["barang"])
                p["refund"] = p["total_awal"] - p["total"]
            break
    return redirect("/admin/siapkan-pesanan")

# ============================================================
# ADMIN: CEK PEMBAYARAN
# ============================================================

@app.route('/admin/cek-pembayaran')
def admin_cek_pembayaran():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    cari = request.args.get('cari', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    if cari:
        hasil = [p for p in pesanan if cari in p['id'].lower() or cari in p['pelanggan'].lower()]
    else:
        hasil = list(pesanan)
    total = len(hasil)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    transaksi = hasil[start:end]
    return render_template('21.cek_pembayaran.html', pesanan=transaksi,
                           page=page, total_pages=total_pages, total=total,
                           keyword=cari)

@app.route('/admin/cek-pembayaran/detail/<trx_id>')
def admin_cek_pembayaran_detail(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    order = None
    for p in pesanan:
        if p['id'] == trx_id:
            order = p
            break
    if not order:
        return "Transaksi tidak ditemukan", 404
    return render_template('21.cek_pembayaran_detail.html', order=order)

# ============================================================
# ADMIN: PENGATURAN
# ============================================================

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'gambar')
DATA_FILE = os.path.join(BASE_DIR, 'data_koperasi.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'nama': 'Koperasi Sekolah',
        'deskripsi': 'Koperasi untuk siswa dan guru',
        'alamat': 'Jl. Pendidikan No. 1',
        'telepon': '0341-123456',
        'jam': '07.00 - 15.00',
        'hari': 'Senin - Jumat',
        'logo': 'newlogo.jpeg'
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

data_koperasi = load_data()

@app.route('/admin/pengaturan', methods=['GET'])
def admin_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template('22.pengaturan_umum.html', **data_koperasi)

@app.route('/admin/simpan_pengaturan', methods=['POST'])
def admin_simpan_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    global data_koperasi
    data_koperasi['nama'] = request.form.get('nama', data_koperasi['nama'])
    data_koperasi['deskripsi'] = request.form.get('deskripsi', data_koperasi['deskripsi'])
    data_koperasi['alamat'] = request.form.get('alamat', data_koperasi['alamat'])
    data_koperasi['telepon'] = request.form.get('telepon', data_koperasi['telepon'])
    data_koperasi['jam'] = request.form.get('jam', data_koperasi['jam'])
    data_koperasi['hari'] = request.form.get('hari', data_koperasi['hari'])

    # Handle logo file upload (from modal form field "gambar")
    file = request.files.get('gambar')
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        data_koperasi['logo'] = filename

    save_data(data_koperasi)
    return redirect(url_for('admin_pengaturan'))

# ============================================================
# PEMBELI: LOGIN & LOGOUT
# ============================================================

@app.route('/pembeli/login', methods=['GET', 'POST'])
def pembeli_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if USERS.get(username) == password:
            session['user'] = username
            session['role'] = 'pembeli'
            session['nama'] = username
            return redirect(url_for('pembeli_home'))
        error = 'Nama akun atau kata sandi tidak cocok.'
    return render_template('login_pembeli.html', error=error)

@app.route('/pembeli/register', methods=['GET', 'POST'])
def pembeli_register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Nama akun dan kata sandi wajib diisi.'
        elif username in USERS:
            error = 'Nama akun sudah digunakan.'
        else:
            USERS[username] = password
            return redirect(url_for('pembeli_login'))
    return render_template('register_pembeli.html', error=error)

@app.route('/pembeli/logout')
def pembeli_logout():
    session.clear()
    return redirect(url_for('pembeli_login'))

# ============================================================
# PEMBELI: RESET PASSWORD (OTP FLOW)
# ============================================================

otp_storage = {}  # email -> otp code

@app.route('/pembeli/reset-password', methods=['GET', 'POST'])
def pembeli_reset_password():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@app.route('/pembeli/kirim-otp', methods=['GET', 'POST'])
def pembeli_kirim_otp():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@app.route('/pembeli/verifikasi-email', methods=['GET', 'POST'])
def pembeli_verifikasi_email():
    error = None
    email = session.get('reset_email', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['reset_email'] = email
        return redirect(url_for('pembeli_verifikasi_otp'))
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@app.route('/pembeli/verifikasi-otp', methods=['GET', 'POST'])
def pembeli_verifikasi_otp():
    error = None
    email = session.get('reset_email', '')
    if request.method == 'POST':
        kode = ''.join([
            request.form.get('kode1', ''),
            request.form.get('kode2', ''),
            request.form.get('kode3', ''),
            request.form.get('kode4', ''),
            request.form.get('kode5', ''),
        ])
        stored_otp = otp_storage.get(email, '')
        if kode == stored_otp:
            session['otp_verified'] = True
            return redirect(url_for('pembeli_ganti_password'))
        error = 'Kode OTP tidak cocok.'
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@app.route('/pembeli/ganti-password', methods=['GET', 'POST'])
def pembeli_ganti_password():
    error = None
    if not session.get('otp_verified'):
        return redirect(url_for('pembeli_reset_password'))
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if not password or len(password) < 8:
            error = 'Kata sandi minimal 8 karakter.'
        elif password != confirm:
            error = 'Konfirmasi kata sandi tidak cocok.'
        else:
            email = session.get('reset_email', '')
            otp_storage.pop(email, None)
            session.pop('otp_verified', None)
            session.pop('reset_email', None)
            return render_template('notifikasi_berhasil_pembeli.html', message='Kata sandi berhasil diubah. Silakan login dengan kata sandi baru.')
    return render_template('reset_pembeli.html', error=error)

# ============================================================
# PEMBELI: HOME
# ============================================================

@app.route('/pembeli')
def pembeli_home():
    if not session.get('user'):
        return redirect(url_for('pembeli_login'))
    cart_count = sum(item['jumlah'] for item in cart.values())
    return render_template('14-kategorialattulis.html', barang=data_barang, cart_count=cart_count)

# ============================================================
# PEMBELI: KATEGORI ALAT TULIS
# ============================================================

barang_pembeli = [
    {"id": 1, "nama": "Pensil", "harga": 2000, "stok": 30, "rating": 4, "gambar": "gambar/gambar pensil.jpeg", "kategori": "Alat Tulis", "deskripsi": "Pensil HB standar untuk menulis dan menggambar."},
    {"id": 2, "nama": "Bolpoin", "harga": 4000, "stok": 40, "rating": 3, "gambar": "gambar/gambar pulpen.jpeg", "kategori": "Alat Tulis", "deskripsi": "Bolpoin hitam dengan tinta lancar."},
    {"id": 3, "nama": "Penghapus", "harga": 2000, "stok": 20, "rating": 2, "gambar": "gambar/gambar penghapus.jpeg", "kategori": "Alat Tulis", "deskripsi": "Penghapus lembut tidak merusak kertas."},
    {"id": 4, "nama": "Tipe x", "harga": 5000, "stok": 25, "rating": 5, "gambar": "gambar/gambar tipe ex.jpeg", "kategori": "Alat Tulis", "deskripsi": "Tipe-X kering cepat kering dan rapi."},
]

@app.route('/pembeli/detail-barang/<int:id>')
def pembeli_detail_barang(id):
    if not session.get('user'):
        return redirect(url_for('pembeli_login'))
    barang = None
    for b in barang_pembeli:
        if b['id'] == id:
            barang = b
            break
    if not barang:
        for b in data_barang:
            if b['no'] == id:
                barang = {'id': b['no'], 'nama': b['nama'], 'harga': b['harga'], 'stok': b['stok'],
                          'gambar': '/static/img/default.png', 'kategori': b['kategori'], 'rating': 4,
                          'deskripsi': f"{b['nama']} dari kategori {b['kategori']}."}
                break
    if not barang:
        return "Barang tidak ditemukan", 404
    return render_template('7-detailbarang.html', barang=barang, formatRp=formatRp)

# ============================================================
# PEMBELI: KERANJANG
# ============================================================

cart = {}

@app.route('/pembeli/tambah-keranjang', methods=['POST'])
def pembeli_tambah_keranjang():
    nama = request.form.get('nama', '').strip()
    harga = int(request.form.get('harga', 0))
    jumlah = int(request.form.get('jumlah', 1))
    if nama and jumlah > 0:
        if nama in cart:
            cart[nama]['jumlah'] += jumlah
        else:
            cart[nama] = {'harga': harga, 'jumlah': jumlah}
    return redirect('/pembeli?added=1')

@app.route('/pembeli/update-keranjang', methods=['POST'])
def pembeli_update_keranjang():
    nama = request.form.get('nama', '').strip()
    aksi = request.form.get('aksi', '')
    if nama in cart:
        if aksi == 'tambah':
            cart[nama]['jumlah'] += 1
        elif aksi == 'kurang':
            cart[nama]['jumlah'] -= 1
            if cart[nama]['jumlah'] <= 0:
                del cart[nama]
        elif aksi == 'hapus':
            del cart[nama]
    return redirect('/pembeli/keranjang')

@app.route('/pembeli/keranjang')
def pembeli_keranjang():
    total = 0
    for nama in cart:
        total += cart[nama]['harga'] * cart[nama]['jumlah']
    return render_template('18-masukkankeranjang.html', cart=cart, total=total)

# ============================================================
# PEMBELI: PILIH PEMBAYARAN
# ============================================================

@app.route('/pembeli/pilih-pembayaran')
def pembeli_pilih_pembayaran():
    items = []
    total_int = 0
    for nama in cart:
        item = cart[nama]
        subtotal = item['harga'] * item['jumlah']
        total_int += subtotal
        items.append({'nama': nama, 'harga': item['harga'], 'qty': item['jumlah'], 'subtotal': subtotal})
    total = formatRp(total_int)
    return render_template('34-pilihpembayaran.html', items=items, total=total, formatRp=formatRp)

# ============================================================
# PEMBELI: BAYAR TUNAI
# ============================================================

def get_items_bayar():
    items = []
    for nama in cart:
        items.append({"nama": nama, "jumlah": cart[nama]['jumlah'], "harga": cart[nama]['harga'], "diskon": 0})
    return items if items else [{"nama": "-", "jumlah": 0, "harga": 0, "diskon": 0}]

def buat_pesanan_dari_cart(metode):
    global cart
    if not cart:
        return
    trx_id = "TRX" + str(random.randint(10000, 99999))
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    pelanggan = session.get('nama', 'Guest')
    barang_list = []
    for nama in cart:
        barang_list.append({"nama": nama, "jumlah": cart[nama]['jumlah'], "harga": cart[nama]['harga']})
    pesanan_baru = {
        "id": trx_id,
        "tanggal": tanggal,
        "pelanggan": pelanggan,
        "metode": metode,
        "status": "Disiapkan",
        "barang": barang_list,
        "total_awal": hitung_total_barang(barang_list),
        "total": hitung_total_barang(barang_list),
        "refund": 0
    }
    pesanan.append(pesanan_baru)
    cart = {}

@app.route('/pembeli/tunai')
def pembeli_tunai():
    session['metode'] = 'Tunai'
    items = get_items_bayar()
    buat_pesanan_dari_cart('Tunai')
    subtotal = 0
    total_diskon = 0
    for item in items:
        subtotal += item["jumlah"] * item["harga"]
        total_diskon += item["diskon"]
    total = subtotal - total_diskon
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%d-%m-%Y")
    jam = sekarang.strftime("%H:%M:%S")
    kode = random.randint(1000, 9999)
    return render_template('12-pembayarantunai.html', items=items, subtotal=subtotal, total_diskon=total_diskon, total=total, tanggal=tanggal, jam=jam, kode=kode)

# ============================================================
# PEMBELI: BAYAR QRIS
# ============================================================

@app.route('/pembeli/qris')
def pembeli_qris():
    session['metode'] = 'QRIS'
    buat_pesanan_dari_cart('QRIS')
    subtotal = 0
    total_diskon = 0
    for item in get_items_bayar():
        subtotal += item["jumlah"] * item["harga"]
        total_diskon += item["diskon"]
    total = subtotal - total_diskon
    return render_template('1-pembayaranqris.html', total=total, formatRp=formatRp)

# ============================================================
# PEMBELI: PESANAN

@app.route('/pembeli/selesai')
def pembeli_selesai():
    pelanggan = session.get('nama', '')
    pesanan_user = [p for p in pesanan if p["pelanggan"] == pelanggan]
    if pesanan_user:
        order = pesanan_user[-1]
        barang = order["barang"]
        metode = order["metode"]
        total = order["total"]
    else:
        barang = get_items_bayar()
        metode = session.get('metode', 'Tunai')
        total = sum(item["jumlah"] * item["harga"] for item in barang)
    return render_template('8_2-detailpesanan.html', barang=barang, status='Selesai', metode=metode, total=total)
# ============================================================

@app.route('/pembeli/pesanan')
def pembeli_pesanan():
    pelanggan = session.get('nama', '')
    pesanan_user = [p for p in pesanan if p["pelanggan"] == pelanggan]
    if pesanan_user:
        last_order = pesanan_user[-1]
        status = last_order["status"]
        total_barang = sum(b["jumlah"] for b in last_order["barang"])
    else:
        status = None
        total_barang = 0
    count_dikemas = len([p for p in pesanan_user if p["status"] == "Disiapkan"])
    count_siap = len([p for p in pesanan_user if p["status"] == "Siap diambil"])
    count_selesai = len([p for p in pesanan_user if p["status"] in ("Selesai", "Sudah diambil")])
    if pesanan_user:
        items = pesanan_user[-1]["barang"]
    else:
        items = get_items_bayar()
    return render_template('8-lihatpesanan.html', items=items, status=status, count_dikemas=count_dikemas, count_siap=count_siap, count_selesai=count_selesai)

@app.route('/pembeli/status')
def pembeli_status():
    pelanggan = session.get('nama', '')
    pesanan_user = [p for p in pesanan if p["pelanggan"] == pelanggan]
    if pesanan_user:
        order = pesanan_user[-1]
        barang = order["barang"]
        status = order["status"]
        metode = order["metode"]
        total = order["total"]
    else:
        barang = []
        status = "Disiapkan"
        metode = "-"
        total = 0
    return render_template('8_2-detailpesanan.html', barang=barang, status=status, metode=metode, total=total)

@app.route("/siap-diambil")
def siap_diambil():
    pelanggan = session.get('nama', '')
    pesanan_siap = [p for p in pesanan if p["status"] == "Siap diambil" and p["pelanggan"] == pelanggan]
    count_dikemas = 0
    count_siap = len(pesanan_siap)
    count_selesai = 0
    return render_template("8-lihatpesanan.html", pesanan_list=pesanan_siap, status="Siap diambil", total_barang=0, count_dikemas=count_dikemas, count_siap=count_siap, count_selesai=count_selesai)

# ============================================================
# PEMBELI: PENILAIAN
# ============================================================

produk_belum_dinilai = [
    {"id": 1, "nama": "Roti Aoka", "gambar": "roti.jpg"},
    {"id": 2, "nama": "Air Mineral Ades", "gambar": "ades.jpg"},
    {"id": 3, "nama": "Bulpoin", "gambar": "bulpoin.jpg"},
]

penilaian_saya = [
    {"id": 1, "nama": "Roti Aoka", "gambar": "roti.jpg", "rating": 4, "tanggal": "01-01-2026 11:24"},
    {"id": 2, "nama": "Air Mineral Ades", "gambar": "ades.jpg", "rating": 5, "tanggal": "20-12-2025 18:22"},
    {"id": 3, "nama": "Bulpoin", "gambar": "bulpoin.jpg", "rating": 3, "tanggal": "18-12-2025 11:35"},
]

@app.route("/pembeli/penilaian")
def pembeli_penilaian():
    return render_template("2-penilaianbarang.html", produk=produk_belum_dinilai, penilaian=penilaian_saya)

@app.route("/pembeli/rating")
def pembeli_rating():
    return render_template("4-inputpenilaian.html")

@app.route("/pembeli/like", methods=["POST"])
def pembeli_like():
    return redirect("/pembeli/penilaian")

# ============================================================
# PEMBELI: STRUK
# ============================================================

@app.route('/pembeli/struk')
def pembeli_struk():
    metode = session.get('metode', 'Tunai')
    pelanggan = session.get('nama', '')
    pesanan_user = [p for p in pesanan if p["pelanggan"] == pelanggan]
    if pesanan_user:
        sumber = pesanan_user[-1]["barang"]
    else:
        sumber = get_items_bayar()
    daftar_produk = []
    for item in sumber:
        daftar_produk.append({
            "nama": item["nama"],
            "qty": item["jumlah"],
            "harga": item["harga"],
            "diskon": item.get("diskon", 0),
        })

    subtotal = 0
    total_diskon = 0
    total_produk = 0
    for item in daftar_produk:
        subtotal += item["qty"] * item["harga"]
        total_diskon += item["diskon"]
        total_produk += item["qty"]
    total = subtotal - total_diskon

    if metode == "Tunai":
        tunai = 50000
        kembali = tunai - total
    else:
        tunai = total
        kembali = 0

    sekarang = datetime.now()
    tanggal = sekarang.strftime("%d-%m-%Y")
    jam = sekarang.strftime("%H:%M:%S")
    kode = random.randint(1000, 9999)

    return render_template('5-strukpembayaran.html', produk=daftar_produk, subtotal=subtotal, total_diskon=total_diskon, total=total, tunai=tunai, kembali=kembali, tanggal=tanggal, jam=jam, kode=kode, total_produk=total_produk, metode=metode)


@app.route('/admin/cetak_pdf')
def admin_cetak_pdf():
    if not session.get('user'):
        return redirect(url_for('admin_login'))

    data_transaksi = []
    for p in pesanan:
        total_barang = sum(b['harga'] * b['jumlah'] for b in p['barang'])
        data_transaksi.append({
            'tanggal': p['tanggal'],
            'id': p['id'],
            'jumlah': sum(b['jumlah'] for b in p['barang']),
            'total': total_barang
        })

    if not data_transaksi:
        data_transaksi = [
            {'tanggal': '2026-05-01', 'id': 'TRX001', 'jumlah': 3, 'total': 15000},
            {'tanggal': '2026-05-02', 'id': 'TRX002', 'jumlah': 5, 'total': 25000},
            {'tanggal': '2026-05-03', 'id': 'TRX003', 'jumlah': 2, 'total': 10000},
        ]

    total_pendapatan = sum(t['total'] for t in data_transaksi)
    modal_barang = int(total_pendapatan * 0.7)
    untung_rugi = total_pendapatan - modal_barang

    return render_template('12. cetaklaporan_pdf.html',
        total_pendapatan=total_pendapatan,
        modal_barang=modal_barang,
        untung_rugi=untung_rugi,
        data_transaksi=data_transaksi)

@app.route('/admin/cetak_excel')
def admin_cetak_excel():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['No', 'Nama', 'Stok', 'Harga', 'Kategori', 'Tanggal'])
    for b in data_barang:
        writer.writerow([b['no'], b['nama'], b['stok'], b['harga'], b['kategori'], b['tanggal']])
    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=laporan_barang.csv'}
    )

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
