from services.base import db_connection, db_session
from utils.validation import validar

FORNECEDOR_SCHEMA = {
    'nome': {'required': True, 'maxlen': 200},
    'nif': {'default': '', 'maxlen': 20, 'pattern': r'^\d*$'},
    'telefone': {'default': '', 'maxlen': 20},
    'email': {'default': '', 'maxlen': 100},
    'morada': {'default': '', 'maxlen': 300},
    'contato': {'default': '', 'maxlen': 100},
}

def listar_fornecedores():
    with db_connection() as conn:
        rows = conn.execute("SELECT * FROM fornecedores ORDER BY nome").fetchall()
        return [dict(r) for r in rows]

def criar_fornecedor(dados):
    erros = validar(dados, FORNECEDOR_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("""INSERT INTO fornecedores (nome,nif,telefone,email,morada,contato)
            VALUES (?,?,?,?,?,?)""",(dados['nome'],dados.get('nif',''),dados.get('telefone',''),
            dados.get('email',''),dados.get('morada',''),dados.get('contato','')))
        return {'ok': True}

def atualizar_fornecedor(id, dados):
    erros = validar(dados, FORNECEDOR_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("""UPDATE fornecedores SET nome=?,nif=?,telefone=?,email=?,morada=?,contato=?
            WHERE id=?""",(dados['nome'],dados.get('nif',''),dados.get('telefone',''),
            dados.get('email',''),dados.get('morada',''),dados.get('contato',''),id))
        return {'ok': True}

def deletar_fornecedor(id):
    with db_session() as conn:
        conn.execute("DELETE FROM fornecedores WHERE id=?",(id,))
        return {'ok': True}
