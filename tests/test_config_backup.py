"""Testes de configurações e backup (manual, listagem e restauro)."""
import os
import tempfile
from database import set_config, get_config, get_db_path


def test_get_configuracoes(client, gerente_login):
    resp = client.get('/api/configuracoes')
    assert resp.status_code == 200
    assert resp.get_json().get('loja_nome') is not None


def test_salvar_configuracoes(client, gerente_login):
    resp = client.post('/api/configuracoes', json={'loja_nome': 'Loja Teste', 'meta_diaria_vendas': '1500'})
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True
    assert get_config('loja_nome') == 'Loja Teste'


def test_backup_manual_cria_ficheiro(client, gerente_login):
    tmp = tempfile.mkdtemp(prefix='bk_test_')
    set_config('backup_pastacaminho', tmp)
    resp = client.post('/api/backup/manual')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['ok'] is True
    assert os.path.isfile(body['caminho'])
    assert body['caminho'].endswith('.db')
    # tratar do duplicate scan: pasta também é captada por DEFAULT_BACKUP_DIR, mas não deve haver escrita lá
    assert body['pasta'] == tmp


def test_backup_manual_nao_configurado(client, gerente_login):
    # aponta para pasta não existente -> usa DEFAULT_BACKUP_DIR (pode faltar). Só garante retorno ok:True.
    set_config('backup_pastacaminho', os.path.join(tempfile.gettempdir(), 'pasta_inexistente_bk'))
    resp = client.post('/api/backup/manual')
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True


def test_listar_backups_apos_manual(client, gerente_login):
    tmp = tempfile.mkdtemp(prefix='bk_list_')
    set_config('backup_pastacaminho', tmp)
    client.post('/api/backup/manual')
    resp = client.get('/api/backups/list')
    assert resp.status_code == 200
    backups = resp.get_json()['backups']
    assert any(b['pasta'] == tmp for b in backups)


def test_restore_por_nome(client, gerente_login):
    tmp = tempfile.mkdtemp(prefix='bk_res_')
    set_config('backup_pastacaminho', tmp)
    mk = client.post('/api/backup/manual').get_json()
    nome = mk['nome']
    assert mk['ok'] is True

    resp = client.post('/api/restore', json={'caminho': nome})
    assert resp.status_code == 200
    assert resp.get_json()['ok'] is True


def test_restore_caminho_invalido(client, gerente_login):
    resp = client.post('/api/restore', json={'caminho': 'nao_existe.db'})
    assert resp.status_code == 404


def test_config_requer_gerente(client):
    client.post('/api/utilizadores/login', json={'nome': 'Caixa 1', 'pin': '0000'})
    resp = client.post('/api/configuracoes', json={'loja_nome': 'X'})
    assert resp.status_code == 403