from flask import render_template, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route("/admin/riwayat")
def admin_riwayat():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template("06.RiwayatTransaksi.html", pesanan=db.pesanan)
