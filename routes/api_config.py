import os, shutil, tempfile, logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from database import get_db_path
from services.config_service import (obter_configuracoes, salvar_configuracoes, obter_info_backup,
                                     criar_backup_manual, listar_backups)
from auth import login_required, gerente_required

log = logging.getLogger(__name__)
api_config_bp = Blueprint('api_config', __name__)

@api_config_bp.route('/api/configuracoes')
@login_required
def api_configuracoes():
    return jsonify(obter_configuracoes())

@api_config_bp.route('/api/configuracoes', methods=['POST'])
@gerente_required
def api_save_configuracoes():
    resultado = salvar_configuracoes(request.json)
    return jsonify(resultado)

@api_config_bp.route('/api/backup')
@gerente_required
def api_backup():
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    try:
        shutil.copy2(get_db_path(), tmp.name)
        tmp.close()
        return send_file(tmp.name, as_attachment=True,
                         download_name=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    finally:
        try: os.unlink(tmp.name)
        except Exception as e: log.warning("Não foi possível remover backup temporário: %s", e)

@api_config_bp.route('/api/restore', methods=['POST'])
@gerente_required
def api_restore():
    caminho = (request.json or {}).get('caminho', '')
    if not caminho:
        return jsonify({'ok': False, 'erro': 'Caminho inválido'}), 400

    # Se for apenas um nome de ficheiro, resolve-o contra as pastas de backup
    if os.path.basename(caminho) == caminho:
        candidates = [b for b in listar_backups() if b['nome'] == caminho]
        if not candidates:
            return jsonify({'ok': False, 'erro': 'Backup não encontrado'}), 404
        caminho_abs = os.path.join(candidates[0]['pasta'], candidates[0]['nome'])
    else:
        caminho_abs = os.path.abspath(caminho)

    if not caminho_abs.endswith('.db'):
        return jsonify({'ok': False, 'erro': 'Formato inválido. Use ficheiro .db'}), 400
    if not os.path.isfile(caminho_abs):
        return jsonify({'ok': False, 'erro': 'Caminho não é um ficheiro'}), 400

    try:
        db_path = get_db_path()
        with open(db_path, 'rb') as f:
            pass
        shutil.copy2(caminho_abs, db_path)
        log.info("Base de dados restaurada a partir de: %s", caminho_abs)
        return jsonify({'ok': True})
    except Exception as e:
        log.error("Erro ao restaurar backup: %s", e)
        return jsonify({'ok': False, 'erro': str(e)}), 500

@api_config_bp.route('/api/backup/manual', methods=['POST'])
@gerente_required
def api_backup_manual():
    return jsonify(criar_backup_manual())

@api_config_bp.route('/api/backups/list')
@gerente_required
def api_backups_list():
    return jsonify({'ok': True, 'backups': listar_backups()})

@api_config_bp.route('/api/backup/info')
@login_required
def api_backup_info():
    return jsonify(obter_info_backup())
