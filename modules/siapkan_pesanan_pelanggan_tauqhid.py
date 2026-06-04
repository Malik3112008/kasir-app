from flask import request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp

@admin_bp.route('/admin/cek-pembayaran/update-status/<trx_id>', methods=['POST'])
def admin_update_status(trx_id):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    
    new_status = request.form.get('status', '').strip()
    if not new_status:
        return "Status tidak boleh kosong", 400
        
    order = None
    for p in db.pesanan:
        if p['id'] == trx_id:
            order = p
            break
            
    if not order:
        return "Transaksi tidak ditemukan", 404
        
    old_status = order.get('status', '')
    if old_status != new_status:
        order['status'] = new_status
        db.save_pesanan()
        
        if new_status == "Siap diambil":
            db.tambah_notifikasi(
                "Pembayaran Dikonfirmasi",
                f"Pembayaran {order['metode']} oleh {order['pelanggan']} senilai {formatRp(order['total'])} telah divalidasi",
                "hijau"
            )
        elif new_status == "Selesai":
            db.tambah_notifikasi(
                "Transaksi Selesai",
                f"Transaksi #{trx_id} oleh {order['pelanggan']} senilai {formatRp(order['total'])} telah selesai",
                "hijau"
            )
            
        admin_name = session.get('user', 'Admin')
        db.tambah_aktivitas(
            "ubah", 
            f"Mengubah status transaksi #{trx_id}: {old_status} -> {new_status}", 
            "Berhasil", 
            admin_name
        )
        
    return redirect(url_for('admin.admin_cek_pembayaran_detail', trx_id=trx_id))
