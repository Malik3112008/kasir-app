from flask import render_template
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/informasi')
def informasi():
    return render_template('informasi.html', koperasi=db.data_koperasi)
