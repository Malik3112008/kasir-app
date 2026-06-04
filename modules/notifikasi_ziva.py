from flask import render_template, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route("/admin/notifikasi")
def admin_notifikasi():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.NotifikasiAdmin.html", notifikasi=db.notifikasi)

@admin_bp.route("/admin/riwayat-notifikasi")
def admin_riwayat_notifikasi():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.RiwayatNotifikasi.html", riwayat=db.riwayat)

@admin_bp.route("/admin/hapus-semua", methods=["POST"])
def admin_hapus_semua():
    db.riwayat.extend(db.notifikasi)
    db.notifikasi.clear()
    db.save_notifikasi()
    return redirect(url_for('admin.admin_notifikasi'))

@admin_bp.route('/admin/hapus-notif/<int:index>', methods=['POST'])
def admin_hapus_notif(index):
    if index < len(db.notifikasi):
        db.riwayat.append(db.notifikasi[index])
        db.notifikasi.pop(index)
        db.save_notifikasi()
    return redirect(url_for('admin.admin_notifikasi'))

@admin_bp.route('/admin/hapus-riwayat-satuan/<int:index>', methods=['POST'])
def admin_hapus_riwayat_satuan(index):
    if index < len(db.riwayat):
        db.riwayat.pop(index)
        db.save_notifikasi()
    return redirect(url_for('admin.admin_riwayat'))

@admin_bp.route("/admin/hapus-riwayat", methods=["POST"])
def admin_hapus_riwayat():
    db.riwayat.clear()
    db.save_notifikasi()
    return redirect(url_for('admin.admin_riwayat'))
