from flask import render_template, request, redirect, url_for, session, Response
from database import db
from helpers import format_kbbi_date, formatRp
from modules.blueprints import admin_bp
import io

@admin_bp.route('/admin/cetak_transaksi_pdf')
def admin_cetak_transaksi_pdf():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    filtered_pesanan = []
    for p in db.pesanan:
        if (not tanggal_awal or p['tanggal'] >= tanggal_awal) and (not tanggal_akhir or p['tanggal'] <= tanggal_akhir):
            filtered_pesanan.append(p)
    return render_template('12.-cetaklaporan_transaksi_pdf.html', pesanan=filtered_pesanan)

@admin_bp.route('/admin/cetak_transaksi_excel')
def admin_cetak_transaksi_excel():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    filtered_pesanan = []
    for p in db.pesanan:
        if (not tanggal_awal or p['tanggal'] >= tanggal_awal) and (not tanggal_akhir or p['tanggal'] <= tanggal_akhir):
            filtered_pesanan.append(p)
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Transaksi"
    ws.append(['No', 'Tanggal', 'ID Transaksi', 'Nama Produk', 'Total', 'Metode', 'Status'])
    for i, p in enumerate(filtered_pesanan, 1):
        total_barang = sum(b['harga'] * b['jumlah'] for b in p['barang'])
        nama_produk = ', '.join(b['nama'] for b in p['barang'])
        tgl_fmt = format_kbbi_date(p['tanggal'])
        ws.append([i, tgl_fmt, p['id'], nama_produk, formatRp(total_barang), p['metode'], p['status']])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment;filename=laporan_transaksi.xlsx'}
    )
