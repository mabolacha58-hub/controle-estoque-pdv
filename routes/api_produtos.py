import os, uuid
from flask import Blueprint, request, jsonify, send_from_directory
from services.produto_service import listar_produtos, criar_produto, atualizar_produto, deletar_produto
from auth import login_required, gerente_required

api_produtos_bp = Blueprint('api_produtos', __name__)

UPLOADS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')

@api_produtos_bp.route('/api/produtos')
@login_required
def api_produtos():
    pagina = request.args.get('pagina', type=int)
    limite = request.args.get('limite', type=int)
    return jsonify(listar_produtos(pagina, limite))

@api_produtos_bp.route('/api/produtos',methods=['POST'])
@gerente_required
def api_add_produto():
    resultado = criar_produto(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_produtos_bp.route('/api/produtos/<int:id>',methods=['PUT'])
@gerente_required
def api_update_produto(id):
    resultado = atualizar_produto(id, request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_produtos_bp.route('/api/produtos/<int:id>',methods=['DELETE'])
@gerente_required
def api_del_produto(id):
    resultado = deletar_produto(id)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_produtos_bp.route('/api/produtos/foto', methods=['POST'])
@gerente_required
def api_upload_foto():
    if 'foto' not in request.files:
        return jsonify({'ok': False, 'erro': 'Nenhum ficheiro enviado'}), 400
    f = request.files['foto']
    if f.filename == '':
        return jsonify({'ok': False, 'erro': 'Ficheiro vazio'}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
        return jsonify({'ok': False, 'erro': 'Formato inválido. Use PNG, JPG, GIF ou WEBP'}), 400
    nome = f'{uuid.uuid4().hex}{ext}'
    f.save(os.path.join(UPLOADS, nome))
    return jsonify({'ok': True, 'foto': nome})

@api_produtos_bp.route('/api/produtos/foto/<nome>')
@login_required
def api_serve_foto(nome):
    return send_from_directory(UPLOADS, nome)
