import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "threading", "os", "tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Melody",
        version = "1.0",
        description = "A music player built using Python Tkinter | www.amanchadha.com",
        options = {"build_exe": build_exe_options},
        executables = [Executable("melody.py", base=base)])