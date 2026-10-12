from flask import Blueprint, request, jsonify
from auth import login_required
from services.venda_service import processar_venda

api_vendas_bp = Blueprint('api_vendas', __name__)

@api_vendas_bp.route('/api/vender',methods=['POST'])
@login_required
def api_vender():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'ok': False, 'erro': 'Dados inválidos'}), 400
    return jsonify(processar_venda(data))
