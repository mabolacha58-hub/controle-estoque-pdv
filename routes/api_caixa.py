from flask import Blueprint, request, jsonify, session
from auth import login_required
from services.caixa_service import listar_caixas, obter_status_caixa, abrir_caixa, fechar_caixa

api_caixa_bp = Blueprint('api_caixa', __name__)

@api_caixa_bp.route('/api/caixa')
@login_required
def api_caixa():
    return jsonify(listar_caixas())

@api_caixa_bp.route('/api/caixa/status')
@login_required
def api_caixa_status():
    return jsonify(obter_status_caixa())

@api_caixa_bp.route('/api/caixa/abrir',methods=['POST'])
@login_required
def api_abrir_caixa():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'ok': False, 'erro': 'Dados inválidos'}), 400
    resultado = abrir_caixa(data.get('utilizador_id', session.get('user_id')), data.get('saldo_inicial', 0))
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo

@api_caixa_bp.route('/api/caixa/fechar',methods=['POST'])
@login_required
def api_fechar_caixa():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'ok': False, 'erro': 'Dados inválidos'}), 400
    resultado = fechar_caixa(data.get('saldo_final', 0), data.get('diferenca', 0))
    codigo = 400 if not resultado.get('ok') else 200
    return jsonify(resultado), codigo
