from tkinter import Misc

import psutil
import os
import sys
from pathlib import Path

import youtube_dl

main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(os.path.realpath(__file__)))


class U:
    """ Static Utility """

    @staticmethod
    def is_running(exe_name):
        # return process id if running else 0
        exe_name = f'{exe_name}.exe'.lower()
        for p in psutil.process_iter():
            try:
                if p.name().lower() == exe_name and p.status() == psutil.STATUS_RUNNING:
                    return p.pid
            except (PermissionError, psutil.Error, AttributeError):
                pass
        return 0

    @staticmethod
    def run_count(exe_name):
        exe_name = f'{exe_name}.exe'.lower()
        __count = 0
        for p in psutil.process_iter():
            try:
                if p.name().lower() == exe_name and p.status() == psutil.STATUS_RUNNING:
                    __count += 1
            except (PermissionError, psutil.AccessDenied, AttributeError):
                pass
        return __count

    @staticmethod
    def load_version(version_file, original_version='0.0'):
        if os.path.exists(version_file):
            with open(version_file, 'r') as _v_file:
                _v = _v_file.read()
                return _v if _v else original_version
        return original_version

    @staticmethod
    def get_new_ver(old_ver_str):
        """
        :param old_ver_str: should have 2 decimals like 5.8.9
        :return: new version in form of '5.9.0' after adding 0.0.1 to old version
        """
        _a, _b, _c = tuple(map(int, old_ver_str.split('.')))
        if _c < 9:
            _c += 1
        else:
            _b += _c - 8
            _c = 0  # resetting last ver int
            if _b > 9:
                _a += _b - 9
                _b = 0  # resetting middle ver int

        return f'{_a}.{_b}.{_c}'

    @staticmethod
    def ensure_key(kwargs: dict, key: str, default: any):
        if key in kwargs:
            val = kwargs[key]
        else:
            val = default
            kwargs[key] = default
        return val

    @staticmethod
    def copy_to_clipboard(r: Misc, text: str, append: bool = False):
        if not append:
            r.clipboard_clear()
        r.clipboard_append(text)
        r.update()  # now it stays on the clipboard after the window is closed


    @staticmethod
    def is_url_youtube(url: str):
        extractors = youtube_dl.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False

    @staticmethod
    def create(path):
        try:
            with open(path, "x"):
                return True
        except FileExistsError:
            return False

    @staticmethod
    def delete(path):
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False


class C:
    """
    class containing constants of media player
    """
    VersionFile = os.path.join(main_dir, 'sdk\\version.txt')
    Version = U.load_version(version_file=VersionFile, original_version='8.7.5')

    ExeName = 'Twilight'
    RegExeName = 'REG'
    UnInstallerExeName = 'Uninstall'
    UpdateExeName = 'Update'
    UpdateFileExt = '.rcup'

    WinTitle = ExeName
    WinClass = 'TkTopLevel'
    WinTitleBarText = WinTitle
    ContextMenuTitle = f'Play with {ExeName}'
    Author = 'Rohan Chauhan'
    ContactEmail = 'com.production.rc@gamail.com'
    Description = f'{ExeName} is a media player that supports almost every ' \
                  '\naudio and video codec out there, boarding unique features and customisations'

    YT_API_KEY = "AIzaSyBthHXvchsFT7NnVinzIgkuqJ6m92bwmLM"

    aspect_ratio_list = [ None, '16:9', '4:3', '1:1', '16:10', '2.21:1', '2.35:1', '2.39:1', '5:4']

    valid_chars = {'K', 'o', '_', 'J', '2', 'B', 'u', 'i', 'F', '1', 's', 'P', '.', 'k', 'a', 'r', 'Z', 'd', 'h', 'm',
                   'q', 'S', 'O', '5', ' ', 'Y', 'Q', 'V', 'j', '-', 'C', 'v', 'T', '(', 'M', 'g', '0', '4', 'N', 'U',
                   'w', 'H', 'I', 't', 'D', 'n', 'X', 'L', ')', 'A', 'R', 'l', '6', 'b', 'f', 'p', 'z', 'W', '7', '8',
                   'x', '3', 'E', 'e', 'c', 'G', '9', 'y'}

    song_format = {'.wav', '.3ga', '.669', '.a52', '.aac', '.ac3', '.adt', '.adts', '.aif', '.aif', '.aifc', '.aiff',
                   '.amr', '.aob', '.ape', '.awb', 'caf', '.dts', '.flac', '.it', '.m4a', '.kar', '.m4b', '.m4p',
                   '.m5p', '.mid', '.mka', '.mlp', '.mod', '.mpa', '.mp1', '.mp2', '.mp3', '.mpc ', '.ogg', '.oga',
                   '.mus', '.mpga'}

    video_format = {'.mp4', '.vob', '.mkv', '.mkv', '.3g2', '.3gp', '.3gp2', '.3gpp', '.amv', '.asf', '.avi',
                    '.bik', '.bin', '.divx', '.drc', '.dv', '.f4v', '.flv ', '.gvi', '.gfx', '.iso', '.m1v,', '.m2v',
                    '.m2t', '.m2ts', '.m4v', '.mov', '.mp2', '.mp2v', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg2',
                    '.mpeg4', '.mpg', '.gif', '.webm'}

    subtitles_format = {'.srt', '.aqt', '.cvd', '.dks', '.jss', '.sub', '.ttxt', '.mpl', '.txt', '.pjs', '.psb',
                        '.rt', '.smi', '.ssf', '.ssa', '.svcd', '.usf', '.idx'}

    all_format = {'.wav', '.3ga', '.669', '.a52', '.aac', '.ac3', '.adt', '.adts', '.aif', '.aif', '.aifc', '.aiff',
                  '.amr', '.aob', '.ape', '.awb', 'caf', '.dts', '.flac', '.it', '.m4a', '.kar', '.m4b', '.m4p', '.m5p',
                  '.mid', '.mka', '.mlp', '.mod', '.mpa', '.mp1', '.mp2', '.mp3', '.mpc ', '.ogg', '.oga', '.mus',
                  '.mpga', '.mp4', '.vob', '.mkv', '.mkv', '.3g2', '.3gp', '.3gp2', '.3gpp', '.amv', '.asf', '.avi',
                  '.bik', '.bin', '.divx', '.drc', '.dv', '.f4v', '.flv ', '.gvi', '.gfx', '.iso', '.m1v,', '.m2v',
                  '.m2t', '.m2ts', '.m4v', '.mov', '.mp2', '.mp2v', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg2',
                  '.mpeg4', '.mpg', '.gif', '.webm'}

    main_ext = ('.avi', '.m4a', '.mkv', '.mpeg', '.gif', '.webm', '.ogg', '.wav', '.vob', '.3gp', '.mp3', '.mp4')

    default_settings = {'save_pos': 1, 'vol_rate': 5, 'seek_rate': 10, 'max_volume': 200, 'current_vol': 70,
                        'exit_check': 0, 'refresh_time': 60, 'scan_sub': 0, 'fulltime_state': 0, 'load_on_start': 1,
                        'controller': 1, 'auto_play': 1, 'controller_coords': (None, None), 'mouse_gestures': 1}

    default_past_info = {'past_media': [], 'play_count': 0}

    frozen = getattr(sys, 'frozen', False)
    main_dir = os.path.dirname(sys.executable) if frozen else os.path.dirname(
        os.path.abspath(os.path.realpath(__file__)))

    user_home_dir = str(Path.home())
    sdk_dir = os.path.join(main_dir, 'sdk')
    lib_dir = os.path.join(main_dir, 'lib')
    sys_dir = os.path.join(sdk_dir, '__sys_dir')
    icons_dir = os.path.join(sdk_dir, 'icons')
    fonts_dir = os.path.join(sdk_dir, 'fonts')
    plugins_dir = os.path.join(sdk_dir, 'plugins')

    user_pictures_dir = os.path.join(user_home_dir, 'Pictures')
    user_screenshots_dir = os.path.join(user_pictures_dir, 'Screenshots')
    user_app_screenshots_dir = os.path.join(user_screenshots_dir, ExeName)
    default_screenshot_dir = os.path.join(sdk_dir, 'screenshots')

    pycache_dir = os.path.join(main_dir, '__pycache__')

    parallel_run_enabled_file = os.path.join(sdk_dir, '__parallel__.cc')
    run_file = os.path.join(sdk_dir, '__run_file.cc')
    app_icon_file = os.path.join(icons_dir, "app.ico")
    past_file = os.path.join(sdk_dir, 'mpast.cc')
    playlist_file = os.path.join(sdk_dir, 'playlists.cc')
    playback_file = os.path.join(sdk_dir, 'playback.cc')
    settings_file = os.path.join(sdk_dir, 'settings.cc')
    bindings_file = os.path.join(sdk_dir, 'bindings.cc')
    libvlc_dll_file = os.path.join(sdk_dir, 'libvlc.dll')
    # libvlc_dll_file = 'libvlc.dll'
    library_zip = os.path.join(lib_dir, 'library.zip')

    exe_path = os.path.join(main_dir, ExeName + '.exe')
    update_exe_path = os.path.join(main_dir, UpdateExeName + '.exe')
    uninstall_exe_path = os.path.join(main_dir, UnInstallerExeName + '.exe')

    default_parallel_run_enabled = False        # default will be False, until i explicitly ship software with parallel code file


    @classmethod
    def save_parallel_run_enabled(cls, enabled: bool):
        is_file = os.path.isfile(cls.parallel_run_enabled_file)
        if enabled:
            return is_file or U.create(cls.parallel_run_enabled_file)
        return not is_file or U.delete(cls.parallel_run_enabled_file)

    @classmethod
    def load_parallel_run_enabled(cls):
        return os.path.isfile(cls.parallel_run_enabled_file)

    @classmethod
    def run_file_exists(cls):
        return os.path.isfile(cls.run_file)

    @classmethod
    def ensure_run_file(cls):
        return cls.run_file_exists() or U.create(cls.run_file)

    @classmethod
    def delete_run_file(cls):
        return not cls.run_file_exists() or U.delete(cls.run_file)

    @classmethod
    def sys_dir_exists(cls):
        return os.path.isdir(cls.sys_dir)

    @classmethod
    def ensure_sys_dir(cls):
        if not cls.sys_dir_exists():
            os.makedirs(C.sys_dir)


class Ui:

    @classmethod
    def ellip(cls, string: str, count: int):
        return string[0:count] + cls.CHR_ELLIP if len(string) > count else string

    @staticmethod
    def secs_to_hms(secs: int):
        mins = int(secs // 60)
        secs = int(secs % 60)

        hrs = int(mins // 60)
        mins = int(mins % 60)

        return hrs, mins, secs

    @staticmethod
    def mills_to_sec(mills: int):
        return round(mills / 1000)

    @classmethod
    def mills_to_hms(cls, mills: int):
        return cls.secs_to_hms(cls.mills_to_sec(mills))

    # @staticmethod
    # def format_mills(mills: int, _tuple: bool = True, full: bool = True, none: str = "0 secs"):
    #     sec_ = int(mills // 1000)
    #     min_ = int(sec_ // 60)
    #     sec_ = int(sec_ % 60)
    #
    #     hr_ = int(min_ // 60)
    #     min_ = int(min_ % 60)
    #
    #     if _tuple:
    #         return f'{hr_:02d}', f'{min_:02d}', f'{sec_:02d}'
    #
    #     if full:
    #         return f'{hr_:02d}:{min_:02d}:{sec_:02d}'
    #
    #     l = ((f'{hr_} hour' + ('s' if hr_ > 1 else '')) if hr_ > 0 else None,
    #          (f'{min_} min' + ('s' if min_ > 1 else '')) if min_ > 0 else None,
    #          (f'{sec_} sec' + ('s' if sec_ > 1 else '')) if sec_ > 0 else None)
    #
    #     r = " ".join(a for a in l if a is not None)
    #     if len(r) == 0:
    #         r = none
    #     return r

    @classmethod
    def format_secs(cls, secs: int, full, full_delimiter=':',
                    short_labels=False,
                    sec_long_label="sec",
                    delimiter=' ',
                    none: str = "0 secs"):

        hr_, min_, sec_ = cls.secs_to_hms(secs)
        if full:
            return f'{hr_:02d}{full_delimiter}{min_:02d}{full_delimiter}{sec_:02d}'

        l = (f'{hr_} {"hr" if short_labels else "hour"}{"s" if hr_ > 1 else ""}' if hr_ else None,
             f'{min_} {"min" if short_labels else "minute"}{"s" if min_ > 1 else ""}' if min_ else None,
             f'{sec_} {"s" if short_labels else sec_long_label + ("s" if sec_ > 1 else "")}' if sec_ else None)

        r = delimiter.join(a for a in l if a)
        return r if r else none

    @staticmethod
    def rgb(*r_g_b):
        return '#%02x%02x%02x' % r_g_b

    @staticmethod
    def rgb_to_hex(*r_g_b):
        return int('%02x%02x%02x' % r_g_b, 16)

    @staticmethod
    def format_aspect(asp):
        return asp if asp else "Best Fit"


    """ Ui Dimensions"""
    dock_h = 65
    im_dim = 32  # pixels
    audio_scale_relwidth = 0.15
    # dock_tl_w = 55
    # dock_tl_padx = 5
    dock_tl_pady = 3
    dock_b_padx = 10
    dock_b_pady = 7
    dock_edge_pady = 10
    dock_edge_padx = 10
    dock_hide_ms = 2000
    dock_anim_step = 4
    dock_anim_ms = 80

    # del_media_scale_length = (dock_tl_w * 2) + (dock_tl_padx * 4)
    # media_scale_padx = dock_tl_w + (dock_tl_padx * 2)
    # del_audio_scale_x = dock_tl_w + (dock_tl_padx * 2)

    # full screen dock
    fsdock_screen_padx = 40
    fsdock_screen_pady = 10
    fsdock_h = 24
    fsdock_pady = 0
    fsdock_hide_ms = 2000
    fsdock_alpha_step = .02
    fsdock_anim_ms = 200

    autohide_cursor_ms = 4000

    # Playlist win dim
    playwin_size = playwin_w, playwin_h = 310, 410

    # subtitle UI
    sub_b_width, sub_b_height = 350, 35
    sub_b_padx, sub_b_pady = 30, 7

    menu_font = ('product sans', 9)
    menu_font_cascade = ('product sans', 10)

    ext_fonts = [
        # "product_sans_light.ttf",
        "product_sans_medium.ttf",
        "product_sans_regular.ttf",
        # "product_sans_thin.ttf"
    ]

    """Format"""
    CHR_BULLET = '\u2022'
    CHR_ELLIP = '\u2026'
    CHR_MIDDLE_DOT = '\u00b7'
    fg_accent = '#%02x%02x%02x' % (103, 161, 223)



class BinDings:
    special_keysym = frozenset(("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R", "space", "Return",
                                "BackSpace", "Delete", "Break", "Escape", "Tab",
                                "Caps_Lock"))  # which can be binded independently in <keysym><another>

    default_bindings = {'playback': {'Play / Pause': '<space>',
                                     'Stop Playback': '<Escape>',
                                     'Play Next Media': '<Alt-Right>',
                                     'Play Previous Media': '<Alt-Left>',
                                     'Seek Forward': '<Right>',
                                     'Seek Backward': '<Left>',
                                     'Volume Up': '<Up>',
                                     'Volume Down': '<Down>'
                                     },

                        'win': {'Save Playlist': '<Control-s>',  #
                                'Load Playlist': '<Control-l>',
                                'Load Media File': '<Control-o>',
                                'Scan Directories': '<Control-f>',
                                'Save As': '<Control-S>',
                                'Shuffle Playlist': '<Control-z>',
                                'Show / Hide Playlist': '<Control-p>',
                                'Change Audio Track': '<b>',
                                'Scan Subtitles': '<q>',
                                'Change Aspect Ratio': '<Control-a>',
                                'Capture Screen Shot': '<Control-x>',
                                'Stream media': '<Control-n>',
                                'Restore Playback': '<Alt-r>',
                                'Show / Hide Menu Bar': '<Control-m>',
                                'Toggle Full Screen': '<Control-Up>'
                                },

                        'playwin': {'Clear Playlist': '<Control-Delete>',
                                    'Save Playlist': '<Control-s>',
                                    'Load Playlist': '<Control-l>',
                                    'Load Media File': '<Control-o>',
                                    'Scan Directories': '<Control-f>',
                                    'Show / Hide Playlist': '<Control-p>',
                                    'Restore Playback': '<Alt-r>',
                                    },

                        'controller_specific': {'Raise Main Window': '<Control-Up>',  # as class function (__SPECIFIC__)
                                                'Dock / UnDock Controller': '<Shift-Up>'
                                                # as class function (__SPECIFIC__)
                                                }
                        }


""" Fonts """
import winfonts

for font in Ui.ext_fonts:
    winfonts.load_font(os.path.join(C.fonts_dir, font))


# import pafy
# pafy.set_api_key(C.YT_API_KEY)

def rgb(*r_g_b):
    return Ui.rgb(*r_g_b)


def rgb_to_hex(*r_g_b):
    return Ui.rgb_to_hex(*r_g_b)
