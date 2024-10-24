# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect ytmusicapi data files
ytmusicapi_datas = collect_data_files('ytmusicapi')

# Initialize binaries list
binaries = []

# Add FFmpeg binary for all platforms if it exists
if sys.platform.startswith('win'):
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
elif sys.platform.startswith('darwin'):
    ffmpeg_path = '/usr/local/bin/ffmpeg'
else:  # Linux
    ffmpeg_path = '/usr/bin/ffmpeg'

if os.path.exists(ffmpeg_path):
    binaries.append((ffmpeg_path, '.'))

a = Analysis(
    ['pythonify_clean.py'],
    pathex=[],
    binaries=binaries,
    datas=ytmusicapi_datas + [('.env', '.')],  # Include .env file
    hiddenimports=['pkg_resources.py2_warn', 'requests'],
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
    name='pythonify_clean',
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
