import os, shutil, time, logging
from datetime import datetime
from database import get_config, set_config, get_db_path

log = logging.getLogger(__name__)

def default_backup_dir():
    docs = os.path.join(os.path.expanduser('~'), 'Documents', 'Controle de Estoque Backups')
    try:
        os.makedirs(docs, exist_ok=True)
        if os.path.isdir(docs):
            return docs
    except Exception as e:
        log.error("Não foi possível criar pasta de backup em Documentos: %s", e)
    fallback = os.path.join(os.path.dirname(get_db_path()), 'backups')
    try:
        os.makedirs(fallback, exist_ok=True)
    except Exception as e:
        log.error("Não foi possível criar pasta de backup alternativa: %s", e)
    return fallback

def auto_backup_worker():
    while True:
        try:
            cfg = get_config('backup_auto', '0')
            if cfg == '1':
                intervalo = int(get_config('backup_intervalo', '24'))
                pasta = get_config('backup_pastacaminho', '') or default_backup_dir()
                if not os.path.isdir(pasta):
                    pasta = default_backup_dir()
                ultimo = get_config('backup_ultimo', '')
                agora = datetime.now()
                deve_fazer = False
                if not ultimo:
                    deve_fazer = True
                else:
                    try:
                        diff = (agora - datetime.strptime(ultimo, '%Y%m%d_%H')).total_seconds()
                        if diff >= intervalo * 3600:
                            deve_fazer = True
                    except:
                        deve_fazer = True
                if deve_fazer and pasta and os.path.isdir(pasta):
                    nome = f'backup_{agora.strftime("%Y%m%d_%H%M%S")}.db'
                    dest = os.path.join(pasta, nome)
                    shutil.copy2(get_db_path(), dest)
                    bks = sorted([f for f in os.listdir(pasta)
                                  if f.startswith('backup_') and f.endswith('.db')])
                    for f in bks[:-30]:
                        try: os.remove(os.path.join(pasta, f))
                        except Exception: log.debug("Não foi possível remover backup antigo: %s", f)
                    set_config('backup_ultimo', agora.strftime('%Y%m%d_%H'))
        except Exception as e: log.error("Erro no backup automático: %s", e)
        time.sleep(3600)
