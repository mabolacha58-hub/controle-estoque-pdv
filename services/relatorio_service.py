from datetime import datetime, timedelta
from services.base import db_connection
from database import moeda

def resumo_diario(data):
    with db_connection() as conn:
        saidas = conn.execute("""
            SELECT COALESCE(SUM(quantidade*preco_unitario),0) FROM movimentacoes
            WHERE tipo='saida' AND date(data)=?""",(data,)).fetchone()[0]
        entradas = conn.execute("""
            SELECT COALESCE(SUM(quantidade*preco_unitario),0) FROM movimentacoes
            WHERE tipo='entrada' AND date(data)=?""",(data,)).fetchone()[0]
        return {'vendas_hoje': float(saidas), 'compras_hoje': float(entradas)}

def vendas_por_periodo(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT date(data) d, COALESCE(SUM(quantidade*preco_unitario),0) total, COUNT(*) qtd
            FROM movimentacoes WHERE tipo='saida' AND data >= date('now',?||' days')
            GROUP BY d ORDER BY d""",(f'-{dias}',)).fetchall()
    row_map = {r[0]: r for r in rows}
    dados = []
    for i in range(dias-1, -1, -1):
        d = (datetime.now()-timedelta(days=i)).strftime('%Y-%m-%d')
        r = row_map.get(d)
        dados.append({'data': d, 'total': float(r[1]) if r else 0, 'qtd': r[2] if r else 0})
    return dados

def lucro_por_periodo(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT date(m.data) d,
                   COALESCE(SUM(CASE WHEN m.tipo='saida' THEN m.quantidade*m.preco_unitario ELSE 0 END),0) receita,
                   COALESCE(SUM(CASE WHEN m.tipo='saida' THEN m.quantidade*p.preco_custo ELSE 0 END),0) custo
            FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
            WHERE m.data >= date('now',?||' days')
            GROUP BY d ORDER BY d""",(f'-{dias}',)).fetchall()
    row_map = {r[0]: r for r in rows}
    dados = []
    for i in range(dias-1, -1, -1):
        d = (datetime.now()-timedelta(days=i)).strftime('%Y-%m-%d')
        r = row_map.get(d)
        receita = float(r[1]) if r else 0
        custo = float(r[2]) if r else 0
        dados.append({'data': d, 'receita': receita, 'custo': custo, 'lucro': receita-custo})
    return dados

def vendas_por_categoria(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT COALESCE(c.nome,'Sem categoria'),
                   SUM(m.quantidade*m.preco_unitario),
                   SUM(m.quantidade)
            FROM movimentacoes m
            JOIN produtos p ON p.id=m.produto_id
            LEFT JOIN categorias c ON c.id=p.categoria_id
            WHERE m.tipo='saida' AND m.data >= date('now',?||' days')
            GROUP BY c.nome ORDER BY SUM(m.quantidade*m.preco_unitario) DESC
        """,(f'-{dias}',)).fetchall()
    return [{'categoria': r[0], 'total': float(r[1] or 0), 'qtd': float(r[2] or 0)} for r in rows]

def dados_pdf_vendas(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT p.nome, SUM(m.quantidade), SUM(m.quantidade*m.preco_unitario)
            FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
            WHERE m.tipo='saida' AND m.data >= date('now',?||' days')
            GROUP BY m.produto_id ORDER BY SUM(m.quantidade*m.preco_unitario) DESC
        """,(f'-{dias}',)).fetchall()
    headers = ['Produto', 'Quantidade', 'Total']
    data = [[r[0], moeda(float(r[1])), moeda(float(r[2]))] for r in rows if r[1] > 0]
    return headers, data

def dados_pdf_stock():
    with db_connection() as conn:
        rows = conn.execute("SELECT nome, quantidade, quantidade_minima, preco_venda FROM produtos ORDER BY quantidade ASC").fetchall()
    headers = ['Produto', 'Stock', 'Mínimo', 'Preço Venda']
    data = [[r[0], moeda(float(r[1])), moeda(float(r[2])), moeda(float(r[3]))] for r in rows]
    return headers, data

def dados_pdf_produtos():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT p.nome, c.nome, p.quantidade, p.preco_venda, p.preco_custo
            FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id
            ORDER BY p.nome
        """).fetchall()
    headers = ['Produto', 'Categoria', 'Stock', 'Preço Venda', 'Preço Custo']
    data = [[r[0], r[1] or '-', moeda(float(r[2])), moeda(float(r[3])), moeda(float(r[4]))] for r in rows]
    return headers, data

def dados_pdf_movimentacoes(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT m.tipo, p.nome, m.quantidade, m.preco_unitario, m.data
            FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
            WHERE m.data >= date('now',?||' days')
            ORDER BY m.data DESC
        """,(f'-{dias}',)).fetchall()
    headers = ['Tipo', 'Produto', 'Qtd', 'Preço Unit.', 'Data']
    data = [[r[0], r[1], moeda(float(r[2])), moeda(float(r[3])), r[4]] for r in rows]
    return headers, data

def dados_pdf_lucro(dias):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT date(m.data),
                   SUM(CASE WHEN m.tipo='saida' THEN m.quantidade*m.preco_unitario ELSE 0 END),
                   SUM(CASE WHEN m.tipo='saida' THEN m.quantidade*p.preco_custo ELSE 0 END)
            FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
            WHERE m.data >= date('now',?||' days')
            GROUP BY date(m.data) ORDER BY date(m.data) DESC
        """,(f'-{dias}',)).fetchall()
    headers = ['Data', 'Receita', 'Custo', 'Lucro']
    data = []
    for r in rows:
        rec = float(r[1] or 0); cst = float(r[2] or 0)
        data.append([r[0], moeda(rec), moeda(cst), moeda(rec-cst)])
    data.append(['TOTAL', moeda(sum(float(r[1] or 0) for r in rows)),
        moeda(sum(float(r[2] or 0) for r in rows)),
        moeda(sum(float(r[1] or 0) for r in rows)-sum(float(r[2] or 0) for r in rows))])
    return headers, data

def dados_pdf_clientes():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT nome,nif,telefone,printf('%.2f',saldo),printf('%.2f',limite_credito)
            FROM clientes ORDER BY nome
        """).fetchall()
    headers = ['Nome', 'NIF', 'Telefone', 'Saldo', 'Limite Crédito']
    data = [[r[0], r[1] or '-', r[2] or '-', moeda(float(r[3] or 0)), moeda(float(r[4] or 0))] for r in rows]
    return headers, data

def dados_pdf_categorias():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT COALESCE(c.nome,'Sem categoria'),
                   COUNT(p.id), SUM(p.quantidade),
                   SUM(p.quantidade*p.preco_venda)
            FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id
            GROUP BY c.nome ORDER BY SUM(p.quantidade*p.preco_venda) DESC
        """).fetchall()
    headers = ['Categoria', 'Produtos', 'Stock Total', 'Valor Total']
    data = [[r[0], str(r[1]), moeda(float(r[2] or 0)), moeda(float(r[3] or 0))] for r in rows]
    return headers, data

PDF_FUNCTIONS = {
    'vendas': dados_pdf_vendas,
    'stock': dados_pdf_stock,
    'produtos': dados_pdf_produtos,
    'movimentacoes': dados_pdf_movimentacoes,
    'lucro': dados_pdf_lucro,
    'clientes': dados_pdf_clientes,
    'categoria': dados_pdf_categorias,
}
