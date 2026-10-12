import os, sys, threading, time, webbrowser

def get_base_path():
    if getattr(sys, '_MEIPASS', None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

os.chdir(get_base_path())
os.environ.setdefault('FLASK_APP', 'app.py')

from app import create_app
from database import init_db
from database_enterprise import migrate_enterprise
from services.backup_service import auto_backup_worker

def start_server():
    init_db()
    migrate_enterprise()
    threading.Thread(target=auto_backup_worker, daemon=True).start()
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')
    print("Sistema iniciado! Acesse http://localhost:5000")
    print("Prima Ctrl+C para sair.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nA encerrar...")
