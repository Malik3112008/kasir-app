from flask import render_template, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/pengisian_barang')
def admin_pengisian_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    return render_template('10.pengisian_barang_.html')

@admin_bp.route('/admin/pengisian_barang/<int:id>')
def admin_pengisian_barang_restok(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    barang = None
    for b in db.data_barang:
        if b['no'] == id:
            barang = b
            break
    if not barang:
        return redirect(url_for('admin.admin_pengisian_barang'))
    return render_template('10.pengisian_barang_.html', barang=barang)
