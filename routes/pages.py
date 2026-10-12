from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash
from database import get_db, moeda, get_config
from auth import login_required, gerente_required, permissao_required, is_safe_url
from extensions import csrf
from services.utilizador_service import autenticar
from services.produto_service import listar_produtos
from services.categoria_service import listar_categorias
from services.cliente_service import listar_clientes
from services.empresa_service import listar_filiais
from services.dashboard_service import (obter_metricas, obter_produtos_top,
    obter_movimentos_recentes, obter_movimentos_diarios_30dias,
    obter_produtos_baixo_stock, obter_lista_produtos_completa,
    obter_vendas_hoje, obter_media_vendas_7dias)
from services.config_service import obter_configuracoes

pages_bp = Blueprint('pages', __name__)

@csrf.exempt
@pages_bp.route('/login', methods=['GET','POST'])
def login_page():
    if request.method == 'POST':
        nome = request.form.get('nome','').strip()
        pin = request.form.get('pin','').strip()
        if not nome or not pin:
            return render_template('login.html', erro='Nome e PIN são obrigatórios')
        ip = request.remote_addr
        user, erro = autenticar(nome, pin, ip)
        if user:
            user_data = {'user_id': user['id'], 'user_nome': user['nome'], 'user_role': user['role']}
            session.clear()
            session.update(user_data)
            session.permanent = True
            nex = request.args.get('next')
            if not nex or not is_safe_url(nex):
                nex = url_for('pages.pdv') if user['role'] == 'caixa' else url_for('pages.dashboard')
            return redirect(nex)
        return render_template('login.html', erro=erro or 'Nome ou PIN inválidos')
    return render_template('login.html')

@pages_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pages.login_page'))

@pages_bp.route('/')
@login_required
def dashboard():
    metricas = obter_metricas()
    dash = obter_produtos_top()
    movs = obter_movimentos_recentes()
    dias = obter_movimentos_diarios_30dias()
    baixo = obter_produtos_baixo_stock()
    prods = obter_lista_produtos_completa()
    vendas_hoje = obter_vendas_hoje()
    media_7dias = obter_media_vendas_7dias()
    meta_diaria = float(get_config('meta_diaria_vendas', '0'))
    return render_template('dashboard.html', pagina='Dashboard',
        total_prod=metricas['total_prod'], total_cat=metricas['total_cat'],
        total_mov=metricas['total_mov'], valor_total=metricas['valor_total'],
        dash=dash, movs=movs, dias=dias, baixo=baixo, prods=prods,
        vendas_hoje=vendas_hoje, media_7dias=media_7dias, meta_diaria=meta_diaria)

@pages_bp.route('/pdv')
@login_required
def pdv():
    prods = listar_produtos()
    stock_critico = sum(1 for p in prods if float(str(p.get('quantidade','0')).replace(',','.')) <= 3)
    return render_template('pdv.html', pagina='PDV',
        prods=prods, categorias=listar_categorias(),
        clientes=listar_clientes(), stock_critico=stock_critico, sidebar_hidden=True,
        filiais=listar_filiais())

@pages_bp.route('/produtos')
@login_required
@permissao_required('gerir_produtos')
def page_produtos():
    return render_template('produtos.html', pagina='Produtos')

@pages_bp.route('/movimentacoes')
@login_required
@permissao_required('gerir_produtos')
def page_movimentacoes():
    return render_template('movimentacoes.html', pagina='Movimentações')

@pages_bp.route('/categorias')
@login_required
@permissao_required('gerir_produtos')
def page_categorias():
    return render_template('categorias.html', pagina='Categorias')

@pages_bp.route('/clientes')
@login_required
@permissao_required('gerir_clientes')
def page_clientes():
    return render_template('clientes.html', pagina='Clientes')

@pages_bp.route('/fornecedores')
@login_required
@permissao_required('gerir_fornecedores')
def page_fornecedores():
    return render_template('fornecedores.html', pagina='Fornecedores')

@pages_bp.route('/utilizadores')
@login_required
@gerente_required
def pagina_utilizadores():
    return render_template('utilizadores.html', pagina='Utilizadores')

@pages_bp.route('/caixa')
@login_required
def pagina_caixa():
    return render_template('caixa.html', pagina='Caixa')

@pages_bp.route('/relatorios')
@login_required
@permissao_required('ver_relatorios')
def page_relatorios():
    return render_template('relatorios.html', pagina='Relatórios')

@pages_bp.route('/configuracoes')
@login_required
@permissao_required('configurar_sistema')
def page_configuracoes():
    return render_template('configuracoes.html', pagina='Configurações')
