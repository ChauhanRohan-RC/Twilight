import os
import pickle
from __c import C

dir_to_save = C.main_dir

info_dic = {'zip_name': 'main.zip',
            'exe_in_zip': [f'{C.RegExeName}.exe', ],
            'soft_name': C.ExeName,
            'version': C.Version,
            'soft_author': C.Author,
            'soft_des': C.Description,
            'uninstall_key_name': C.ExeName,
            'main_exe_name': C.ExeName}

with open(os.path.join(dir_to_save, 'info.cc'), 'wb+') as _f:
    pickle.dump(info_dic, _f)
