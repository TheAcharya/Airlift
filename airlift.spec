# -*- mode: python ; coding: utf-8 -*-
import os
import certifi

block_cipher = None

spec_root = os.path.abspath(SPECPATH)

# Get the path to certifi's certificate file
certifi_cert_path = certifi.where()

a = Analysis(['airlift/__main__.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[(certifi_cert_path, '.')],  # Include certifi certificates
             hiddenimports=['certifi'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='airlift',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
