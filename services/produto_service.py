import os
from services.base import db_connection, db_session
from utils.validation import validar

PRODUTO_SCHEMA = {
    'nome': {'required': True, 'maxlen': 200},
    'codigo': {'default': ''},
    'descricao': {'default': '', 'maxlen': 500},
    'categoria_id': {'coerce': int, 'default': None},
    'quantidade': {'coerce': float, 'default': 0, 'min': 0},
    'quantidade_minima': {'coerce': float, 'default': 0, 'min': 0},
    'preco_custo': {'coerce': float, 'default': 0, 'min': 0},
    'preco_venda': {'coerce': float, 'default': 0, 'min': 0},
    'iva': {'coerce': float, 'default': 0, 'min': 0, 'max': 100},
    'unidade': {'default': 'UN', 'maxlen': 20},
    'foto': {'default': None},
}

def listar_produtos(pagina=None, limite=None):
    with db_connection() as conn:
        if pagina and limite:
            offset = (pagina - 1) * limite
            total = conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
            rows = conn.execute("""
                SELECT p.id,p.nome,IFNULL(p.codigo_barras,'-') codigo_barras,
                       IFNULL(p.codigo_barras,'-') codigo,
                       IFNULL(c.nome,'-') categoria_nome,p.quantidade,p.quantidade_minima,
                       p.preco_custo,p.preco_venda,p.iva,p.unidade,p.foto,
                       p.categoria_id, IFNULL(c.nome,'-') categoria
                FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id
                ORDER BY p.nome LIMIT ? OFFSET ?""", (limite, offset)).fetchall()
            return {
                'dados': [dict(r) for r in rows],
                'total': total,
                'pagina': pagina,
                'limite': limite,
                'total_paginas': max(1, (total + limite - 1) // limite)
            }
        rows = conn.execute("""
            SELECT p.id,p.nome,IFNULL(p.codigo_barras,'-') codigo_barras,
                   IFNULL(p.codigo_barras,'-') codigo,
                   IFNULL(c.nome,'-') categoria_nome,p.quantidade,p.quantidade_minima,
                   p.preco_custo,p.preco_venda,p.iva,p.unidade,p.foto,
                   p.categoria_id, IFNULL(c.nome,'-') categoria
            FROM produtos p LEFT JOIN categorias c ON p.categoria_id=c.id
            ORDER BY p.nome""").fetchall()
        return [dict(r) for r in rows]

def criar_produto(dados):
    erros = validar(dados, PRODUTO_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        cod = dados.get('codigo','').strip() or None
        conn.execute("""INSERT INTO produtos (nome,codigo_barras,descricao,categoria_id,quantidade,
            quantidade_minima,preco_custo,preco_venda,iva,unidade,foto) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (dados['nome'],cod,dados.get('descricao',''),
             dados.get('categoria_id'),dados.get('quantidade',0),dados.get('quantidade_minima',0),
             dados.get('preco_custo',0),dados.get('preco_venda',0),dados.get('iva',0),
             dados.get('unidade','UN'),dados.get('foto')))
        return {'ok': True}

def atualizar_produto(id, dados):
    erros = validar(dados, {k: v for k, v in PRODUTO_SCHEMA.items() if k not in ('codigo', 'foto') or k in dados})
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        cod = dados.get('codigo','').strip() or None
        conn.execute("""UPDATE produtos SET nome=?,codigo_barras=?,descricao=?,categoria_id=?,
            quantidade_minima=?,preco_custo=?,preco_venda=?,iva=?,unidade=?,foto=? WHERE id=?""",
            (dados['nome'],cod,dados.get('descricao',''),
             dados.get('categoria_id'),dados.get('quantidade_minima',0),
             dados.get('preco_custo',0),dados.get('preco_venda',0),dados.get('iva',0),
             dados.get('unidade','UN'),dados.get('foto'),id))
        return {'ok': True}

def deletar_produto(id):
    with db_session() as conn:
        if conn.execute("SELECT COUNT(*) FROM movimentacoes WHERE produto_id=?",(id,)).fetchone()[0]:
            return {'ok': False, 'erro': 'Produto com movimentações'}
        foto = conn.execute("SELECT foto FROM produtos WHERE id=?",(id,)).fetchone()
        conn.execute("DELETE FROM produtos WHERE id=?",(id,))
        if foto and foto[0]:
            try: os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', foto[0]))
            except Exception: pass
        return {'ok': True}
