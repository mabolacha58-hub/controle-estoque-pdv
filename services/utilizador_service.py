import time
from werkzeug.security import generate_password_hash, check_password_hash
from services.base import db_connection, db_session
from utils.validation import validar

UTILIZADOR_SCHEMA = {
    'nome': {'required': True, 'maxlen': 100},
    'pin': {'default': '', 'maxlen': 20, 'minlen': 4},
    'role': {'default': 'caixa', 'choices': ['caixa', 'gerente']},
    'ativo': {'coerce': int, 'default': 1, 'choices': [0, 1]},
}

MAX_TENTATIVAS = 5
BLOQUEIO_SEGUNDOS = 300

_tentativas = {}

def _chave_tentativa(nome, ip):
    return f"{nome}:{ip}"

def verificar_bloqueio(nome, ip):
    chave = _chave_tentativa(nome, ip)
    dados = _tentativas.get(chave)
    if not dados:
        return False, 0
    if dados['bloqueio_ate'] and time.time() < dados['bloqueio_ate']:
        restante = int(dados['bloqueio_ate'] - time.time())
        return True, restante
    if dados['bloqueio_ate'] and time.time() >= dados['bloqueio_ate']:
        _tentativas.pop(chave, None)
        return False, 0
    return False, 0

def registrar_falha(nome, ip):
    chave = _chave_tentativa(nome, ip)
    dados = _tentativas.get(chave, {'count': 0, 'bloqueio_ate': None})
    dados['count'] += 1
    if dados['count'] >= MAX_TENTATIVAS:
        dados['bloqueio_ate'] = time.time() + BLOQUEIO_SEGUNDOS
        dados['count'] = 0
    _tentativas[chave] = dados

def limpar_falhas(nome, ip):
    chave = _chave_tentativa(nome, ip)
    _tentativas.pop(chave, None)

def autenticar(nome, pin, ip=None):
    nome = (nome or '').strip()
    pin = (pin or '').strip()
    if not nome:
        return None, 'Nome é obrigatório'
    if not pin:
        return None, 'PIN é obrigatório'
    if ip:
        bloqueado, restante = verificar_bloqueio(nome, ip)
        if bloqueado:
            return None, f'Temporariamente bloqueado. Tente novamente em {restante}s'
    with db_connection() as conn:
        row = conn.execute("SELECT id,nome,role,pin FROM utilizadores WHERE nome=? AND ativo=1",
                           (nome,)).fetchone()
        if row and check_password_hash(row[3], pin):
            if ip:
                limpar_falhas(nome, ip)
            return {'id': row[0], 'nome': row[1], 'role': row[2]}, None
        if ip:
            registrar_falha(nome, ip)
        _, restante = verificar_bloqueio(nome, ip) if ip else (False, 0)
        if restante > 0:
            return None, f'Credenciais inválidas. Bloqueado por {restante}s'
        return None, 'Credenciais inválidas'

def listar_utilizadores():
    with db_connection() as conn:
        rows = conn.execute("SELECT id,nome,role,ativo FROM utilizadores ORDER BY nome").fetchall()
        return [dict(r) for r in rows]

def criar_utilizador(dados):
    erros = validar(dados, UTILIZADOR_SCHEMA)
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        conn.execute("INSERT INTO utilizadores (nome,pin,role) VALUES (?,?,?)",
                     (dados['nome'],generate_password_hash(dados.get('pin','0000')),dados.get('role','caixa')))
        return {'ok': True}

def atualizar_utilizador(id, dados):
    erros = validar(dados, {k: v for k, v in UTILIZADOR_SCHEMA.items() if k != 'pin' or k in dados})
    if erros:
        return {'ok': False, 'erros': erros}
    with db_session() as conn:
        pin = dados.get('pin')
        if pin:
            conn.execute("UPDATE utilizadores SET nome=?,pin=?,role=?,ativo=? WHERE id=?",
                (dados['nome'],generate_password_hash(pin),dados.get('role','caixa'),dados.get('ativo',1),id))
        else:
            conn.execute("UPDATE utilizadores SET nome=?,role=?,ativo=? WHERE id=?",
                (dados['nome'],dados.get('role','caixa'),dados.get('ativo',1),id))
        return {'ok': True}

def deletar_utilizador(id):
    with db_session() as conn:
        conn.execute("DELETE FROM utilizadores WHERE id=?",(id,))
        return {'ok': True}
