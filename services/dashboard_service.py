from datetime import datetime, timedelta
from services.base import db_connection

def obter_metricas():
    with db_connection() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as tp, 
                   (SELECT COUNT(*) FROM categorias) as tc,
                   (SELECT COUNT(*) FROM movimentacoes) as tm,
                   SUM(quantidade*preco_venda) as vt
            FROM produtos
        """).fetchone()
        return {
            'total_prod': row[0] or 0,
            'total_cat': row[1] or 0,
            'total_mov': row[2] or 0,
            'valor_total': float(row[3]) if row[3] else 0
        }

def obter_produtos_top(limite=5):
    with db_connection() as conn:
        rows = conn.execute("SELECT nome,preco_venda FROM produtos ORDER BY quantidade*preco_venda DESC LIMIT ?",(limite,)).fetchall()
        return [list(r) for r in rows]

def obter_movimentos_recentes(limite=8):
    with db_connection() as conn:
        return conn.execute("""
            SELECT m.id,m.data,p.nome,m.tipo,printf('%.2f',m.quantidade)||' '||p.unidade,
                   printf('%.2f',m.preco_unitario),IFNULL(m.documento,'-')
            FROM movimentacoes m JOIN produtos p ON m.produto_id=p.id
            ORDER BY m.data DESC LIMIT ?""",(limite,)).fetchall()

def obter_movimentos_diarios_30dias():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT date(data) d,
                   COALESCE(SUM(CASE WHEN tipo='entrada' THEN quantidade*preco_unitario ELSE 0 END),0) entrada,
                   COALESCE(SUM(CASE WHEN tipo='saida' THEN quantidade*preco_unitario ELSE 0 END),0) saida
            FROM movimentacoes WHERE data >= date('now','-29 days')
            GROUP BY d ORDER BY d""").fetchall()
    row_map = {r[0]: r for r in rows}
    dias = []
    for i in range(29, -1, -1):
        d = (datetime.now()-timedelta(days=i)).strftime('%Y-%m-%d')
        r = row_map.get(d)
        dias.append({'data': d[-5:], 'entrada': float(r[1]) if r else 0, 'saida': float(r[2]) if r else 0})
    return dias

def obter_produtos_baixo_stock(limite=10):
    with db_connection() as conn:
        return conn.execute("""
            SELECT nome,quantidade,quantidade_minima FROM produtos
            WHERE quantidade_minima>0 AND quantidade<=quantidade_minima
            ORDER BY quantidade ASC LIMIT ?""",(limite,)).fetchall()

def obter_vendas_hoje():
    with db_connection() as conn:
        row = conn.execute("""
            SELECT COALESCE(SUM(quantidade*preco_unitario),0) FROM movimentacoes
            WHERE tipo='saida' AND date(data)=date('now','localtime')
        """).fetchone()
        return float(row[0]) if row else 0

def obter_media_vendas_7dias():
    with db_connection() as conn:
        row = conn.execute("""
            SELECT COALESCE(AVG(diario),0) FROM (
                SELECT SUM(quantidade*preco_unitario) diario FROM movimentacoes
                WHERE tipo='saida' AND data >= date('now','-7 days','localtime') AND data < date('now','localtime')
                GROUP BY date(data)
            )
        """).fetchone()
        return float(row[0]) if row else 0

def obter_lista_produtos_completa():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT p.nome,p.quantidade,p.preco_custo,p.preco_venda,IFNULL(c.nome,'-') categoria
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id
            ORDER BY p.nome""").fetchall()
        return [dict(r) for r in rows]
