from flask import render_template, request, redirect, url_for, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from database import db
from modules.blueprints import pembeli_bp

@pembeli_bp.route("/pembeli/penilaian")
def pembeli_penilaian():
    return render_template("2-penilaianbarang.html", ulasan_tags="", produk=db.produk_belum_dinilai, ulasan="", nama="", rating=0, ulasan_foto="", tanggal="", penilaian=db.penilaian_saya)

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
