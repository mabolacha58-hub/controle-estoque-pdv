from services.base import db_connection, db_session
from utils.validation import validar

MOVIMENTO_SCHEMA = {
    'produto_id': {'required': True, 'coerce': int, 'min': 1},
    'tipo': {'required': True, 'choices': ['entrada', 'saida']},
    'quantidade': {'required': True, 'coerce': float, 'min': 0.01},
    'preco': {'coerce': float, 'default': 0, 'min': 0},
    'documento': {'default': '', 'maxlen': 100},
    'observacao': {'default': '', 'maxlen': 500},
}

def listar_movimentacoes(pagina=None, limite=None, busca=None):
    with db_connection() as conn:
        base_sql = """FROM movimentacoes m JOIN produtos p ON m.produto_id=p.id"""
        params = []
        if busca:
            busca_sql = " WHERE (p.nome LIKE ? OR IFNULL(m.documento,'') LIKE ? OR IFNULL(m.observacao,'') LIKE ?)"
            params = [f'%{busca}%'] * 3
            base_sql += busca_sql

        if pagina and limite:
            offset = (pagina - 1) * limite
            total = conn.execute(f"SELECT COUNT(*) {base_sql}", params).fetchone()[0]
            rows = conn.execute(f"""
                SELECT m.id,m.data,p.nome,m.tipo,
                       printf('%.2f',m.quantidade) qtd,printf('%.2f',m.preco_unitario) preco,
                       IFNULL(m.documento,'-') doc,IFNULL(m.observacao,'-') obs,
                       IFNULL(m.desconto,0) desconto
                {base_sql} ORDER BY m.data DESC LIMIT ? OFFSET ?""",
                params + [limite, offset]).fetchall()
            return {
                'dados': [dict(r) for r in rows],
                'total': total,
                'pagina': pagina,
                'limite': limite,
                'total_paginas': max(1, (total + limite - 1) // limite)
            }
        rows = conn.execute(f"""
            SELECT m.id,m.data,p.nome,m.tipo,
                   printf('%.2f',m.quantidade) qtd,printf('%.2f',m.preco_unitario) preco,
                   IFNULL(m.documento,'-') doc,IFNULL(m.observacao,'-') obs,
                   IFNULL(m.desconto,0) desconto
            {base_sql} ORDER BY m.data DESC""", params).fetchall()
        return [dict(r) for r in rows]

def criar_movimentacao(dados):
    erros = validar(dados, MOVIMENTO_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        delta = dados['quantidade'] if dados['tipo']=='entrada' else -dados['quantidade']
        if dados['tipo'] == 'saida':
            atual = conn.execute("SELECT quantidade FROM produtos WHERE id=?", (dados['produto_id'],)).fetchone()
            if not atual or atual[0] < dados['quantidade']:
                return {'ok': False, 'erros': ['Estoque insuficiente']}
        conn.execute("UPDATE produtos SET quantidade=quantidade+? WHERE id=? AND (quantidade+?)>=0",(delta,dados['produto_id'],delta))
        conn.execute("""INSERT INTO movimentacoes (produto_id,tipo,quantidade,preco_unitario,documento,observacao)
            VALUES (?,?,?,?,?,?)""",(dados['produto_id'],dados['tipo'],dados['quantidade'],
            dados.get('preco',0),dados.get('documento',''),dados.get('observacao','')))
        return {'ok': True}

def deletar_movimentacao(id):
    with db_session() as conn:
        row = conn.execute("SELECT produto_id,tipo,quantidade,preco_unitario,cliente_id FROM movimentacoes WHERE id=?",(id,)).fetchone()
        if not row:
            return {'ok': False, 'erro': 'Não encontrada'}
        delta = -row[2] if row[1]=='entrada' else row[2]
        conn.execute("UPDATE produtos SET quantidade=quantidade+? WHERE id=?",(delta,row[0]))
        if row[4]:
            conn.execute("UPDATE clientes SET saldo=saldo-? WHERE id=?",(row[2]*row[3],row[4]))
        conn.execute("DELETE FROM movimentacoes WHERE id=?",(id,))
        return {'ok': True}
