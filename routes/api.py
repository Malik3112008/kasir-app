from flask import Blueprint, jsonify, request
from datetime import datetime
from database import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/barang', methods=['GET', 'POST'])
def api_barang():
    if request.method == 'GET':
        return jsonify(db.data_barang)
    elif request.method == 'POST':
        req_data = request.get_json() or request.form
        if not req_data:
            return jsonify({"error": "No data provided"}), 400
        no_baru = max([b['no'] for b in db.data_barang], default=0) + 1
        new_item = {
            'no': no_baru,
            'nama': req_data.get('nama', ''),
            'berat': req_data.get('berat', '-'),
            'satuan': req_data.get('satuan', ''),
            'stok': int(req_data.get('stok', 0)),
            'harga': int(req_data.get('harga', 0)),
            'kategori': req_data.get('kategori', ''),
            'tanggal_restok': req_data.get('tanggal_restok', ''),
            'expired': req_data.get('expired', '-'),
            'tanggal': req_data.get('tanggal', datetime.now().strftime("%Y-%m-%d")),
            'gambar': req_data.get('gambar', ''),
            'rating': int(req_data.get('rating', 0)),
            'emoji': req_data.get('emoji', '📦')
        }
        db.data_barang.append(new_item)
        db.save_data_barang()
        return jsonify(new_item), 201

@api_bp.route('/api/barang/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_barang_detail(id):
    item = next((b for b in db.data_barang if b['no'] == id), None)
    if not item:
        return jsonify({"error": "Product not found"}), 404
        
    if request.method == 'GET':
        return jsonify(item)
    elif request.method == 'PUT':
        req_data = request.get_json() or request.form
        if not req_data:
            return jsonify({"error": "No data provided"}), 400
        item['nama'] = req_data.get('nama', item['nama'])
        item['berat'] = req_data.get('berat', item['berat'])
        item['satuan'] = req_data.get('satuan', item.get('satuan', ''))
        item['stok'] = int(req_data.get('stok', item['stok']))
        item['harga'] = int(req_data.get('harga', item['harga']))
        item['kategori'] = req_data.get('kategori', item['kategori'])
        item['tanggal_restok'] = req_data.get('tanggal_restok', item.get('tanggal_restok', ''))
        item['expired'] = req_data.get('expired', item.get('expired', ''))
        item['gambar'] = req_data.get('gambar', item.get('gambar', ''))
        item['rating'] = int(req_data.get('rating', item.get('rating', 0)))
        item['emoji'] = req_data.get('emoji', item.get('emoji', '📦'))
        db.save_data_barang()
        return jsonify(item)
    elif request.method == 'DELETE':
        db.data_barang = [b for b in db.data_barang if b['no'] != id]
        db.save_data_barang()
        return jsonify({"message": "Product deleted successfully"})

@api_bp.route('/api/pesanan', methods=['GET'])
def api_pesanan():
    return jsonify(db.pesanan)
