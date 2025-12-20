# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files


a = Analysis(
    ['main.py'],
    # A linha abaixo precisa do seu caminho exato. Se você estava usando pathex=[],
    # o PyInstaller pode assumir o diretório atual, mas deixei o placeholder conforme instruído:
    pathex=['/Users/usuario/Projetos/Python/Sys_Fornecedor'], 
    binaries=[],
    # ESTAS SÃO AS LINHAS QUE GARANTEM O FUNCIONAMENTO DO PDF E DO PANDAS:
    datas=collect_data_files('reportlab'),
    # CORREÇÃO: Adicionando reportlab.rl_settings para forçar as configurações internas
    hiddenimports=['pandas._libs.tslibs.timedeltas', 'reportlab.rl_settings'],
    # FIM DAS CORREÇÕES
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [], # Binários e dados não vão no EXE no modo one-directory
    exclude_binaries=True,
    name='Sys_Fornecedor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Modo GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 1. DEFINE O COLLECT (coleção de arquivos)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sys_Fornecedor',
)

# 2. USA O COLLECT (coll) para criar o BUNDLE (.app)
app = BUNDLE(
    coll, 
    name='Sys_Fornecedor.app', # Nome do pacote .app
    icon=None, # Aqui você adicionaria o caminho para um ícone (.icns) se tivesse um
    bundle_name='Sys_Fornecedor'
)