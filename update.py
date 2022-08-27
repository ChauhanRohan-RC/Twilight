import os
import sys
from tkinter import Tk, filedialog, messagebox
from zipfile import ZipFile
import pickle
from subprocess import Popen
import ctypes
from __c import C, U


def is_admin():
    """ returns 1 if admin ,0 otherwise"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as __admin_e:
        print(__admin_e)
        return 0


def run_as_admin(executable, arg=None):
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', executable, arg, None, 1)


class Update:

    def __init__(self, plz_update_file):
        self.update_file_path = plz_update_file
        self.main_dir = C.main_dir
        self.update_file_ext = C.UpdateFileExt
        self.config_dir = C.sdk_dir

        self.version_file = C.VersionFile
        self.icons_dir = C.icons_dir

        self.lib_zip_path = C.library_zip               # library zip path
        self.lib_dir = os.path.dirname(self.lib_zip_path)
        self._temp_lib_dir = os.path.join(self.lib_dir, '__temp_lib')  # used to extract library.zip temporarily

        self.update_bat_path = os.path.join(self.lib_dir, '__update.bat')  # to update library.zip
        # self.vbs_file_path = os.path.join(self.lib_dir, '__hidden_update.vbs')  # to execute without console window

        """
        info dictionary loaded from update file in form 
                                {'code': {'file1.pyc': file1 data, 'file2.pyc': file2 data...},
                                 'icons': {'icon1.png': data, 'icon2.ico': data.....},
                                 'version': 'new_version in form of 8.4'
                                 'config': {'file1.cc': file1 data, 'file2.cc': file2 data...}, #  added to config_dir
                                }               
        """
        self.info_dic = None

        self.code_updated = False
        self.icons_updated = False
        self.config_updated = False
        self.version_updated = False

        self.errors = []

    def load_info(self):
        if os.path.isfile(self.update_file_path) and os.path.splitext(self.update_file_path)[1] == self.update_file_ext:
            try:
                with open(self.update_file_path, 'rb') as __uf:
                    self.info_dic = pickle.load(__uf)
            except Exception as e:
                print(e)
            else:
                return True
                # version check
                # if 'version' in self.info_dic:
                #     if U.get_new_ver(C.Version) == self.info_dic['version']:
                #         return True
        return False

    def _join_temp_path(self, plz_path):
        return os.path.join(self._temp_lib_dir, plz_path)

    def update(self, load_info=False):
        self.errors.clear()
        if load_info:
            code_ = self.load_info()
            if not code_:
                return False

        # 1. Updating code if any
        if 'code' in self.info_dic:
            try:
                # 1. Extracting lib to temp dir
                os.makedirs(self._temp_lib_dir)
                with ZipFile(self.lib_zip_path, 'r') as _p_lib:
                    _p_lib.extractall(self._temp_lib_dir)

                # 2. Modifying data in temp
                _code_dic = self.info_dic['code']
                for _c_name, _c_data in _code_dic.items():
                    with open(os.path.join(self._temp_lib_dir, _c_name), 'wb+') as _c_file:
                        _c_file.write(_c_data)

                self.init_update_seq()
            except Exception as _code_e:
                print(_code_e)
                self.code_updated = False
                self.errors.append('code')
            else:
                self.code_updated = True
        else:
            self.code_updated = False

        # 2. Updating icons if any
        if 'icons' in self.info_dic:
            try:
                _icons_dic = self.info_dic['icons']
                for _n_icon, _d_icon in _icons_dic.items():
                    with open(os.path.join(self.icons_dir, _n_icon), 'wb+') as _i_file:
                        _i_file.write(_d_icon)
            except Exception as _icons_e:
                print(_icons_e)
                self.icons_updated = False
                self.errors.append('icon')
            else:
                self.icons_updated = True
        else:
            self.icons_updated = False

        # 3. Updating config files if any
        if 'config' in self.info_dic:
            try:
                _config_dic = self.info_dic['config']
                for _n_config, _d_config in _config_dic.items():
                    with open(os.path.join(self.config_dir, _n_config), 'wb+') as _config_file:
                        _config_file.write(_d_config)
            except Exception as _config_e:
                print(_config_e)
                self.config_updated = False
                self.errors.append('config')
            else:
                self.config_updated = True
        else:
            self.config_updated = False

        # 4. Updating version if any
        if 'version' in self.info_dic:
            try:
                _ver = self.info_dic['version']
                with open(self.version_file, 'w+') as _ver_file:
                    _ver_file.write(_ver)
            except Exception as _ver_e:
                print(_ver_e)
                self.version_updated = False
                self.errors.append('version')
            else:
                self.version_updated = True
        else:
            self.version_updated = False

    def init_update_seq(self):
        # 1. zip temp directory to library.zip
        # 2. remove temp dir

        update_line = f'powershell.exe "& Compress-Archive -Path ' + f"'{self._temp_lib_dir}\\*'" + f' -DestinationPath ' + f"'{self.lib_zip_path}'" + ' -force"'
        rmdir_line = f'rmdir /Q /S "{self._temp_lib_dir}"'

        with open(self.update_bat_path, 'w+') as bat_file:
            bat_file.writelines((update_line, "\n", rmdir_line))

        # to execute without console window
        # with open(self.vbs_file_path, 'w+') as vbs_file:
        #     vbs_file.write(f'CreateObject("Wscript.Shell").Run """{self.update_bat_path}""", 0, True')
        #
        # return self.vbs_file_path


def main(update_file=None, update_info=None):
    win = Tk()
    win.withdraw()

    # loading update file if none
    if not update_file:
        update_file = filedialog.askopenfilename(title='Browse Update file', initialdir="C;\\", filetypes=((f'Update File ({C.UpdateFileExt})', f'*{C.UpdateFileExt}'), ), master=win)
        if not update_file:
            win.destroy()
            return

    updator = Update(plz_update_file=update_file)

    # manually loading update info
    if not update_info:
        _code = updator.load_info()
        if not _code:
            messagebox.showerror('Error', 'Update Failed, package may be corrupted or deprecated', parent=win)
            win.destroy()
            return
    else:
        # careful
        updator.info_dic = update_info

    # killing media player if running
    if U.is_running(C.ExeName):
        from __classes import WinHandler
        __wh = WinHandler()
        __wh.close_window(C.WinTitleBarText, C.WinClass)

    updator.update()
    if not updator.errors:  # no errors
        # updating the registry entries
        _reg_p = Popen([os.path.join(C.main_dir, C.RegExeName + '.exe')])
        _reg_p.wait()

        # main update
        if updator.code_updated and os.path.exists(updator.update_bat_path):            # init update seq
            # os.startfile(updator.vbs_file_path)
            _main_p = Popen([updator.update_bat_path])
            _main_p.wait()
        messagebox.showinfo('Update Complete', 'Patch has been integrated successfully', parent=win)
        win.destroy()
        sys.exit()
    else:
        messagebox.showerror('Error', f'Update Failed, package may be corrupted or deprecated\n Errors: {updator.errors}', parent=win)
        win.destroy()

    win.mainloop()


__update_file = sys.argv[1] if len(sys.argv) > 1 else None
if is_admin():
    # main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    main(update_file=__update_file)
else:
    run_as_admin(sys.executable, __update_file)

sys.exit()
