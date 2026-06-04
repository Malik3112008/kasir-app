from flask import render_template, request, redirect, url_for, session
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/kelola_akun_penjual')
def admin_kelola_akun_penjual():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    keyword = request.args.get('cari', '').lower()
    if keyword:
        filtered = [p for p in db.data_penjual if keyword in p['nama'].lower() or keyword in p['email'].lower()]
    else:
        filtered = db.data_penjual
        
    return render_template('08.pengelola_akun_penjual.html', penjual=filtered, keyword=keyword)

@admin_bp.route('/admin/tambah-akun', methods=['GET', 'POST'])
def admin_tambah_akun():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    if request.method == 'POST':
        max_id = max([p['id'] for p in db.data_penjual], default=0)
        akun_baru = {
            'id': max_id + 1,
            'nama': request.form['nama'],
            'email': request.form['email'],
            'status': request.form['status'],
            'foto': 'profile.png'
        }
        db.data_penjual.append(akun_baru)
        db.save_penjual()
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
    return render_template('08.tambah_akun.html')

@admin_bp.route('/admin/edit-akun/<int:id>', methods=['GET', 'POST'])
def admin_edit_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    akun = next((p for p in db.data_penjual if p['id'] == id), None)
    if not akun:
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
        
    if request.method == 'POST':
        akun['nama'] = request.form['nama']
        akun['email'] = request.form['email']
        akun['status'] = request.form['status']
        db.save_penjual()
        return redirect(url_for('admin.admin_kelola_akun_penjual'))
    return render_template('08.edit_akun.html', akun=akun)

@admin_bp.route('/admin/hapus-akun/<int:id>')
def admin_hapus_akun(id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    db.data_penjual = [p for p in db.data_penjual if p['id'] != id]
    db.save_penjual()
    return redirect(url_for('admin.admin_kelola_akun_penjual'))
