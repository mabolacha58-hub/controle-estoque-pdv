# Controle de Estoque — Sistema PDV

Sistema completo de controle de estoque e ponto de venda (PDV) desenvolvido em Python/Flask.

## Funcionalidades

- **PDV** — Venda rápida com leitor de código de barras
- **Estoque** — Cadastro de produtos, categorias, controlo de stock mínimo
- **Movimentações** — Entradas e saídas com histórico completo
- **Clientes** — Cadastro, saldo, limite de crédito
- **Fornecedores** — Cadastro e gestão
- **Utilizadores** — Perfis gerente/caixa com autenticação por PIN
- **Caixa** — Abertura/fecho diário com controlo de vendas
- **Relatórios** — Vendas, lucro, stock, PDF exportável
- **Backup** — Automático e manual
- **Dashboard** — Visão geral com gráficos

## Credenciais Padrão

| Utilizador     | PIN  | Perfil   |
|----------------|------|----------|
| Administrador  | 1234 | gerente  |
| Caixa 1        | 0000 | caixa    |

## Requisitos

- Python 3.11+
- pip

## Setup Rápido

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python app.py
```

Acesse http://localhost:5000

## Setup com Docker

```bash
docker compose up -d
```

Acesse http://localhost:5000

## Variáveis de Ambiente

| Variável     | Descrição                    | Padrão            |
|--------------|------------------------------|-------------------|
| `SECRET_KEY` | Chave secreta Flask (CSRF)   | (auto-gerada)     |
| `DB_PATH`    | Caminho do banco SQLite      | `controle_estoque.db` |

## Testes

```bash
pytest tests/ -v
```

## Estrutura do Projeto

```
controle_estoque/
├── app.py                 # Inicialização da aplicação
├── config.py              # Configurações
├── database.py            # Conexão com banco SQLite
├── auth.py                # Autenticação/autorização
├── extensions.py          # Extensões Flask (CSRF)
├── models.py              # Modelos de dados
├── routes/                # Rotas (controllers)
│   ├── pages.py           # Páginas renderizadas (SSR)
│   ├── api_produtos.py    # API de produtos
│   ├── api_vendas.py      # API de vendas (PDV)
│   ├── api_cadastros.py   # API clientes/fornecedores/utilizadores
│   ├── api_caixa.py       # API caixa
│   ├── api_movimentacoes.py # API movimentações/categorias
│   ├── api_config.py      # API configurações/backup
│   └── api_relatorios.py  # API relatórios
├── services/              # Camada de serviço (lógica de negócio)
│   ├── base.py            # Gerenciadores de conexão
│   ├── produto_service.py
│   ├── venda_service.py
│   ├── cliente_service.py
│   ├── fornecedor_service.py
│   ├── utilizador_service.py
│   ├── caixa_service.py
│   ├── movimento_service.py
│   ├── categoria_service.py
│   ├── config_service.py
│   ├── relatorio_service.py
│   ├── dashboard_service.py
│   ├── audit_logger.py    # Log de mutações
│   └── backup_service.py  # Backup automático
├── templates/             # HTML (Jinja2)
├── static/                # CSS/JS
├── utils/                 # Utilitários (PDF)
├── tests/                 # Testes (40 testes pytest)
├── Dockerfile
└── docker-compose.yml
```
