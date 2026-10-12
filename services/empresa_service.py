from services.base import db_session, db_connection

def listar_empresas():
    with db_connection() as conn:
        r = conn.execute("SELECT * FROM empresas ORDER BY nome").fetchall()
        return [dict(row) for row in r]

def listar_filiais(empresa_id=1):
    try:
        with db_connection() as conn:
            r = conn.execute("SELECT * FROM filiais WHERE empresa_id=? ORDER BY nome", (empresa_id,)).fetchall()
            return [dict(row) for row in r]
    except Exception:
        return []

def criar_filial(empresa_id, nome, endereco="", telefone="", email=""):
    with db_session() as conn:
        c = conn.execute("INSERT INTO filiais (empresa_id,nome,endereco,telefone,email) VALUES (?,?,?,?,?)",
                       (empresa_id, nome, endereco, telefone, email))
        return c.lastrowid

def obter_stock_filial(produto_id, filial_id=1):
    with db_connection() as conn:
        r = conn.execute("SELECT quantidade FROM produto_filial WHERE produto_id=? AND filial_id=?",
                       (produto_id, filial_id)).fetchone()
        return r[0] if r else 0

def atualizar_stock_filial(produto_id, filial_id, quantidade):
    with db_session() as conn:
        conn.execute('''INSERT INTO produto_filial (produto_id,filial_id,quantidade)
                      VALUES (?,?,?) ON CONFLICT(produto_id,filial_id)
                      DO UPDATE SET quantidade=quantidade+?''',
                  (produto_id, filial_id, quantidade, quantidade))

def listar_lotes(produto_id=None, filial_id=1):
    with db_connection() as conn:
        if produto_id:
            r = conn.execute("SELECT * FROM lotes WHERE produto_id=? AND filial_id=? ORDER BY data_validade",
                           (produto_id, filial_id)).fetchall()
        else:
            r = conn.execute("SELECT * FROM lotes WHERE filial_id=? ORDER BY data_validade",
                           (filial_id,)).fetchall()
        return [dict(row) for row in r]

def criar_lote(produto_id, codigo_lote, quantidade, data_validade, preco_custo=0, filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO lotes (produto_id,filial_id,codigo_lote,quantidade,data_validade,preco_custo)
                          VALUES (?,?,?,?,?,?)''',
                       (produto_id, filial_id, codigo_lote, quantidade, data_validade, preco_custo))
        return c.lastrowid

def editar_filial(id, nome, endereco="", telefone="", email=""):
    with db_session() as conn:
        conn.execute("UPDATE filiais SET nome=?, endereco=?, telefone=?, email=? WHERE id=?",
                   (nome, endereco, telefone, email, id))

def excluir_filial(id):
    with db_session() as conn:
        conn.execute("DELETE FROM filiais WHERE id=?", (id,))

def listar_transferencias(filial_id=None):
    with db_connection() as conn:
        if filial_id:
            r = conn.execute('''SELECT t.*, p.nome as produto, f_orig.nome as origem, f_dest.nome as destino
                              FROM transferencias t
                              JOIN produtos p ON t.produto_id=p.id
                              JOIN filiais f_orig ON t.filial_origem=f_orig.id
                              JOIN filiais f_dest ON t.filial_destino=f_dest.id
                              WHERE t.filial_origem=? OR t.filial_destino=?
                              ORDER BY t.data_criacao DESC''', (filial_id, filial_id)).fetchall()
        else:
            r = conn.execute('''SELECT t.*, p.nome as produto, f_orig.nome as origem, f_dest.nome as destino
                              FROM transferencias t
                              JOIN produtos p ON t.produto_id=p.id
                              JOIN filiais f_orig ON t.filial_origem=f_orig.id
                              JOIN filiais f_dest ON t.filial_destino=f_dest.id
                              ORDER BY t.data_criacao DESC''').fetchall()
        return [dict(row) for row in r]

def criar_transferencia(produto_id, quantidade, filial_origem, filial_destino, observacao=""):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO transferencias (produto_id,quantidade,filial_origem,filial_destino,observacao)
                          VALUES (?,?,?,?,?)''',
                       (produto_id, quantidade, filial_origem, filial_destino, observacao))
        return c.lastrowid

def confirmar_transferencia(id):
    with db_session() as conn:
        t = conn.execute("SELECT * FROM transferencias WHERE id=?", (id,)).fetchone()
        if not t or t["status"] != "pendente":
            return False
        atual = conn.execute("SELECT quantidade FROM produto_filial WHERE produto_id=? AND filial_id=?",
                           (t["produto_id"], t["filial_origem"])).fetchone()
        if not atual or atual[0] < t["quantidade"]:
            return False
        conn.execute('''UPDATE produto_filial SET quantidade=quantidade-?
                      WHERE produto_id=? AND filial_id=? AND quantidade>=?''',
                   (t["quantidade"], t["produto_id"], t["filial_origem"], t["quantidade"]))
        conn.execute('''INSERT INTO produto_filial (produto_id,filial_id,quantidade)
                      VALUES (?,?,?) ON CONFLICT(produto_id,filial_id)
                      DO UPDATE SET quantidade=quantidade+?''',
                   (t["produto_id"], t["filial_destino"], t["quantidade"], t["quantidade"]))
        conn.execute("UPDATE transferencias SET status='concluida', data_conclusao=datetime('now','localtime') WHERE id=?",
                   (id,))
        return True
