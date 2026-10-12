from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import session, request, jsonify, redirect, url_for, render_template
from database import get_db

def login_required(f):
    @wraps(f)
    def wrapper(*a,**kw):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'ok':False,'erro':'Autenticação necessária'}),401
            return redirect(url_for('pages.login_page', next=request.path))
        return f(*a,**kw)
    return wrapper

def gerente_required(f):
    @wraps(f)
    def wrapper(*a,**kw):
        if session.get('user_role') != 'gerente':
            if request.is_json:
                return jsonify({'ok':False,'erro':'Acesso restrito a gerentes'}),403
            return render_template('erro.html', pagina='Erro', codigo=403,
                                   mensagem='Acesso restrito a gerentes'), 403
        return f(*a,**kw)
    return wrapper

def permissao_required(permissao):
    def decorator(f):
        @wraps(f)
        def wrapper(*a,**kw):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'ok':False,'erro':'Autenticação necessária'}),401
                return redirect(url_for('pages.login_page', next=request.path))
            role = session.get('user_role')
            if role == 'gerente':
                return f(*a,**kw)
            try:
                from services.permissoes_service import tem_permissao
                if not tem_permissao(session['user_id'], permissao):
                    if request.is_json:
                        return jsonify({'ok':False,'erro':'Sem permissão'}),403
                    return render_template('erro.html', pagina='Erro', codigo=403,
                                           mensagem='Sem permissão para aceder a esta página'), 403
            except Exception:
                if request.is_json:
                    return jsonify({'ok':False,'erro':'Sem permissão'}),403
                return render_template('erro.html', pagina='Erro', codigo=403,
                                       mensagem='Sem permissão para aceder a esta página'), 403
            return f(*a,**kw)
        return wrapper
    return decorator

def is_safe_url(target):
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ('http','https') and ref.netloc == test.netloc

def inject_user():
    user = None
    store = {}
    if 'user_id' in session:
        try:
            conn = get_db()
            u = conn.execute("SELECT id,nome,role FROM utilizadores WHERE id=?",
                             (session['user_id'],)).fetchone()
            if u: user = {'id':u[0],'nome':u[1],'role':u[2]}
            if not request.path.startswith('/api/'):
                rows = conn.execute("SELECT chave,valor FROM configuracoes").fetchall()
                store = {r[0]: r[1] for r in rows}
            conn.close()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Erro em inject_user: %s", e)
    return {'current_user': user, 'store': store}

def require_api_auth():
    if request.path.startswith('/api/') and request.path != '/api/utilizadores/login':
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'ok':False,'erro':'Autenticação necessária'}),401
            return redirect(url_for('pages.login_page', next=request.path))
