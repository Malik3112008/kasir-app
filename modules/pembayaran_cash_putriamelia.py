from flask import render_template, request, redirect, url_for, session
from datetime import datetime
import random
from database import db
from helpers import format_kbbi_date, formatRp
from modules.blueprints import pembeli_bp

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
        f"Transaksi {trx_id} oleh {pelanggan} senilai {total_formatted}",
        "biru"
    )

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
