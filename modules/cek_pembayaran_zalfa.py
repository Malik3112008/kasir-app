from flask import render_template, request, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/cek-pembayaran')
def admin_cek_pembayaran():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    cari = request.args.get('cari', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    if cari:
        hasil = [p for p in db.pesanan if cari in p['id'].lower() or cari in p['pelanggan'].lower()]
    else:
        hasil = list(db.pesanan)
    total = len(hasil)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    transaksi = hasil[start:end]
    return render_template('21.cek_pembayaran.html', pesanan=transaksi,
                           page=page, total_pages=total_pages, total=total,
                           keyword=cari)

@admin_bp.route('/admin/cek-pembayaran/detail/<trx_id>')
def admin_cek_pembayaran_detail(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    order = None
    for p in db.pesanan:
        if p['id'] == trx_id:
            order = p
            break
    if not order:
        return "Transaksi tidak ditemukan", 404
    return render_template('21.cek_pembayaran_detail.html', order=order)
