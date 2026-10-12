from flask import Blueprint, render_template
from auth import login_required, permissao_required
from datetime import datetime

pages_enterprise_bp = Blueprint('pages_enterprise', __name__)

@pages_enterprise_bp.route('/filiais')
@login_required
@permissao_required('gerir_filiais')
def filiais_page():
    return render_template('filiais.html', pagina='Filiais')

@pages_enterprise_bp.route('/compras')
@login_required
@permissao_required('gerir_compras')
def compras_page():
    return render_template('compras.html', pagina='Compras')

@pages_enterprise_bp.route('/financeiro')
@login_required
@permissao_required('gerir_financeiro')
def financeiro_page():
    return render_template('financeiro.html', pagina='Financeiro')

@pages_enterprise_bp.route('/fiscal')
@login_required
@permissao_required('gerir_fiscal')
def fiscal_page():
    return render_template('fiscal.html', pagina='Documentos Fiscais')

@pages_enterprise_bp.route('/crm')
@login_required
@permissao_required('gerir_crm')
def crm_page():
    return render_template('crm.html', pagina='CRM')

@pages_enterprise_bp.route('/rh')
@login_required
@permissao_required('gerir_rh')
def rh_page():
    return render_template('rh.html', pagina='Recursos Humanos', ano_atual=datetime.now().year)

@pages_enterprise_bp.route('/cargas')
@login_required
@permissao_required('gerir_rh')
def cargas_page():
    return render_template('cargas.html', pagina='Cargas')

@pages_enterprise_bp.route('/dashboard-enterprise')
@login_required
@permissao_required('ver_dashboard_enterprise')
def dashboard_enterprise_page():
    return render_template('dashboard_enterprise.html', pagina='Dashboard Empresarial')

@pages_enterprise_bp.route('/config-fiscal')
@login_required
@permissao_required('gerir_fiscal')
def config_fiscal_page():
    return render_template('config_fiscal.html', pagina='Configuração Fiscal')

@pages_enterprise_bp.route('/fiscal-municipal')
@login_required
@permissao_required('gerir_fiscal')
def fiscal_municipal_page():
    return render_template('fiscal_municipal.html', pagina='Fiscal Municipal')

@pages_enterprise_bp.route('/auditoria')
@login_required
@permissao_required('gerir_utilizadores')
def auditoria_page():
    return render_template('auditoria.html', pagina='Auditoria')
