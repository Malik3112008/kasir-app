from flask import Blueprint, render_template, request, redirect, url_for, session, make_response, Response, jsonify
from datetime import datetime
import random
import os
from werkzeug.utils import secure_filename
from database import db
from helpers import format_kbbi_date, formatRp

pembeli_bp = Blueprint('pembeli', __name__)

def get_items_bayar():
    items = []
    for nama in db.cart:
        items.append({"nama": nama, "jumlah": db.cart[nama]['jumlah'], "harga": db.cart[nama]['harga'], "diskon": 0})
    return items if items else [{"nama": "-", "jumlah": 0, "harga": 0, "diskon": 0}]

def buat_pesanan_dari_cart(metode):
    if not db.cart:
        return
    trx_id = "TRX" + str(random.randint(10000, 99999))
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    waktu = sekarang.strftime("%H:%M:%S")
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    barang_list = []
    for nama in db.cart:
        qty = db.cart[nama]['jumlah']
        barang_list.append({"nama": nama, "jumlah": qty, "harga": db.cart[nama]['harga']})
        for b in db.data_barang:
            if b['nama'] == nama:
                b['stok'] = max(0, b['stok'] - qty)
                if b['stok'] <= 5:
                    db.tambah_notifikasi(
                        "Stok Menipis",
                        f"Produk {b['nama']} tersisa {b['stok']} unit",
                        "orange"
                    )
                break
    db.save_data_barang()
    
    total_bayar = db.hitung_total_barang(barang_list)
    pesanan_baru = {
        "id": trx_id,
        "tanggal": tanggal,
        "waktu": waktu,
        "pelanggan": pelanggan,
        "metode": metode,
        "status": "Disiapkan",
        "barang": barang_list,
        "total_awal": total_bayar,
        "total": total_bayar,
        "refund": 0
    }
    db.pesanan.append(pesanan_baru)
    db.save_pesanan()
    
    # Trigger Pembelian Baru notification
    total_formatted = formatRp(total_bayar)
    db.tambah_notifikasi(
        "Pembelian Baru",
        f"Transaksi #{trx_id} oleh {pelanggan} senilai {total_formatted}",
        "biru"
    )
    
    db.cart.clear()


@pembeli_bp.route('/pembeli/login', methods=['GET', 'POST'])
def pembeli_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if db.USERS.get(username) == password:
            session['user'] = username
            session['role'] = 'pembeli'
            session['nama'] = username
            return redirect(url_for('pembeli.pembeli_home'))
        error = 'Nama akun atau kata sandi tidak cocok.'
    return render_template('login_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/register', methods=['GET', 'POST'])
def pembeli_register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Nama akun dan kata sandi wajib diisi.'
        elif username in db.USERS:
            error = 'Nama akun sudah digunakan.'
        else:
            db.USERS[username] = password
            db.save_users()
            return redirect(url_for('pembeli.pembeli_login'))
    return render_template('register_pembeli.html', error=error)


@pembeli_bp.route('/pembeli/logout')
def pembeli_logout():
    session.clear()
    return redirect(url_for('pembeli.pembeli_login'))

@pembeli_bp.route('/pembeli/reset-password', methods=['GET', 'POST'])
def pembeli_reset_password():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            db.otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli.pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/kirim-otp', methods=['GET', 'POST'])
def pembeli_kirim_otp():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            db.otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli.pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/verifikasi-email', methods=['GET', 'POST'])
def pembeli_verifikasi_email():
    error = None
    email = session.get('reset_email', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['reset_email'] = email
        return redirect(url_for('pembeli.pembeli_verifikasi_otp'))
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@pembeli_bp.route('/pembeli/verifikasi-otp', methods=['GET', 'POST'])
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
        stored_otp = db.otp_storage.get(email, '')
        if kode == stored_otp:
            session['otp_verified'] = True
            return redirect(url_for('pembeli.pembeli_ganti_password'))
        error = 'Kode OTP tidak cocok.'
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@pembeli_bp.route('/pembeli/ganti-password', methods=['GET', 'POST'])
def pembeli_ganti_password():
    error = None
    if not session.get('otp_verified'):
        return redirect(url_for('pembeli.pembeli_reset_password'))
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if not password or len(password) < 8:
            error = 'Kata sandi minimal 8 karakter.'
        elif password != confirm:
            error = 'Konfirmasi kata sandi tidak cocok.'
        else:
            email = session.get('reset_email', '')
            username = db.EMAIL_TO_USER.get(email)
            if not username:
                username = email.split('@')[0]
                if username in db.USERS:
                    db.EMAIL_TO_USER[email] = username
            
            if username and username in db.USERS:
                db.USERS[username] = password
                db.save_users()
                
            db.otp_storage.pop(email, None)
            session.pop('otp_verified', None)
            session.pop('reset_email', None)
            return render_template('notifikasi_berhasil_pembeli.html', message='Kata sandi berhasil diubah. Silakan login dengan kata sandi baru.')

    return render_template('reset_pembeli.html', error=error, show_password_form=True)

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

@pembeli_bp.route('/pembeli/pilih-pembayaran')
def pembeli_pilih_pembayaran():
    items = []
    total_int = 0
    for nama in db.cart:
        item = db.cart[nama]
        subtotal = item['harga'] * item['jumlah']
        total_int += subtotal
        items.append({'nama': nama, 'harga': item['harga'], 'qty': item['jumlah'], 'subtotal': subtotal, 'gambar': item.get('gambar', '')})
    total = total_int
    return render_template('34-pilihpembayaran.html', items=items, total=total, formatRp=formatRp)

@pembeli_bp.route('/pembeli/tunai')
def pembeli_tunai():
    session['metode'] = 'Tunai'
    items = get_items_bayar()
    buat_pesanan_dari_cart('Tunai')
    total = 0
    for item in items:
        total += item["jumlah"] * item["harga"]
    nama = session.get('nama') or session.get('user') or 'Guest'
    kode = random.randint(1000, 9999)
    session['tunai_items'] = items
    session['tunai_total'] = total
    session['tunai_kode'] = kode
    return render_template('11-rincian-tunai.html', items=items, total=total, nama=nama, kode=kode, status='belum')

@pembeli_bp.route('/pembeli/qris')
def pembeli_qris():
    session['metode'] = 'QRIS'
    if db.cart:
        subtotal = 0
        total_diskon = 0
        for item in get_items_bayar():
            subtotal += item["jumlah"] * item["harga"]
            total_diskon += item["diskon"]
        total = subtotal - total_diskon
        session['qris_total'] = total
        buat_pesanan_dari_cart('QRIS')
    else:
        total = session.get('qris_total')
        if total is None:
            pelanggan = session.get('nama') or session.get('user') or 'Guest'
            pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan and p["metode"] == "QRIS"]
            if pesanan_user:
                total = pesanan_user[-1]["total"]
            else:
                total = 0
    return render_template('1-pembayaranqris.html', total=total, formatRp=formatRp)

@pembeli_bp.route('/pembeli/selesai')
def pembeli_selesai():
    return redirect(url_for('pembeli.pembeli_pesanan_selesai'))

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

@pembeli_bp.route("/pembeli/penilaian")
def pembeli_penilaian():
    return render_template("2-penilaianbarang.html", produk=db.produk_belum_dinilai, penilaian=db.penilaian_saya)

@pembeli_bp.route("/pembeli/rating")
def pembeli_rating():
    produk_id = request.args.get('id', type=int)
    nama_produk = "Roti Aoka"
    gambar_produk = "gambar-dan-icon/gambar-roti-aoka.jpeg"
    varian_produk = "Vanilla"
    tanggal_pembelian = "28 Nov 2025"
    nama_pengguna = session.get('nama', '')

    if produk_id:
        for p in db.produk_belum_dinilai:
            if p['id'] == produk_id:
                nama_produk = p['nama']
                gambar_produk = p['gambar']
                for b in db.data_barang:
                    if b['nama'].lower() in nama_produk.lower() or nama_produk.lower() in b['nama'].lower():
                        varian_produk = f"{b.get('berat', '')} {b.get('satuan', '')}".strip() or "Vanilla"
                        break
                break

    return render_template("4-inputpenilaian.html",
        nama_produk=nama_produk,
        gambar_produk=gambar_produk,
        varian_produk=varian_produk,
        tanggal_pembelian=tanggal_pembelian,
        nama_pengguna=nama_pengguna)

@pembeli_bp.route("/pembeli/submit-rating", methods=["POST"])
def pembeli_submit_rating():
    nama_produk = request.form.get('produk_nama', '')
    rating = int(request.form.get('rating', 0))
    ulasan = request.form.get('ulasan', '').strip()
    ulasan_tags = request.form.get('ulasan_tags', '').strip()
    nama = request.form.get('nama', '').strip()

    if not nama:
        nama = session.get('nama', 'Anonim')

    if rating < 1:
        rating = 1

    foto_filename = None
    foto = request.files.get('foto')
    if foto and foto.filename:
        foto_filename = secure_filename(foto.filename)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(base_dir, 'static', 'uploads', 'rating')
        os.makedirs(upload_dir, exist_ok=True)
        foto.save(os.path.join(upload_dir, foto_filename))

    now = datetime.now()
    tanggal = now.strftime("%d-%m-%Y %H:%M")

    db.penilaian_saya.insert(0, {
        "id": len(db.penilaian_saya) + 1,
        "nama": nama_produk,
        "gambar": foto_filename or "default.jpg",
        "rating": rating,
        "tanggal": tanggal,
        "ulasan": ulasan,
        "ulasan_tags": ulasan_tags,
        "oleh": nama,
    })

    # Remove from belum_dinilai list
    db.produk_belum_dinilai = [p for p in db.produk_belum_dinilai if p['nama'] != nama_produk]
    db.save_penilaian()

    for b in db.data_barang:
        if b['nama'] == nama_produk:
            b['rating'] = rating
            db.save_data_barang()
            break

    return redirect(url_for('pembeli.pembeli_penilaian'))


@pembeli_bp.route("/pembeli/like", methods=["POST"])
def pembeli_like():
    return redirect(url_for('pembeli.pembeli_penilaian'))

@pembeli_bp.route('/pembeli/struk')
def pembeli_struk():
    trx_id = request.args.get('trx_id')
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    
    if trx_id:
        order = next((p for p in db.pesanan if p["id"] == trx_id and p["pelanggan"] == pelanggan), None)
    else:
        pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
        order = pesanan_user[-1] if pesanan_user else None
        
    if order:
        sumber = order["barang"]
        metode = order["metode"]
        total_final = order["total"]
        try:
            sekarang = datetime.strptime(order["tanggal"], "%Y-%m-%d")
        except:
            sekarang = datetime.now()
        trx_id = order["id"]
        
        if "waktu" in order:
            jam = order["waktu"]
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            if order["tanggal"] == today_str:
                jam = datetime.now().strftime("%H:%M:%S")
            else:
                jam = "00:00:00"
    else:
        sumber = get_items_bayar()
        metode = session.get('metode', 'Tunai')
        total_final = None
        sekarang = datetime.now()
        trx_id = "TRX-TEMP"
        jam = sekarang.strftime("%H:%M:%S")

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
    
    total = total_final if total_final is not None else (subtotal - total_diskon)

    if metode == "Tunai":
        tunai = 50000
        kembali = tunai - total
    else:
        tunai = total
        kembali = 0

    tanggal = format_kbbi_date(sekarang)
    kode = session.get('tunai_kode', random.randint(1000, 9999))

    return render_template('5-strukpembayaran.html', produk=daftar_produk, subtotal=subtotal, total_diskon=total_diskon, total=total, tunai=tunai, kembali=kembali, tanggal=tanggal, jam=jam, kode=kode, total_produk=total_produk, metode=metode, nama=pelanggan, trx_id=trx_id)
