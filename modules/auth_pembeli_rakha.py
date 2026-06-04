from flask import render_template, request, redirect, url_for, session
import random
from database import db
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli/login', methods=['GET', 'POST'])
def pembeli_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if db.USERS.get(username) == password:
            session['user'] = username
            session['role'] = 'pembeli'
            session['nama'] = username
            return redirect(url_for('pembeli.pembeli_home'))
        error = 'Nama akun atau kata sandi tidak cocok.'
    return render_template('login_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/register', methods=['GET', 'POST'])
def pembeli_register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Nama akun dan kata sandi wajib diisi.'
        elif username in db.USERS:
            error = 'Nama akun sudah digunakan.'
        else:
            db.USERS[username] = password
            db.save_users()
            return redirect(url_for('pembeli.pembeli_login'))
    return render_template('register_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/logout')
def pembeli_logout():
    session.clear()
    return redirect(url_for('pembeli.pembeli_login'))

@pembeli_bp.route('/pembeli/reset-password', methods=['GET', 'POST'])
def pembeli_reset_password():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            db.otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli.pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/kirim-otp', methods=['GET', 'POST'])
def pembeli_kirim_otp():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            error = 'Email wajib diisi.'
        else:
            otp = str(random.randint(10000, 99999))
            db.otp_storage[email] = otp
            session['reset_email'] = email
            return redirect(url_for('pembeli.pembeli_verifikasi_email'))
    return render_template('reset_pembeli.html', error=error)

@pembeli_bp.route('/pembeli/verifikasi-email', methods=['GET', 'POST'])
def pembeli_verifikasi_email():
    error = None
    email = session.get('reset_email', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['reset_email'] = email
        return redirect(url_for('pembeli.pembeli_verifikasi_otp'))
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@pembeli_bp.route('/pembeli/verifikasi-otp', methods=['GET', 'POST'])
def pembeli_verifikasi_otp():
    error = None
    email = session.get('reset_email', '')
    if request.method == 'POST':
        kode = ''.join([
            request.form.get('kode1', ''),
            request.form.get('kode2', ''),
            request.form.get('kode3', ''),
            request.form.get('kode4', ''),
            request.form.get('kode5', ''),
        ])
        stored_otp = db.otp_storage.get(email, '')
        if kode == stored_otp:
            session['otp_verified'] = True
            return redirect(url_for('pembeli.pembeli_ganti_password'))
        error = 'Kode OTP tidak cocok.'
    return render_template('verifikasi_email_pembeli.html', error=error, email=email)

@pembeli_bp.route('/pembeli/ganti-password', methods=['GET', 'POST'])
def pembeli_ganti_password():
    error = None
    if not session.get('otp_verified'):
        return redirect(url_for('pembeli.pembeli_reset_password'))
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if not password or len(password) < 8:
            error = 'Kata sandi minimal 8 karakter.'
        elif password != confirm:
            error = 'Konfirmasi kata sandi tidak cocok.'
        else:
            email = session.get('reset_email', '')
            username = db.EMAIL_TO_USER.get(email)
            if not username:
                username = email.split('@')[0]
                if username in db.USERS:
                    db.EMAIL_TO_USER[email] = username
            
            if username and username in db.USERS:
                db.USERS[username] = password
                db.save_users()
                
            db.otp_storage.pop(email, None)
            session.pop('otp_verified', None)
            session.pop('reset_email', None)
            return render_template('notifikasi_berhasil_pembeli.html', message='Kata sandi berhasil diubah. Silakan login dengan kata sandi baru.')

    return render_template('reset_pembeli.html', error=error, show_password_form=True)
