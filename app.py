import logging, os
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from extensions import csrf
from database import init_db, moeda
from database_enterprise import migrate_enterprise
from auth import inject_user, require_api_auth
from services.backup_service import auto_backup_worker
from routes.pages import pages_bp
from routes.api_produtos import api_produtos_bp
from routes.api_movimentacoes import api_mov_bp
from routes.api_vendas import api_vendas_bp
from routes.api_cadastros import api_cad_bp
from routes.api_caixa import api_caixa_bp
from routes.api_config import api_config_bp
from routes.api_relatorios import api_rel_bp
from routes.api_enterprise import api_enterprise_bp
from routes.pages_enterprise import pages_enterprise_bp
from services.audit_logger import logar_mutation

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_PERMANENT'] = False

    csrf.init_app(app)

    app.jinja_env.globals['moeda'] = moeda

    app.context_processor(inject_user)
    app.before_request(require_api_auth)

    # Prevent CSRF protection from blocking JSON API requests made by frontend fetch calls
    csrf.exempt(api_produtos_bp)
    csrf.exempt(api_mov_bp)
    csrf.exempt(api_vendas_bp)
    csrf.exempt(api_cad_bp)
    csrf.exempt(api_caixa_bp)
    csrf.exempt(api_config_bp)
    csrf.exempt(api_rel_bp)
    csrf.exempt(api_enterprise_bp)

    @app.after_request
    def audit_mutations(response):
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH') and response.status_code < 400:
            user = session.get('user_id', 'anônimo')
            ip = request.remote_addr or 'desconhecido'
            detalhe = ''
            if request.is_json and request.method != 'DELETE':
                try:
                    data = request.get_json(silent=True) or {}
                    if isinstance(data, dict):
                        detalhe = ', '.join(f'{k}={v}' for k, v in list(data.items())[:3])
                except Exception:
                    pass
            logar_mutation(f'{user} | {ip} | {request.method} {request.path}', detalhe)
        return response

    @app.errorhandler(404)
    def not_found(e):
        return render_template('erro.html', pagina='Erro', codigo=404, mensagem='Página não encontrada'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('erro.html', pagina='Erro', codigo=500, mensagem='Erro interno do servidor'), 500

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_produtos_bp)
    app.register_blueprint(api_mov_bp)
    app.register_blueprint(api_vendas_bp)
    app.register_blueprint(api_cad_bp)
    app.register_blueprint(api_caixa_bp)
    app.register_blueprint(api_config_bp)
    app.register_blueprint(api_rel_bp)
    app.register_blueprint(api_enterprise_bp)
    app.register_blueprint(pages_enterprise_bp)

    return app

if __name__ == '__main__':
    init_db()
    migrate_enterprise()
    import threading
    threading.Thread(target=auto_backup_worker, daemon=True).start()
    app = create_app()
    log.info("Servidor iniciado! Acesse http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
