from flask import render_template, request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp
import random

@admin_bp.route('/admin/laporan_penjualan', methods=['GET', 'POST'])
def admin_laporan_penjualan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))

    tanggal_awal = request.values.get("tanggal_awal") or "2026-01-01"
    tanggal_akhir = request.values.get("tanggal_akhir") or "2026-12-31"
    if tanggal_akhir < tanggal_awal:
        tanggal_akhir = tanggal_awal

    def Rupiah(angka):
        return "Rp{:,.2f}".format(angka).replace(",", "X").replace(".", ",").replace("X", ".")

    real_transactions = [p for p in db.pesanan if tanggal_awal <= p['tanggal'] <= tanggal_akhir]

    if real_transactions:
        totalTransaksi = len(real_transactions)
        totalPendapatan_num = sum(p['total'] for p in real_transactions)
        modalBarang_num = int(totalPendapatan_num * 0.75)
        untungRugi_num = totalPendapatan_num - modalBarang_num

        total_produk = {}
        for p in real_transactions:
            for b in p.get('barang', []):
                nama = b['nama']
                total_produk[nama] = total_produk.get(nama, 0) + b['jumlah']
        namaProduk = list(total_produk.keys())
        jumlahProduk = list(total_produk.values())
        warna_pool = ["blue", "orange", "red", "yellow", "purple", "green", "pink", "cyan", "teal", "brown"]
        warnadiagramPT = [random.choice(warna_pool) for _ in namaProduk]

        prod_categories = {b['nama']: b.get('kategori', 'Lainnya') for b in db.data_barang}
        total_kategori = {}
        for p in real_transactions:
            for b in p.get('barang', []):
                cat = prod_categories.get(b['nama'], 'Lainnya')
                total_kategori[cat] = total_kategori.get(cat, 0) + b['harga'] * b['jumlah']
        kategori = list(total_kategori.keys())
        pendapatanPerkategori = list(total_kategori.values())
        warnadiagramPP = [random.choice(warna_pool) for _ in kategori]

        bulan_label = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        pendapatanPerbulan = []
        jumlahTransaksiPerbulan = []
        for m in range(1, 13):
            bulan_str = f"2026-{m:02d}"
            trx_bulan = [p for p in db.pesanan if p['tanggal'].startswith(bulan_str)]
            if trx_bulan:
                pendapatanPerbulan.append(sum(p['total'] for p in trx_bulan))
                jumlahTransaksiPerbulan.append(len(trx_bulan))
            else:
                pendapatanPerbulan.append(None)
                jumlahTransaksiPerbulan.append(None)
    else:
        totalTransaksi = 0
        totalPendapatan_num = 0
        modalBarang_num = 0
        untungRugi_num = 0
        namaProduk = ["Air Mineral", "Roti Aoka", "Pensil", "Pulpen", "Buku Tulis"]
        jumlahProduk = [10, 7, 9, 8, 5]
        warnadiagramPT = ["blue", "orange", "red", "yellow", "purple"]
        kategori = ["Minuman", "Makanan", "Alat Tulis"]
        pendapatanPerkategori = [30000, 25000, 45000]
        warnadiagramPP = ["blue", "green", "red"]
        bulan_label = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        pendapatanPerbulan = [None] * 12
        jumlahTransaksiPerbulan = [None] * 12

    return render_template('15.Laporan_Penjualan.html',
        TT=totalTransaksi,
        TP=Rupiah(totalPendapatan_num),
        MB=Rupiah(modalBarang_num),
        UG=Rupiah(untungRugi_num),
        NP=namaProduk,
        JP=jumlahProduk,
        WPT=warnadiagramPT,
        KT=kategori,
        PPK=pendapatanPerkategori,
        WPP=warnadiagramPP,
        PL=bulan_label,
        PPB=pendapatanPerbulan,
        TSP=bulan_label,
        JTP=jumlahTransaksiPerbulan,
        tanggal_awal=tanggal_awal,
        tanggal_akhir=tanggal_akhir
    )
