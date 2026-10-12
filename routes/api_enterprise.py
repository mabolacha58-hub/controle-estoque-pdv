from flask import Blueprint, request, jsonify, session
from auth import login_required, gerente_required, permissao_required
from services.dashboard_enterprise_service import (
    obter_kpis, obter_receita_despesa_mensal,
    obter_top_clientes_fidelidade, obter_comparativo_filiais,
    obter_kpis_vendas, obter_vendas_mensais, obter_produtos_stock_critico
)
from services.permissoes_service import (
    listar_permissoes_utilizador, definir_permissoes,
    listar_permissoes_todos, PERMISSOES_DISPONIVEIS
)
from services.auditoria_service import (
    listar, registrar, listar_resumo_por_data, resumo_hoje
)
from services.empresa_service import (
    listar_filiais, criar_filial, editar_filial, excluir_filial,
    listar_lotes, criar_lote,
    listar_transferencias, criar_transferencia, confirmar_transferencia
)
from services.financeiro_service import (
    listar_contas_pagar, criar_conta_pagar, pagar_conta,
    listar_contas_receber, criar_conta_receber, receber_conta,
    listar_movimentos_financeiros, registrar_movimento_financeiro,
    listar_bancos, criar_banco, fluxo_caixa
)
from services.compra_service import (
    listar_compras, criar_compra, receber_compra, obter_compra,
    cancelar_compra, atualizar_compra
)
from services.fiscal_service import (
    emitir_documento, listar_documentos, anular_documento,
    listar_series, TIPOS_DOCUMENTO
)
from services.fiscal_at_service import (
    gerar_xml_e_fatura, simular_enviar_at, enviar_pendentes,
    listar_documentos_at, listar_config, get_config, set_config,
    gerar_saft, obter_log_envio
)
from services.crm_service import (
    obter_fidelizacao, atualizar_fidelizacao, adicionar_cashback,
    listar_cashback, listar_clientes_fidelidade, registrar_comunicacao,
    listar_comunicacoes
)
from services.rh_service import (
    listar_funcionarios, criar_funcionario, editar_funcionario, excluir_funcionario,
    registrar_presenca, listar_presencas, registrar_comissao, listar_comissoes,
    pagar_comissao,
    processar_folha, listar_folhas, pagar_folha, excluir_folha, atualizar_folha,
    listar_alugueres, criar_aluguer, pagar_aluguer, excluir_aluguer,
    registrar_adiantamento_salarial, listar_adiantamentos_salariais,
    excluir_adiantamento_salarial, total_adiantamentos_pendentes_funcionario
)
from services.fiscal_municipal_service import (
    listar_fiscal_municipal, criar_fiscal_municipal, pagar_fiscal_municipal,
    excluir_fiscal_municipal, obter_resumo_fiscal_municipal, listar_tipos
)
from services.carga_service import (
    listar_cargas, criar_carga, finalizar_carga, pagar_carga, excluir_carga,
    listar_adiantamentos, registrar_adiantamento, excluir_adiantamento,
    obter_acerto
)

api_enterprise_bp = Blueprint('api_enterprise', __name__)

# ===================== FILIAIS =====================
@api_enterprise_bp.route('/api/filiais', methods=['GET'])
@login_required
def get_filiais():
    return jsonify(listar_filiais())

@api_enterprise_bp.route('/api/filiais', methods=['POST'])
@login_required
@gerente_required
def post_filial():
    data = request.get_json()
    return jsonify({"id": criar_filial(1, data["nome"], data.get("endereco", ""),
                  data.get("telefone", ""), data.get("email", ""))}), 201

@api_enterprise_bp.route('/api/filiais/<int:id>', methods=['PUT'])
@login_required
@gerente_required
def put_filial(id):
    data = request.get_json()
    editar_filial(id, data["nome"], data.get("endereco", ""),
                  data.get("telefone", ""), data.get("email", ""))
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/filiais/<int:id>', methods=['DELETE'])
@login_required
@gerente_required
def delete_filial(id):
    excluir_filial(id)
    return jsonify({"ok": True})

# ===================== LOTES =====================
@api_enterprise_bp.route('/api/lotes', methods=['GET'])
@login_required
def get_lotes():
    return jsonify(listar_lotes(request.args.get("produto_id", type=int)))

@api_enterprise_bp.route('/api/lotes', methods=['POST'])
@login_required
@gerente_required
def post_lote():
    d = request.get_json()
    return jsonify({"id": criar_lote(d["produto_id"], d["codigo_lote"],
                  d["quantidade"], d["data_validade"], d.get("preco_custo", 0))}), 201

# ===================== TRANSFERÊNCIAS =====================
@api_enterprise_bp.route('/api/transferencias', methods=['GET'])
@login_required
def get_transferencias():
    return jsonify(listar_transferencias(request.args.get("filial_id", type=int)))

@api_enterprise_bp.route('/api/transferencias', methods=['POST'])
@login_required
@gerente_required
def post_transferencia():
    d = request.get_json()
    return jsonify({"id": criar_transferencia(d["produto_id"], d["quantidade"],
                  d["filial_origem"], d["filial_destino"], d.get("observacao", ""))}), 201

@api_enterprise_bp.route('/api/transferencias/<int:id>/confirmar', methods=['POST'])
@login_required
@gerente_required
def confirmar_transferencia_route(id):
    if confirmar_transferencia(id):
        return jsonify({"ok": True})
    return jsonify({"erro": "Transferência não encontrada ou já concluída"}), 400

# ===================== CONTAS A PAGAR =====================
@api_enterprise_bp.route('/api/contas-pagar', methods=['GET'])
@login_required
def get_contas_pagar():
    return jsonify(listar_contas_pagar(request.args.get("status"), filial_id=1))

@api_enterprise_bp.route('/api/contas-pagar', methods=['POST'])
@login_required
@gerente_required
def post_conta_pagar():
    d = request.get_json()
    return jsonify({"id": criar_conta_pagar(d["fornecedor_id"], d["descricao"],
                  d["valor"], d["data_vencimento"])}), 201

@api_enterprise_bp.route('/api/contas-pagar/<int:id>/pagar', methods=['POST'])
@login_required
@gerente_required
def pagar_conta_route(id):
    d = request.get_json()
    if pagar_conta(id, d["valor"], d.get("banco_id"), d.get("forma_pagamento", "dinheiro")):
        return jsonify({"ok": True})
    return jsonify({"erro": "Conta não encontrada"}), 400

# ===================== CONTAS A RECEBER =====================
@api_enterprise_bp.route('/api/contas-receber', methods=['GET'])
@login_required
def get_contas_receber():
    return jsonify(listar_contas_receber(request.args.get("status"), filial_id=1))

@api_enterprise_bp.route('/api/contas-receber', methods=['POST'])
@login_required
@gerente_required
def post_conta_receber():
    d = request.get_json()
    return jsonify({"id": criar_conta_receber(d["cliente_id"], d["descricao"],
                  d["valor"], d["data_vencimento"])}), 201

@api_enterprise_bp.route('/api/contas-receber/<int:id>/receber', methods=['POST'])
@login_required
@gerente_required
def receber_conta_route(id):
    d = request.get_json()
    if receber_conta(id, d["valor"], d.get("banco_id"), d.get("forma_pagamento", "dinheiro")):
        return jsonify({"ok": True})
    return jsonify({"erro": "Conta não encontrada"}), 400

# ===================== MOVIMENTOS FINANCEIROS =====================
@api_enterprise_bp.route('/api/movimentos-financeiros', methods=['GET'])
@login_required
def get_movimentos_financeiros():
    return jsonify(listar_movimentos_financeiros(filial_id=1,
                   dias=request.args.get("dias", 30, type=int)))

@api_enterprise_bp.route('/api/movimentos-financeiros', methods=['POST'])
@login_required
@gerente_required
def post_movimento_financeiro():
    d = request.get_json()
    return jsonify({"id": registrar_movimento_financeiro(d["tipo"], d["categoria"],
                  d["descricao"], d["valor"], d.get("forma_pagamento", "dinheiro"),
                  d.get("banco_id"))}), 201

@api_enterprise_bp.route('/api/fluxo-caixa', methods=['GET'])
@login_required
def get_fluxo_caixa():
    return jsonify(fluxo_caixa(filial_id=1, dias=request.args.get("dias", 30, type=int)))

# ===================== BANCOS =====================
@api_enterprise_bp.route('/api/bancos', methods=['GET'])
@login_required
def get_bancos():
    return jsonify(listar_bancos())

@api_enterprise_bp.route('/api/bancos', methods=['POST'])
@login_required
@gerente_required
def post_banco():
    d = request.get_json()
    return jsonify({"id": criar_banco(d["nome"], d.get("numero_conta", ""),
                  d.get("titular", ""), d.get("saldo", 0))}), 201

# ===================== COMPRAS =====================
@api_enterprise_bp.route('/api/compras', methods=['GET'])
@login_required
def get_compras():
    return jsonify(listar_compras(request.args.get("status"), filial_id=1))

@api_enterprise_bp.route('/api/compras', methods=['POST'])
@login_required
@gerente_required
def post_compra():
    d = request.get_json()
    return jsonify({"id": criar_compra(d["fornecedor_id"], d["itens"],
                  d.get("observacao", ""))}), 201

@api_enterprise_bp.route('/api/compras/<int:id>', methods=['GET'])
@login_required
def get_compra(id):
    compra, itens = obter_compra(id)
    if compra:
        return jsonify({"compra": compra, "itens": itens})
    return jsonify({"erro": "Compra não encontrada"}), 400

@api_enterprise_bp.route('/api/compras/<int:id>/receber', methods=['POST'])
@login_required
@gerente_required
def receber_compra_route(id):
    if receber_compra(id):
        return jsonify({"ok": True})
    return jsonify({"erro": "Compra não encontrada ou já recebida"}), 400

@api_enterprise_bp.route('/api/compras/<int:id>', methods=['PUT'])
@login_required
@gerente_required
def put_compra(id):
    d = request.get_json()
    return jsonify({"id": atualizar_compra(id, d["fornecedor_id"], d["itens"],
                  d.get("observacao", ""))})

@api_enterprise_bp.route('/api/compras/<int:id>', methods=['DELETE'])
@login_required
@gerente_required
def delete_compra(id):
    cancelar_compra(id)
    return jsonify({"ok": True})

# ===================== FISCAL =====================
@api_enterprise_bp.route('/api/fiscal/documentos', methods=['GET'])
@login_required
def get_documentos_fiscais():
    return jsonify(listar_documentos(request.args.get("tipo"), filial_id=1,
                   limite=request.args.get("limite", 50, type=int)))

@api_enterprise_bp.route('/api/fiscal/documentos', methods=['POST'])
@login_required
@gerente_required
def post_documento_fiscal():
    d = request.get_json()
    return jsonify(emitir_documento(d["tipo"], d.get("cliente_id"), d["cliente_nome"],
                  d["cliente_nif"], d["total"], d.get("iva_total", 0),
                  d.get("venda_id"))), 201

@api_enterprise_bp.route('/api/fiscal/documentos/<int:id>/anular', methods=['POST'])
@login_required
@gerente_required
def anular_doc_fiscal(id):
    if anular_documento(id, request.get_json().get("motivo", "")):
        return jsonify({"ok": True})
    return jsonify({"erro": "Documento não encontrado ou já anulado"}), 400

@api_enterprise_bp.route('/api/fiscal/series', methods=['GET'])
@login_required
def get_series():
    return jsonify(listar_series(request.args.get("tipo"), filial_id=1))

@api_enterprise_bp.route('/api/fiscal/tipos', methods=['GET'])
@login_required
def get_tipos_documento():
    return jsonify([{"sigla": k, "nome": v} for k, v in TIPOS_DOCUMENTO.items()])

# ===================== AT E-FATURA (MOÇAMBIQUE) =====================
@api_enterprise_bp.route('/api/fiscal/at/documentos', methods=['GET'])
@login_required
def get_at_documentos():
    return jsonify(listar_documentos_at(
        request.args.get("status"), filial_id=1,
        limite=request.args.get("limite", 100, type=int)
    ))

@api_enterprise_bp.route('/api/fiscal/at/documentos/<int:id>/xml', methods=['GET'])
@login_required
def get_at_xml(id):
    xml = gerar_xml_e_fatura(id)
    if xml:
        return xml, 200, {"Content-Type": "application/xml"}
    return jsonify({"erro": "Documento não encontrado"}), 400

@api_enterprise_bp.route('/api/fiscal/at/documentos/<int:id>/enviar', methods=['POST'])
@login_required
@gerente_required
def post_at_enviar(id):
    return jsonify(simular_enviar_at(id))

@api_enterprise_bp.route('/api/fiscal/at/enviar-pendentes', methods=['POST'])
@login_required
@gerente_required
def post_at_enviar_pendentes():
    return jsonify({"resultados": enviar_pendentes()})

@api_enterprise_bp.route('/api/fiscal/at/documentos/<int:id>/log', methods=['GET'])
@login_required
def get_at_log(id):
    return jsonify(obter_log_envio(id))

@api_enterprise_bp.route('/api/fiscal/at/config', methods=['GET'])
@login_required
def get_at_config():
    return jsonify(listar_config())

@api_enterprise_bp.route('/api/fiscal/at/config', methods=['POST'])
@login_required
@gerente_required
def post_at_config():
    d = request.get_json()
    for chave, valor in d.items():
        set_config(chave, valor)
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/fiscal/at/saft', methods=['GET'])
@login_required
def get_at_saft():
    xml = gerar_saft()
    return xml, 200, {"Content-Type": "application/xml", "Content-Disposition": "attachment; filename=SAFT-MZ.xml"}

# ===================== CRM / FIDELIZAÇÃO =====================
@api_enterprise_bp.route('/api/fidelizacao/<int:cliente_id>', methods=['GET'])
@login_required
def get_fidelizacao(cliente_id):
    return jsonify(obter_fidelizacao(cliente_id))

@api_enterprise_bp.route('/api/fidelizacao/clientes', methods=['GET'])
@login_required
def get_fidelizacao_clientes():
    return jsonify(listar_clientes_fidelidade())

@api_enterprise_bp.route('/api/cashback/<int:cliente_id>', methods=['GET'])
@login_required
def get_cashback(cliente_id):
    return jsonify(listar_cashback(cliente_id))

@api_enterprise_bp.route('/api/cashback/<int:cliente_id>', methods=['POST'])
@login_required
@gerente_required
def post_cashback(cliente_id):
    d = request.get_json()
    adicionar_cashback(cliente_id, d["valor"], d.get("tipo", "acumulo"), d.get("venda_id"))
    return jsonify({"ok": True}), 201

@api_enterprise_bp.route('/api/comunicacoes', methods=['POST'])
@login_required
@gerente_required
def post_comunicacao():
    d = request.get_json()
    return jsonify({"id": registrar_comunicacao(d["cliente_id"], d["tipo"],
                  d["destinatario"], d["mensagem"])}), 201

# ===================== RH =====================
@api_enterprise_bp.route('/api/funcionarios', methods=['GET'])
@login_required
def get_funcionarios():
    return jsonify(listar_funcionarios(
        request.args.get("ativo", "1") == "1",
        filial_id=1
    ))

@api_enterprise_bp.route('/api/funcionarios', methods=['POST'])
@login_required
@gerente_required
def post_funcionario():
    d = request.get_json()
    return jsonify({"id": criar_funcionario(d["nome"], d["cargo"],
                  d.get("salario_base", 0), d.get("utilizador_id"))}), 201

@api_enterprise_bp.route('/api/presencas', methods=['GET'])
@login_required
def get_presencas():
    return jsonify(listar_presencas(request.args.get("funcionario_id", type=int),
                   dias=request.args.get("dias", 30, type=int)))

@api_enterprise_bp.route('/api/presencas', methods=['POST'])
@login_required
@gerente_required
def post_presenca():
    d = request.get_json()
    registrar_presenca(d["funcionario_id"], d.get("hora_entrada"), d.get("hora_saida"))
    return jsonify({"ok": True}), 201

@api_enterprise_bp.route('/api/comissoes', methods=['GET'])
@login_required
def get_comissoes():
    return jsonify(listar_comissoes(request.args.get("funcionario_id", type=int),
                   pago=request.args.get("pago", type=int)))

@api_enterprise_bp.route('/api/comissoes', methods=['POST'])
@login_required
@gerente_required
def post_comissao():
    d = request.get_json()
    return jsonify({"valor_comissao": registrar_comissao(d["funcionario_id"],
                  d["venda_id"], d["valor_venda"], d["percentagem"])}), 201

@api_enterprise_bp.route('/api/comissoes/<int:id>/pagar', methods=['POST'])
@login_required
@gerente_required
def pagar_comissao_route(id):
    pagar_comissao(id)
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/funcionarios/<int:id>', methods=['PUT'])
@login_required
@gerente_required
def put_funcionario(id):
    d = request.get_json()
    return jsonify({"id": editar_funcionario(id, d["nome"], d["cargo"],
                  d.get("salario_base", 0))})

@api_enterprise_bp.route('/api/funcionarios/<int:id>', methods=['DELETE'])
@login_required
@gerente_required
def delete_funcionario(id):
    excluir_funcionario(id)
    return jsonify({"ok": True})

# ===================== FOLHA DE SALÁRIO =====================
@api_enterprise_bp.route('/api/folhas-salario', methods=['GET'])
@login_required
def get_folhas():
    return jsonify(listar_folhas(
        mes=request.args.get("mes", type=int),
        ano=request.args.get("ano", type=int),
        funcionario_id=request.args.get("funcionario_id", type=int),
        status=request.args.get("status")
    ))

@api_enterprise_bp.route('/api/folhas-salario/processar', methods=['POST'])
@login_required
@gerente_required
def post_processar_folha():
    d = request.get_json()
    mes = d.get("mes")
    ano = d.get("ano")
    if not mes or not ano:
        return jsonify({"erro": "Mês e ano são obrigatórios"}), 400
    ids = processar_folha(mes, ano)
    return jsonify({"ids": ids, "quantidade": len(ids)}), 201

@api_enterprise_bp.route('/api/folhas-salario/<int:id>', methods=['PUT'])
@login_required
@gerente_required
def put_folha(id):
    d = request.get_json()
    atualizar_folha(id, d)
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/folhas-salario/<int:id>/pagar', methods=['POST'])
@login_required
@gerente_required
def pagar_folha_route(id):
    d = request.get_json()
    pagar_folha(id, d.get("data_pagamento"))
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/folhas-salario/<int:id>', methods=['DELETE'])
@login_required
@gerente_required
def delete_folha(id):
    excluir_folha(id)
    return jsonify({"ok": True})

# ===================== PAGAMENTO DE ALUGUER =====================
@api_enterprise_bp.route('/api/alugueres', methods=['GET'])
@login_required
def get_alugueres():
    return jsonify(listar_alugueres(
        mes=request.args.get("mes", type=int),
        ano=request.args.get("ano", type=int),
        status=request.args.get("status")
    ))

@api_enterprise_bp.route('/api/alugueres', methods=['POST'])
@login_required
@gerente_required
def post_aluguer():
    d = request.get_json()
    return jsonify({"id": criar_aluguer(
        d["descricao"], d.get("proprietario", ""),
        d["valor"], d.get("data_vencimento", ""),
        d["mes"], d["ano"],
        d.get("observacao", "")
    )}), 201

@api_enterprise_bp.route('/api/alugueres/<int:id>/pagar', methods=['POST'])
@login_required
@gerente_required
def pagar_aluguer_route(id):
    d = request.get_json()
    pagar_aluguer(id, d.get("data_pagamento"))
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/alugueres/<int:id>', methods=['DELETE'])
@login_required
@gerente_required
def delete_aluguer(id):
    excluir_aluguer(id)
    return jsonify({"ok": True})

# ===================== DASHBOARD ENTERPRISE =====================
@api_enterprise_bp.route('/api/enterprise/dashboard', methods=['GET'])
@login_required
def get_enterprise_dashboard():
    kpis = obter_kpis()
    kpis_vendas = obter_kpis_vendas()
    receita_despesa = obter_receita_despesa_mensal(6)
    vendas_mensais = obter_vendas_mensais(6)
    top_clientes = obter_top_clientes_fidelidade(5)
    comparativo = obter_comparativo_filiais()
    stock_critico = obter_produtos_stock_critico(10)
    return jsonify({
        "kpis": {**kpis, **kpis_vendas},
        "receita_despesa": receita_despesa,
        "vendas_mensais": vendas_mensais,
        "top_clientes": top_clientes,
        "comparativo_filiais": comparativo,
        "stock_critico": stock_critico
    })

# ===================== FISCAL MUNICIPAL =====================
@api_enterprise_bp.route('/api/fiscal-municipal/tipos', methods=['GET'])
def get_fiscal_municipal_tipos():
    return jsonify(listar_tipos())

@api_enterprise_bp.route('/api/fiscal-municipal', methods=['GET'])
def get_fiscal_municipal():
    lista = listar_fiscal_municipal(request.args.get("status"))
    resumo = obter_resumo_fiscal_municipal()
    return jsonify({"lista": lista, "resumo": resumo})

@api_enterprise_bp.route('/api/fiscal-municipal', methods=['POST'])
def post_fiscal_municipal():
    d = request.get_json()
    return jsonify({"id": criar_fiscal_municipal(
        d["tipo"], d.get("descricao", ""), d["valor"],
        d["data_vencimento"], d.get("observacao", ""),
        d.get("filial_id", 1)
    )}), 201

@api_enterprise_bp.route('/api/fiscal-municipal/<int:id>/pagar', methods=['POST'])
def pagar_fiscal_municipal_route(id):
    d = request.get_json()
    if pagar_fiscal_municipal(id, d["valor_pago"], d["data_pagamento"], d.get("observacao", "")):
        return jsonify({"ok": True})
    return jsonify({"erro": "Taxa não encontrada"}), 400

@api_enterprise_bp.route('/api/fiscal-municipal/<int:id>', methods=['DELETE'])
def delete_fiscal_municipal(id):
    excluir_fiscal_municipal(id)
    return jsonify({"ok": True})

# ===================== CARGAS =====================
@api_enterprise_bp.route('/api/cargas', methods=['GET'])
def get_cargas():
    status = request.args.get("status")
    return jsonify(listar_cargas(status))

@api_enterprise_bp.route('/api/cargas', methods=['POST'])
def post_carga():
    d = request.get_json()
    return jsonify({"id": criar_carga(
        d["destino"], d["data_inicio"],
        d.get("valor_combinado", 0),
        d.get("observacao", ""),
        d.get("filial_id", 1)
    )}), 201

@api_enterprise_bp.route('/api/cargas/<int:id>/finalizar', methods=['POST'])
def finalizar_carga_route(id):
    d = request.get_json()
    finalizar_carga(id, d.get("data_fim", ""))
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/cargas/<int:id>', methods=['DELETE'])
def delete_carga(id):
    excluir_carga(id)
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/cargas/<int:id>/pagar', methods=['POST'])
def pagar_carga_route(id):
    d = request.get_json()
    if pagar_carga(id, d.get("data_pagamento", "")):
        return jsonify({"ok": True})
    return jsonify({"erro": "Carga já paga ou não finalizada"}), 400

@api_enterprise_bp.route('/api/cargas/<int:id>/acerto', methods=['GET'])
def get_acerto_carga(id):
    acerto = obter_acerto(id)
    if acerto:
        return jsonify(acerto)
    return jsonify({"erro": "Carga não encontrada"}), 404

@api_enterprise_bp.route('/api/adiantamentos', methods=['GET'])
def get_adiantamentos():
    carga_id = request.args.get("carga_id", type=int)
    funcionario_id = request.args.get("funcionario_id", type=int)
    return jsonify(listar_adiantamentos(carga_id, funcionario_id))

@api_enterprise_bp.route('/api/adiantamentos', methods=['POST'])
def post_adiantamento():
    d = request.get_json()
    return jsonify({"id": registrar_adiantamento(
        d["carga_id"], d["funcionario_id"],
        d["valor"], d["data"],
        d.get("observacao", "")
    )}), 201

@api_enterprise_bp.route('/api/adiantamentos/<int:id>', methods=['DELETE'])
def delete_adiantamento(id):
    excluir_adiantamento(id)
    return jsonify({"ok": True})

# ===================== ADIANTAMENTOS SALARIAIS =====================
@api_enterprise_bp.route('/api/adiantamentos-salariais', methods=['GET'])
def get_adiantamentos_salariais():
    return jsonify(listar_adiantamentos_salariais(
        funcionario_id=request.args.get("funcionario_id", type=int),
        processado=request.args.get("processado", type=int)
    ))

@api_enterprise_bp.route('/api/adiantamentos-salariais', methods=['POST'])
def post_adiantamento_salarial():
    d = request.get_json()
    return jsonify({"id": registrar_adiantamento_salarial(
        d["funcionario_id"], d["valor"], d["data"], d.get("observacao", "")
    )}), 201

@api_enterprise_bp.route('/api/adiantamentos-salariais/<int:id>', methods=['DELETE'])
def delete_adiantamento_salarial(id):
    excluir_adiantamento_salarial(id)
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/adiantamentos-salariais/pendentes/<int:funcionario_id>', methods=['GET'])
def get_adiantamentos_pendentes_total(funcionario_id):
    return jsonify({"total": total_adiantamentos_pendentes_funcionario(funcionario_id)})

# ===================== PERMISSÕES =====================
@api_enterprise_bp.route('/api/permissoes/tipos', methods=['GET'])
@login_required
def get_tipos_permissao():
    return jsonify([{"chave": k, "label": v} for k, v in PERMISSOES_DISPONIVEIS])

@api_enterprise_bp.route('/api/permissoes/<int:utilizador_id>', methods=['GET'])
@login_required
def get_permissoes(utilizador_id):
    return jsonify(listar_permissoes_utilizador(utilizador_id))

@api_enterprise_bp.route('/api/permissoes/<int:utilizador_id>', methods=['POST'])
@login_required
@gerente_required
def post_permissoes(utilizador_id):
    d = request.get_json()
    definir_permissoes(utilizador_id, d.get("permissoes", []))
    registrar("atualizar_permissoes", "utilizador", utilizador_id, f"Permissões atualizadas")
    return jsonify({"ok": True})

@api_enterprise_bp.route('/api/permissoes', methods=['GET'])
@login_required
def get_permissoes_todos():
    return jsonify(listar_permissoes_todos())

# ===================== AUDITORIA =====================
@api_enterprise_bp.route('/api/auditoria', methods=['GET'])
@login_required
def get_auditoria():
    return jsonify(listar(
        limite=request.args.get("limite", 200, type=int),
        entidade=request.args.get("entidade"),
        utilizador_id=request.args.get("utilizador_id", type=int)
    ))

@api_enterprise_bp.route('/api/auditoria/resumo', methods=['GET'])
@login_required
def get_auditoria_resumo():
    return jsonify({
        "hoje": resumo_hoje(),
        "por_data": listar_resumo_por_data(request.args.get("dias", 30, type=int))
    })
