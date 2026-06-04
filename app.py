from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify
from jinja2 import ChoiceLoader, FileSystemLoader
import os
import socket
from database import db
from helpers import format_kbbi_date, formatRp
from modules import api_bp, admin_bp, pembeli_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev_secret_key')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(BASE_DIR, 'kasir-admin', 'templates')),
    FileSystemLoader(os.path.join(BASE_DIR, 'kasir-pembeli', 'templates')),
])

@app.template_filter('tgl_indo')
def tgl_indo_filter(tanggal_str):
    return format_kbbi_date(tanggal_str)

class DynamicNotifCount:
    def __int__(self):
        return len(db.notifikasi) if hasattr(db, 'notifikasi') else 0
    def __len__(self):
        return int(self)
    def __bool__(self):
        return int(self) > 0
    def __gt__(self, other):
        return int(self) > other
    def __lt__(self, other):
        return int(self) < other
    def __eq__(self, other):
        return int(self) == other
    def __str__(self):
        return str(int(self))
    def __html__(self):
        return str(int(self))

@app.context_processor
def inject_globals():
    return {
        'now': format_kbbi_date(datetime_now()),
        'notif_count': DynamicNotifCount()
    }


def datetime_now():
    from datetime import datetime
    return datetime.now()

@app.before_request
def load_db_to_globals():
    db.load_all()

app.jinja_env.globals.update(formatRp=formatRp, notif_count=DynamicNotifCount())


app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pembeli_bp)

@app.errorhandler(404)
def page_not_found(e):
    return '''
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Halaman Tidak Ditemukan</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { text-align: center; background: white; padding: 60px 50px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { font-size: 100px; color: #e74c3c; margin-bottom: 10px; }
            h2 { font-size: 24px; color: #333; margin-bottom: 15px; }
            p { color: #666; margin-bottom: 30px; font-size: 16px; }
            a { display: inline-block; padding: 12px 30px; background: #3498db; color: white; border-radius: 8px; text-decoration: none; font-size: 16px; margin: 5px; }
            a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>404</h1>
            <h2>Halaman Tidak Ditemukan</h2>
            <p>URL yang Anda cari tidak tersedia.</p>
            <a href="/admin/login">Admin</a>
            <a href="/pembeli/login">Pembeli</a>
        </div>
    </body>
    </html>
    ''', 404

if __name__ == '__main__':
    port = 5000
    while port <= 5010:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                break
        port += 1
    print(f"Starting server on port {port}")
    app.run(debug=True, port=port)
