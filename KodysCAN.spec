# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('app_config', 'app_config'), ('kodys', 'kodys'), ('app_assets', 'app_assets'), ('config', 'config'), ('db.sqlite3', '.'), ('application_code/splash_screen.png', '.'), ('.venv_mac/lib/python3.13/site-packages/spectrum/data/DOLPHINS.wav', 'spectrum/data'), ('.venv_mac/lib/python3.13/site-packages/nolds/datasets/brown72.npy', 'nolds/datasets')]
binaries = []
hiddenimports = ['PyQt5.QtWebEngineWidgets', 'PyQt5.QtPrintSupport', 'cv2', 'setuptools', 'distutils', 'fitz', 'pymupdf', 'cryptography.fernet', 'cryptography.hazmat.backends', 'pkg_resources', 'heartpy', 'pyhrv', 'pyhrv.time_domain', 'pyhrv.frequency_domain', 'pyhrv.nonlinear', 'peakutils', 'scipy.signal', 'scipy.optimize', 'scipy.interpolate', 'scipy.stats', 'matplotlib', 'matplotlib.pyplot', 'pandas', 'serial', 'xlsxwriter', 'pdfkit', 'requests', 'psutil', 'biosppy', 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles']
datas += copy_metadata('setuptools')
datas += copy_metadata('heartpy')
tmp_ret = collect_all('heartpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyhrv')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('biosppy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('xlsxwriter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pdfkit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pkg_resources')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('setuptools')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['application_code/run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='KodysCAN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx=True,
    upx_exclude=[],
    name='KodysCAN',
)
app = BUNDLE(
    coll,
    name='KodysCAN.app',
    icon=None,
    bundle_identifier='com.kodys.can',
)
