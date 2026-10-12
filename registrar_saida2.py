import sqlite3
from datetime import datetime

conn = sqlite3.connect(r'D:\DEV\Control de estoque\Controle\controle_estoque\controle_estoque.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Verificar produto atual
produto = c.execute('SELECT id, nome, quantidade FROM produtos WHERE id = 1').fetchone()
print(f'Antes: {produto["nome"]} - Quantidade: {produto["quantidade"]}')

# Registrar saída de 3 unidades
quantidade_saida = 3
c.execute('''
    INSERT INTO movimentacoes (produto_id, tipo, quantidade, preco_unitario, data, documento, observacao)
    VALUES (?, 'saida', ?, ?, ?, ?, ?)
''', (1, quantidade_saida, 400, 
      datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'TESTE-002', 'Segunda saída registrada via script'))

# Atualizar estoque do produto
nova_qtd = produto["quantidade"] - quantidade_saida
c.execute('UPDATE produtos SET quantidade = ? WHERE id = 1', (nova_qtd,))

conn.commit()

# Verificar depois
produto_atualizado = c.execute('SELECT id, nome, quantidade FROM produtos WHERE id = 1').fetchone()
print(f'Depois: {produto_atualizado["nome"]} - Quantidade: {produto_atualizado["quantidade"]}')

# Mostrar última movimentação
ultima = c.execute('SELECT * FROM movimentacoes ORDER BY id DESC LIMIT 1').fetchone()
print(f'Movimentação registrada: ID {ultima["id"]} | Tipo: {ultima["tipo"]} | Qtd: {ultima["quantidade"]} | Data: {ultima["data"]}')

conn.close()