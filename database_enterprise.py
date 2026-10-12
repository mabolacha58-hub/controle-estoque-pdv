import sqlite3, os, logging
from database import get_db_path

log = logging.getLogger(__name__)

def migrate_enterprise():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.executescript('''
        -- ===================== MULTI-EMPRESA / MULTI-FILIAL =====================
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nif TEXT,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            logotipo TEXT,
            data_criacao TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS filiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL DEFAULT 1,
            nome TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );

        CREATE TABLE IF NOT EXISTS produto_filial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            filial_id INTEGER NOT NULL DEFAULT 1,
            quantidade REAL DEFAULT 0,
            quantidade_minima REAL DEFAULT 0,
            preco_venda REAL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id),
            UNIQUE(produto_id, filial_id)
        );

        -- ===================== LOTE E VALIDADE =====================
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            filial_id INTEGER DEFAULT 1,
            codigo_lote TEXT NOT NULL,
            quantidade REAL DEFAULT 0,
            data_fabricacao TEXT,
            data_validade TEXT,
            preco_custo REAL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        -- ===================== COMPRAS =====================
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor_id INTEGER,
            filial_id INTEGER DEFAULT 1,
            numero_pedido TEXT,
            data_pedido TEXT DEFAULT (datetime('now','localtime')),
            data_rececao TEXT,
            status TEXT DEFAULT 'pendente',
            total REAL DEFAULT 0,
            observacao TEXT,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS compra_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compra_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade REAL DEFAULT 1,
            preco_unitario REAL DEFAULT 0,
            iva REAL DEFAULT 0,
            total REAL DEFAULT 0,
            quantidade_recebida REAL DEFAULT 0,
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );

        -- ===================== FINANCEIRO =====================
        CREATE TABLE IF NOT EXISTS bancos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            numero_conta TEXT,
            titular TEXT,
            saldo REAL DEFAULT 0,
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS contas_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor_id INTEGER,
            compra_id INTEGER,
            descricao TEXT,
            valor REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            data_vencimento TEXT,
            data_pagamento TEXT,
            status TEXT DEFAULT 'pendente',
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id),
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            venda_id INTEGER,
            descricao TEXT,
            valor REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            data_vencimento TEXT,
            data_recebimento TEXT,
            status TEXT DEFAULT 'pendente',
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS movimentos_financeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            categoria TEXT,
            descricao TEXT,
            valor REAL DEFAULT 0,
            banco_id INTEGER,
            forma_pagamento TEXT,
            data_movimento TEXT DEFAULT (datetime('now','localtime')),
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (banco_id) REFERENCES bancos(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS conciliacao_bancaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            banco_id INTEGER NOT NULL,
            data_inicio TEXT,
            data_fim TEXT,
            saldo_extrato REAL DEFAULT 0,
            saldo_sistema REAL DEFAULT 0,
            diferenca REAL DEFAULT 0,
            conciliado INTEGER DEFAULT 0,
            data_conciliacao TEXT,
            FOREIGN KEY (banco_id) REFERENCES bancos(id)
        );

        -- ===================== CRM =====================
        CREATE TABLE IF NOT EXISTS fidelizacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            pontos REAL DEFAULT 0,
            nivel TEXT DEFAULT 'bronze',
            total_compras REAL DEFAULT 0,
            ultima_compra TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS cashback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            valor REAL DEFAULT 0,
            tipo TEXT DEFAULT 'acumulo',
            venda_id INTEGER,
            data TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS comunicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            tipo TEXT DEFAULT 'sms',
            destinatario TEXT,
            mensagem TEXT,
            status TEXT DEFAULT 'pendente',
            data_envio TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        -- ===================== FISCAL (MOÇAMBIQUE) =====================
        CREATE TABLE IF NOT EXISTS series_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT NOT NULL,
            serie TEXT NOT NULL,
            numero_atual INTEGER DEFAULT 0,
            numero_maximo INTEGER DEFAULT 999999,
            ativo INTEGER DEFAULT 1,
            filial_id INTEGER DEFAULT 1,
            empresa_id INTEGER DEFAULT 1,
            UNIQUE(tipo_documento, serie, filial_id)
        );

        CREATE TABLE IF NOT EXISTS documentos_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT NOT NULL,
            serie TEXT NOT NULL,
            numero INTEGER NOT NULL,
            hash TEXT,
            qrcode TEXT,
            data_emissao TEXT DEFAULT (datetime('now','localtime')),
            cliente_id INTEGER,
            cliente_nome TEXT,
            cliente_nif TEXT,
            total REAL DEFAULT 0,
            iva_total REAL DEFAULT 0,
            status TEXT DEFAULT 'normal',
            venda_id INTEGER,
            anulado_por INTEGER,
            data_anulacao TEXT,
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (venda_id) REFERENCES movimentacoes(id)
        );

        -- ===================== RECURSOS HUMANOS =====================
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilizador_id INTEGER,
            nome TEXT NOT NULL,
            cargo TEXT,
            salario_base REAL DEFAULT 0,
            data_admissao TEXT DEFAULT (datetime('now','localtime')),
            data_demissao TEXT,
            ativo INTEGER DEFAULT 1,
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        CREATE TABLE IF NOT EXISTS presencas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            data TEXT DEFAULT (datetime('now','localtime')),
            hora_entrada TEXT,
            hora_saida TEXT,
            horas_trabalhadas REAL DEFAULT 0,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        );

        CREATE TABLE IF NOT EXISTS comissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            venda_id INTEGER,
            valor_venda REAL DEFAULT 0,
            percentagem REAL DEFAULT 0,
            valor_comissao REAL DEFAULT 0,
            pago INTEGER DEFAULT 0,
            data TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        );

        -- ===================== METAS E INDICADORES =====================
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT,
            valor_meta REAL DEFAULT 0,
            valor_atual REAL DEFAULT 0,
            periodo_inicio TEXT,
            periodo_fim TEXT,
            filial_id INTEGER,
            funcionario_id INTEGER,
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        );

        -- ===================== TRANSFERÊNCIA ENTRE FILIAIS =====================
        CREATE TABLE IF NOT EXISTS transferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade REAL DEFAULT 0,
            filial_origem INTEGER NOT NULL,
            filial_destino INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            data_criacao TEXT DEFAULT (datetime('now','localtime')),
            data_conclusao TEXT,
            observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (filial_origem) REFERENCES filiais(id),
            FOREIGN KEY (filial_destino) REFERENCES filiais(id)
        );

        -- ===================== ÍNDICES =====================
        CREATE INDEX IF NOT EXISTS idx_prod_filial_produto ON produto_filial(produto_id);
        CREATE INDEX IF NOT EXISTS idx_prod_filial_filial ON produto_filial(filial_id);
        CREATE INDEX IF NOT EXISTS idx_lotes_produto ON lotes(produto_id);
        CREATE INDEX IF NOT EXISTS idx_lotes_validade ON lotes(data_validade);
        CREATE INDEX IF NOT EXISTS idx_compras_fornecedor ON compras(fornecedor_id);
        CREATE INDEX IF NOT EXISTS idx_compras_status ON compras(status);
        CREATE INDEX IF NOT EXISTS idx_ctas_pagar_status ON contas_pagar(status);
        CREATE INDEX IF NOT EXISTS idx_ctas_receber_status ON contas_receber(status);
        CREATE INDEX IF NOT EXISTS idx_mov_financeiros_data ON movimentos_financeiros(data_movimento);
        CREATE INDEX IF NOT EXISTS idx_doc_fiscais_tipo ON documentos_fiscais(tipo_documento);
        CREATE INDEX IF NOT EXISTS idx_doc_fiscais_serie ON documentos_fiscais(serie, numero);
        CREATE INDEX IF NOT EXISTS idx_presencas_data ON presencas(data);
        CREATE INDEX IF NOT EXISTS idx_transferencias_status ON transferencias(status);
    ''')

    # Inserir empresa padrão se não existir
    if not c.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]:
        c.execute("INSERT INTO empresas (nome, nif) VALUES (?, ?)",
                  ("Minha Empresa", ""))

    # Inserir filial padrão se não existir
    if not c.execute("SELECT COUNT(*) FROM filiais").fetchone()[0]:
        c.execute("INSERT INTO filiais (empresa_id, nome) VALUES (?, ?)",
                  (1, "Filial Principal"))

    # Migrar quantidades existentes para produto_filial
    existentes = c.execute("SELECT COUNT(*) FROM produto_filial").fetchone()[0]
    if existentes == 0:
        c.execute('''INSERT OR IGNORE INTO produto_filial (produto_id, filial_id, quantidade, quantidade_minima)
                     SELECT id, 1, quantidade, quantidade_minima FROM produtos''')

    # Séries fiscais padrão (Moçambique)
    if not c.execute("SELECT COUNT(*) FROM series_fiscais").fetchone()[0]:
        series = [
            ("FT", "Factura"),
            ("FR", "Factura-Recibo"),
            ("GR", "Guia de Remessa"),
            ("NC", "Nota de Crédito"),
            ("ND", "Nota de Débito"),
        ]
        for sigla, _ in series:
            try:
                c.execute("INSERT INTO series_fiscais (tipo_documento, serie) VALUES (?, ?)",
                          (sigla, f"{sigla}001"))
            except Exception:
                pass

    # Add AT e-fatura columns to documentos_fiscais if missing
    for col in ["at_status", "at_mensagem", "at_data_envio", "at_xml", "at_tentativas"]:
        try:
            c.execute(f"ALTER TABLE documentos_fiscais ADD COLUMN {col} TEXT")
        except Exception:
            pass

    # AT submission log
    c.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_at_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento_fiscal_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT DEFAULT 'pendente',
            xml_enviado TEXT,
            resposta TEXT,
            data_envio TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (documento_fiscal_id) REFERENCES documentos_fiscais(id)
        )
    ''')

    # Configuração fiscal
    c.execute('''
        CREATE TABLE IF NOT EXISTS config_fiscal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT
        )
    ''')
    for chave, valor in [
        ("empresa_nif", "000000000"),
        ("empresa_nome", "Minha Empresa"),
        ("empresa_endereco", ""),
        ("empresa_telefone", ""),
        ("empresa_email", ""),
        ("at_validacao_key", "AT-MZ-DEV-KEY"),
        ("at_ambiente", "teste"),
        ("at_ultima_serializacao", ""),
    ]:
        try:
            c.execute("INSERT OR IGNORE INTO config_fiscal (chave, valor) VALUES (?, ?)", (chave, valor))
        except Exception:
            pass

    # ===================== FISCAL MUNICIPAL =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_municipal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT,
            valor REAL DEFAULT 0,
            data_vencimento TEXT,
            data_pagamento TEXT,
            valor_pago REAL DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            observacao TEXT,
            data_registo TEXT DEFAULT (datetime('now','localtime')),
            filial_id INTEGER DEFAULT 1,
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_municipal_status ON fiscal_municipal(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_municipal_vencimento ON fiscal_municipal(data_vencimento)')
    c.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_municipal_tipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT
        )
    ''')
    for tipo in [
        ("Alvará Comercial", "Licença anual para funcionamento do estabelecimento"),
        ("Taxa de Licença", "Taxa de licenciamento de atividades económicas"),
        ("Taxa de Publicidade", "Taxa de publicidade e propaganda"),
        ("Imposto Predial", "Imposto predial autárquico"),
        ("Taxa de Ocupação", "Taxa de ocupação de via pública"),
        ("Taxa de Higiene", "Taxa de higiene e salubridade"),
        ("Taxa de Estacionamento", "Taxa de estacionamento"),
        ("Multa Municipal", "Multas e penalidades municipais"),
        ("Outros", "Outros impostos e taxas municipais"),
        ("Taxa por Carga", "Taxa municipal por carga de mercadoria (300 MT)"),
    ]:
        try:
            c.execute("INSERT OR IGNORE INTO fiscal_municipal_tipos (nome, descricao) VALUES (?, ?)", tipo)
        except Exception:
            pass

    # ===================== FOLHA DE SALÁRIO =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS folhas_salario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            salario_base REAL DEFAULT 0,
            outros_descontos REAL DEFAULT 0,
            total_descontos REAL DEFAULT 0,
            salario_liquido REAL DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            data_processamento TEXT DEFAULT (datetime('now','localtime')),
            data_pagamento TEXT,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_folhas_funcionario ON folhas_salario(funcionario_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_folhas_periodo ON folhas_salario(ano, mes)')
    try:
        c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_folhas_func_periodo ON folhas_salario(funcionario_id, ano, mes)')
    except Exception:
        pass

    # ===================== PAGAMENTO DE ALUGUER =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos_aluguer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            proprietario TEXT,
            valor REAL DEFAULT 0,
            data_vencimento TEXT,
            data_pagamento TEXT,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            observacao TEXT,
            filial_id INTEGER DEFAULT 1,
            data_registo TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_aluguer_periodo ON pagamentos_aluguer(ano, mes)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_aluguer_status ON pagamentos_aluguer(status)')

    # ===================== CARGAS E ADIANTAMENTOS =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS cargas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destino TEXT NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE,
            valor_combinado REAL DEFAULT 0,
            pago INTEGER DEFAULT 0,
            data_pagamento TEXT,
            filial_id INTEGER DEFAULT 1,
            status TEXT DEFAULT 'em_andamento',
            observacao TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (filial_id) REFERENCES filiais(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS adiantamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carga_id INTEGER NOT NULL,
            funcionario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data DATE NOT NULL,
            observacao TEXT,
            FOREIGN KEY (carga_id) REFERENCES cargas(id),
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_adiantamentos_carga ON adiantamentos(carga_id)')
    try:
        c.execute("ALTER TABLE cargas ADD COLUMN pago INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE cargas ADD COLUMN data_pagamento TEXT")
    except Exception:
        pass

    # ===================== ADIANTAMENTOS SALARIAIS =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS salario_adiantamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            observacao TEXT,
            processado INTEGER DEFAULT 0,
            folha_id INTEGER,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
            FOREIGN KEY (folha_id) REFERENCES folhas_salario(id)
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sal_adiant_func ON salario_adiantamentos(funcionario_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sal_adiant_processado ON salario_adiantamentos(processado)')

    # ===================== PERMISSÕES E AUDITORIA =====================
    c.execute('''
        CREATE TABLE IF NOT EXISTS permissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilizador_id INTEGER NOT NULL,
            permissao TEXT NOT NULL,
            FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id),
            UNIQUE(utilizador_id, permissao)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilizador_id INTEGER,
            utilizador_nome TEXT,
            acao TEXT NOT NULL,
            entidade TEXT,
            entidade_id INTEGER,
            detalhes TEXT,
            ip TEXT,
            data TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (utilizador_id) REFERENCES utilizadores(id)
        )
    ''')

    conn.commit()
    conn.close()
    log.info("Migração enterprise concluída")
