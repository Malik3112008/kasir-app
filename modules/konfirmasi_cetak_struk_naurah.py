from flask import render_template, request, session
from datetime import datetime
import random
from database import db
from helpers import format_kbbi_date
from modules.blueprints import pembeli_bp
from modules.pembayaran_cash_putriamelia import get_items_bayar

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
