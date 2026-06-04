from flask import render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from database import db
from modules.blueprints import admin_bp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'gambar')

@admin_bp.route('/admin/pengaturan', methods=['GET'])
def admin_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    logo_path = db.data_koperasi.get('logo', '')
    if logo_path:
        full_path = os.path.join(BASE_DIR, 'static', logo_path)
        if not os.path.exists(full_path):
            logo_path = 'image/logo_3.png'
    else:
        logo_path = 'image/logo_3.png'
        
    data = dict(db.data_koperasi)
    data['logo'] = logo_path
    return render_template('22.pengaturan_umum.html', **data)

@admin_bp.route('/admin/simpan_pengaturan', methods=['POST'])
def admin_simpan_pengaturan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    db.data_koperasi['nama'] = request.form.get('nama', db.data_koperasi['nama'])
    db.data_koperasi['deskripsi'] = request.form.get('deskripsi', db.data_koperasi['deskripsi'])
    db.data_koperasi['alamat'] = request.form.get('alamat', db.data_koperasi['alamat'])
    db.data_koperasi['telepon'] = request.form.get('telepon', db.data_koperasi['telepon'])
    db.data_koperasi['jam'] = request.form.get('jam', db.data_koperasi['jam'])
    db.data_koperasi['hari'] = request.form.get('hari', db.data_koperasi['hari'])

    file = request.files.get('gambar')
    if file and file.filename:
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        db.data_koperasi['logo'] = 'gambar/' + filename
        
        file.seek(0)
        file.save(os.path.join(BASE_DIR, 'static', 'image', 'logo_3.png'))

    db.save_koperasi()
    return redirect(url_for('admin.admin_pengaturan'))
