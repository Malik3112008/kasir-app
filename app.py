from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response
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

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = os.environ.get('FLASK_SECRET', 'dev_secret_key')

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
    {"id": 1, "text": "Rak Makanan Ringan", "icon": "fa-solid fa-cookie-bite", "href": "/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 130},
    {"id": 2, "text": "Rak Snack", "icon": "fa-solid fa-candy-cane", "href": "/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 300},
    {"id": 3, "text": "Rak Cemilan", "icon": "fa-solid fa-pizza-slice", "href": "/makanan_ringan", "width": 290, "height": 120, "left": 40, "top": 470},
    {"id": 4, "text": "Meja Kasir", "icon": "fa-solid fa-cash-register", "href": "/meja_kasir", "width": 220, "height": 180, "left": 520, "top": 140},
    {"id": 5, "text": "Rak Alat Tulis", "icon": "fa-solid fa-book-open", "href": "/alat_tulis", "width": 180, "height": 230, "left": 870, "top": 130},
    {"id": 6, "text": "Rak Makanan", "icon": "fa-solid fa-burger", "href": "/makanan", "width": 180, "height": 230, "left": 870, "top": 430},
    {"id": 7, "text": "Rak Minuman", "icon": "fa-solid fa-bottle-water", "href": "/minuman", "width": 180, "height": 430, "left": 1160, "top": 120},
    {"id": 8, "text": "Pintu Masuk/Keluar", "icon": "fa-solid fa-door-open", "href": "/pintu", "width": 420, "height": 120, "left": 430, "top": 640},
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
    is_admin = request.args.get('admin') == '1'
    edit_mode = is_admin and request.args.get('edit') == '1'
    edit_card_id = request.args.get('edit_card', type=int) if is_admin else None
    edit_card = None
    if edit_card_id is not None:
        for card in cards:
            if card['id'] == edit_card_id:
                edit_card = card
                break
    return render_template('04.Denah.html', cards=cards, edit_mode=edit_mode, edit_card=edit_card, is_admin=is_admin, page='home')

@app.route('/admin/delete/<int:card_id>', methods=['POST'])
def admin_delete_card(card_id):
    is_admin = request.args.get('admin') == '1'
    if not is_admin:
        return "Unauthorized", 403
    cards = load_cards()
    cards = [c for c in cards if c['id'] != card_id]
    save_cards(cards)
    return redirect('/admin/denah?admin=1&edit=1')

@app.route('/admin/update/<int:card_id>', methods=['POST'])
def admin_update_card(card_id):
    is_admin = request.args.get('admin') == '1'
    if not is_admin:
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
    return redirect('/admin/denah?admin=1&edit=1')

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
    return render_template("06.RiwayatNotifikasi.html", riwayat=riwayat)

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

# ============================================================
# ADMIN: PENGISIAN BARANG
# ============================================================

@app.route('/admin/pengisian_barang')
def admin_pengisian_barang():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template('10.pengisian_barang_.html')

@app.route('/admin/simpan', methods=['POST'])
def admin_simpan():
    kategori = request.form['kategori']
    nama_barang = request.form['nama_barang']
    tanggal = request.form['tanggal']
    jumlah = request.form['jumlah']
    harga = request.form['harga']
    catatan = request.form['catatan']
    return render_template('10.rekap_barang.html', kategori=kategori, nama_barang=nama_barang, tanggal=tanggal, jumlah=jumlah, harga=harga, catatan=catatan)

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

# ============================================================
# ADMIN: CETAK LAPORAN
# ============================================================

data_barang = [
    {"no": 1, "nama": "Roti Aoka", "stok": 15, "harga": 3000, "kategori": "Makanan", "tanggal": "2026-05-03"},
    {"no": 2, "nama": "Donat", "stok": 10, "harga": 5000, "kategori": "Makanan", "tanggal": "2026-05-03"},
    {"no": 3, "nama": "Mie Instan", "stok": 50, "harga": 4000, "kategori": "Makanan", "tanggal": "2026-05-08"},
    {"no": 4, "nama": "Keripik Kentang", "stok": 22, "harga": 10000, "kategori": "Makanan", "tanggal": "2026-05-11"},
    {"no": 5, "nama": "Sosis", "stok": 20, "harga": 2000, "kategori": "Makanan", "tanggal": "2026-05-12"},
    {"no": 6, "nama": "Air Mineral", "stok": 35, "harga": 3000, "kategori": "Minuman", "tanggal": "2026-05-06"},
    {"no": 7, "nama": "Teh Botol", "stok": 18, "harga": 5000, "kategori": "Minuman", "tanggal": "2026-05-07"},
    {"no": 8, "nama": "Susu Kotak", "stok": 12, "harga": 7000, "kategori": "Minuman", "tanggal": "2026-05-10"},
    {"no": 9, "nama": "Kopi Sachet", "stok": 30, "harga": 4000, "kategori": "Minuman", "tanggal": "2026-05-13"},
    {"no": 10, "nama": "Es Krim", "stok": 15, "harga": 4500, "kategori": "Minuman", "tanggal": "2026-05-14"},
    {"no": 11, "nama": "Pensil", "stok": 30, "harga": 2000, "kategori": "Alat Tulis", "tanggal": "2026-05-03"},
    {"no": 12, "nama": "Bolpoin", "stok": 25, "harga": 4000, "kategori": "Alat Tulis", "tanggal": "2026-05-04"},
    {"no": 13, "nama": "Buku Tulis", "stok": 40, "harga": 6000, "kategori": "Alat Tulis", "tanggal": "2026-05-05"},
    {"no": 14, "nama": "Penghapus", "stok": 15, "harga": 2000, "kategori": "Alat Tulis", "tanggal": "2026-05-09"},
    {"no": 15, "nama": "Spidol", "stok": 14, "harga": 8000, "kategori": "Alat Tulis", "tanggal": "2026-05-12"},
    {"no": 16, "nama": "Tipe X", "stok": 25, "harga": 5000, "kategori": "Alat Tulis", "tanggal": "2026-05-15"},
]

@app.route('/admin/cetak_laporan', methods=['GET', 'POST'])
def admin_cetak_laporan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    return render_template('12. cetaklaporan.html', barang=data_barang, formatRp=formatRp)

@app.route('/admin/laporan_penjualan', methods=['GET', 'POST'])
def admin_laporan_penjualan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    now = datetime.now()
    bulan = int(request.form.get('bulan', now.month)) if request.method == 'POST' else now.month
    tanggal = request.form.get('tanggal', now.strftime('%Y-%m-%d')) if request.method == 'POST' else now.strftime('%Y-%m-%d')
    TT = 47
    TP = 114000
    MB = 65000
    UG = TP - MB
    NP = ["Roti Aoka", "Air Mineral", "Bolpoin", "Mie Instan", "Teh Botol"]
    JP = [15, 12, 10, 8, 7]
    WPT = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
    KT = ["Makanan", "Minuman", "Alat Tulis"]
    PPK = [50000, 38000, 26000]
    WPP = ["#FF6384", "#36A2EB", "#FFCE56"]
    PL = ["Jan", "Feb", "Mar", "Apr", "Mei"]
    PPB = [80000, 95000, 70000, 110000, 114000]
    TSP = ["Jan", "Feb", "Mar", "Apr", "Mei"]
    JTP = [30, 35, 25, 42, 47]
    return render_template('15.Laporan_Penjualan.html',
        bulan=bulan, tanggal=tanggal,
        tanggal_min=f"{now.year}-01-01", tanggal_max=f"{now.year}-12-31",
        TT=TT, TP=TP, MB=MB, UG=UG,
        NP=NP, JP=JP, WPT=WPT,
        KT=KT, PPK=PPK, WPP=WPP,
        PL=PL, PPB=PPB, TSP=TSP, JTP=JTP)

# ============================================================
# ADMIN: SIAPKAN PESANAN
# ============================================================

status_tunai = ["Disiapkan", "Siap diambil", "Menunggu", "Sudah diambil"]
status_qris  = ["Disiapkan", "Siap diambil", "Sudah diambil"]

pesanan = [
    {"id": "TRX001", "tanggal": "2025-11-15", "pelanggan": "Ahmad Rizki", "metode": "Tunai", "status": "Disiapkan",
     "barang": [{"nama": "Roti Tawar", "jumlah": 2, "harga": 8000}, {"nama": "Air Mineral", "jumlah": 1, "harga": 3000}]},
    {"id": "TRX002", "tanggal": "2025-11-15", "pelanggan": "Siti Nurhazila", "metode": "QRIS", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000}, {"nama": "Pensil", "jumlah": 4, "harga": 10000}]},
    {"id": "TRX003", "tanggal": "2025-11-15", "pelanggan": "Diki Nurhazila", "metode": "Tunai", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000}, {"nama": "Pensil", "jumlah": 4, "harga": 10000}]},
    {"id": "TRX004", "tanggal": "2025-11-15", "pelanggan": "Siti riki", "metode": "QRIS", "status": "Disiapkan",
     "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000}, {"nama": "Pensil", "jumlah": 4, "harga": 10000}]},
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
        for i in pesanan:
            if i['id'] == trx_id:
                ganti = get_status_list(i)
                ubah = ganti.index(i['status'])
                if ubah + 1 < len(ganti):
                    i['status'] = ganti[ubah + 1]
                break
        return redirect('/admin/siapkan-pesanan')
    return render_template('19.SiapkanPesanan.html', pesanan=pesanan, formatRp=formatRp)

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
        'logo': 'logo.svg'
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

@app.route('/pembeli/logout')
def pembeli_logout():
    session.clear()
    return redirect(url_for('pembeli_login'))

# ============================================================
# PEMBELI: HOME
# ============================================================

@app.route('/pembeli')
def pembeli_home():
    if not session.get('user'):
        return redirect(url_for('pembeli_login'))
    return render_template('14-kategorialattulis.html', barang=barang_pembeli)

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

cart = {
    "Roti Aoka": {"harga": 4000, "jumlah": 1},
    "Air Mineral": {"harga": 3000, "jumlah": 1},
    "Bolpoin": {"harga": 4000, "jumlah": 1}
}

@app.route('/pembeli/keranjang')
def pembeli_keranjang():
    total = 0
    for item in cart:
        harga = cart[item]["harga"]
        jumlah = cart[item]["jumlah"]
        total += harga * jumlah
    return render_template('18-masukkankeranjang.html', cart=cart, total=total)

# ============================================================
# PEMBELI: PILIH PEMBAYARAN
# ============================================================

@app.route('/pembeli/pilih-pembayaran')
def pembeli_pilih_pembayaran():
    items = [
        {'nama': 'Le Mineral', 'harga': 'Rp 3.000', 'qty': 1, 'gambar': 'gambar le mineral.jpeg'},
        {'nama': 'Pulpen', 'harga': 'Rp 4.000', 'qty': 1, 'gambar': 'gambar pulpen.jpeg'},
        {'nama': 'Roti Aoka', 'harga': 'Rp 8.000', 'qty': 1, 'gambar': 'gambar roti aoka.jpeg'}
    ]
    total = 'Rp 15.000'
    return render_template('34-pilihpembayaran.html', items=items, total=total)

# ============================================================
# PEMBELI: BAYAR TUNAI
# ============================================================

items_bayar = [
    {"nama": "Roti tawar", "jumlah": 2, "harga": 8000, "diskon": 2000},
    {"nama": "Air mineral", "jumlah": 1, "harga": 3000, "diskon": 0},
    {"nama": "Kopi sachet", "jumlah": 1, "harga": 4000, "diskon": 0},
    {"nama": "Susu cimory", "jumlah": 2, "harga": 6500, "diskon": 1000},
    {"nama": "Es krim", "jumlah": 2, "harga": 4500, "diskon": 0},
    {"nama": "Sosis", "jumlah": 2, "harga": 2000, "diskon": 1000},
]

@app.route('/pembeli/tunai')
def pembeli_tunai():
    session['metode'] = 'Tunai'
    subtotal = 0
    total_diskon = 0
    for item in items_bayar:
        subtotal += item["jumlah"] * item["harga"]
        total_diskon += item["diskon"]
    total = subtotal - total_diskon
    return render_template('12-pembayarantunai.html', items=items_bayar, subtotal=subtotal, total_diskon=total_diskon, total=total)

# ============================================================
# PEMBELI: BAYAR QRIS
# ============================================================

@app.route('/pembeli/qris')
def pembeli_qris():
    session['metode'] = 'QRIS'
    subtotal = 0
    total_diskon = 0
    for item in items_bayar:
        subtotal += item["jumlah"] * item["harga"]
        total_diskon += item["diskon"]
    total = subtotal - total_diskon
    return render_template('1-pembayaranqris.html', total=total, formatRp=formatRp)

# ============================================================
# PEMBELI: PESANAN

@app.route('/pembeli/selesai')
def pembeli_selesai():
    return render_template('8_2-detailpesanan.html', items=items_bayar, status='selesai')
# ============================================================

@app.route('/pembeli/pesanan')
def pembeli_pesanan():
    return render_template('8-lihatpesanan.html', items=items_bayar)

@app.route('/pembeli/status')
def pembeli_status():
    return render_template('8_2-detailpesanan.html')

@app.route("/siap-diambil")
def siap_diambil():
    pesanan_siap = [p for p in pesanan if p["status"] == "Siap diambil"]
    return render_template("8-lihatpesanan.html", items=pesanan_siap)

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
    daftar_produk = []
    for item in items_bayar:
        daftar_produk.append({
            "nama": item["nama"],
            "qty": item["jumlah"],
            "harga": item["harga"],
            "diskon": item["diskon"],
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
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Laporan Barang</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #4A90D9; color: white; }
        tr:nth-child(even) { background: #f2f2f2; }
    </style></head><body>
    <h1>Laporan Data Barang</h1>
    <p style="text-align:center;">Tanggal cetak: ''' + datetime.now().strftime("%d-%m-%Y %H:%M") + '''</p>
    <table><thead><tr><th>No</th><th>Nama</th><th>Stok</th><th>Harga</th><th>Kategori</th><th>Tanggal</th><th>Total</th></tr></thead><tbody>'''
    for b in data_barang:
        html += f'<tr><td>{b["no"]}</td><td>{b["nama"]}</td><td>{b["stok"]}</td>'
        html += f'<td>{formatRp(b["harga"])}</td><td>{b["kategori"]}</td><td>{b["tanggal"]}</td>'
        html += f'<td>{formatRp(b["stok"] * b["harga"])}</td></tr>'
    html += '</tbody></table><script>window.print();</script></body></html>'
    return html

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
