from services.base import db_connection

def obter_kpis():
    with db_connection() as conn:
        result = {}

        r = conn.execute("SELECT COALESCE(SUM(saldo),0) FROM contas_pagar WHERE status IN ('pendente','parcial')").fetchone()
        result["contas_pagar"] = float(r[0])

        r = conn.execute("SELECT COALESCE(SUM(saldo),0) FROM contas_receber WHERE status IN ('pendente','parcial')").fetchone()
        result["contas_receber"] = float(r[0])

        r = conn.execute("SELECT COALESCE(SUM(saldo),0) FROM bancos").fetchone()
        result["saldo_bancos"] = float(r[0])

        r = conn.execute("SELECT COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END),0) - COALESCE(SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END),0) FROM movimentos_financeiros WHERE strftime('%Y-%m',data_movimento)=strftime('%Y-%m','now')").fetchone()
        result["fluxo_mes"] = float(r[0])

        r = conn.execute("SELECT COALESCE(COUNT(*),0) FROM contas_pagar WHERE status IN ('pendente','parcial') AND data_vencimento < date('now')").fetchone()
        result["contas_vencidas"] = int(r[0])

        r = conn.execute("SELECT COALESCE(COUNT(*),0) FROM filiais WHERE ativo=1").fetchone()
        result["total_filiais"] = int(r[0])

        return result

def obter_kpis_vendas():
    with db_connection() as conn:
        result = {}

        r = conn.execute("""
            SELECT COALESCE(SUM(m.quantidade * m.preco_unitario),0)
            FROM movimentacoes m
            WHERE m.tipo='saida' AND strftime('%Y-%m',m.data)=strftime('%Y-%m','now')
        """).fetchone()
        result["vendas_mes"] = float(r[0])

        r = conn.execute("SELECT COALESCE(COUNT(*),0) FROM produtos").fetchone()
        result["total_produtos"] = int(r[0])

        r = conn.execute("""
            SELECT COALESCE(COUNT(*),0) FROM produtos
            WHERE quantidade <= quantidade_minima AND quantidade_minima > 0
        """).fetchone()
        result["produtos_stock_baixo"] = int(r[0])

        r = conn.execute("""
            SELECT COALESCE(COUNT(*),0) FROM movimentacoes
            WHERE tipo='saida' AND strftime('%Y-%m',data)=strftime('%Y-%m','now')
        """).fetchone()
        total_vendas = int(r[0])
        result["total_vendas_mes"] = total_vendas
        result["ticket_medio"] = float(result["vendas_mes"] / total_vendas) if total_vendas > 0 else 0

        return result

def obter_vendas_mensais(meses=6):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m',data) mes,
                   SUM(quantidade * preco_unitario) total,
                   COUNT(*) total_vendas
            FROM movimentacoes
            WHERE tipo='saida' AND data >= date('now',?||' months')
            GROUP BY mes ORDER BY mes
        """, (f'-{meses}',)).fetchall()
        return [dict(r) for r in rows]

def obter_produtos_stock_critico(limite=10):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT p.id, p.nome, p.quantidade, p.quantidade_minima,
                   p.preco_venda, c.nome as categoria
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id=c.id
            WHERE p.quantidade <= p.quantidade_minima AND p.quantidade_minima > 0
            ORDER BY (p.quantidade - p.quantidade_minima) ASC
            LIMIT ?
        """, (limite,)).fetchall()
        return [dict(r) for r in rows]

def obter_receita_despesa_mensal(meses=6):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m',data_movimento) mes,
                   SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END) entradas,
                   SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END) saidas
            FROM movimentos_financeiros
            WHERE data_movimento >= date('now',?||' months')
            GROUP BY mes ORDER BY mes
        """, (f'-{meses}',)).fetchall()
        return [dict(r) for r in rows]

def obter_top_clientes_fidelidade(limite=5):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT c.nome, f.pontos, f.nivel, f.total_compras
            FROM fidelizacao f JOIN clientes c ON f.cliente_id=c.id
            ORDER BY f.pontos DESC LIMIT ?
        """, (limite,)).fetchall()
        return [dict(r) for r in rows]

def obter_comparativo_filiais():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT f.nome,
                   (SELECT COUNT(*) FROM movimentos_financeiros mf WHERE mf.filial_id=f.id) total_movimentos,
                   (SELECT COALESCE(SUM(CASE WHEN mf2.tipo='entrada' THEN mf2.valor ELSE 0 END),0) FROM movimentos_financeiros mf2 WHERE mf2.filial_id=f.id AND strftime('%Y-%m',mf2.data_movimento)=strftime('%Y-%m','now')) entradas_mes,
                   (SELECT COALESCE(SUM(CASE WHEN mf3.tipo='saida' THEN mf3.valor ELSE 0 END),0) FROM movimentos_financeiros mf3 WHERE mf3.filial_id=f.id AND strftime('%Y-%m',mf3.data_movimento)=strftime('%Y-%m','now')) saidas_mes
            FROM filiais f WHERE f.ativo=1
            ORDER BY f.nome
        """).fetchall()
        return [dict(r) for r in rows]
