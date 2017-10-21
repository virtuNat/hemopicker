import sys
from cx_Freeze import setup, Executable

# Dependency list.
build_exe_options = {
    "packages": ["pygame"], 
    "excludes": ["tkinter", "numpy"],
    "include_files": ["textures"]
}
# Base for GUI apps on Windows.
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name = 'Hemopicker',
    version = '1.0.0',
    description = 'Fantroll Hemopicker Utility',
    author = 'virtuNat',
    license = 'GPL',
    url = 'https://github.com/virtuNat/hemopicker',
    options = {"build_exe": build_exe_options},
    executables = [Executable('hemopicker.py', base=base)]
)
