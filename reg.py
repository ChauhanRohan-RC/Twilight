import reg_api
from __c import C
import sys
import os

if reg_api.is_admin():
    # main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    # exe_path = os.path.join(main_dir, C.ExeName + '.exe')
    # uninstall_exe_path = os.path.join(main_dir, C.UnInstallerExeName + '.exe')

    # setting context menu commands
    reg_api.set_context_command(C.main_ext, C.ContextMenuTitle, C.exe_path, C.ExeName, C.exe_path)

    # setting open with list
    reg_api.add_open_with(C.main_ext, C.exe_path, C.ExeName)

    # creating start menu shortcut
    reg_api.create_start_menu_link(C.exe_path, os.path.join(C.main_dir, 'sdk\\icons\\app.ico'))

    # adding uninstall info  (task of adding un installer)
    reg_api.add_uninstall_info(display_name=f'{C.ExeName} {C.Version} x86', uninstall_exe=C.uninstall_exe_path, publisher=C.Author, version=C.Version,
                               exe_name=C.ExeName, icon=C.exe_path, install_dir=C.main_dir)
    sys.exit(0)
else:
    reg_api.run_as_admin(sys.executable)
    sys.exit(2)
