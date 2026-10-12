# -*- mode: python ; coding: utf-8 -*-

import os
block_cipher = None
BASE = os.path.abspath('.')

a = Analysis(
    ['launcher_desktop.py'],
    pathex=[BASE],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('routes', 'routes'),
        ('services', 'services'),
        ('utils', 'utils'),
        ('.env', '.'),
        ('config.py', '.'),
        ('auth.py', '.'),
        ('database.py', '.'),
        ('database_enterprise.py', '.'),
        ('extensions.py', '.'),
        ('controle_estoque.db', '.'),
    ],
    hiddenimports=[
        'flask', 'flask_wtf', 'dotenv', 'werkzeug', 'webview',
        'routes.pages', 'routes.api_produtos', 'routes.api_movimentacoes',
        'routes.api_vendas', 'routes.api_cadastros', 'routes.api_caixa',
        'routes.api_config', 'routes.api_relatorios', 'routes.api_enterprise',
        'routes.pages_enterprise',
        'services.backup_service', 'services.audit_logger',
        'services.produto_service', 'services.categoria_service',
        'services.cliente_service', 'services.movimento_service',
        'services.venda_service', 'services.caixa_service',
        'services.config_service', 'services.relatorio_service',
        'services.permissoes_service', 'services.utilizador_service',
        'services.fornecedor_service', 'services.compra_service',
        'services.carga_service', 'services.crm_service',
        'services.financeiro_service', 'services.rh_service',
        'services.dashboard_service', 'services.empresa_service',
        'services.fiscal_service', 'services.fiscal_at_service',
        'services.fiscal_municipal_service',
        'services.dashboard_enterprise_service',
        'services.auditoria_service', 'services.base',
        'utils.pdf', 'utils.validation',
        'clr_loader', 'pythonnet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ControleEstoqueDesktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='electron/icon_profissional.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ControleEstoqueDesktop',
)
