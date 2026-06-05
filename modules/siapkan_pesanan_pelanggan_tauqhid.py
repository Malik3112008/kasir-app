from flask import render_template, request, redirect, url_for, session
from database import db
from helpers import formatRp
from modules.blueprints import admin_bp
from datetime import datetime

status_qris = ['Menunggu konfirmasi', 'Pesanan diproses', 'Siap diambil', 'Sudah diambil']
status_tunai = ['Menunggu konfirmasi', 'Pesanan diproses', 'Siap diambil', 'Sudah diambil']

def get_status_list(pesan):
    return status_qris if pesan['metode'].lower() == 'qris' else status_tunai

@admin_bp.route('/admin/siapkan-pesanan', methods=['GET', 'POST'])
def admin_siapkan_pesanan():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    if request.method == 'POST':
        trx_id = request.form['trx_id']
        new_status = request.form.get('status')
        for i in db.pesanan:
            if i['id'] == trx_id:
                if new_status:
                    ganti = get_status_list(i)
                    if new_status in ganti:
                        i['status'] = new_status
                else:
                    ganti = get_status_list(i)
                    ubah = ganti.index(i['status'])
                    if ubah + 1 < len(ganti):
                        i['status'] = ganti[ubah + 1]
                break
        db.save_pesanan()
        return redirect('/admin/siapkan-pesanan')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(db.pesanan)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    pesanan_page = []
    for p in db.pesanan[start:end]:
        p_copy = dict(p)
        try:
            tgl = datetime.strptime(p['tanggal'], '%Y-%m-%d')
            p_copy['tanggal_fmt'] = f"{tgl.day:02d}/{tgl.month:02d}/{tgl.year}"
        except Exception:
            p_copy['tanggal_fmt'] = p['tanggal']
        pesanan_page.append(p_copy)
    return render_template('19.SiapkanPesanan.html', pesanan=pesanan_page, formatRp=formatRp,
                           status=get_status_list, page=page, total_pages=total_pages, total=total)

@admin_bp.route('/admin/hapus-barang', methods=['POST'])
def admin_hapus_barang():
    trx_id = request.form['trx_id']
    nama_barang = request.form['nama_barang']
    for p in db.pesanan:
        if p['id'] == trx_id:
            dihapus = None
            for b in p['barang']:
                if b['nama'] == nama_barang:
                    dihapus = b
                    break
            if dihapus:
                dihapus['jumlah'] -= 1
                for item in db.data_barang:
                    if item['nama'] == nama_barang:
                        item['stok'] += 1
                        break
                db.save_data_barang()
                if dihapus['jumlah'] <= 0:
                    p['barang'].remove(dihapus)
                p['total'] = sum(b['harga'] * b['jumlah'] for b in p['barang'])
                p['refund'] = p.get('total_awal', p['total']) - p['total']
                db.save_pesanan()
            break
    return redirect('/admin/siapkan-pesanan')

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
