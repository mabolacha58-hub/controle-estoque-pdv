from services.base import db_connection, db_session
from utils.validation import validar

CLIENTE_SCHEMA = {
    'nome': {'required': True, 'maxlen': 200},
    'nif': {'default': '', 'maxlen': 20, 'pattern': r'^\d*$'},
    'telefone': {'default': '', 'maxlen': 20},
    'email': {'default': '', 'maxlen': 100},
    'morada': {'default': '', 'maxlen': 300},
    'limite_credito': {'coerce': float, 'default': 0, 'min': 0},
}

def listar_clientes():
    with db_connection() as conn:
        rows = conn.execute("""SELECT id,nome,nif,telefone,email,morada,
            printf('%.2f',saldo) saldo,printf('%.2f',limite_credito) limite_credito,data_cadastro
            FROM clientes ORDER BY nome""").fetchall()
        return [dict(r) for r in rows]

def criar_cliente(dados):
    erros = validar(dados, CLIENTE_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("""INSERT INTO clientes (nome,nif,telefone,email,morada,limite_credito)
            VALUES (?,?,?,?,?,?)""",(dados['nome'],dados.get('nif',''),dados.get('telefone',''),
            dados.get('email',''),dados.get('morada',''),dados.get('limite_credito',0)))
        return {'ok': True}

def atualizar_cliente(id, dados):
    erros = validar(dados, CLIENTE_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("""UPDATE clientes SET nome=?,nif=?,telefone=?,email=?,morada=?,limite_credito=?
            WHERE id=?""",(dados['nome'],dados.get('nif',''),dados.get('telefone',''),
            dados.get('email',''),dados.get('morada',''),dados.get('limite_credito',0),id))
        return {'ok': True}

def deletar_cliente(id):
    with db_session() as conn:
        conn.execute("DELETE FROM clientes WHERE id=?",(id,))
        return {'ok': True}
