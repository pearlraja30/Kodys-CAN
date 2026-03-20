# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['application_code/run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app_config', 'app_config'),
        ('kodys', 'kodys'),
        ('templates', 'templates'),
        ('app_assets', 'app_assets'),
        ('application_code/splash_screen.png', '.'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'heartpy',
        'pyhrv',
        'spectrum',
        'nolds',
        'scipy.signal',
        'numpy',
        'app_config.wsgi',
        'app_config.settings',
    ],
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
    [],
    exclude_binaries=True,
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='run',
)
