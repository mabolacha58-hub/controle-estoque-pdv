from services.base import db_connection, db_session
from utils.validation import validar

CATEGORIA_SCHEMA = {
    'nome': {'required': True, 'maxlen': 100},
    'descricao': {'default': '', 'maxlen': 200},
}

def listar_categorias():
    with db_connection() as conn:
        rows = conn.execute("""
            SELECT c.id,c.nome,IFNULL(c.descricao,'-') descricao,
                   (SELECT COUNT(*) FROM produtos WHERE categoria_id=c.id) qtd
            FROM categorias c ORDER BY c.nome""").fetchall()
        return [dict(r) for r in rows]

def criar_categoria(dados):
    erros = validar(dados, CATEGORIA_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("INSERT INTO categorias (nome,descricao) VALUES (?,?)",
                     (dados['nome'],dados.get('descricao','')))
        return {'ok': True}

def deletar_categoria(id):
    with db_session() as conn:
        if conn.execute("SELECT COUNT(*) FROM produtos WHERE categoria_id=?",(id,)).fetchone()[0]:
            return {'ok': False, 'erro': 'Categoria com produtos'}
        conn.execute("DELETE FROM categorias WHERE id=?",(id,))
        return {'ok': True}
