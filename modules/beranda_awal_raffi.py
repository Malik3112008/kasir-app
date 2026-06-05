from flask import render_template, redirect, url_for
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/')
def beranda_root():
    return redirect(url_for('admin.admin_beranda_awal'))

@admin_bp.route('/admin')
def admin_beranda_awal():
    return render_template('03.Beranda_awal.html')

@admin_bp.route('/informasi')
def informasi():
    return render_template('informasi.html', koperasi=db.data_koperasi)
