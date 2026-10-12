import os, tempfile, sys

# Redirect DB to a temporary file BEFORE any module imports/reads the path.
tmpdir = tempfile.mkdtemp(prefix='cest_tests_')
_test_db = os.path.join(tmpdir, 'controle_estoque_test.db')
os.environ['DB_PATH'] = _test_db

import pytest
from app import create_app
from database import init_db, get_db

@pytest.fixture()
def app():
    # Fresh schema + seed data for each test
    init_db()
    application = create_app()
    application.config['TESTING'] = True
    yield application

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def gerente_login(client):
    """Log in as the seeded gerente (Administrador / pin 1234)."""
    resp = client.post('/api/utilizadores/login',
                       json={'nome': 'Administrador', 'pin': '1234'})
    assert resp.status_code == 200
    return resp.get_json()

def _cria_produto(client, nome='Teste Produto', preco_custo=10, preco_venda=20, quantidade=5, qtd_minima=0):
    return client.post('/api/produtos', json={
        'nome': nome,
        'preco_custo': preco_custo,
        'preco_venda': preco_venda,
        'quantidade': quantidade,
        'quantidade_minima': qtd_minima,
        'categoria_id': None
    })

@pytest.fixture()
def produto(client, gerente_login):
    resp = _cria_produto(client)
    assert resp.status_code == 200, resp.get_data(as_text=True)
    body = resp.get_json()
    assert body.get('ok'), body
    with get_db() as conn:
        pid = conn.execute("SELECT id FROM produtos WHERE nome='Teste Produto' ORDER BY id DESC").fetchone()[0]
    return {'id': pid, 'nome': 'Teste Produto'}

@pytest.fixture()
def cria_produto(client, gerente_login):
    """Helper fixture: returns a function that creates a product and returns its id."""
    def _criar(nome='Produto', preco_custo=10, preco_venda=20, quantidade=5, qtd_minima=0):
        resp = _cria_produto(client, nome=nome, preco_custo=preco_custo,
                             preco_venda=preco_venda, quantidade=quantidade,
                             qtd_minima=qtd_minima)
        assert resp.status_code == 200, resp.get_data(as_text=True)
        with get_db() as conn:
            pid = conn.execute("SELECT id FROM produtos WHERE nome=? ORDER BY id DESC",
                               (nome,)).fetchone()[0]
        return pid
    return _criar