from flask import render_template, request, redirect, url_for, session, jsonify
from database import db
from modules.blueprints import admin_bp

@admin_bp.route("/admin/riwayat-aktivitas")
def admin_riwayat_aktivitas():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    daftar_admin = list(set(d['admin'] for d in db.data_aktivitas))
    return render_template("24.RiwayatAktivitas.html", daftar_admin=daftar_admin)

@admin_bp.route("/admin/api/aktivitas")
def admin_api_aktivitas():
    search = request.args.get('search', '').lower()
    admin_filter = request.args.get('admin', 'Pilihan Admin')
    tanggal = request.args.get('tanggal', '')
    hasil = db.data_aktivitas
    if search:
        hasil = [d for d in hasil if search in d['catatan'].lower()]
    if admin_filter != 'Pilihan Admin':
        hasil = [d for d in hasil if admin_filter in d['admin']]
    if tanggal:
        hasil = [d for d in hasil if d['waktu'].startswith(tanggal)]
    return jsonify(hasil)
