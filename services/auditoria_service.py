from services.base import db_connection, db_session
from flask import session, request

def registrar(acao, entidade=None, entidade_id=None, detalhes=None):
    with db_session() as conn:
        utilizador_id = session.get("user_id")
        utilizador_nome = session.get("user_nome", "Desconhecido")
        ip = request.remote_addr or "desconhecido"
        conn.execute('''INSERT INTO auditoria (utilizador_id, utilizador_nome, acao, entidade, entidade_id, detalhes, ip)
                      VALUES (?,?,?,?,?,?,?)''',
                   (utilizador_id, utilizador_nome, acao, entidade, entidade_id, detalhes, ip))

def listar(limite=200, entidade=None, utilizador_id=None):
    with db_connection() as conn:
        sql = "SELECT * FROM auditoria"
        params = []
        wheres = []
        if entidade:
            wheres.append("entidade=?")
            params.append(entidade)
        if utilizador_id:
            wheres.append("utilizador_id=?")
            params.append(utilizador_id)
        if wheres:
            sql += " WHERE " + " AND ".join(wheres)
        sql += " ORDER BY data DESC LIMIT ?"
        params.append(limite)
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

def listar_resumo_por_data(dias=30):
    with db_connection() as conn:
        rows = conn.execute('''SELECT date(data) as dia, COUNT(*) as total,
                             SUM(CASE WHEN acao LIKE 'criar%' THEN 1 ELSE 0 END) as criacoes,
                             SUM(CASE WHEN acao LIKE 'atualizar%' THEN 1 ELSE 0 END) as atualizacoes,
                             SUM(CASE WHEN acao LIKE 'excluir%' THEN 1 ELSE 0 END) as exclusoes
                      FROM auditoria
                      WHERE data >= date('now',?||' days')
                      GROUP BY date(data) ORDER BY dia''', (f'-{dias}',)).fetchall()
        return [dict(row) for row in rows]

def resumo_hoje():
    with db_connection() as conn:
        r = conn.execute("SELECT COUNT(*) total FROM auditoria WHERE date(data)=date('now','localtime')").fetchone()
        return r[0] if r else 0
