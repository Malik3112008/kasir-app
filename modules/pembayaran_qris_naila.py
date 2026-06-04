from flask import render_template, request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import pembeli_bp
from modules.pembayaran_cash_putriamelia import get_items_bayar, buat_pesanan_dari_cart

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
