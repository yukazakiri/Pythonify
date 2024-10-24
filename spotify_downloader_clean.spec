# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect ytmusicapi data files
ytmusicapi_datas = collect_data_files('ytmusicapi')

# Add FFmpeg binary for Windows
if sys.platform.startswith('win'):
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        binaries = [(ffmpeg_path, '.')]
    else:
        binaries = []
else:
    binaries = []

a = Analysis(
    ['spotify_downloader_clean.py'],
    pathex=[],
    binaries=binaries,
    datas=ytmusicapi_datas,
    hiddenimports=['pkg_resources.py2_warn'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='spotify_downloader_clean',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
