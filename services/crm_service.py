from services.base import db_session, db_connection

NIVEIS = ["bronze", "prata", "ouro", "platina", "diamante"]
LIMIARES = {"bronze": 0, "prata": 10000, "ouro": 50000, "platina": 100000, "diamante": 500000}
TAXA_CASHBACK = {"bronze": 0.005, "prata": 0.01, "ouro": 0.015, "platina": 0.02, "diamante": 0.03}

def obter_fidelizacao(cliente_id):
    with db_session() as conn:
        r = conn.execute("SELECT * FROM fidelizacao WHERE cliente_id=?", (cliente_id,)).fetchone()
        if not r:
            conn.execute("INSERT INTO fidelizacao (cliente_id) VALUES (?)", (cliente_id,))
            r = conn.execute("SELECT * FROM fidelizacao WHERE cliente_id=?", (cliente_id,)).fetchone()
        return dict(r) if r else None

def atualizar_fidelizacao(cliente_id, valor_compra):
    with db_session() as conn:
        f = obter_fidelizacao(cliente_id)
        if not f:
            return
        novo_total = f["total_compras"] + valor_compra
        novo_nivel = "bronze"
        for nivel, limiar in sorted(LIMIARES.items(), key=lambda x: x[1], reverse=True):
            if novo_total >= limiar:
                novo_nivel = nivel
                break
        pontos_ganhos = valor_compra * TAXA_CASHBACK.get(novo_nivel, 0.005)
        conn.execute('''UPDATE fidelizacao SET pontos=pontos+?, total_compras=?, nivel=?,
                      ultima_compra=datetime('now','localtime') WHERE cliente_id=?''',
                   (pontos_ganhos, novo_total, novo_nivel, cliente_id))

def adicionar_cashback(cliente_id, valor, tipo="acumulo", venda_id=None):
    with db_session() as conn:
        conn.execute("INSERT INTO cashback (cliente_id,valor,tipo,venda_id) VALUES (?,?,?,?)",
                   (cliente_id, valor, tipo, venda_id))
        if tipo == "acumulo":
            conn.execute("UPDATE clientes SET saldo=saldo+? WHERE id=?", (valor, cliente_id))
        elif tipo == "resgate":
            conn.execute("UPDATE clientes SET saldo=saldo-? WHERE id=?", (valor, cliente_id))

def listar_cashback(cliente_id):
    with db_connection() as conn:
        r = conn.execute("SELECT * FROM cashback WHERE cliente_id=? ORDER BY data DESC", (cliente_id,)).fetchall()
        return [dict(row) for row in r]

def registrar_comunicacao(cliente_id, tipo, destinatario, mensagem):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO comunicacoes (cliente_id,tipo,destinatario,mensagem)
                          VALUES (?,?,?,?)''', (cliente_id, tipo, destinatario, mensagem))
        return c.lastrowid

def listar_comunicacoes(cliente_id=None):
    with db_connection() as conn:
        if cliente_id:
            r = conn.execute("SELECT * FROM comunicacoes WHERE cliente_id=? ORDER BY data_envio DESC",
                           (cliente_id,)).fetchall()
        else:
            r = conn.execute("SELECT * FROM comunicacoes ORDER BY data_envio DESC LIMIT 50").fetchall()
        return [dict(row) for row in r]

def listar_clientes_fidelidade():
    with db_connection() as conn:
        r = conn.execute('''SELECT f.*, c.nome, c.nif, c.telefone, c.email, c.saldo
                          FROM fidelizacao f JOIN clientes c ON f.cliente_id=c.id
                          ORDER BY f.total_compras DESC''').fetchall()
        return [dict(row) for row in r]
