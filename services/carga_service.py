from services.base import db_session, db_connection
from datetime import datetime

def listar_cargas(status=None):
    with db_connection() as conn:
        sql = '''SELECT c.*, f.nome as filial_nome FROM cargas c
                 LEFT JOIN filiais f ON c.filial_id=f.id'''
        params = []
        if status:
            sql += " WHERE c.status=?"
            params.append(status)
        sql += " ORDER BY c.data_inicio DESC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def criar_carga(destino, data_inicio, valor_combinado=0, observacao="", filial_id=1):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO cargas (destino, data_inicio, valor_combinado, observacao, filial_id)
                          VALUES (?,?,?,?,?)''', (destino, data_inicio, valor_combinado, observacao, filial_id))
        return c.lastrowid

def finalizar_carga(id, data_fim):
    with db_session() as conn:
        conn.execute("UPDATE cargas SET status='finalizada', data_fim=? WHERE id=?", (data_fim, id))

def pagar_carga(id, data_pagamento):
    acerto = obter_acerto(id)
    if not acerto or acerto["carga"]["status"] != "finalizada":
        return False
    if acerto["carga"].get("pago"):
        return False
    with db_session() as conn:
        conn.execute("UPDATE cargas SET pago=1, data_pagamento=? WHERE id=?", (data_pagamento, id))
    from services.financeiro_service import registrar_movimento_financeiro
    registrar_movimento_financeiro(
        tipo="saida",
        categoria="salario",
        descricao=f"Pagamento carga: {acerto['carga']['destino']}",
        valor=float(acerto["valor_liquido"]),
        forma_pagamento="dinheiro",
        banco_id=None
    )
    return True

def excluir_carga(id):
    with db_session() as conn:
        conn.execute("DELETE FROM adiantamentos WHERE carga_id=?", (id,))
        conn.execute("DELETE FROM cargas WHERE id=?", (id,))

def listar_adiantamentos(carga_id=None, funcionario_id=None):
    with db_connection() as conn:
        sql = '''SELECT a.*, f.nome as funcionario_nome FROM adiantamentos a
                 LEFT JOIN funcionarios f ON a.funcionario_id=f.id'''
        params = []
        wheres = []
        if carga_id:
            wheres.append("a.carga_id=?")
            params.append(carga_id)
        if funcionario_id:
            wheres.append("a.funcionario_id=?")
            params.append(funcionario_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY a.data DESC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def registrar_adiantamento(carga_id, funcionario_id, valor, data, observacao=""):
    with db_session() as conn:
        c = conn.execute('''INSERT INTO adiantamentos (carga_id, funcionario_id, valor, data, observacao)
                          VALUES (?,?,?,?,?)''', (carga_id, funcionario_id, valor, data, observacao))
        return c.lastrowid

def excluir_adiantamento(id):
    with db_session() as conn:
        conn.execute("DELETE FROM adiantamentos WHERE id=?", (id,))

def obter_acerto(carga_id):
    with db_connection() as conn:
        carga = conn.execute('''SELECT c.*, f.nome as filial_nome FROM cargas c
                              LEFT JOIN filiais f ON c.filial_id=f.id
                              WHERE c.id=?''', (carga_id,)).fetchone()
        if not carga:
            return None
        adiantamentos = conn.execute('''SELECT a.*, f.nome as funcionario_nome
                                      FROM adiantamentos a LEFT JOIN funcionarios f ON a.funcionario_id=f.id
                                      WHERE a.carga_id=? ORDER BY a.data''', (carga_id,)).fetchall()
        carga = dict(carga)
        adiantamentos = [dict(a) for a in adiantamentos]
        total_adiantamentos = sum(a["valor"] for a in adiantamentos)
        return {
            "carga": carga,
            "adiantamentos": adiantamentos,
            "total_adiantamentos": total_adiantamentos,
            "valor_combinado": carga["valor_combinado"],
            "valor_liquido": carga["valor_combinado"] - total_adiantamentos,
        }
