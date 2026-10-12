import sqlite3

conn = sqlite3.connect(r'D:\DEV\Control de estoque\Controle\controle_estoque\controle_estoque.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print('=== PRODUTOS ===')
for row in c.execute('SELECT id, nome, codigo_barras, quantidade, quantidade_minima, preco_venda, iva, unidade FROM produtos'):
    print(f'  {row["id"]}: {row["nome"]} | Código: {row["codigo_barras"]} | Qtd: {row["quantidade"]} {row["unidade"]} | Min: {row["quantidade_minima"]} | Preço: {row["preco_venda"]} | IVA: {row["iva"]}%')

print('\n=== CATEGORIAS ===')
for row in c.execute('SELECT * FROM categorias'):
    print(f'  {row["id"]}: {row["nome"]}')

print('\n=== MOVIMENTAÇÕES (últimas 10) ===')
for row in c.execute('SELECT * FROM movimentacoes ORDER BY data DESC LIMIT 10'):
    print(f'  {row["id"]}: Produto {row["produto_id"]} | {row["tipo"]} | Qtd: {row["quantidade"]} | {row["data"]}')

print('\n=== CLIENTES ===')
for row in c.execute('SELECT * FROM clientes'):
    print(f'  {row["id"]}: {row["nome"]} | NIF: {row["nif"]} | Saldo: {row["saldo"]}')

print('\n=== FORNECEDORES ===')
for row in c.execute('SELECT * FROM fornecedores'):
    print(f'  {row["id"]}: {row["nome"]}')

print('\n=== UTILIZADORES ===')
for row in c.execute('SELECT * FROM utilizadores'):
    print(f'  {row["id"]}: {row["nome"]} | Role: {row["role"]} | Ativo: {row["ativo"]}')

print('\n=== CAIXA ===')
for row in c.execute('SELECT * FROM caixa'):
    print(f'  {row["id"]}: User {row["utilizador_id"]} | Abertura: {row["abertura"]} | Fecho: {row["fecho"]} | Status: {row["status"]}')

print('\n=== CONFIGURAÇÕES ===')
for row in c.execute('SELECT * FROM configuracoes'):
    print(f'  {row["chave"]}: {row["valor"]}')

conn.close()