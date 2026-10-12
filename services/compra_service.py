from services.base import db_session, db_connection
from services.empresa_service import criar_lote, atualizar_stock_filial

def listar_compras(status=None, filial_id=1):
    with db_connection() as conn:
        sql = '''SELECT c.*, f.nome as fornecedor
                 FROM compras c LEFT JOIN fornecedores f ON c.fornecedor_id=f.id
                 WHERE c.filial_id=?'''
        params = [filial_id]
        if status:
            sql += " AND c.status=?"
            params.append(status)
        sql += " ORDER BY c.data_pedido DESC"
        r = conn.execute(sql, params).fetchall()
        return [dict(row) for row in r]

def criar_compra(fornecedor_id, itens, observacao="", filial_id=1):
    with db_session() as conn:
        total = sum(i.get("total", i["quantidade"] * i["preco_unitario"]) for i in itens)
        c = conn.execute('''INSERT INTO compras (fornecedor_id,filial_id,total,observacao,status)
                          VALUES (?,?,?,?,'pendente')''',
                       (fornecedor_id, filial_id, total, observacao))
        compra_id = c.lastrowid
        for item in itens:
            total_item = item.get("total", item["quantidade"] * item["preco_unitario"])
            conn.execute('''INSERT INTO compra_itens (compra_id,produto_id,quantidade,preco_unitario,iva,total)
                          VALUES (?,?,?,?,?,?)''',
                       (compra_id, item["produto_id"], item["quantidade"],
                        item["preco_unitario"], item.get("iva", 0), total_item))
        return compra_id

def receber_compra(id):
    with db_session() as conn:
        compra = conn.execute("SELECT * FROM compras WHERE id=?", (id,)).fetchone()
        if not compra or compra["status"] != "pendente":
            return False
        itens = conn.execute("SELECT * FROM compra_itens WHERE compra_id=?", (id,)).fetchall()
        for item in itens:
            qtd_receber = item["quantidade"] - item["quantidade_recebida"]
            if qtd_receber <= 0:
                continue
            atualizar_stock_filial(item["produto_id"], compra["filial_id"], qtd_receber)
            conn.execute("UPDATE compra_itens SET quantidade_recebida=quantidade WHERE compra_id=? AND produto_id=?",
                       (id, item["produto_id"]))
            if item.get("codigo_lote"):
                criar_lote(item["produto_id"], item["codigo_lote"], qtd_receber,
                           item.get("data_validade", ""), item["preco_unitario"], compra["filial_id"])
        conn.execute('''UPDATE compras SET status='recebido', data_rececao=datetime('now','localtime')
                      WHERE id=?''', (id,))
        return True

def cancelar_compra(id):
    with db_session() as conn:
        conn.execute("UPDATE compras SET status='cancelada' WHERE id=? AND status='pendente'", (id,))

def atualizar_compra(id, fornecedor_id, itens, observacao=""):
    with db_session() as conn:
        total = sum(i.get("total", i["quantidade"] * i["preco_unitario"]) for i in itens)
        conn.execute("UPDATE compras SET fornecedor_id=?, total=?, observacao=? WHERE id=? AND status='pendente'",
                   (fornecedor_id, total, observacao, id))
        conn.execute("DELETE FROM compra_itens WHERE compra_id=?", (id,))
        for item in itens:
            total_item = item.get("total", item["quantidade"] * item["preco_unitario"])
            conn.execute('''INSERT INTO compra_itens (compra_id,produto_id,quantidade,preco_unitario,iva,total)
                          VALUES (?,?,?,?,?,?)''',
                       (id, item["produto_id"], item["quantidade"],
                        item["preco_unitario"], item.get("iva", 0), total_item))
        return id

def obter_compra(id):
    with db_connection() as conn:
        compra = conn.execute('''SELECT c.*, f.nome as fornecedor, f.nif as fornecedor_nif
                               FROM compras c LEFT JOIN fornecedores f ON c.fornecedor_id=f.id
                               WHERE c.id=?''', (id,)).fetchone()
        if not compra:
            return None
        itens = conn.execute('''SELECT ci.*, p.nome as produto_nome, p.codigo_barras
                               FROM compra_itens ci JOIN produtos p ON ci.produto_id=p.id
                               WHERE ci.compra_id=?''', (id,)).fetchall()
        return dict(compra), [dict(i) for i in itens]
