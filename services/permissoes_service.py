from services.base import db_connection, db_session

PERMISSOES_DISPONIVEIS = [
    ("acesso_enterprise", "Acesso ao módulo Enterprise"),
    ("gerir_produtos", "Gerir Produtos"),
    ("gerir_clientes", "Gerir Clientes"),
    ("gerir_fornecedores", "Gerir Fornecedores"),
    ("gerir_utilizadores", "Gerir Utilizadores"),
    ("gerir_filiais", "Gerir Filiais"),
    ("gerir_compras", "Gerir Compras"),
    ("gerir_financeiro", "Gerir Financeiro"),
    ("gerir_fiscal", "Gerir Documentos Fiscais"),
    ("gerir_crm", "Gerir CRM / Fidelização"),
    ("gerir_rh", "Gerir Recursos Humanos"),
    ("ver_relatorios", "Ver Relatórios"),
    ("ver_dashboard_enterprise", "Ver Dashboard Empresarial"),
    ("configurar_sistema", "Configurar Sistema"),
    ("anular_documentos", "Anular Documentos"),
    ("exportar_dados", "Exportar Dados"),
]

def listar_permissoes_utilizador(utilizador_id):
    with db_connection() as conn:
        rows = conn.execute("SELECT permissao FROM permissoes WHERE utilizador_id=?", (utilizador_id,)).fetchall()
        return [row["permissao"] for row in rows]

def tem_permissao(utilizador_id, permissao):
    with db_connection() as conn:
        r = conn.execute("SELECT 1 FROM permissoes WHERE utilizador_id=? AND permissao=?", (utilizador_id, permissao)).fetchone()
        return r is not None

def definir_permissoes(utilizador_id, permissoes):
    with db_session() as conn:
        conn.execute("DELETE FROM permissoes WHERE utilizador_id=?", (utilizador_id,))
        for p in permissoes:
            conn.execute("INSERT INTO permissoes (utilizador_id, permissao) VALUES (?, ?)", (utilizador_id, p))

def listar_permissoes_todos():
    with db_connection() as conn:
        rows = conn.execute('''SELECT u.id, u.nome, u.role, GROUP_CONCAT(p.permissao, ',') as permissoes
                             FROM utilizadores u LEFT JOIN permissoes p ON u.id=p.utilizador_id
                             GROUP BY u.id ORDER BY u.nome''').fetchall()
        return [dict(row) for row in rows]

def permissoes_com_labels(perm_list):
    labels = {k: v for k, v in PERMISSOES_DISPONIVEIS}
    return [{"chave": p, "label": labels.get(p, p)} for p in perm_list]
