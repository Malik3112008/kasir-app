from flask import render_template, redirect, url_for, session
from database import db
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli/pesanan')
def pembeli_pesanan():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    
    count_dikemas = len([p for p in pesanan_user if p["status"] == "Disiapkan"])
    count_siap = len([p for p in pesanan_user if p["status"] in ("Siap diambil", "Menunggu Pembayaran")])
    count_selesai = len([p for p in pesanan_user if p["status"] in ("Selesai", "Sudah diambil")])
    
    return render_template('8-lihatpesanan.html', 
                           count_dikemas=count_dikemas, 
                           count_siap=count_siap, 
                           count_selesai=count_selesai)

@pembeli_bp.route('/pembeli/pesanan/dikemas')
def pembeli_pesanan_dikemas():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] == "Disiapkan"]
    return render_template('8_1-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/pesanan/siapdiambil')
def pembeli_pesanan_siapdiambil():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] in ("Siap diambil", "Menunggu Pembayaran")]
    return render_template('8_2-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/pesanan/selesai')
def pembeli_pesanan_selesai():
    pelanggan = session.get('nama') or session.get('user') or 'Guest'
    pesanan_user = [p for p in db.pesanan if p["pelanggan"] == pelanggan]
    pesanan_to_show = [p for p in pesanan_user if p["status"] in ("Selesai", "Sudah diambil")]
    return render_template('8_3-detailpesanan.html', pesanan_list=pesanan_to_show)

@pembeli_bp.route('/pembeli/status')
def pembeli_status():
    return redirect(url_for('pembeli.pembeli_pesanan_dikemas'))

@pembeli_bp.route("/siap-diambil")
def siap_diambil():
    return redirect(url_for('pembeli.pembeli_pesanan_siapdiambil'))
