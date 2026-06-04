from flask import render_template, redirect, url_for, session
from database import db
from helpers import format_kbbi_date
from modules.blueprints import admin_bp

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
