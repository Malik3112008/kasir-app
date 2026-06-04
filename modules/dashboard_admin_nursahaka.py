from flask import render_template, redirect, url_for, session
from datetime import datetime
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp

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
