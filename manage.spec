# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['manage.py'],
             pathex=['/home/ubuntu/MarkSystem'],
             binaries=[],
             datas=[],
             hiddenimports=['rest_framework.authentication', 'rest_framework.permissions', 'rest_framework.parsers', 'rest_framework.negotiation', 'rest_framework.metadata', 'rest_framework.apps', 'corsheaders', 'corsheaders.middleware', 'xgboost'],
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
          name='manage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
