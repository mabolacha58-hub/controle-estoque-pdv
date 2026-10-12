from flask import Blueprint, request, jsonify
from services.movimento_service import listar_movimentacoes, criar_movimentacao, deletar_movimentacao
from services.categoria_service import listar_categorias, criar_categoria, deletar_categoria
from auth import login_required, gerente_required

api_mov_bp = Blueprint('api_movimentacoes', __name__)

@api_mov_bp.route('/api/movimentacoes')
@login_required
def api_movimentacoes():
    pagina = request.args.get('pagina', type=int)
    limite = request.args.get('limite', type=int)
    busca = request.args.get('busca', '').strip()
    return jsonify(listar_movimentacoes(pagina, limite, busca or None))

@api_mov_bp.route('/api/movimentacoes',methods=['POST'])
@gerente_required
def api_add_movimentacao():
    resultado = criar_movimentacao(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_mov_bp.route('/api/movimentacoes/<int:id>',methods=['DELETE'])
@gerente_required
def api_delete_movimentacao(id):
    resultado = deletar_movimentacao(id)
    codigo = 404 if not resultado.get('ok') and resultado.get('erro') == 'Não encontrada' else 200
    return jsonify(resultado), codigo

@api_mov_bp.route('/api/categorias')
@login_required
def api_categorias():
    return jsonify(listar_categorias())

@api_mov_bp.route('/api/categorias',methods=['POST'])
@gerente_required
def api_add_categoria():
    resultado = criar_categoria(request.json)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_mov_bp.route('/api/categorias/<int:id>',methods=['DELETE'])
@gerente_required
def api_del_categoria(id):
    resultado = deletar_categoria(id)
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo
