import os
import pickle
from __c import C, U


""" update contents """
update_codes = ('__c',
'__classes',
'main_player',
'Mediaplayer',
'reg',
'reg_api',
'setup',
'uninstall',
'update',
'winfonts')  # only name without ext of code (.py) files

update_icons = ()  # full name with ext of icons

update_config = ()  # full name with ext of config files

# ............................................................
update_info = {'code': {}, 'icons': {}, 'config': {}, 'version': ''}

for _code_name in update_codes:
    code_cache_path = os.path.join(C.pycache_dir, f'{_code_name}.cpython-37.pyc')
    if os.path.exists(code_cache_path):
        with open(code_cache_path, 'rb') as _c_file:
            update_info['code'][f'{_code_name}.pyc'] = _c_file.read()
    else:
        print(f'no cache availabel for {_code_name}, compile one first')

for _icon_fname in update_icons:
    _i_path = os.path.join(C.icons_dir, _icon_fname)
    if os.path.exists(_i_path):
        with open(_i_path, 'rb') as _i_file:
            update_info['icons'][_icon_fname] = _i_file.read()
    else:
        print(f'no icon present: {_icon_fname}, add one first')


for _c_fname in update_config:
    config_file_path = os.path.join(C.sdk_dir, _c_fname)
    if os.path.exists(config_file_path):
        with open(config_file_path, 'rb') as _config_file:
            update_info['config'][_c_fname] = _config_file.read()
    else:
        print(f'no config file present: {_c_fname}, add one first')


""" setting version and saving for script """
old_ver = C.Version
new_ver = U.get_new_ver(old_ver)
update_info['version'] = new_ver
with open(C.VersionFile, 'w+') as _ver_file:
    _ver_file.write(new_ver)

""" should have '_' for separating name with new version """
update_file_path = os.path.join(C.sdk_dir, f'Twilight_{new_ver}{C.UpdateFileExt}')
with open(update_file_path, 'wb+') as __Update_file:
    pickle.dump(update_info, __Update_file)

print(f"Updated from version {old_ver} -> {new_ver}")