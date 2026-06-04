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
