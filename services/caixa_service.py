from datetime import datetime
from services.base import db_connection, db_session

def listar_caixas(limite=20):
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT cx.id,cx.abertura,cx.fecho,cx.saldo_inicial,cx.saldo_final,cx.status,
                   IFNULL(u.nome,'-') operador
            FROM caixa cx LEFT JOIN utilizadores u ON cx.utilizador_id=u.id
            ORDER BY cx.id DESC LIMIT ?""",(limite,)).fetchall()
        return [dict(r) for r in rows]

def obter_status_caixa():
    with db_connection() as conn:
        cx = conn.execute("""
            SELECT cx.id,cx.abertura,u.nome operador
            FROM caixa cx JOIN utilizadores u ON cx.utilizador_id=u.id
            WHERE cx.status='aberto' ORDER BY cx.id DESC LIMIT 1""").fetchone()
        if cx:
            hoje = datetime.now().strftime('%Y-%m-%d')
            vendas = conn.execute("""
                SELECT COALESCE(SUM(quantidade*preco_unitario),0)
                FROM movimentacoes WHERE tipo='saida' AND date(data)=?
                AND documento='PDV'""",(hoje,)).fetchone()[0]
            return {'aberto': True, 'caixa_id': cx[0], 'abertura': cx[1],
                    'operador': cx[2], 'vendas_hoje': float(vendas)}
        return {'aberto': False}

def abrir_caixa(utilizador_id, saldo_inicial=0):
    with db_session() as conn:
        aberto = conn.execute("SELECT id FROM caixa WHERE status='aberto'").fetchone()
        if aberto:
            return {'ok': False, 'erro': 'Caixa já está aberto'}
        conn.execute("""INSERT INTO caixa (utilizador_id,saldo_inicial,status)
            VALUES (?,?,'aberto')""",(utilizador_id, saldo_inicial))
        return {'ok': True}

def fechar_caixa(saldo_final, diferenca=0):
    with db_session() as conn:
        cx = conn.execute("SELECT id,saldo_inicial FROM caixa WHERE status='aberto' ORDER BY id DESC LIMIT 1").fetchone()
        if not cx:
            return {'ok': False, 'erro': 'Nenhum caixa aberto'}
        hoje = datetime.now().strftime('%Y-%m-%d')
        vendas = conn.execute("""
            SELECT COALESCE(SUM(quantidade*preco_unitario),0)
            FROM movimentacoes WHERE tipo='saida' AND date(data)=? AND documento='PDV'""",(hoje,)).fetchone()[0]
        total = float(cx[1]) + float(vendas) + float(diferenca)
        conn.execute("""UPDATE caixa SET fecho=datetime('now','localtime'),saldo_final=?,status='fechado'
            WHERE id=?""",(total, cx[0]))
        return {'ok': True, 'saldo_final': total, 'vendas_hoje': float(vendas)}
