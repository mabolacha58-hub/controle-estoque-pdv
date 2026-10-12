from services.base import db_session, db_connection

def listar_tipos():
    with db_connection() as conn:
        rows = conn.execute("SELECT id, nome, descricao FROM fiscal_municipal_tipos ORDER BY nome").fetchall()
        return [dict(r) for r in rows]

def listar_fiscal_municipal(status=None):
    with db_connection() as conn:
        if status:
            rows = conn.execute("""
                SELECT fm.*, f.nome as filial_nome
                FROM fiscal_municipal fm
                LEFT JOIN filiais f ON fm.filial_id=f.id
                WHERE fm.status=?
                ORDER BY fm.data_vencimento ASC
            """, (status,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT fm.*, f.nome as filial_nome
                FROM fiscal_municipal fm
                LEFT JOIN filiais f ON fm.filial_id=f.id
                ORDER BY fm.data_vencimento ASC
            """).fetchall()
        return [dict(r) for r in rows]

def criar_fiscal_municipal(tipo, descricao, valor, data_vencimento, observacao="", filial_id=1):
    with db_session() as conn:
        c = conn.execute("""
            INSERT INTO fiscal_municipal (tipo, descricao, valor, data_vencimento, observacao, filial_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pendente')
        """, (tipo, descricao, valor, data_vencimento, observacao, filial_id))
        return c.lastrowid

def pagar_fiscal_municipal(id, valor_pago, data_pagamento, observacao=""):
    with db_session() as conn:
        item = conn.execute("SELECT tipo, valor, valor_pago FROM fiscal_municipal WHERE id=?", (id,)).fetchone()
        if not item:
            return False
        total_pago = float(item["valor_pago"]) + float(valor_pago)
        novo_status = "pago" if total_pago >= float(item["valor"]) else "parcial"
        obs = f"{observacao}" if observacao else ""
        conn.execute("""
            UPDATE fiscal_municipal
            SET valor_pago=?, status=?, data_pagamento=?, observacao=CASE WHEN ?!='' THEN ? ELSE observacao END
            WHERE id=?
        """, (total_pago, novo_status, data_pagamento, obs, obs, id))
    from services.financeiro_service import registrar_movimento_financeiro
    registrar_movimento_financeiro(
        tipo="saida",
        categoria="fiscal_municipal",
        descricao=f"Pagamento: {item['tipo']}",
        valor=float(valor_pago),
        forma_pagamento="dinheiro",
        banco_id=None
    )
    return True

def excluir_fiscal_municipal(id):
    with db_session() as conn:
        conn.execute("DELETE FROM fiscal_municipal WHERE id=?", (id,))
    return True

def obter_resumo_fiscal_municipal():
    with db_connection() as conn:
        pendente = conn.execute("""
            SELECT COALESCE(COUNT(*),0) as total, COALESCE(SUM(valor - valor_pago),0) as saldo
            FROM fiscal_municipal WHERE status IN ('pendente','parcial')
        """).fetchone()
        vencido = conn.execute("""
            SELECT COALESCE(COUNT(*),0) as total, COALESCE(SUM(valor - valor_pago),0) as saldo
            FROM fiscal_municipal
            WHERE status IN ('pendente','parcial') AND data_vencimento < date('now')
        """).fetchone()
        pago_mes = conn.execute("""
            SELECT COALESCE(SUM(valor_pago),0) as total
            FROM fiscal_municipal
            WHERE status='pago' AND strftime('%Y-%m',data_pagamento)=strftime('%Y-%m','now')
        """).fetchone()
        return {
            "pendentes": int(pendente["total"]),
            "saldo_pendente": float(pendente["saldo"]),
            "vencidos": int(vencido["total"]),
            "saldo_vencido": float(vencido["saldo"]),
            "pago_mes": float(pago_mes["total"]),
        }
