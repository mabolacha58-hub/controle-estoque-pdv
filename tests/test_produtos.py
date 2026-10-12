"""Testes do CRUD de produtos através da API."""


def test_listar_produtos_vazio(client, gerente_login):
    resp = client.get('/api/produtos')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_criar_produto(client, gerente_login, cria_produto):
    pid = cria_produto('Produto Teste 1')
    lista = client.get('/api/produtos').get_json()
    assert any(p['id'] == pid for p in lista)


def test_criar_produto_sem_nome(client, gerente_login):
    resp = client.post('/api/produtos', json={'preco_venda': 20})
    assert resp.status_code == 400
    assert resp.get_json()['ok'] is False


def test_atualizar_produto(client, gerente_login, cria_produto):
    pid = cria_produto('Produto Renomear')
    resp = client.put(f'/api/produtos/{pid}', json={
        'nome': 'Produto Renomeado', 'preco_venda': 99})
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True
    atual = [p for p in client.get('/api/produtos').get_json() if p['id'] == pid][0]
    assert atual['nome'] == 'Produto Renomeado'
    assert atual['preco_venda'] == 99


def test_deletar_produto_sem_mov(client, gerente_login, cria_produto):
    pid = cria_produto('Produto Deletar')
    resp = client.delete(f'/api/produtos/{pid}')
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True
    ids = [p['id'] for p in client.get('/api/produtos').get_json()]
    assert pid not in ids


def test_criar_sem_gerente(client):
    client.post('/api/utilizadores/login', json={'nome': 'Caixa 1', 'pin': '0000'})
    resp = client.post('/api/produtos', json={'nome': 'Sem permissao', 'preco_venda': 10})
    assert resp.status_code == 403