from flask import render_template, redirect, url_for, session
from database import db
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli')
def pembeli_home():
    if not session.get('user'):
        return redirect(url_for('pembeli.pembeli_login'))
    cart_count = sum(item['jumlah'] for item in db.cart.values())
    sorted_barang = sorted(db.data_barang, key=lambda b: (b['stok'] == 0, b['nama']))
    return render_template('14-kategorialattulis.html', barang=sorted_barang, cart_count=cart_count)
