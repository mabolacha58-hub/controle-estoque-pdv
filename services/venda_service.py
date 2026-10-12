from datetime import datetime
from services.base import db_session
from utils.validation import validar
from services.fiscal_service import emitir_documento
from services.crm_service import atualizar_fidelizacao
from services.auditoria_service import registrar

VENDA_SCHEMA = {
    'itens': {'required': True},
    'pagamento': {'required': True, 'choices': ['Dinheiro', 'Cartão Débito', 'Cartão Crédito', 'Transferência', 'Faturar']},
    'cliente_id': {'coerce': int, 'default': None},
    'desconto_total': {'coerce': float, 'default': 0, 'min': 0, 'max': 100},
    'data': {'default': ''},
    'cliente': {'default': 'Consumidor Final'},
    'filial_id': {'coerce': int, 'default': 1},
}

def processar_venda(dados):
    erros_valid = validar(dados, VENDA_SCHEMA)
    if erros_valid:
        return {'ok': False, 'erros': erros_valid}

    itens = dados.get('itens')
    if not itens or not isinstance(itens, list) or len(itens) == 0:
        return {'ok': False, 'erros': ['Nenhum item na venda']}

    with db_session() as conn:
        erros = []
        cx = conn.execute("SELECT id FROM caixa WHERE status='aberto' ORDER BY id DESC LIMIT 1").fetchone()
        if not cx:
            return {'ok': False, 'erros': ['Caixa fechado! Abra o caixa antes de vender.']}

        usar_data = dados.get('data', '').strip()
        if usar_data:
            try:
                datetime.strptime(usar_data, '%Y-%m-%d')
            except ValueError:
                return {'ok': False, 'erros': [f'Data inválida: {usar_data}. Use AAAA-MM-DD.']}

        total_venda = 0
        total_iva = 0
        for item in itens:
            pid = item.get('id')
            if not pid:
                erros.append("Item sem ID")
                continue
            try:
                qtd = float(item['quantidade'])
                preco = float(item.get('preco_final', item['preco']))
            except (KeyError, ValueError, TypeError):
                erros.append(f"Item #{pid}: dados inválidos (quantidade/preco)")
                continue
            estoque = conn.execute("SELECT quantidade, iva FROM produtos WHERE id=?",(pid,)).fetchone()
            if not estoque or estoque[0] < qtd:
                erros.append(f"{item.get('nome','?')}: estoque insuficiente")
                continue
            conn.execute("UPDATE produtos SET quantidade=quantidade-? WHERE id=? AND quantidade>=?",(qtd,pid,qtd))
            desconto = float(item.get('desconto',0))
            desc_total = float(dados.get('desconto_total',0))
            preco_final = preco * (1 - desc_total/100)
            total_venda += preco_final * qtd
            iva_prod = float(estoque[1] or 0)
            total_iva += (preco_final * qtd) * (iva_prod / 100)
            obs = f"Venda {dados.get('cliente','Consumidor Final')} - {dados.get('pagamento','Dinheiro')}"
            if desc_total:
                obs += f" | Desc global: {desc_total}%"
            if dados.get('cliente_id'):
                obs += f" | Cliente #{dados['cliente_id']}"
            if usar_data:
                conn.execute("""INSERT INTO movimentacoes (produto_id,tipo,quantidade,preco_unitario,
                    desconto,documento,observacao,cliente_id,data) VALUES (?,?,?,?,?,?,?,?,?)""",
                    (pid,"saida",qtd,preco,desconto,"PDV",obs,dados.get('cliente_id'),usar_data))
            else:
                conn.execute("""INSERT INTO movimentacoes (produto_id,tipo,quantidade,preco_unitario,
                    desconto,documento,observacao,cliente_id) VALUES (?,?,?,?,?,?,?,?)""",
                    (pid,"saida",qtd,preco,desconto,"PDV",obs,dados.get('cliente_id')))
            if dados.get('cliente_id') and dados.get('pagamento')=='Faturar':
                conn.execute("UPDATE clientes SET saldo=saldo+? WHERE id=?",(preco_final*qtd,dados['cliente_id']))
        if erros:
            return {'ok': False, 'erros': erros}

    # Enterprise integrations (outside the transaction to avoid locking)
    cliente_id = dados.get('cliente_id')
    cliente_nome = dados.get('cliente', 'Consumidor Final')
    try:
        if cliente_id:
            atualizar_fidelizacao(cliente_id, total_venda)
    except Exception:
        pass
    try:
        tipo_doc = "FR" if dados.get('pagamento') in ("Dinheiro", "Cartão Débito", "Cartão Crédito", "Transferência") else "FT"
        emitir_documento(tipo_doc, cliente_id, cliente_nome,
                         dados.get('cliente_nif', ''), total_venda, total_iva,
                         filial_id=dados.get('filial_id', 1))
    except Exception:
        pass
    try:
        registrar("criar_venda", "venda", None, f"Total: {total_venda:.2f} MT - {dados.get('pagamento')} - {cliente_nome}")
    except Exception:
        pass

    return {'ok': True, 'total': total_venda, 'cliente': cliente_nome}
