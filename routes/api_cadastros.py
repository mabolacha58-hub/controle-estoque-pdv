from flask import Blueprint, request, jsonify, session
from auth import login_required, gerente_required
from extensions import csrf
from services.cliente_service import listar_clientes, criar_cliente, atualizar_cliente, deletar_cliente
from services.fornecedor_service import listar_fornecedores, criar_fornecedor, atualizar_fornecedor, deletar_fornecedor
from services.utilizador_service import listar_utilizadores, autenticar, criar_utilizador, atualizar_utilizador, deletar_utilizador

api_cad_bp = Blueprint('api_cadastros', __name__)

# ─── Clientes ────────────────────────────────────────────────
@api_cad_bp.route('/api/clientes')
@login_required
def api_clientes():
    return jsonify(listar_clientes())

@api_cad_bp.route('/api/clientes',methods=['POST'])
@gerente_required
def api_add_cliente():
    resultado = criar_cliente(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/clientes/<int:id>',methods=['PUT'])
@gerente_required
def api_update_cliente(id):
    resultado = atualizar_cliente(id, request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/clientes/<int:id>',methods=['DELETE'])
@gerente_required
def api_del_cliente(id):
    return jsonify(deletar_cliente(id))

# ─── Fornecedores ────────────────────────────────────────────
@api_cad_bp.route('/api/fornecedores')
@login_required
def api_fornecedores():
    return jsonify(listar_fornecedores())

@api_cad_bp.route('/api/fornecedores',methods=['POST'])
@gerente_required
def api_add_fornecedor():
    resultado = criar_fornecedor(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/fornecedores/<int:id>',methods=['PUT'])
@gerente_required
def api_update_fornecedor(id):
    resultado = atualizar_fornecedor(id, request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/fornecedores/<int:id>',methods=['DELETE'])
@gerente_required
def api_del_fornecedor(id):
    return jsonify(deletar_fornecedor(id))

# ─── Utilizadores ────────────────────────────────────────────
@api_cad_bp.route('/api/utilizadores')
@login_required
def api_utilizadores():
    return jsonify(listar_utilizadores())

@csrf.exempt
@api_cad_bp.route('/api/utilizadores/login',methods=['POST'])
def api_login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'ok': False, 'erro': 'Dados inválidos'}), 400
    nome = (data.get('nome') or '').strip()
    pin = (data.get('pin') or '').strip()
    if not nome or not pin:
        return jsonify({'ok': False, 'erro': 'Nome e PIN são obrigatórios'}), 400
    ip = request.remote_addr
    user, erro = autenticar(nome, pin, ip)
    if user:
        user_data = {'user_id': user['id'], 'user_nome': user['nome'], 'user_role': user['role']}
        session.clear()
        session.update(user_data)
        session.permanent = True
        return jsonify({'ok': True, 'utilizador': user})
    return jsonify({'ok': False, 'erro': erro or 'Credenciais inválidas'}), 401

@api_cad_bp.route('/api/utilizadores',methods=['POST'])
@gerente_required
def api_add_utilizador():
    resultado = criar_utilizador(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/utilizadores/<int:id>',methods=['PUT'])
@gerente_required
def api_update_utilizador(id):
    resultado = atualizar_utilizador(id, request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_cad_bp.route('/api/utilizadores/<int:id>',methods=['DELETE'])
@gerente_required
def api_del_utilizador(id):
    return jsonify(deletar_utilizador(id))
