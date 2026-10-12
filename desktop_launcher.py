import threading
import time
import sys
import webview
from app import create_app
from database import init_db
from database_enterprise import migrate_enterprise
from services.backup_service import auto_backup_worker

def start_server():
    init_db()
    migrate_enterprise()
    t = threading.Thread(target=auto_backup_worker, daemon=True)
    t.start()
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1.5)
    webview.create_window(
        'Controle de Estoque — PDV/ERP',
        'http://127.0.0.1:5000',
        width=1280, height=800,
        resizable=True,
        min_size=(1024, 600),
    )
