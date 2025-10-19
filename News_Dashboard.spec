# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('news.png', '.'),
    ],
    hiddenimports=[
        'eel',
        'bottle',
        'bottle_websocket',
        'gevent',
        'gevent.socket',
        'geventwebsocket',
        'geventwebsocket.handler',
        'geventwebsocket.websocket',
        'bs4',
        'lxml',
        'deep_translator',
        'deep_translator.google',
        'deep_translator.constants',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'tkinter',
        # All scraper modules
        'fastighetsvarlden_scraper',
        'cision_scraper',
        'lokalguiden_scraper',
        'di_scraper',
        'fastighetsnytt_scraper',
        'nordicpropertynews_scraper',
        # Config module
        'config',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='News Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='news.png',
)

