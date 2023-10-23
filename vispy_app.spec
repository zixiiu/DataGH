# -*- mode: python -*-
import sys
from PyInstaller.compat import is_win, is_darwin, is_linux
from PyInstaller.utils.hooks import collect_submodules,collect_dynamic_libs
import vispy.glsl
import vispy.io
import freetype

block_cipher = None

data_files = [
    (os.path.dirname(vispy.glsl.__file__), os.path.join("vispy", "glsl")),
    (os.path.join(os.path.dirname(vispy.io.__file__), "_data"), os.path.join("vispy", "io", "_data")),
    (os.path.dirname(vispy.util.__file__), os.path.join("vispy", "util")),
    (os.path.dirname(freetype.__file__), os.path.join("freetype")),
]

hidden_imports = [
    "vispy.ext._bundled.six",
    "vispy.app.backends._wx",
    "vispy.app.backends._pyqt5",
    "freetype"
]

if is_win:
    hidden_imports += collect_submodules("encodings")

a = Analysis(['vispy_app.py'],
             pathex=['C:\\sixdof\\telegraph2'],
             datas=data_files,
             hiddenimports=hidden_imports,
             binaries=[],
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
          name='vispy_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)

exe2 = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='vispy_app_large_font',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)