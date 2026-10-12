import os, shutil, logging
from datetime import datetime
from database import get_db_path, get_config, set_config

log = logging.getLogger(__name__)

DEFAULT_BACKUP_DIR = r'C:\Users\Mateus Mabolacha\ControleEstoque\backups'

def obter_configuracoes():
    from services.base import db_connection
    with db_connection() as conn:
        rows = conn.execute("SELECT chave,valor FROM configuracoes").fetchall()
        return {r[0]: r[1] for r in rows}

def salvar_configuracoes(dados):
    for k, v in dados.items():
        set_config(k, v)
    return {'ok': True}

def obter_info_backup():
    if not os.path.exists(get_db_path()):
        return {'tamanho': 0, 'data': '-'}
    size = os.path.getsize(get_db_path())
    mtime = datetime.fromtimestamp(os.path.getmtime(get_db_path())).strftime('%d/%m/%Y %H:%M')
    pasta = get_config('backup_pastacaminho', '')
    ultimo = get_config('backup_ultimo', '')
    return {'tamanho': size, 'data': mtime, 'pasta': pasta, 'ultimo_backup': ultimo}

def descartar_antigos(pasta, prefixo='backup_', manter=30):
    try:
        bks = sorted([f for f in os.listdir(pasta)
                      if f.startswith(prefixo) and f.endswith('.db')])
        for f in bks[:-manter]:
            try: os.remove(os.path.join(pasta, f))
            except Exception as e: log.debug("Não foi possível remover backup antigo: %s", e)
    except Exception as e:
        log.debug("Erro ao limpar backups antigos em %s: %s", pasta, e)

def _backup_folder():
    pasta = get_config('backup_pastacaminho', '')
    if pasta and os.path.isdir(pasta):
        return pasta
    return DEFAULT_BACKUP_DIR

def criar_backup_manual():
    try:
        pasta = _backup_folder()
        os.makedirs(pasta, exist_ok=True)
        nome = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        dest = os.path.join(pasta, nome)
        shutil.copy2(get_db_path(), dest)
        descartar_antigos(pasta, 'backup_', 30)
        set_config('backup_ultimo', datetime.now().strftime('%Y%m%d_%H'))
        return {'ok': True, 'caminho': dest, 'nome': nome, 'pasta': pasta}
    except Exception as e:
        log.error('Erro ao criar backup manual: %s', e)
        return {'ok': False, 'erro': str(e)}

def listar_backups():
    resultados = []
    pastas = []
    pasta = get_config('backup_pastacaminho', '')
    if pasta and os.path.isdir(pasta):
        pastas.append(pasta)
    if os.path.isdir(DEFAULT_BACKUP_DIR):
        pastas.append(DEFAULT_BACKUP_DIR)
    for p in pastas:
        try:
            for f in sorted(os.listdir(p)):
                if f.endswith('.db'):
                    fp = os.path.join(p, f)
                    st = os.stat(fp)
                    resultados.append({
                        'nome': f,
                        'pasta': p,
                        'tamanho': st.st_size,
                        'data': datetime.fromtimestamp(st.st_mtime).strftime('%d/%m/%Y %H:%M'),
                    })
        except Exception as e:
            log.debug('Erro ao listar backups em %s: %s', p, e)
    resultados.sort(key=lambda x: x['data'], reverse=True)
    return resultados
