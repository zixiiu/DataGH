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

a_nom = Analysis(['vispy_app_nom.py'],
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

pyz_nom = PYZ(a_nom.pure, a_nom.zipped_data,
             cipher=block_cipher)

exe_nom = EXE(pyz_nom,
          a_nom.scripts,
          a_nom.binaries,
          a_nom.zipfiles,
          a_nom.datas,
          [],
          name='vispy_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)

a_lf = Analysis(['vispy_app_large_font.py'],
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


pyz_lf = PYZ(a_lf.pure, a_lf.zipped_data,
             cipher=block_cipher)

exe_lf = EXE(pyz_lf,
          a_lf.scripts,
          a_lf.binaries,
          a_lf.zipfiles,
          a_lf.datas,
          [],
          name='vispy_app_large_font',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)

a_gb5 = Analysis(['vispy_app_gb5.py'],
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


pyz_gb5 = PYZ(a_gb5.pure, a_gb5.zipped_data,
             cipher=block_cipher)

exe_gb5 = EXE(pyz_gb5,
          a_gb5.scripts,
          a_gb5.binaries,
          a_gb5.zipfiles,
          a_gb5.datas,
          [],
          name='vispy_app_gb5',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)