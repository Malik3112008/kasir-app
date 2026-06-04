from flask import render_template, request, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/pengaturan-laporan')
def admin_pengaturan_laporan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    laporan_type = request.args.get('laporan', 'barang')
    return render_template("16.pengaturan_laporan.html",
                           barang=db.data_barang,
                           tanggal_awal=tanggal_awal,
                           tanggal_akhir=tanggal_akhir,
                           laporan_type=laporan_type)
