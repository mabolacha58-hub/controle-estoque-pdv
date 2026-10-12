from services.base import db_session, db_connection

def listar_contas_pagar(status=None, filial_id=1):
    with db_connection() as conn:
        sql = '''SELECT cp.*, f.nome as fornecedor
                 FROM contas_pagar cp LEFT JOIN fornecedores f ON cp.fornecedor_id=f.id
                 WHERE cp.filial_id=?'''
        params = [filial_id]
        if status:
            sql += " AND cp.status=?"
            params.append(status)
        sql += " ORDER BY cp.data_vencimento"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def criar_conta_pagar(fornecedor_id, descricao, valor, data_vencimento, compra_id=None, filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO contas_pagar (fornecedor_id,compra_id,descricao,valor,saldo,data_vencimento,filial_id)
                          VALUES (?,?,?,?,?,?,?)''',
                       (fornecedor_id, compra_id, descricao, valor, valor, data_vencimento, filial_id))
        return c.lastrowid

def pagar_conta(id, valor_pago, banco_id=None, forma_pagamento="dinheiro"):
    with db_session() as conn:
        cp = conn.execute("SELECT * FROM contas_pagar WHERE id=?", (id,)).fetchone()
        if not cp:
            return False
        novo_saldo = cp["saldo"] - valor_pago
        status = "pago" if novo_saldo <= 0 else "parcial"
        conn.execute("UPDATE contas_pagar SET saldo=?, status=?, data_pagamento=datetime('now','localtime') WHERE id=?",
                   (max(0, novo_saldo), status, id))
        conn.execute('''INSERT INTO movimentos_financeiros (tipo,categoria,descricao,valor,banco_id,forma_pagamento,filial_id)
                      VALUES (?,?,?,?,?,?,?)''',
                   ("saida", "contas_pagar", cp["descricao"], valor_pago, banco_id, forma_pagamento, cp["filial_id"]))
        if banco_id:
            atual = conn.execute("SELECT saldo FROM bancos WHERE id=?", (banco_id,)).fetchone()
            if not atual or atual[0] < valor_pago:
                return False
            conn.execute("UPDATE bancos SET saldo=saldo-? WHERE id=? AND saldo>=?", (valor_pago, banco_id, valor_pago))
        return True

def listar_contas_receber(status=None, filial_id=1):
    with db_connection() as conn:
        sql = '''SELECT cr.*, cl.nome as cliente
                 FROM contas_receber cr LEFT JOIN clientes cl ON cr.cliente_id=cl.id
                 WHERE cr.filial_id=?'''
        params = [filial_id]
        if status:
            sql += " AND cr.status=?"
            params.append(status)
        sql += " ORDER BY cr.data_vencimento"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def criar_conta_receber(cliente_id, descricao, valor, data_vencimento, venda_id=None, filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO contas_receber (cliente_id,venda_id,descricao,valor,saldo,data_vencimento,filial_id)
                          VALUES (?,?,?,?,?,?,?)''',
                       (cliente_id, venda_id, descricao, valor, valor, data_vencimento, filial_id))
        return c.lastrowid

def receber_conta(id, valor_recebido, banco_id=None, forma_pagamento="dinheiro"):
    with db_session() as conn:
        cr = conn.execute("SELECT * FROM contas_receber WHERE id=?", (id,)).fetchone()
        if not cr:
            return False
        novo_saldo = cr["saldo"] - valor_recebido
        status = "pago" if novo_saldo <= 0 else "parcial"
        conn.execute("UPDATE contas_receber SET saldo=?, status=?, data_recebimento=datetime('now','localtime') WHERE id=?",
                   (max(0, novo_saldo), status, id))
        conn.execute('''INSERT INTO movimentos_financeiros (tipo,categoria,descricao,valor,banco_id,forma_pagamento,filial_id)
                      VALUES (?,?,?,?,?,?,?)''',
                   ("entrada", "contas_receber", cr["descricao"], valor_recebido, banco_id, forma_pagamento, cr["filial_id"]))
        if banco_id:
            conn.execute("UPDATE bancos SET saldo=saldo+? WHERE id=?", (valor_recebido, banco_id))
        return True

def listar_movimentos_financeiros(filial_id=1, dias=30):
    with db_connection() as conn:
        r = conn.execute('''SELECT * FROM movimentos_financeiros
                          WHERE filial_id=? AND data_movimento >= datetime('now', ?)
                          ORDER BY data_movimento DESC''',
                       (filial_id, f'-{dias} days')).fetchall()
        return [dict(row) for row in r]

def registrar_movimento_financeiro(tipo, categoria, descricao, valor, forma_pagamento="dinheiro", banco_id=None, filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO movimentos_financeiros (tipo,categoria,descricao,valor,banco_id,forma_pagamento,filial_id)
                          VALUES (?,?,?,?,?,?,?)''',
                       (tipo, categoria, descricao, valor, banco_id, forma_pagamento, filial_id))
        if banco_id:
            delta = valor if tipo == "entrada" else -valor
            conn.execute("UPDATE bancos SET saldo=saldo+? WHERE id=?", (delta, banco_id))
        return c.lastrowid

def listar_bancos(filial_id=1):
    with db_connection() as conn:
        r = conn.execute("SELECT * FROM bancos WHERE filial_id=? ORDER BY nome", (filial_id,)).fetchall()
        return [dict(row) for row in r]

def criar_banco(nome, numero_conta, titular, saldo=0, filial_id=1):
    with db_session() as conn:
        c = conn.execute("INSERT INTO bancos (nome,numero_conta,titular,saldo,filial_id) VALUES (?,?,?,?,?)",
                       (nome, numero_conta, titular, saldo, filial_id))
        return c.lastrowid

def fluxo_caixa(filial_id=1, dias=30):
    with db_connection() as conn:
        r = conn.execute('''SELECT date(data_movimento) as dia,
                                 SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END) as entradas,
                                 SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END) as saidas
                          FROM movimentos_financeiros
                          WHERE filial_id=? AND data_movimento >= datetime('now', ?)
                          GROUP BY date(data_movimento)
                          ORDER BY dia''', (filial_id, f'-{dias} days')).fetchall()
        return [dict(row) for row in r]
