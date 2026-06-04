from flask import render_template
from database import db
from helpers import formatRp
from modules.blueprints import pembeli_bp

@pembeli_bp.route('/pembeli/pilih-pembayaran')
def pembeli_pilih_pembayaran():
    items = []
    total_int = 0
    for nama in db.cart:
        item = db.cart[nama]
        subtotal = item['harga'] * item['jumlah']
        total_int += subtotal
        items.append({'nama': nama, 'harga': item['harga'], 'qty': item['jumlah'], 'subtotal': subtotal, 'gambar': item.get('gambar', '')})
    total = total_int
    return render_template('34-pilihpembayaran.html', items=items, total=total, formatRp=formatRp)
