import os
import sys
import reg_api
from __c import C, U
from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW
from __classes import WinHandler


class UnInstaller:
    def __init__(self):
        # self.main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        self.des_bat_path = os.path.join(C.main_dir, 'des_bat.bat')
        self.s_info = None
        if os.name == 'nt':
            self.s_info = STARTUPINFO()
            self.s_info.dwFlags |= STARTF_USESHOWWINDOW

        self.bg = 'white'
        self.fg = 'black'
        self.l_font = 'Times 16'
        self.notice_l_font = 'Times 11 italic'

    def force_uninstall(self):
        if U.is_running(C.ExeName):
            self.quit_win()
        self.remove_reg()
        Popen([self.des_bat_path], startupinfo=self.s_info)

    def ui_uninstall(self):
        from tkinter import Tk, messagebox
        win = Tk()
        win.overrideredirect(True)
        win.withdraw()
        remove_in = messagebox.askyesno(f'Uninstall {C.ExeName}', message=f'This will remove {C.ExeName} and all of its components for this pc\n Are you sure to continue ??',  parent=win)
        if remove_in:
            if U.is_running(C.ExeName):
                kill_in = messagebox.askyesno('Uninstall Warning', 'Process is still running!, Do you want to continue anyway ??', parent=win)
                if kill_in:
                    self.quit_win()
                else:
                    win.destroy()
                    return

            self.remove_reg()
            messagebox.showinfo('Uninstall Complete', message='Uninstall Process Complete, Updating System Info and registry will occur as this window closes....', parent=win)
            win.quit()
            win.destroy()
            Popen([self.des_bat_path], startupinfo=self.s_info)
        else:
            win.destroy()

    @staticmethod
    def quit_win():
        __wh = WinHandler()
        __wh.close_window(C.WinTitleBarText, C.WinClass)

    def remove_reg(self):
        try:
            reg_api.delete_context_menu_command(C.main_ext, C.ExeName)  # removing context menu command
            reg_api.delete_open_with(C.ExeName)  # removing open with entry
            reg_api.delete_start_menu_link(C.ExeName)  # removing shortcut
            reg_api.delete_uninstall_info(C.ExeName)  # removing uninstall info
        except Exception as _e:
            print(_e)

        with open(self.des_bat_path, 'w+') as _des_bat:
            _des_bat.write('rmdir /Q /S "%s"' % C.main_dir)


force_arg = sys.argv[1] if len(sys.argv) > 1 else None
if reg_api.is_admin():
    un_installer = UnInstaller()
    if force_arg == '-force':
        un_installer.force_uninstall()
    else:
        un_installer.ui_uninstall()
else:
    reg_api.run_as_admin(sys.executable, force_arg)
