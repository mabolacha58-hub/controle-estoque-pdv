from datetime import datetime
from services.base import db_session, db_connection

def processar_folha(mes, ano):
    with db_session() as conn:
        funcionarios = conn.execute(
            "SELECT id, salario_base FROM funcionarios WHERE ativo=1"
        ).fetchall()
        ids = []
        for f in funcionarios:
            salario = f["salario_base"] or 0

            adiantamentos = conn.execute(
                "SELECT COALESCE(SUM(valor),0) as total FROM salario_adiantamentos WHERE funcionario_id=? AND processado=0",
                (f["id"],)
            ).fetchone()
            outros_descontos = adiantamentos["total"]

            existente = conn.execute(
                "SELECT id, salario_liquido FROM folhas_salario WHERE funcionario_id=? AND mes=? AND ano=?",
                (f["id"], mes, ano)
            ).fetchone()

            if existente:
                if outros_descontos > 0:
                    conn.execute('''UPDATE folhas_salario SET
                        outros_descontos = outros_descontos + ?,
                        total_descontos = total_descontos + ?,
                        salario_liquido = salario_liquido - ?
                        WHERE id=?''',
                        (outros_descontos, outros_descontos, outros_descontos, existente["id"]))
                    conn.execute("UPDATE salario_adiantamentos SET processado=1, folha_id=? WHERE funcionario_id=? AND processado=0",
                               (existente["id"], f["id"]))
                    ids.append(existente["id"])
                continue

            salario_liquido = salario - outros_descontos
            c = conn.execute('''INSERT INTO folhas_salario
                (funcionario_id, mes, ano, salario_base, outros_descontos, total_descontos, salario_liquido)
                VALUES (?,?,?,?,?,?,?)''',
                (f["id"], mes, ano, salario, outros_descontos, outros_descontos, salario_liquido))
            folha_id = c.lastrowid

            if outros_descontos > 0:
                conn.execute("UPDATE salario_adiantamentos SET processado=1, folha_id=? WHERE funcionario_id=? AND processado=0",
                           (folha_id, f["id"]))
            ids.append(folha_id)
        return ids

def listar_folhas(mes=None, ano=None, funcionario_id=None, status=None):
    with db_connection() as conn:
        sql = '''SELECT f.*, func.nome as funcionario_nome, func.cargo
                 FROM folhas_salario f
                 JOIN funcionarios func ON f.funcionario_id = func.id'''
        wheres = []
        params = []
        if mes:
            wheres.append("f.mes=?")
            params.append(mes)
        if ano:
            wheres.append("f.ano=?")
            params.append(ano)
        if funcionario_id:
            wheres.append("f.funcionario_id=?")
            params.append(funcionario_id)
        if status:
            wheres.append("f.status=?")
            params.append(status)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY f.ano DESC, f.mes DESC, func.nome"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def pagar_folha(id, data_pagamento=None):
    with db_session() as conn:
        data = data_pagamento or datetime.now().strftime("%Y-%m-%d")
        conn.execute("UPDATE folhas_salario SET status='pago', data_pagamento=? WHERE id=?",
                   (data, id))

def excluir_folha(id):
    with db_session() as conn:
        conn.execute("DELETE FROM folhas_salario WHERE id=?", (id,))

def atualizar_folha(id, dados):
    with db_session() as conn:
        campos = []
        valores = []
        for campo in ["outros_descontos"]:
            if campo in dados:
                campos.append(f"{campo}=?")
                valores.append(dados[campo])
        if campos:
            valor_desc = dados.get("outros_descontos", 0)
            row = conn.execute("SELECT salario_base FROM folhas_salario WHERE id=?", (id,)).fetchone()
            if row:
                liquido = row["salario_base"] - valor_desc
                campos.append("total_descontos=?")
                valores.append(valor_desc)
                campos.append("salario_liquido=?")
                valores.append(liquido)
            sql = f"UPDATE folhas_salario SET {','.join(campos)} WHERE id=?"
            valores.append(id)
            conn.execute(sql, valores)

def listar_funcionarios(ativo=True, filial_id=1):
    with db_connection() as conn:
        r = conn.execute('''SELECT f.*, u.nome as utilizador_nome
                          FROM funcionarios f LEFT JOIN utilizadores u ON f.utilizador_id=u.id
                          WHERE f.filial_id=? AND f.ativo=?
                          ORDER BY f.nome''', (filial_id, 1 if ativo else 0)).fetchall()
        return [dict(row) for row in r]

def criar_funcionario(nome, cargo, salario_base=0, utilizador_id=None, filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO funcionarios (utilizador_id,nome,cargo,salario_base,filial_id)
                          VALUES (?,?,?,?,?)''',
                       (utilizador_id, nome, cargo, salario_base, filial_id))
        return c.lastrowid

def editar_funcionario(id, nome, cargo, salario_base=0):
    with db_session() as conn:
        conn.execute("UPDATE funcionarios SET nome=?, cargo=?, salario_base=? WHERE id=?",
                   (nome, cargo, salario_base, id))

def excluir_funcionario(id):
    with db_session() as conn:
        conn.execute("UPDATE funcionarios SET ativo=0 WHERE id=?", (id,))

def registrar_presenca(funcionario_id, hora_entrada=None, hora_saida=None):
    with db_session() as conn:
        hoje = datetime.now().strftime("%Y-%m-%d")
        existente = conn.execute("SELECT * FROM presencas WHERE funcionario_id=? AND date(data)=?",
                               (funcionario_id, hoje)).fetchone()
        if existente and hora_saida:
            entrada = datetime.strptime(f"{hoje} {existente['hora_entrada']}", "%Y-%m-%d %H:%M")
            saida = datetime.strptime(f"{hoje} {hora_saida}", "%Y-%m-%d %H:%M")
            horas = round((saida - entrada).total_seconds() / 3600, 2)
            conn.execute("UPDATE presencas SET hora_saida=?, horas_trabalhadas=? WHERE id=?",
                       (hora_saida, horas, existente["id"]))
        elif not existente:
            conn.execute("INSERT INTO presencas (funcionario_id,hora_entrada) VALUES (?,?)",
                       (funcionario_id, hora_entrada or datetime.now().strftime("%H:%M")))

def listar_presencas(funcionario_id=None, dias=30):
    with db_connection() as conn:
        if funcionario_id:
            r = conn.execute('''SELECT p.*, f.nome as funcionario
                              FROM presencas p JOIN funcionarios f ON p.funcionario_id=f.id
                              WHERE p.funcionario_id=? AND p.data >= datetime('now',?)
                              ORDER BY p.data DESC''', (funcionario_id, f'-{dias} days')).fetchall()
        else:
            r = conn.execute('''SELECT p.*, f.nome as funcionario
                              FROM presencas p JOIN funcionarios f ON p.funcionario_id=f.id
                              WHERE p.data >= datetime('now',?)
                              ORDER BY p.data DESC''', (f'-{dias} days',)).fetchall()
        return [dict(row) for row in r]

def registrar_comissao(funcionario_id, venda_id, valor_venda, percentagem):
    valor_comissao = valor_venda * (percentagem / 100)
    with db_session() as conn:
        conn.execute('''INSERT INTO comissoes (funcionario_id,venda_id,valor_venda,percentagem,valor_comissao)
                      VALUES (?,?,?,?,?)''', (funcionario_id, venda_id, valor_venda, percentagem, valor_comissao))
        return valor_comissao

def pagar_comissao(id):
    with db_session() as conn:
        conn.execute("UPDATE comissoes SET pago=1 WHERE id=?", (id,))

def listar_comissoes(funcionario_id=None, pago=None):
    with db_connection() as conn:
        sql = '''SELECT c.*, f.nome as funcionario FROM comissoes c
                 JOIN funcionarios f ON c.funcionario_id=f.id'''
        params = []
        wheres = []
        if funcionario_id:
            wheres.append("c.funcionario_id=?")
            params.append(funcionario_id)
        if pago is not None:
            wheres.append("c.pago=?")
            params.append(1 if pago else 0)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY c.data DESC"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

# ===================== PAGAMENTO DE ALUGUER =====================

def listar_alugueres(mes=None, ano=None, status=None):
    with db_connection() as conn:
        sql = '''SELECT * FROM pagamentos_aluguer'''
        wheres = []
        params = []
        if mes:
            wheres.append("mes=?")
            params.append(mes)
        if ano:
            wheres.append("ano=?")
            params.append(ano)
        if status:
            wheres.append("status=?")
            params.append(status)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY ano DESC, mes DESC, descricao"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def criar_aluguer(descricao, proprietario, valor, data_vencimento, mes, ano, observacao="", filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO pagamentos_aluguer
            (descricao, proprietario, valor, data_vencimento, mes, ano, observacao, filial_id)
            VALUES (?,?,?,?,?,?,?,?)''',
            (descricao, proprietario, valor, data_vencimento, mes, ano, observacao, filial_id))
        return c.lastrowid

def pagar_aluguer(id, data_pagamento=None):
    with db_session() as conn:
        data = data_pagamento or datetime.now().strftime("%Y-%m-%d")
        conn.execute("UPDATE pagamentos_aluguer SET status='pago', data_pagamento=? WHERE id=?", (data, id))

def excluir_aluguer(id):
    with db_session() as conn:
        conn.execute("DELETE FROM pagamentos_aluguer WHERE id=?", (id,))

# ===================== ADIANTAMENTOS SALARIAIS =====================

def registrar_adiantamento_salarial(funcionario_id, valor, data, observacao=""):
    with db_session() as conn:
        c = conn.execute("INSERT INTO salario_adiantamentos (funcionario_id, valor, data, observacao) VALUES (?,?,?,?)",
                       (funcionario_id, valor, data, observacao))
        return c.lastrowid

def listar_adiantamentos_salariais(funcionario_id=None, processado=None):
    with db_connection() as conn:
        sql = '''SELECT a.*, f.nome as funcionario_nome
                 FROM salario_adiantamentos a
                 JOIN funcionarios f ON a.funcionario_id = f.id'''
        wheres = []
        params = []
        if funcionario_id:
            wheres.append("a.funcionario_id=?")
            params.append(funcionario_id)
        if processado is not None:
            wheres.append("a.processado=?")
            params.append(1 if processado else 0)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY a.data DESC"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def excluir_adiantamento_salarial(id):
    with db_session() as conn:
        conn.execute("DELETE FROM salario_adiantamentos WHERE id=? AND processado=0", (id,))

def total_adiantamentos_pendentes_funcionario(funcionario_id):
    with db_connection() as conn:
        r = conn.execute("SELECT COALESCE(SUM(valor),0) as total FROM salario_adiantamentos WHERE funcionario_id=? AND processado=0",
                       (funcionario_id,)).fetchone()
        return r["total"]
