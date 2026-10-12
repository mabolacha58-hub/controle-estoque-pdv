import logging
import json
from datetime import datetime
from flask import request, session

log = logging.getLogger('auditoria')
log.setLevel(logging.INFO)
handler = logging.FileHandler('auditoria.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
log.addHandler(handler)
log.propagate = False

def log_mutation(acao, detalhe=''):
    usuario = session.get('user_id', 'anônimo')
    ip = request.remote_addr or 'desconhecido'
    log.info('%s | %s | %s %s | %s',
             usuario, ip, request.method, request.path, detalhe)

def logar_mutation(acao, dados_resumo=''):
    try:
        log_mutation(acao, dados_resumo)
    except Exception:
        pass
