from flask import render_template, request, redirect, url_for, session
import secrets
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if db.USERS.get(username) == password:
            session['user'] = username
            session['role'] = 'admin'
            db.tambah_aktivitas("login", "Log in system", "Sukses", username)
            return redirect(url_for('admin.admin_dashboard'))
        error = 'Nama akun atau kata sandi tidak cocok.'
    return render_template('05.1.login.html', error=error)

@admin_bp.route('/admin/logout')
def admin_logout():
    admin_name = session.get('user', 'Admin')
    db.tambah_aktivitas("logout", "Log out system", "Sukses", admin_name)
    session.clear()
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not username or not email or not password:
            error = 'Lengkapi semua bidang.'
        elif password != confirm:
            error = 'Kata sandi dan konfirmasi tidak cocok.'
        elif username in db.USERS:
            error = 'Nama pengguna sudah terdaftar.'
        else:
            db.USERS[username] = password
            db.EMAIL_TO_USER[email] = username
            db.save_users()
            return redirect(url_for('admin.admin_login'))
    return render_template('05.2.register.html', error=error)

@admin_bp.route('/admin/forgot', methods=['GET', 'POST'])
def admin_forgot():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['reset_email'] = email
        session['reset_user'] = db.EMAIL_TO_USER.get(email)
        otp = f"{secrets.randbelow(900000) + 100000}"
        session['otp'] = otp
        print(f"[DEBUG] OTP for {email}: {otp}")
        return redirect(url_for('admin.admin_verify'))
    return render_template('05.3.forgot.html', error=error)

@admin_bp.route('/admin/verify', methods=['GET', 'POST'])
def admin_verify():
    error = None
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if otp and otp == session.get('otp'):
            return redirect(url_for('admin.admin_reset'))
        error = 'Kode OTP tidak valid.'
    return render_template('05.4.verify_otp.html', error=error, email=session.get('reset_email'))

@admin_bp.route('/admin/reset', methods=['GET', 'POST'])
def admin_reset():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password:
            error = 'Masukkan kata sandi baru.'
        elif password != confirm:
            error = 'Konfirmasi kata sandi tidak cocok.'
        else:
            user = session.get('reset_user')
            if user:
                db.USERS[user] = password
                db.save_users()
            session.pop('otp', None)
            session.pop('reset_email', None)
            session.pop('reset_user', None)
            return redirect(url_for('admin.admin_login'))
    return render_template('05.5.reset.html', error=error)
