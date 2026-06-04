from flask import render_template, request, redirect, url_for, session, make_response, jsonify
from database import db
from modules.blueprints import admin_bp

@admin_bp.route('/admin/denah')
def admin_denah():
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    if session.get('role') != 'admin':
        return redirect(url_for('pembeli.pembeli_denah'))
    edit_mode = request.args.get('edit') == '1'
    edit_card_id = request.args.get('edit_card', type=int) if edit_mode else None
    edit_card = None
    if edit_card_id is not None:
        for card in db.CARDS_DATA:
            if card['id'] == edit_card_id:
                edit_card = card
                break
    return render_template('04.Denah.html', cards=db.CARDS_DATA, edit_mode=edit_mode, edit_card=edit_card, is_admin=True, page='home')

@admin_bp.route('/admin/delete/<int:card_id>', methods=['POST'])
def admin_delete_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    db.CARDS_DATA = [c for c in db.CARDS_DATA if c['id'] != card_id]
    return redirect(url_for('admin.admin_denah', edit=1))

@admin_bp.route('/admin/update/<int:card_id>', methods=['POST'])
def admin_update_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    for card in db.CARDS_DATA:
        if card['id'] == card_id:
            card['text'] = request.form.get('text', card['text'])
            card['icon'] = request.form.get('icon', card['icon'])
            card['icon_size'] = int(request.form.get('icon_size', card.get('icon_size', 30)))
            card['width'] = int(request.form.get('width', card['width']))
            card['height'] = int(request.form.get('height', card['height']))
            break
    return redirect(url_for('admin.admin_denah', edit=1))

@admin_bp.route('/admin/move/<int:card_id>', methods=['POST'])
def admin_move_card(card_id):
    if not session.get('user'):
        return "Unauthorized", 403
    data = request.get_json()
    for card in db.CARDS_DATA:
        if card['id'] == card_id:
            card['left'] = int(data.get('left', card['left']))
            card['top'] = int(data.get('top', card['top']))
            break
    return jsonify({'ok': True})

@admin_bp.route('/dynamic_cards.css')
def dynamic_cards_css():
    css_content = ""
    for card in db.CARDS_DATA:
        css_content += f".card-id-{card['id']} {{ width: {card['width']}px; height: {card['height']}px; left: {card['left']}px; top: {card['top']}px; }}\n"
    response = make_response(css_content)
    response.headers['Content-Type'] = 'text/css'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@admin_bp.route('/admin/denah/<folder>')
def admin_detail(folder):
    if not session.get('user'):
        return redirect(url_for('admin.admin_login'))
    if session.get('role') != 'admin':
        return redirect(url_for('pembeli.pembeli_detail', folder=folder))
    title = folder.replace('-', ' ').replace('_', ' ').title()
    return render_template('04.Denah.html', title=title, folder=folder, page='detail', is_admin=True)
