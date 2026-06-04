from flask import render_template, request, redirect, url_for, session, Response
from database import db
from helpers import format_kbbi_date, formatRp
from modules.blueprints import admin_bp
import io

@admin_bp.route('/admin/cetak_laporan_barang')
def admin_cetak_laporan_barang():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    total_nilai = sum(b['harga'] * b['stok'] for b in db.data_barang)
    return render_template('12.-cetaklaporan_barang.html',
        data_barang=db.data_barang,
        total_nilai=total_nilai)

@admin_bp.route('/admin/cetak_barang_pdf')
def admin_cetak_barang_pdf():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    filtered_barang = []
    for b in db.data_barang:
        if (not tanggal_awal or b['tanggal'] >= tanggal_awal) and (not tanggal_akhir or b['tanggal'] <= tanggal_akhir):
            filtered_barang.append(b)
    total_nilai = sum(b['harga'] * b['stok'] for b in filtered_barang)
    return render_template('12.-cetaklaporan_barang_pdf.html',
        data_barang=filtered_barang,
        total_nilai=total_nilai)

@admin_bp.route('/admin/cetak_barang_excel')
def admin_cetak_barang_excel():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    filtered_barang = []
    for b in db.data_barang:
        if (not tanggal_awal or b['tanggal'] >= tanggal_awal) and (not tanggal_akhir or b['tanggal'] <= tanggal_akhir):
            filtered_barang.append(b)
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Data Barang"
    ws.append(['No', 'Nama', 'Stok', 'Harga', 'Kategori', 'Tanggal', 'Total'])
    for b in filtered_barang:
        ws.append([b['no'], b['nama'], b['stok'], formatRp(b['harga']), b['kategori'], format_kbbi_date(b['tanggal']), formatRp(b['harga'] * b['stok'])])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment;filename=laporan_data_barang.xlsx'}
    )
