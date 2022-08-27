from cx_Freeze import setup, Executable
from __c import C
import sys

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", 'PIL', 'mutagen', 'shutil', 'random', 'pickle', 'threading', 'io', 'urlvalidator', 'win32gui', 'psutil', 'pyglet', 'youtube_dl'], "includes": ["tkinter", ], "excludes": ['numpy', ]}

# GUI applications require a different base on Windows (the default is for a
# console application).

base = None
if sys.platform == 'win32':
    base = "Win32GUI"

player = Executable(
    script="mp.__init__.py",
    targetName=C.ExeName,
    base=base,
    icon="sdk//icons//app.ico"
    )

reg_exe = Executable(
    script="reg.__init__.py",
    targetName=C.RegExeName,
    base=base,
    icon="sdk//icons//app.ico"
    )

updator_exe = Executable(
    script="update.__init__.py",
    targetName=C.UpdateExeName,
    base=base,
    icon="sdk//icons//app.ico"
    )

uninstall_exe = Executable(
    script="uninstall.__init__.py",
    targetName=C.UnInstallerExeName,
    base=base,
    icon="sdk//icons//app.ico"
    )


setup(
    name=C.ExeName,
    version=C.Version,
    description=C.Description,
    author=C.Author,
    options={"build_exe": build_exe_options},
    executables=[player, reg_exe, updator_exe, uninstall_exe])
