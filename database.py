import sqlite3, os, logging
from datetime import datetime
from werkzeug.security import generate_password_hash

log = logging.getLogger(__name__)

def get_db_path():
    return os.environ.get('DB_PATH') or os.path.join(os.path.dirname(__file__), 'controle_estoque.db')

DB_PATH = get_db_path()

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT
        );
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, codigo_barras TEXT,
            descricao TEXT, categoria_id INTEGER, quantidade REAL DEFAULT 0,
            quantidade_minima REAL DEFAULT 0, preco_custo REAL DEFAULT 0,
            preco_venda REAL DEFAULT 0, iva REAL DEFAULT 0, unidade TEXT DEFAULT 'UN',
            data_criacao TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, quantidade REAL NOT NULL, preco_unitario REAL DEFAULT 0,
            desconto REAL DEFAULT 0, data TEXT DEFAULT (datetime('now','localtime')),
            documento TEXT, observacao TEXT, cliente_id INTEGER,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
            nif TEXT, telefone TEXT, email TEXT, morada TEXT,
            saldo REAL DEFAULT 0, limite_credito REAL DEFAULT 0,
            data_cadastro TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
            nif TEXT, telefone TEXT, email TEXT, morada TEXT, contato TEXT
        );
        CREATE TABLE IF NOT EXISTS utilizadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
            pin TEXT NOT NULL DEFAULT '1234', role TEXT DEFAULT 'caixa',
            ativo INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT, utilizador_id INTEGER,
            abertura TEXT DEFAULT (datetime('now','localtime')),
            fecho TEXT, saldo_inicial REAL DEFAULT 0, saldo_final REAL,
            status TEXT DEFAULT 'aberto',
            FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
        );
    ''')
    padrao = [("Alimentos",""),("Bebidas",""),("Limpeza",""),("Ferramentas",""),
        ("Material de Escritório",""),("Vestuário",""),("Eletrônicos",""),
        ("Embalagens",""),("Matéria-Prima",""),("Outros","")]
    for nome, desc in padrao:
        try: c.execute("INSERT INTO categorias (nome,descricao) VALUES (?,?)", (nome, desc))
        except Exception: log.debug("Categoria '%s' já existe", nome)
    if not c.execute("SELECT COUNT(*) FROM utilizadores").fetchone()[0]:
        c.execute("INSERT INTO utilizadores (nome,pin,role) VALUES (?,?,?)",
                  ("Administrador", generate_password_hash("1234"), "gerente"))
        c.execute("INSERT INTO utilizadores (nome,pin,role) VALUES (?,?,?)",
                  ("Caixa 1", generate_password_hash("0000"), "caixa"))
    else:
        for row in c.execute("SELECT id,pin FROM utilizadores").fetchall():
            if row[1] and not row[1].startswith(('pbkdf2:sha', 'scrypt:')):
                h = generate_password_hash(row[1])
                c.execute("UPDATE utilizadores SET pin=? WHERE id=?", (h, row[0]))
    if not c.execute("SELECT COUNT(*) FROM caixa").fetchone()[0]:
        c.execute("INSERT INTO caixa (utilizador_id,status) VALUES (1,'fechado')")
    c.execute('''CREATE TABLE IF NOT EXISTS configuracoes (
        chave TEXT PRIMARY KEY, valor TEXT NOT NULL DEFAULT ''
    )''')
    defaults = {'loja_nome':'Controle de Estoque','loja_nif':'','loja_endereco':'',
        'loja_telefone':'','loja_email':'','iva_padrao':'0',
        'backup_auto':'1','backup_intervalo':'6','backup_pastacaminho':'',
        'notif_stock':'1','notif_som':'1','impressao_automatica':'0',
        'meta_diaria_vendas':'0'}
    for k,v in defaults.items():
        try: c.execute("INSERT OR IGNORE INTO configuracoes (chave,valor) VALUES (?,?)", (k,v))
        except Exception as e: log.error("Erro ao inserir config '%s': %s", k, e)
    try: c.execute("ALTER TABLE produtos ADD COLUMN foto TEXT DEFAULT NULL")
    except Exception: log.debug("Coluna 'foto' já existe em produtos")
    for col_table in [('produtos','iva'), ('movimentacoes','desconto'), ('movimentacoes','cliente_id')]:
        try: c.execute(f"ALTER TABLE {col_table[0]} ADD COLUMN {col_table[1]} {'INTEGER' if col_table[1]=='cliente_id' else 'REAL'} DEFAULT 0")
        except Exception: log.debug("Coluna '%s' já existe em %s", col_table[1], col_table[0])
    for idx in [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo_barras)",
        "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria_id)",
        "CREATE INDEX IF NOT EXISTS idx_mov_produto ON movimentacoes(produto_id)",
        "CREATE INDEX IF NOT EXISTS idx_mov_data ON movimentacoes(data)",
        "CREATE INDEX IF NOT EXISTS idx_mov_cliente ON movimentacoes(cliente_id)",
        "CREATE INDEX IF NOT EXISTS idx_clientes_nif ON clientes(nif)"
    ]:
        try: c.execute(idx)
        except Exception as e: log.error("Erro ao criar índice: %s", e)
    conn.commit()
    conn.close()

def moeda(valor):
    try: v = float(valor)
    except: return str(valor)
    s = f"{v:,.2f}".replace(',',' ').replace('.',',')
    return s.replace(' ','.') + " MT"

def fmt_data(data):
    if not data: return '-'
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try: return datetime.strptime(data, fmt).strftime('%d/%m/%Y %H:%M' if ' ' in data else '%d/%m/%Y')
        except ValueError: continue
    return data

def get_config(chave, default=''):
    try:
        conn = get_db()
        r = conn.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,)).fetchone()
        conn.close()
        return r[0] if r else default
    except Exception as e: log.error("get_config(%s): %s", chave, e); return default

def set_config(chave, valor):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO configuracoes (chave,valor) VALUES (?,?)", (chave, str(valor)))
    conn.commit(); conn.close()
