import os
import pickle
from io import BytesIO
from threading import Thread
from tkinter import *

import PIL.Image
import psutil
import win32gui
from mutagen.id3 import ID3
# import youtube_dl
from urlvalidator import URLValidator, ValidationError
from win32con import WM_CLOSE

from __c import U, Ui, C, rgb

"""
Functions and algorithms often used in Media player
"""


def dump(ob, filepath):
    with open(filepath, 'wb+') as _file_:
        pickle.dump(ob, _file_)


def load(filepath, none_value=None, exception_value=None):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as _file_:
                return pickle.load(_file_)
        return none_value
    except Exception as e:
        print(e)
        return exception_value


def get_audio_thumb(song_path):
    """
    returns song thumbnail as PIL.Image object if exists else default song image
    """

    def get_im_(tags_):
        """ returns image data in bytes"""
        for key in tags_:
            if 'APIC' in key:
                return tags_[key].data
        return None

    _tags_ = ID3(song_path)
    _im_data_ = get_im_(_tags_)

    return PIL.Image.open(BytesIO(_im_data_)) if _im_data_ else None


def search_name_in_paths(file_name, paths_seq):
    """
    searches only a part of file_name from file names in paths
    """
    results__ = []
    for path_ in paths_seq:
        if file_name.lower() in os.path.basename(path_).lower():
            results__.append(path_)
    return results__


def search_exts(ext_list, start, mode='path'):
    """
    ext_list should be a list or tuple (iterable) with all extensions in lower case like ['.mp3', '.m4a']
    """
    names__ = []
    paths__ = []
    for path, subdir, files in os.walk(start):
        for file in files:
            if os.path.splitext(file)[1].lower() in ext_list:
                names__.append(file)
                paths__.append(os.path.join(path, file))
    if mode == "name":
        return names__
    elif mode == "path":
        return paths__
    return paths__, names__


class CallbackWrapper:
    """
    A wrapper for a callback
    """

    def __init__(self, callback, _filter=None):
        """

        :param callback: callback to wrap
        :param _filter: an optional filter that returns a bool
        """
        self.__callback = callback
        self.__filter = _filter

    def set_callback(self, callback):
        self.__callback = callback

    def set_filter(self, _filter=None):
        self.__filter = _filter

    def invoke(self, *args, **kw):
        if not self.__filter or self.__filter(*args, *kw):
            self.__callback(*args, *kw)
            return True

        return False

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, *kwargs)


"""  
Classes Used in mediaplayer..........
"""


class BaseDialogFrame(Frame):
    DEFAULT_font = ("product sans", 10)
    DEFAULT_bg_dark = rgb(30, 30, 30)
    DEFAULT_bg_medium = rgb(70, 70, 70)
    DEFAULT_bg_light = rgb(100, 100, 100)
    DEFAULT_fg_dark = rgb(255, 255, 255)
    DEFAULT_fg_medium = rgb(240, 240, 240)
    DEFAULT_fg_light = rgb(190, 190, 190)
    __sInstanceCount: int = 0

    @staticmethod
    def on_created(dialog):
        BaseDialogFrame.__sInstanceCount += 1

    @staticmethod
    def on_destroyed(dialog):
        BaseDialogFrame.__sInstanceCount -= 1

    @staticmethod
    def has_instances():
        return BaseDialogFrame.__sInstanceCount > 0

    def __init__(self, master, title, font=DEFAULT_font, bg_dark=DEFAULT_bg_dark, bg_medium=DEFAULT_bg_medium, bg_light=DEFAULT_bg_light, fg_dark=DEFAULT_fg_dark, fg_medium=DEFAULT_fg_medium, fg_light=DEFAULT_fg_light, drag_allowed=True, **kwargs):
        self.master = master
        self.title = title

        self.bg_dark = bg_dark
        self.bg_medium = bg_medium
        self.bg_light = bg_light
        self.fg_dark = fg_dark
        self.fg_medium = fg_medium
        self.fg_light = fg_light

        self.font = font

        self.drag_allowed = drag_allowed

        super().__init__(master=self.master, bg=self.bg_dark, **kwargs)
        self.title_click_event = None

        self.title_frame = Frame(self, bg=self.bg_medium)
        self.title_l = Label(self.title_frame, text=self.title, font=font, relief="flat", bg=self.bg_medium, fg=self.fg_dark,
                             anchor='center')
        self.close_b = Button(self.title_frame, text=" X ", command=self.destroy,
                              relief="flat", bd=0, bg=self.bg_medium, fg=self.fg_dark, font=font,
                              activebackground=self.bg_dark, activeforeground=self.fg_medium)

        if drag_allowed:
            self.title_frame.bind("<Button-1>", self.on_title_click)
            self.title_frame.bind('<B1-Motion>', self.on_title_drag)

        BaseDialogFrame.on_created(self)

    def destroy(self):
        super().destroy()
        BaseDialogFrame.on_destroyed(self)

    def on_title_click(self, event):
        self.title_click_event = event

    def on_title_drag(self, event):
        relx = (self.winfo_x() - self.title_click_event.x + event.x) / self.master.winfo_width()
        rely = (self.winfo_y() - self.title_click_event.y + event.y) / self.master.winfo_height()
        self.place_configure(anchor='nw', relx=relx, rely=rely)

    def pack_widgets(self):     # TODO: call in child class
        self.close_b.pack(side="right", fill="y")
        self.title_l.pack(side="left", fill="both", padx=4, pady=2)
        self.title_frame.pack(side='top', fill='x', padx=2, pady=2)

    def place_at_center(self, deiconify_master=True):
        if deiconify_master:
            self.master.deiconify()
            self.master.update()
        self.place(anchor='center', relx=0.5, rely=0.5)


class BasrCaptionDialogFrame(BaseDialogFrame):
    DEFAULT_CAP_FONT = ("product sans medium", 11)

    def __init__(self, master, title, caption, cap_font=DEFAULT_CAP_FONT, cap_padx=32, cap_pady=10, **kwargs):
        self.caption = caption
        self.cap_padx = cap_padx
        self.cap_pady = cap_pady
        self.cap_font = cap_font

        super().__init__(master, title, **kwargs)
        self.caption_l = Label(self, text=caption, font=cap_font, relief="flat", bg=self.bg_dark, fg=self.fg_medium)


    def pack_widgets(self):     # TODO: call in child class
        super().pack_widgets()
        self.caption_l.pack(side='top', anchor='center', padx=self.cap_padx, pady=self.cap_pady)


class RcDiag(BasrCaptionDialogFrame):
    """
    returns '' if no value or destroyed by the user
    """

    input_cache = {}

    def __init__(self, master, title, caption, command, font=BaseDialogFrame.DEFAULT_font, cap_font=("product sans medium", 10), cap_padx=40, retain_value=False, drag_allowed=True, **kwargs):
        self.master = master
        self.retain_value = retain_value
        self.command = command

        self.value = ""  # variable that contains main_value
        self.temp = StringVar()

        super().__init__(master, title=title, caption=caption, font=font, cap_font=cap_font, cap_padx=cap_padx, drag_allowed=drag_allowed, **kwargs)

        if self.retain_value and self.title in self.__class__.input_cache.keys():
            self.temp.set(self.__class__.input_cache[self.title])

        self.e_frame = Frame(self, bg=self.bg_dark)
        self.entry = Entry(self.e_frame, relief='flat', textvariable=self.temp, font=font)
        self.clear_b = Button(self.e_frame, text=" Clear ", command=self.clear_entry,
                              relief="flat", bd=0, bg=self.bg_dark, fg=self.fg_medium, font=font,
                              activebackground=self.bg_medium, activeforeground=self.fg_dark)

        self.ok_b = Button(self, text="  OK  ", command=self.submit,
                           relief="flat", bd=0, bg=self.bg_dark, fg=self.fg_medium, font=font,
                           activebackground=self.bg_medium, activeforeground=self.fg_dark)

        self.pack_widgets()

        self.entry.bind('<Return>', self.submit)
        self.entry.bind('<Escape>', lambda event: self.destroy())
        # self.e.bind('<FocusOut>', lambda event: self.destroy())

        self.entry.focus_force()

    def pack_widgets(self):
        super().pack_widgets()

        # placing widgets
        self.clear_b.pack(side="right", fill="none", padx=4, anchor='center')
        self.entry.pack(side="right", fill="x")
        self.e_frame.pack(side='top', anchor='center', fill='x', padx=30, pady=8)
        self.ok_b.pack(side='top', anchor='center', pady=10)

    def clear_entry(self, event=None):
        self.entry.delete(0, END)

    def submit(self, event=None):
        self.value = self.entry.get()
        self.command(self.value)

    # def on_success(self, text, fg='white', font=('product sans medium', 10)):
    #     self.bind('<Return>', lambda event: self.destroy())
    #     if self.retain_value:
    #         self.__class__.input_cache[self.title_] = self.value
    #     _c = Canvas(self, bg=self.rgb(90, 90, 90), relief='flat', bd=0)
    #     _c.create_text(self.size[0] / 2, self.size[1] / 2, text=text, fill=fg, font=font, anchor='center')
    #     _c.place(x=0, y=0, relwidth=1, relheight=1)

    def on_success(self):
        # self.bind('<Return>', lambda event: self.destroy())
        self.destroy()
        if self.retain_value:
            self.__class__.input_cache[self.title] = self.value
        # _c = Canvas(self, bg=self.rgb(90, 90, 90), relief='flat', bd=0)
        # _c.create_text(self.size[0] / 2, self.size[1] / 2, text=msg, fill=fg, font=font, anchor='center')
        # _c.place(x=0, y=0, relwidth=1, relheight=1)

        # s = SnackBar(master=self.master, msg=msg, duration=duration, show_cancel=show_cancel, action=action, action_text=action_text, font=font, offset_y=offset_y)
        # s.show_at_top_center()


class WinHandler:
    def __init__(self):
        self.pids = []
        self.req_pid = None
        self.found_hwnds = []

    def get_hwnds(self, win_title, win_class):
        self.found_hwnds.clear()
        win32gui.EnumWindows(self.enum_handler, (win_title, win_class))
        return self.found_hwnds

    @staticmethod
    def get_pid(exe_name):
        exe_name = f'{exe_name}.exe'.lower()
        for __p in psutil.process_iter():
            try:
                if __p.name().lower() == exe_name and __p.status() == psutil.STATUS_RUNNING:
                    return __p.pid, __p.t
            except (PermissionError, psutil.Error, AttributeError):
                pass
        return None

    def enum_handler(self, __hwnd, info_):
        if info_[1] == win32gui.GetClassName(__hwnd) and info_[0] in win32gui.GetWindowText(__hwnd):
            self.found_hwnds.append(__hwnd)

    def close_window(self, win_title, win_class):
        _hwnd_win = self.get_hwnds(win_title, win_class)
        for _hwnd in _hwnd_win:
            win32gui.SendMessage(_hwnd, WM_CLOSE)


class RcBool:
    def __init__(self, val=True):
        self.v = val
        self.__name__ = 'RcBool'

    def set(self, val):
        self.v = val

    def get(self):
        return self.v

    def __bool__(self):
        return self.v

    def __call__(self):
        self.v = not self.v

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.v == other.v
        elif type(other) == bool:
            return self.v == other

    def __repr__(self):
        return f'RcBool({self.v})'


class RcInt:
    def __init__(self, val=0):
        self.v = round(val)
        self.__name__ = 'RcInt'

    def __repr__(self):
        return f'RcInt({self.v})'

    def __str__(self):
        return f'value: {self.v}'

    def set(self, val, round_=False):
        self.v = round(val) if round_ else val

    def get(self):
        return self.v

    def __bool__(self):
        return False if self.v == 0 else True

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.v == other.v
        elif type(other) == int:
            return self.v == other

    def __add__(self, other):
        if other.__class__ == self.__class__:
            self.v += other.v
            return self
        elif type(other) == int:
            self.v += other
            return self

    def __sub__(self, other):
        if other.__class__ == self.__class__:
            self.v -= other.v
            return self
        elif type(other) == int:
            self.v -= other
            return self

    def __call__(self, val):
        self.v = round(val)


class RcStr:
    def __init__(self, value='', alt_value='', key_var=0, main_key=0, alt_key=1):
        self.v = value
        self.altv = alt_value
        self.main_key = main_key
        self.alt_key = alt_key
        self.key = key_var
        self.dic_ = {self.main_key: self.v, self.alt_key: self.altv}

    def __getitem__(self, i):
        return self.dic_[i]

    def get_key(self):
        return self.key

    def get_keyv(self):
        return self.dic_[self.key]

    def set_key(self, val):
        self.key = val

    def __repr__(self):
        return f'RcStr({self.v})'

    def set(self, value):
        self.v = value

    def get(self):
        return self.v

    def __bool__(self):
        return False if self.v == '' else True

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return self.v == other.v
        elif type(other) == str:
            return self.v == other

    def __add__(self, other):
        if other.__class__ == self.__class__:
            self.v += other.v
            return self
        elif type(other) == str:
            self.v += other
            return self

    def __sub__(self, other):
        if other.__class__ == self.__class__:
            self.v -= other.v
            return self
        elif type(other) == int:
            self.v -= other
            return self


class RcVar:
    def __init__(self, value):
        self.v = value

    def __repr__(self):
        return f'RcVar({self.v})'

    def set(self, value):
        self.v = value

    def get(self):
        return self.v

    def __call__(self, value):
        self.v = value


class _RcScale(Scale):
    def __init__(self, master, **kwargs):
        Scale.__init__(self, master=master, **kwargs)
        self.start_ = kwargs['from_']
        self.end_ = kwargs['to']
        self.range_ = self.end_ - self.start_

    def get_value_from_x(self, x):
        x0, y0 = self.coords(self.start_)
        x1, y1 = self.coords(self.end_)

        pix = x1 - x0
        pix_per_value = pix / self.range_

        return (x - x0) / pix_per_value

    def find(self, x, y):
        return self.identify(x, y)


class BaseNotification(Frame):

    @staticmethod
    def consider_undock(n):
        if n:
            n.undock()

    def __init__(self, master, undock_time=1000, *args, **kwargs):     # <=0 for no auto hide
        self.master = master
        self.undock_time = undock_time  # in ms
        self.__undock_timer = None
        self.state = 0  # 0 for un docked, 1 for docked
        super().__init__(master=master, *args, **kwargs)

    def is_docked(self):
        return self.state == 1

    def cancel_timer(self):
        if self.__undock_timer is not None:
            try:
                self.master.after_cancel(self.__undock_timer)
            except Exception as e:
                print(e)
            finally:
                self.__undock_timer = None

    def reset_timer(self):
        self.cancel_timer()
        if self.undock_time > 0:
            self.__undock_timer = self.master.after(self.undock_time, lambda arg=False: self.__undock(arg))

    def __undock(self, cancel_timer: bool):
        if self.state == 1:
            self.state = 0
            if cancel_timer:
                self.cancel_timer()
            self.place_forget()
            self._on_undocked()

    def undock(self):
        self.__undock(True)

    def dock(self, cnf: dict = None, config_if_docked=True, **kw):
        self.cancel_timer()
        if self.state == 0:
            self.state = 1
            self.place(cnf, **kw)
            self._on_docked(True)
        else:
            if config_if_docked:
                self.place_configure(cnf, **kw)
            self._on_docked(False)
        self.reset_timer()

    def place_configure(self, cnf: dict = None, **kw):
        if self.is_docked():
            if cnf is None:
                cnf = {}
            super().place_configure(cnf, **kw)

    def _on_docked(self, first: bool):
        pass

    def _on_undocked(self):
        pass

    def get_x(self):
        return int(self.place_info()['x'])

    def set_x(self, x):
        self.place_configure(x=x)

    def x_offset(self, by):
        self.set_x(self.get_x() + by)

    def set_y(self, y):
        self.place_configure(y=y)

    def get_y(self, update: bool=False):
        if update:
            self.update()
        return self.winfo_y()

    def get_height(self, update: bool=False):
        if update:
            self.update()
        return self.winfo_height()

    def get_y2(self, update=False):
        return self.get_y(update=update) + self.get_height(update=False)

    def y_offset(self, by):
        self.set_y(self.get_y() + by)


class SnackBar(BaseNotification):
    # docked_height = 0
    docked_stack = []

    @classmethod
    def get_last_docked(cls):
        return cls.docked_stack[-1] if cls.docked_stack else None

    @classmethod
    def get_last_docked_y2(cls):
        s = cls.get_last_docked()
        return s.get_y2() if s else 0

    @classmethod
    def on_docked(cls, s):
        # SnackBar.docked_height += s.height
        cls.docked_stack.append(s)

    @classmethod
    def __on_undocked_at(cls, index: int):
        last_y2 = cls.docked_stack[index - 1].get_y2() if index > 0 else 0
        for e in range(index + 1, len(cls.docked_stack)):
            _s = cls.docked_stack[e]
            _s.set_y_from_last_y2(last_y2)
            last_y2 = _s.get_y2()
        cls.docked_stack.pop(index)

    @classmethod
    def on_undocked(cls, s):
        try:
            i = cls.docked_stack.index(s)
            cls.__on_undocked_at(i)
        except ValueError:
            print("Notification is not found in docked list")
            pass

    @classmethod
    def _hide(cls, s):
        cls.consider_undock(s)

    @staticmethod
    def show_msg(master, msg:str, duration=3000, show_cancel=False, action=None, action_text="", font=('product sans', 12),
                 offset_y=10, deiconify_master=True):
        s = SnackBar(master=master, msg=msg, duration=duration, show_cancel=show_cancel, action=action,
                     action_text=action_text, font=font, offset_y=offset_y)

        if deiconify_master and isinstance(master, Wm):
            master.deiconify()
            master.update()
        s.show_at_top_center()

    @classmethod
    def show_msg_copied_to_clipboard(cls, master, label: str, duration: int = 4000, show_cancel=False):
        cls.show_msg(master, msg=label + " copied to clipboard", show_cancel=show_cancel, duration=duration)

    def __init__(self, master, msg, duration=1000, action=None, action_text="OK", show_cancel=True, stack=True, offset_y=6, padx=8, pady=2, **kw):
        self.action = action
        self.stack = stack                  # whether to register this instance as stacked snackbar
        self.offset_y = offset_y            # only used if stack is True
        # self.height = height

        self.bg = U.ensure_key(kw, 'bg', rgb(30, 30, 30))
        self.fg = U.ensure_key(kw, 'fg', rgb(255, 255, 255))
        self.action_fg = Ui.fg_accent
        self.activebackground = U.ensure_key(kw, 'activebackground', self.bg)
        self.activeforeground = U.ensure_key(kw, 'activeforeground', rgb(255, 255, 255))
        self.font = U.ensure_key(kw, 'font', ('product sans', 11))
        self.place_kw = {'anchor': 'n'}
        super().__init__(master, undock_time=duration, bg=self.bg)

        self.label = Label(self, text=msg, bg=self.bg, relief='flat', fg=self.fg, font=self.font)

        if show_cancel:
            self.cancel_b = Button(self, text='X', relief='flat', bd=0, bg=self.bg, fg=self.fg, font=self.font,
                                   activebackground=self.activebackground, command=self.undock,
                                   activeforeground=self.activeforeground, width=4)
        else:
            self.cancel_b = None

        if action:
            self.action_b = Button(self, text=action_text, command=self._on_click_action,
                                   relief='flat', bd=0, bg=self.bg, fg=self.action_fg, font=self.font,
                                   activebackground=self.activebackground,
                                   activeforeground=self.action_fg)
        else:
            self.action_b = None

        if self.cancel_b:
            self.cancel_b.pack(side='right', anchor='e', padx=padx, pady=pady)

        if self.action_b:
            self.action_b.pack(side='right', anchor='e', pady=pady, padx=0 if self.cancel_b else padx)
            self.label.pack(side='left', anchor='w', pady=pady, padx=padx)
        else:
            self.label.config(anchor='center')
            self.label.pack(expand=True, fill="x", pady=pady, padx=padx)

        # self.dock(x=0, y=SnackBar.docked_height + 4, relwidth=1, height=self.height)

    # def get_height(self):
    #     return self.height

    def _get_y_stacked(self, y2: int):
        return y2 + self.offset_y

    def _get_last_y_stacked(self):
        return self._get_y_stacked(self.__class__.get_last_docked_y2())

    def show(self):
        if self.stack and not self.is_docked():
            self.place_kw['y'] = self._get_last_y_stacked()
        # self.place_kw['height'] = self.height
        self.dock(config_if_docked=not self.stack, **self.place_kw)

    def place_configure(self, cnf: dict = None, **kw):
        super().place_configure(cnf, **kw)
        # self.place_kw = kw

    def set_y_from_last_y2(self, last_y2: int):
        if self.stack:
            self.set_y(self._get_y_stacked(last_y2))

    def show_at(self, **kw):
        self.place_kw = kw
        self.show()

    def show_at_top_center(self):
        self.show_at(anchor='n', relx=0.5, y=self.offset_y)

    def show_at_top_right(self, offset_relx: float = 0):
        self.show_at(anchor='ne', relx=1 - offset_relx, y=self.offset_y)

    def _on_click_action(self):
        try:
            self.action()
        except Exception as e:
            return e
        finally:
            self.undock()

    def _on_docked(self, first: bool):
        super()._on_docked(first)
        if self.stack and first:
            self.__class__.on_docked(self)

    def _on_undocked(self):
        super()._on_undocked()
        if self.stack:
            self.__class__.on_undocked(self)

    def set_msg(self, msg: str):
        self.label['text'] = msg


class RestorePlaynackSnackbar(SnackBar):
    INSTANCE = None

    @classmethod
    def show_instance(cls, master, callback):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(master, 'Do you want to resume where you left' + Ui.CHR_ELLIP + "\t\t", callback)
            # cls.INSTANCE.show_at(x=0, relwidth=1)
            cls.INSTANCE.show_at_top_center()
        else:
            cls.INSTANCE.action = callback
            cls.INSTANCE.show()

    @classmethod
    def hide_instance(cls):
        cls._hide(cls.INSTANCE)

    def __init__(self, master, msg, callback, duration=10000, offset_y=10, **kw):
        super().__init__(master, msg=msg, duration=duration, action=callback, action_text='Reload', show_cancel=True, offset_y=offset_y, **kw)


class ScreenshotSnackbar(SnackBar):

    def __init__(self, master, path: str, success: bool, **kw):

        if success:
            super().__init__(master, msg="Screenshot saved to " + os.path.basename(path), duration=6000, action=lambda: os.startfile(path), action_text='View', show_cancel=True, **kw)
        else:
            super().__init__(master, msg="Failed to capture screenshot", duration=2000, action=None, action_text="", show_cancel=False, **kw)


class TopRightSnackbar(SnackBar):
    INSTANCE_AUDIO_TRACK = None
    INSTANCE_SUB_TRACK = None
    INSTANCE_VOLUME = None

    @classmethod
    def show_audio_track(cls, master: Tk, msg):
        if cls.INSTANCE_AUDIO_TRACK is None:
            cls.INSTANCE_AUDIO_TRACK = cls(master, msg)
            cls.INSTANCE_AUDIO_TRACK.show_at_top_right(0.005)
        else:
            cls.INSTANCE_AUDIO_TRACK.set_msg(msg)
            cls.INSTANCE_AUDIO_TRACK.show()

    @classmethod
    def hide_audio_track(cls):
        cls._hide(cls.INSTANCE_AUDIO_TRACK)

    @classmethod
    def show_sub_track(cls, master: Tk, msg):
        if cls.INSTANCE_SUB_TRACK is None:
            cls.INSTANCE_SUB_TRACK = cls(master, msg)
            cls.INSTANCE_SUB_TRACK.show_at_top_right(0.005)
        else:
            cls.INSTANCE_SUB_TRACK.set_msg(msg)
            cls.INSTANCE_SUB_TRACK.show()

    @classmethod
    def hide_sub_track(cls):
        cls._hide(cls.INSTANCE_SUB_TRACK)

    @classmethod
    def show_volume(cls, master: Tk, vol_per: int):
        msg = f'VOL: {vol_per}%'
        if cls.INSTANCE_VOLUME is None:
            cls.INSTANCE_VOLUME = cls(master, msg, font=('product sans', 20), offset_y=14, height=50)
            cls.INSTANCE_VOLUME.show_at_top_right(0.01)
        else:
            cls.INSTANCE_VOLUME.set_msg(msg)
            cls.INSTANCE_VOLUME.show()

    @classmethod
    def hide_volume(cls):
        cls._hide(cls.INSTANCE_VOLUME)

    def __init__(self, master, msg, duration=2000, font=('product sans', 14), offset_y=8, **kw):
        super().__init__(master, msg=msg, duration=duration, action=None, show_cancel=False, font=font, offset_y=offset_y, **kw)


class TopCenterSnackbar(SnackBar):
    INSTANCE_ASP_RATIO = None

    @classmethod
    def show_asp_ratio(cls, master: Tk, asp):
        msg = Ui.format_aspect(asp)

        if cls.INSTANCE_ASP_RATIO is None:
            cls.INSTANCE_ASP_RATIO = cls(master, msg= msg, duration=1600, show_cancel=False, font=('product sans', 20), pady=2, offset_y=5)
            cls.INSTANCE_ASP_RATIO.show_at_top_center()
        else:
            cls.INSTANCE_ASP_RATIO.set_msg(msg)
            cls.INSTANCE_ASP_RATIO.show()

    @classmethod
    def hide_asp_ratio(cls):
        cls._hide(cls.INSTANCE_ASP_RATIO)


class PlaybackSnackBar(SnackBar):

    INSTANCE = None

    @classmethod
    def _ensure_instance(cls, master: Tk):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(master)
        return cls.INSTANCE

    @classmethod
    def set_instance_ms(cls, master: Tk, ms: int):
        cls._ensure_instance(master).set_ms(ms)

    @classmethod
    def instance_fw(cls, master: Tk, ms: int):
        cls._ensure_instance(master).fw(ms)

    @classmethod
    def instance_bw(cls, master: Tk, ms: int):
        cls._ensure_instance(master).bw(ms)

    @classmethod
    def hide_instance(cls):
        cls._hide(cls.INSTANCE)

    def __init__(self, master: Tk, duration=2000, **kw):
        self.offset_relx = 0.01      # pixels
        self.ms = 0         # 0 for none, -ve for backward, +ve for forward
        super().__init__(master, msg="", duration=duration, action=None, show_cancel=False, stack=False, pady=2, padx=6, font=('product sans', 14), **kw)

    def set_ms(self, ms: int):
        self.ms = ms
        if abs(ms) < 1000:          # less than a sec
            self.undock()
        else:
            fw = ms > 0
            msg = Ui.format_secs(Ui.mills_to_sec(abs(ms)), full=False, short_labels=True)
            if fw:
                msg += ' >'
            else:
                msg = '< ' + msg
            self.set_msg(msg)

            if fw:
                self.show_at(anchor='e', relx=1 - self.offset_relx, rely=0.5)
            else:
                self.show_at(anchor='w', relx=self.offset_relx, rely=0.5)

    def _on_undocked(self):
        super()._on_undocked()
        self.ms = 0

    def fw(self, ms: int):
        ms = abs(ms)
        if self.is_docked() and self.ms > 0:
            ms += self.ms
        self.set_ms(ms)

    def bw(self, ms: int):
        if ms > 0:
            ms *= -1
        if self.is_docked() and self.ms < 0:
            ms += self.ms
        self.set_ms(ms)


class YtStreamInfo:
    TYPE_AUDIO = 1
    TYPE_NORMAL = 2
    TYPE_VIDEO_NA = 3       # Video only, no-audio track

    def __init__(self, stream, type_code: int=None):
        self.stream = stream
        self.size = stream.get_filesize()
        self.url = stream.url
        self.ext = stream.extension
        self.quality = stream.quality
        self.type = stream.mediatype

        if not type_code:
            if self.type == 'audio':
                type_code = self.__class__.TYPE_AUDIO
            elif self.type == 'video':
                type_code = self.__class__.TYPE_VIDEO_NA
            else:
                type_code = self.__class__.TYPE_NORMAL
        self.type_code = type_code

    def __repr__(self):
        size_str = round(self.size / (1024 ** 2), 2)  # in MiB
        str_ = f'{self.quality} {Ui.CHR_MIDDLE_DOT} {size_str} MiB'
        if self.type_code == self.__class__.TYPE_VIDEO_NA:
            str_ += f' {Ui.CHR_MIDDLE_DOT} No Audio'
        return str_

    def __str__(self):
        return self.__repr__()


class StreamFrame(BasrCaptionDialogFrame):

    sInstance = None

    @classmethod
    def show_instance(cls, master, stream_call, *args, **kwargs):
        if not cls.sInstance:
            cls.sInstance = cls(master=master, stream_call=stream_call, *args, **kwargs)
        cls.sInstance.place_at_center()

    @classmethod
    def destroy_instance(cls):
        if cls.sInstance:
            cls.sInstance.destroy()
            cls.sInstance = None

    def __init__(self, master, stream_call, title='Network Stream', **kwargs):
        self.stream_call = stream_call
        self.info_dic = {}
        self.yt_infos = []  # url info to be given to master
        self.yt__ = None
        self.chunk_size = 1024  # in bytes

        # self.title_ = title
        # if self.pos is None:
        #     self.pos = self.master.winfo_rootx() + round(
        #         (self.master.winfo_width() - size[0]) / 2), self.master.winfo_rooty() + round(
        #         (self.master.winfo_height() - size[1]) / 2) - 20

        super().__init__(master, title=title, caption="", cap_padx=30, drag_allowed=True, **kwargs)
        # self.url_frame_ = self.UrlFrame(self)

        self.url_e = Entry(self, font=self.font, bg=self.fg_medium, fg=self.bg_dark, relief='groove', bd=2)

        self.submit_b = Button(self, text='  Stream  ', font=self.font, relief='flat', bd=0, bg=self.bg_dark,
                               activebackground=self.bg_medium, activeforeground=self.fg_medium, fg=self.fg_medium, command=self.submit)

        # self.analyse_progress = RcScale(self, width=self.size[0], height=10, value=0, slider=False,
        #                                 troughcolor1='skyblue', bg='grey')

        # Yt widgets
        self.yt_streams_frame = None
        self.video_frame = None
        self.audio_frame = None
        self.b_frame = None
        self.video_l = None
        self.audio_l = None
        self.buttons = None
        self.stream_b = None
        self.copy_url_b = None
        self.var_ = None

        self.pack_entry_widgets()

        # self.pack(expand='yes', fill=BOTH)

    def destroy(self):
        super().destroy()
        self.__class__.sInstance = None

    def set_analysis_progress(self, progress: int):
        self.caption_l['text'] = f'Analysing{Ui.CHR_ELLIP }' + (' ' + str(progress) + '%' if progress else '')

    def check_var(self):
        return self.var_ and 0 <= self.var_.get() < len(self.yt_infos)

    def check_var_or_hsow_msg(self):
        if not self.check_var():
            # messagebox.showwarning("Warning", "No stream selected. Tap on a stream to select it", parent=self.master)
            SnackBar.show_msg(self.master, "No stream selected yet. Tap on a stream to select it")
            return False
        return True

    def on_var_changed(self, *args, **kwargs):
        state = NORMAL if self.check_var() else DISABLED
        self.stream_b['state'] = self.copy_url_b['state'] = state

    def copy_url(self):
        if not self.check_var_or_hsow_msg():
            return
        U.copy_to_clipboard(self, self.yt_infos[self.var_.get()].url, append=False)
        SnackBar.show_msg_copied_to_clipboard(self.master, label="Youtube stream link")

    def __stream_ytinfo_thread(self, info: YtStreamInfo):
        try:
            self.stream_call(url=info.url, title=self.info_dic['title'])
        except Exception as e:
            SnackBar.show_msg(self.master, f'failed to stream {self.info_dic["title"]} {Ui.CHR_MIDDLE_DOT} {str(info)}')
        finally:
            self.after(1000, self.reset_stream_b)

    def stream(self):
        """
        returns info_object : list of tuples (type_, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
        """
        if not self.check_var_or_hsow_msg():
            return

        self.stream_b['text'] = 'Streaming' + Ui.CHR_ELLIP
        self.stream_b['state_'] = DISABLED
        info = self.yt_infos[self.var_.get()]

        stream_th__ = Thread(target=self.__stream_ytinfo_thread, args=(info, ))
        stream_th__.setDaemon(True)
        stream_th__.start()

    def reset_stream_b(self):
        self.stream_b['state_'] = NORMAL
        self.stream_b['text'] = 'Stream'

    def reset_cap_l_pack(self):
        self.caption_l.pack_configure(padx=self.cap_padx, pady=self.cap_pady)

    def pack_entry_widgets(self, call_super=True):

        # # ..........................................
        # self.master.overrideredirect(False)
        # self.master.protocol('WM_DELETE_WINDOW', self.master.destroy)
        # # ................................................

        self.caption_l['text']= '\tEnter URL or MRL\t'
        if call_super:
            self.pack_widgets()
        else:
            self.reset_cap_l_pack()

        self.caption_l.update()
        self.close_b.configure(state=NORMAL)
        self.url_e.delete(0, END)
        self.url_e.pack(side='top', anchor='center', padx=20, pady=6, fill='x')
        self.submit_b.pack(side='top', anchor='center', padx=10, pady=4)

        self.url_e.focus_set()
        self.url_e.bind('<Escape>', lambda event__: self.master.destroy())
        self.url_e.bind('<Return>', lambda event__: self.submit())
        self.url_e.bind('<Control-x>', lambda event__, _a=0, b=END: self.url_e.delete(_a, b))

    def unbind_url_e(self):
        self.url_e.focus_set()
        self.url_e.unbind('<Escape>')
        self.url_e.unbind('<Return>')
        self.url_e.unbind('<Control-x>')

    def submit(self):
        url_ = self.url_e.get()

        if not url_:
            # messagebox.showwarning('Waring', 'Please enter a url : ERR_NO_INPUT', parent=self.master)
            SnackBar.show_msg(self.master, 'Please enter a URL first' + Ui.CHR_ELLIP)
            return

        validator = URLValidator()
        try:
            validator(url_)
        except ValidationError:
            # messagebox.showerror('Error', 'Invalid URL : ERR_MEDIA_RESOURCE_LOCATOR', parent=self.master)
            SnackBar.show_msg(self.master, 'Invalid URL. Please verify the entered URL' + Ui.CHR_ELLIP)
            self.url_e.delete(0, END)
            return
        # if 'youtube' in url_.lower() or 'youtu.be' in url_.lower():
        if U.is_url_youtube(url_):
            self.unbind_url_e()
            self.url_e.pack_forget()
            self.submit_b.pack_forget()
            self.set_analysis_progress(0)
            self.caption_l.pack_configure(padx=40, pady=30)
            self.close_b.configure(state=DISABLED)        # in process

            analyse_thread = Thread(target=self.analyse_youtube_url, args=(url_,))
            analyse_thread.setDaemon(True)
            analyse_thread.start()
        else:
            try:
                self.stream_call(url=url_)
            except Exception as e:
                self.pack_entry_widgets(False)
                # messagebox.showerror("Error", "failed to stream " + url_ + ". Check your internet connection and access to url", parent=self.master)
                SnackBar.show_msg(self.master, "Failed to stream " + url_ + "\nCheck your internet connection and access to this url")
            else:
                self.destroy()

    def analyse_youtube_url(self, url__):
        import pafy

        try:
            self.set_analysis_progress(10)
            # videos_count = 0

            pafy.set_api_key(C.YT_API_KEY)
            self.yt__ = pafy.new(url__)
            self.set_analysis_progress(50)
            self.info_dic['title'] = ''.join(i for i in self.yt__.title if
                                             i in {'K', 'o', '_', 'J', '2', 'B', 'u', 'i', 'F', '1', 's', 'P', '.',
                                                   'k', 'a', 'r', 'Z', 'd', 'h', 'm', 'q',
                                                   'S', 'O', '5', ' ', 'Y', 'Q', 'V', 'j', '-', 'C', 'v', 'T', '(',
                                                   'M', 'g', '0', '4', 'N', 'U', 'w', 'H',
                                                   'I', 't', 'D', 'n', 'X', 'L', ')', 'A', 'R', 'l', '6', 'b', 'f',
                                                   'p', 'z', 'W', '7', '8', 'x', '3', 'E',
                                                   'e', 'c', 'G', '9', 'y'})
            self.set_analysis_progress(60)

            all_streams = self.yt__.allstreams

            if self.yt__.audiostreams:
                self.info_dic['main_audio'] = YtStreamInfo(self.yt__.audiostreams[0], YtStreamInfo.TYPE_AUDIO)

            self.info_dic.update(
                {'author': self.yt__.author, 'description': self.yt__.description, 'likes': self.yt__.likes,
                 'dislikes': self.yt__.dislikes, 'rating': self.yt__.rating, 'thumb_url': self.yt__.thumb,
                 'hdthumb_url': self.yt__.bigthumbhd, 'views': self.yt__.viewcount, 'genre': self.yt__.category}
            )

            for stream in all_streams:
                info = YtStreamInfo(stream)
                if info.type != YtStreamInfo.TYPE_AUDIO and info.ext == 'webm':
                    continue
                # if info.type == YtStreamInfo.TYPE_NORMAL:
                #     videos_count += 1
                self.yt_infos.append(info)

            self.set_analysis_progress(90)

            # self.size[0] = 400
            # self.size[1] = (videos_count * 28) + 105
            self.set_analysis_progress(100)
            self.close_b['state'] = NORMAL
            self.youtube_stream_ui()
        except Exception as e:
            print(e)
            # self.analyse_progress.pack_forget()
            self.pack_entry_widgets(False)
            SnackBar.show_msg(self.master, 'Sorry, Couldn\'t connect to YouTube right now!')

            # messagebox.showerror('Network Error', 'Connection to server failed : ERR_NO_INTERNET', parent=self.master)

    def create_b(self, master, index: int, text: str):
        return Radiobutton(master, text=text
                           , value=index, variable=self.var_, font=('product sans', 10),
                           relief='flat', indicator=0, overrelief='raised',
                           bg=self.bg_dark, fg=self.fg_medium, bd=0, selectcolor=self.bg_medium, anchor='center')

    def youtube_stream_ui(self):
        """
        info_object : list of tuples (type_code, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
        """
        # self.analyse_progress.pack_forget()
        # self.analyse_progress.set(0)
        # self.cap_.pack_forget()
        # self.cap_['font'] = ('product sans', 9)
        self.caption_l['text'] = Ui.ellip(self.info_dic['title'], 50)
        self.reset_cap_l_pack()
        self.caption_l.update()

        # self.master.geometry(
        #     f'{self.size[0]}x{self.size[1]}+{self.master.pos[0] + round(self.master.size[0] / 2) - round(self.size[0] / 2)}+{self.master.pos[1] + round(self.master.size[1] / 2) - round(self.size[1] / 2)}')

        self.yt_streams_frame = Frame(self, bg=self.bg_dark)
        self.video_frame = Frame(self.yt_streams_frame, bg=self.bg_dark)
        self.audio_frame = Frame(self.yt_streams_frame, bg=self.bg_dark)
        self.b_frame = Frame(self, bg=self.bg_dark)

        self.video_l = Label(self.video_frame, text='VIDEO', font=self.font, relief='flat',
                             bg=self.bg_dark,
                             bd=0, fg=self.fg_medium)

        self.audio_l = Label(self.audio_frame, text='AUDIO', font=self.font, relief='flat',
                             bg=self.bg_dark,
                             bd=0, fg=self.fg_medium)
        self.buttons = []

        self.stream_b = Button(self.b_frame, text='  Stream  ', font=self.font, relief='flat',
                               bg=self.bg_dark, bd=2, activebackground=self.bg_medium, fg=Ui.fg_accent, activeforeground=self.fg_dark, disabledforeground=self.fg_light, command=self.stream, state=DISABLED)
        self.copy_url_b = Button(self.b_frame, text='  Copy Link  ', font=self.font, relief='flat',
                                 bg=self.bg_dark, bd=2, activebackground=self.bg_medium, fg=self.fg_medium, activeforeground=self.fg_dark, disabledforeground=self.fg_light, command=self.copy_url, state=DISABLED)

        self.var_ = IntVar(self.master, -1)
        self.var_.trace_add(("write", "unset"), self.on_var_changed)

        self.video_l.pack(side='top', pady=5, anchor='center')
        self.audio_l.pack(side='top', pady=5, anchor='center')

        for i, info in enumerate(self.yt_infos):
            button = self.create_b(self.audio_frame if info.type_code == YtStreamInfo.TYPE_AUDIO else self.video_frame, i, str(info))
            self.buttons.append(button)
            button.pack(side='top', anchor='center', padx=2, pady=2, fill='x', expand='yes')

        # self.cap_.place(y=5, relx=0.5, anchor='n')
        # self.video_frame.place(x=0, y=30, relwidth=0.5)
        # self.audio_frame.place(relx=.5, y=30, relwidth=0.5)
        #
        # self.stream_b.place(anchor='s', relx=0.25, rely=.95, relwidth=0.45)
        # self.copy_url_b.place(anchor='s', relx=0.75, rely=.95, relwidth=0.45)

        self.video_frame.pack(side='left', anchor='n', expand=True, padx=1, pady=2)
        self.audio_frame.pack(side='right', anchor='n', expand=True, padx=1, pady=2)
        self.yt_streams_frame.pack(side='top', fill='x', expand=True, padx=6, pady=2)

        self.stream_b.pack(side='right', padx=2)
        self.copy_url_b.pack(side='right', padx=2)

        self.b_frame.pack(side='top', anchor='e', padx=2, pady=8)

        # ..........................
        # self.master.focus_set()
        # self.master.protocol('WM_DELETE_WINDOW', self.master.destroy)
        # ..................................




    # class UrlFrame(Frame):
    #     def __init__(self, master, **kwargs):
    #         self.master = master
    #         self.size = list(self.master.size)
    #
    #         # .........
    #         self.master.geometry(
    #             f'{self.size[0]}x{self.size[1]}+{self.master.pos[0]}+{self.master.pos[1]}')
    #         # .........
    #
    #         self.info_dic = {}
    #         self.yt_infos = []  # url info to be given to master
    #         self.yt__ = None
    #         self.chunk_size = 1024  # in bytes
    #
    #         Frame.__init__(self, master, bg=self.bg, **kwargs)
    #         # .......................Reusable widgets
    #         self.cap_ = Label(self, font=('product sans', 10, 'bold'), relief='flat', bg=self.bg, bd=0, fg=self.fg)
    #
    #         # .........................
    #         self.url_e = Entry(self, font=('product sans', 10), fg=self.fg, bg=rgb(200, 200, 200), relief='groove',
    #                            width=self.size[0] // 8, bd=2)
    #
    #         self.submit_b = Button(self, text='OK', font=('product sans', 10), relief='flat', width=6, bg=self.bg,
    #                                bd=0,
    #                                activebackground=self.abg, activeforeground=self.fg, fg=self.fg,
    #                                command=self.submit)
    #
    #         self.analyse_progress = RcScale(self, width=self.size[0], height=10, value=0, slider=False,
    #                                         troughcolor1='skyblue', bg='grey')
    #
    #         self.video_frame = None
    #         self.audio_frame = None
    #         self.video_l = None
    #         self.audio_l = None
    #         self.buttons = None
    #         self.stream_b = None
    #         self.copy_url_b = None
    #         self.var_ = None
    #
    #         self.pack_entry_widgets()
    #
    #         self.pack(expand='yes', fill=BOTH)
    #
    #     def check_var(self):
    #         return self.var_ and 0 <= self.var_.get() < len(self.yt_infos)
    #
    #     def check_var_or_hsow_msg(self):
    #         if not self.check_var():
    #             messagebox.showwarning("Warning", "No stream selected. Tap on a stream to select it", parent=self.master)
    #             return False
    #         return True
    #
    #     def on_var_changed(self, *args, **kwargs):
    #         state = NORMAL if self.check_var() else DISABLED
    #         self.stream_b['state'] = self.copy_url_b['state'] = state
    #
    #     def copy_url(self):
    #         if not self.check_var_or_hsow_msg():
    #             return
    #         U.copy_to_clipboard(self, self.yt_infos[self.var_.get()].url, append=False)
    #         SnackBar.show_msg_copied_to_clipboard(self.master.master, label="Youtube stream link")
    #
    #     def __stream_ytinfo_thread(self, info: YtStreamInfo):
    #         try:
    #             self.master.stream_call(url=info.url, title=self.info_dic['title'])
    #         except Exception as e:
    #             messagebox.showerror("Error", "failed to stream " + self.info_dic['title'], parent=self.master)
    #         finally:
    #             self.master.after(1000, self.reset_stream_b)
    #
    #     def stream(self):
    #         """
    #         returns info_object : list of tuples (type_, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
    #         """
    #         if not self.check_var_or_hsow_msg():
    #             return
    #
    #         self.stream_b['text'] = 'Streaming' + Ui.CHR_ELLIP
    #         self.stream_b['state_'] = DISABLED
    #         info = self.yt_infos[self.var_.get()]
    #
    #         stream_th__ = Thread(target=self.__stream_ytinfo_thread, args=(info, ))
    #         stream_th__.setDaemon(True)
    #         stream_th__.start()
    #
    #     def reset_stream_b(self):
    #         self.stream_b['state_'] = NORMAL
    #         self.stream_b['text'] = 'Stream'
    #
    #     def pack_entry_widgets(self):
    #
    #         # ..........................................
    #         self.master.overrideredirect(False)
    #         self.master.protocol('WM_DELETE_WINDOW', self.master.destroy)
    #         # ................................................
    #
    #         self.cap_['font'] = ('product sans', 10, 'bold')
    #         self.cap_['text'] = 'Enter the URL'
    #         self.url_e.delete(0, END)
    #         self.cap_.pack(pady=10)
    #         self.url_e.pack(padx=15)
    #         self.submit_b.pack(pady=10)
    #
    #         self.url_e.focus_set()
    #         self.url_e.bind('<Escape>', lambda event__: self.master.destroy())
    #         self.url_e.bind('<Return>', lambda event__: self.submit())
    #         self.url_e.bind('<Control-x>', lambda event__, _a=0, b=END: self.url_e.delete(_a, b))
    #
    #     def unbind_url_e(self):
    #         self.url_e.focus_set()
    #         self.url_e.unbind('<Escape>')
    #         self.url_e.unbind('<Return>')
    #         self.url_e.unbind('<Control-x>')
    #
    #     def submit(self):
    #         url_ = self.url_e.get()
    #
    #         if not url_:
    #             messagebox.showwarning('Waring', 'Please enter a url : ERR_NO_INPUT', parent=self.master)
    #             return
    #
    #         validator = URLValidator()
    #         try:
    #             validator(url_)
    #         except ValidationError:
    #             messagebox.showerror('Error', 'Invalid URL : ERR_MEDIA_RESOURCE_LOCATOR', parent=self.master)
    #             self.url_e.delete(0, END)
    #             return
    #         # if 'youtube' in url_.lower() or 'youtu.be' in url_.lower():
    #         if U.is_url_youtube(url_):
    #             self.unbind_url_e()
    #             self.url_e.pack_forget()
    #             self.submit_b.pack_forget()
    #             self.cap_.pack_forget()
    #             self.cap_['font'] = ('product sans', 10, 'bold')
    #             self.cap_['text'] = 'Analysing'
    #             self.cap_.pack(pady=25)
    #             self.analyse_progress.pack(side=BOTTOM, anchor=S, pady=0)
    #
    #             # ..........................................
    #             self.master.protocol('WM_DELETE_WINDOW', lambda: print('cannot destroy stream window'))
    #             # ................................................
    #
    #             analyse_thread = Thread(target=self.analyse_youtube_url, args=(url_,))
    #             analyse_thread.setDaemon(True)
    #             analyse_thread.start()
    #         else:
    #             try:
    #                 self.master.stream_call(url=url_)
    #             except Exception as e:
    #                 messagebox.showerror("Error", "failed to stream " + url_ + ". Check your internet connection and access to url", parent=self.master)
    #             finally:
    #                 self.master.destroy()
    #
    #     def analyse_youtube_url(self, url__):
    #         import pafy
    #         """
    #         info_object : list of tuples (type_, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
    #         """
    #         try:
    #             self.analyse_progress.set(10)
    #             videos_count = 0
    #
    #             pafy.set_api_key(C.YT_API_KEY)
    #             self.yt__ = pafy.new(url__)
    #             self.analyse_progress.set(50)
    #             self.info_dic['title'] = ''.join(i for i in self.yt__.title if
    #                                              i in {'K', 'o', '_', 'J', '2', 'B', 'u', 'i', 'F', '1', 's', 'P', '.',
    #                                                    'k', 'a', 'r', 'Z', 'd', 'h', 'm', 'q',
    #                                                    'S', 'O', '5', ' ', 'Y', 'Q', 'V', 'j', '-', 'C', 'v', 'T', '(',
    #                                                    'M', 'g', '0', '4', 'N', 'U', 'w', 'H',
    #                                                    'I', 't', 'D', 'n', 'X', 'L', ')', 'A', 'R', 'l', '6', 'b', 'f',
    #                                                    'p', 'z', 'W', '7', '8', 'x', '3', 'E',
    #                                                    'e', 'c', 'G', '9', 'y'})
    #             self.analyse_progress.set(60)
    #
    #             all_streams = self.yt__.allstreams
    #
    #             if self.yt__.audiostreams:
    #                 self.info_dic['main_audio'] = YtStreamInfo(self.yt__.audiostreams[0], YtStreamInfo.TYPE_AUDIO)
    #
    #             self.info_dic.update(
    #                 {'author': self.yt__.author, 'description': self.yt__.description, 'likes': self.yt__.likes,
    #                  'dislikes': self.yt__.dislikes, 'rating': self.yt__.rating, 'thumb_url': self.yt__.thumb,
    #                  'hdthumb_url': self.yt__.bigthumbhd, 'views': self.yt__.viewcount, 'genre': self.yt__.category}
    #             )
    #
    #             for stream in all_streams:
    #                 info = YtStreamInfo(stream)
    #                 if info.type != YtStreamInfo.TYPE_AUDIO and info.ext == 'webm':
    #                     continue
    #                 if info.type == YtStreamInfo.TYPE_NORMAL:
    #                     videos_count += 1
    #                 self.yt_infos.append(info)
    #
    #             self.analyse_progress.set(90)
    #
    #             self.size[0] = 400
    #             self.size[1] = (videos_count * 28) + 105
    #             self.analyse_progress.set(100)
    #             self.youtube_stream_ui()
    #
    #         except Exception as e:
    #             print(e)
    #             self.analyse_progress.pack_forget()
    #             self.pack_entry_widgets()
    #             messagebox.showerror('Network Error', 'Connection to server failed : ERR_NO_INTERNET', parent=self.master)
    #
    #     def create_b(self, master, index: int, text: str):
    #         return Radiobutton(master, text=text
    #                            , value=index, variable=self.var_, font=('product sans', 10),
    #                            relief='flat', indicator=0, overrelief='raised',
    #                            bg=self.bg, fg=self.fg, bd=0, selectcolor=self.abg)
    #
    #     def youtube_stream_ui(self):
    #         """
    #         info_object : list of tuples (type_code, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
    #         """
    #         self.analyse_progress.pack_forget()
    #         self.analyse_progress.set(0)
    #         self.cap_.pack_forget()
    #         self.cap_['font'] = ('product sans', 9)
    #         self.cap_['text'] = Ui.ellip(self.info_dic['title'], 50)
    #
    #         self.master.geometry(
    #             f'{self.size[0]}x{self.size[1]}+{self.master.pos[0] + round(self.master.size[0] / 2) - round(self.size[0] / 2)}+{self.master.pos[1] + round(self.master.size[1] / 2) - round(self.size[1] / 2)}')
    #
    #         self.video_frame = Frame(self, bg=self.bg)
    #         self.audio_frame = Frame(self, bg=self.bg)
    #
    #         self.video_l = Label(self.video_frame, text='VIDEO', font=('product sans medium', 10), relief='flat',
    #                              bg=self.bg,
    #                              bd=0, fg=self.fg)
    #
    #         self.audio_l = Label(self.audio_frame, text='AUDIO', font=('product sans medium', 10), relief='flat',
    #                              bg=self.bg,
    #                              bd=0, fg=self.fg)
    #         self.buttons = []
    #
    #         self.stream_b = Button(self, text='Stream', font=('product sans', 10), relief='flat',
    #                                bg=self.abg, bd=2, activebackground=self.abg, fg=self.fg, command=self.stream, state=DISABLED)
    #         self.copy_url_b = Button(self, text='Copy Link', font=('product sans', 10), relief='flat',
    #                                  bg=self.abg, bd=2, activebackground=self.abg, fg=self.fg, command=self.copy_url, state=DISABLED)
    #
    #         self.var_ = IntVar(self.master, -1)
    #         self.var_.trace_add(("write", "unset"), self.on_var_changed)
    #
    #         self.video_l.pack(pady=5)
    #         self.audio_l.pack(pady=5)
    #
    #         for i, info in enumerate(self.yt_infos):
    #             button = self.create_b(self.audio_frame if info.type_code == YtStreamInfo.TYPE_AUDIO else self.video_frame, i, str(info))
    #             self.buttons.append(button)
    #             button.pack(pady=2, fill='x', padx=2, expand='yes')
    #
    #         self.cap_.place(y=5, relx=0.5, anchor='n')
    #
    #         self.video_frame.place(x=0, y=30, relwidth=0.5)
    #         self.audio_frame.place(relx=.5, y=30, relwidth=0.5)
    #
    #         self.stream_b.place(anchor='s', relx=0.25, rely=.95, relwidth=0.45)
    #         self.copy_url_b.place(anchor='s', relx=0.75, rely=.95, relwidth=0.45)
    #
    #         # ..........................
    #         self.master.focus_set()
    #         self.master.protocol('WM_DELETE_WINDOW', self.master.destroy)
    #         # ..................................


class VolWin(Toplevel):
    Instance = None

    def __init__(self, master, range_=200, color1=rgb(255, 112, 52),
                 color2=rgb(40, 40, 40), out_color=rgb(30, 30, 30), width_=35, outwidth=2, pad=0, destruct_time=2000,
                 **kwargs):
        self.master = master
        self.width = round(width_)
        self.range = range_
        self.pad = pad
        self.destruct_time = destruct_time  # in ms
        self.out_width = outwidth  # pixels of outline
        self.height = round((self.range * 2) + self.pad + (self.out_width * 2))
        self.x = round((self.master.winfo_screenwidth() - self.width - 30))
        self.y = round((self.master.winfo_screenheight() - self.height) / 2)

        self.color2 = color2
        self.color1 = color1
        self.out_color = out_color

        self.pix_per_value_ = self.pix_per_value()

        Toplevel.__init__(self, master, **kwargs)
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.wm_attributes('-alpha', .6)
        self['bg'] = color2
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        self.canvas = Canvas(self, bg=color2, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand='yes')
        self.outrect_coords = (self.pad // 2, self.pad // 2, self.width - (self.pad // 2),
                               self.height - (self.pad // 2))

        self.canvas.create_rectangle(self.outrect_coords[0], self.outrect_coords[1], self.outrect_coords[2],
                                     self.outrect_coords[3], outline=self.out_color, width=self.out_width)
        self.inrect = None
        self.destruct = self.master.after(self.destruct_time, self.destroy_)
        VolWin.Instance = self

    def pix_per_value(self):
        return round((self.height - self.pad - (self.out_width * 2)) / self.range)

    def vol_to_pix(self, volume):
        return volume * self.pix_per_value_

    def draw(self, volume):
        self.timer_cancel()
        pix = self.vol_to_pix(volume)
        x1, y1 = self.width - (self.pad // 2) - self.out_width, self.height - (self.pad // 2) - self.out_width
        x0, y0 = self.pad // 2 + self.out_width, y1 - pix
        self.inrect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.color1, width=0)
        self.destruct = self.master.after(self.destruct_time, self.destroy_)

    def update_(self, volume):
        self.timer_cancel()
        pix = self.vol_to_pix(volume)
        x1, y1 = self.width - (self.pad // 2) - self.out_width, self.height - (self.pad // 2) - self.out_width
        x0, y0 = self.pad // 2 + self.out_width, y1 - pix
        self.canvas.coords(self.inrect, x0, y0, x1, y1)
        self.destruct = self.master.after(self.destruct_time, self.destroy_)

    def timer_cancel(self):
        if self.destruct is not None:
            self.master.after_cancel(self.destruct)
            self.destruct = None

    def destroy_(self):
        try:
            self.timer_cancel()
            self.destroy()
        except Exception as e:
            print(e)
        VolWin.Instance = None


class RcScale(Canvas):
    __name__ = 'RcScale'

    def __init__(self, master, value=0, mode='normal', troughcolor1='skyblue', troughcolor2='white', outline='',
                 outwidth=0, width=100, height=5, slider=True, slidercolor=None, **kwargs):
        """
        kwargs : for configuring underlying canvas
        width, height : for canvas in pixels
        value : in percent of range_

        troughcolor1: color of trough left to slider
        troughcolor2 : color of trough right to slider

        ...................... Refrences..........
        slider_w: slider widget refrence
        in_rect : trough
        out_rect : border rectangle
        """

        self.state = 'normal'
        self.width = width
        self.height = height
        self.out_width = outwidth

        self.trough_color1 = troughcolor1
        self.trough_color2 = troughcolor2
        kwargs['bg'] = self.trough_color2
        self.out_color = outline

        self.mode = mode
        self.slider = slider
        self.slider_color = slidercolor

        if self.slider_color is None:
            self.slider_color = self.trough_color1

        self.fixed = self.out_width, self.height - self.out_width  # in form of y0, y1
        self.auto_mode_coords = [0, 0]  # in form of x0, x1

        self.master = master

        self.in_width = self.width - (self.out_width * 2)
        self.in_height = self.height - (self.out_width * 2)
        self.value = value  # in percent

        Canvas.__init__(self, master, width=self.width, height=self.height, **kwargs)
        if self.out_width > 0:
            self.out_rect = self.create_rectangle(self.out_width / 2, self.out_width / 2,
                                                  self.width - (self.out_width / 2),
                                                  self.height - (self.out_width / 2), outline=outline, fill='',
                                                  width=outwidth)
        else:
            self.out_rect = None

        self.in_rect = None
        self.slider_w = None

        if self.mode == 'normal':
            self.set(value)
            self.auto_ = False
        else:
            self.auto_ = True

    def get_pix(self, value=None):
        if value is None:
            value = self.value
        """
        value : in percent
        """
        return (value * self.in_width) / 100

    def get_value(self, pix):
        """
        returns value in percent
        """
        return (pix / self.in_width) * 100

    @staticmethod
    def check(value):
        if value >= 100:
            return 100
        if value < 0:
            return 0
        return value

    def set(self, value):
        self.value = self.check(value)
        _pix_ = self.get_pix(self.value)
        if self.in_rect is None:
            self.in_rect = self.create_rectangle(self.out_width, self.fixed[0], self.out_width + _pix_, self.fixed[1],
                                                 fill=self.trough_color1, width=0)
        else:
            self.coords(self.in_rect, self.out_width, self.fixed[0], self.out_width + _pix_, self.fixed[1])

        if self.slider and self.state == 'normal':
            x0 = _pix_ + self.out_width - (self.height / 2) + 1
            x1 = x0 + self.height - 2
            if self.slider_w is None:
                self.slider_w = self.create_oval(x0, 1, x1, self.height - 1, fill=self.slider_color, width=0)
                # self.tag_bind(self.slider_w, '<B1-Motion>', self._auto_set)
            else:
                self.coords(self.slider_w, x0, 1, x1, self.height - 1)

    def get(self):
        return self.value

    def del_slider(self):
        if self.slider and self.slider_w is not None:
            self.delete(self.slider_w)
            self.slider_w = None

    def start(self, time=2, stepp=5, loop_master=None):
        self.auto_ = True
        self.del_slider()

        self.delete(self.in_rect)
        _step = stepp
        _time = round(((time * 1000) / (self.in_width * 2)) * _step)

        if _time < 5:
            _time = 5
            _step = ((self.in_width * 2) * _time) / (time * 1000)

        if loop_master is None:
            loop_master = self.master

        self.in_rect = self.create_rectangle(self.out_width, self.out_width, self.out_width, self.fixed[1],
                                             fill=self.trough_color1, width=0)

        def gen(cur=self.out_width):
            if self.auto_:
                if cur - self.out_width < self.in_width:
                    self.coords(self.in_rect, self.out_width, self.out_width, cur + _step, self.fixed[1])
                    loop_master.after(_time, gen, cur + _step)
                else:
                    des()

        def des(cur=self.out_width):
            if self.auto_:
                if cur < self.width - self.out_width - 1:
                    self.coords(self.in_rect, cur + _step, self.out_width, self.width - self.out_width - 1,
                                self.fixed[1])
                    loop_master.after(_time, des, cur + _step)
                else:
                    gen()

        gen()

    def stop(self, value=None):
        self.auto_ = False
        if value is None:
            value = self.value
        self.set(value)

    def set_slider(self, value=None):
        if not self.slider:
            return
        if self.state == 'disabled':
            return
        if value is None:
            value = self.value
        x0 = self.get_pix(value) + self.out_width - (self.height / 2)
        x1 = x0 + self.height
        if self.slider_w is None:
            self.slider_w = self.create_oval(x0, 0, x1, self.height, fill=self.slider_color, width=0)
        else:
            self.coords(self.slider_w, x0, 0, x1, self.height)

    def find_(self, x, y):
        _pix_ = self.get_pix() + self.out_width

        if self.slider and _pix_ - (self.height / 2) < x < _pix_ + (self.height / 2):
            return 'slider'

        if y < self.out_width or y > self.height - self.out_width:
            return 'border'

        if self.out_width < x <= _pix_:
            return 'trough1'
        return 'trough2'

    def __repr__(self):
        return f'RcScale({self.master.__class__.__name__}, {self.value}, {self.mode}, {self.trough_color1}, {self.trough_color2}, {self.out_color}, {self.out_width}, {self.width}, {self.height}, {self.slider}, {self.slider_color})'

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return other.value == self.value
        return False

    def _auto_set(self, event):
        self.set(self.get_value_from_x(event.x))

    def __add__(self, other):
        if other.__class__ == self.__class__:
            self.set(self.value + other.value)
            return True
        if type(other) in (int, float):
            self.set(self.value + other)
            return True
        return False

    def __sub__(self, other):
        if other.__class__ == self.__class__:
            self.set(self.value - other.value)
            return True
        if type(other) in (int, float):
            self.set(self.value - other)
            return True
        return False

    def __str__(self):
        return self.__repr__()

    def get_value_from_x(self, x):
        return self.get_value(x - self.out_width)

    def get_x_from_value(self, value):
        return self.get_pix(value) + self.out_width

    def disable(self):
        self.del_slider()
        self.config(state=DISABLED)
        self.state = 'disabled'

    def enable(self):
        self.config(state=NORMAL)
        self.state = 'normal'
        self.set_slider(self.value)

    def config_dim(self, width=None, height=None, out_width=None):
        if width is None and height is None:
            return
        if width is None and height == self.height:
            return
        if height is None and width == self.width:
            return

        if width is None:
            width = self.width
        if height is None:
            height = self.height
        if out_width is None:
            out_width = self.out_width

        self.width = self['width'] = width
        self.height = self['height'] = height
        self.out_width = out_width
        self.in_width = self.width - (out_width * 2)
        self.in_height = self.height - (out_width * 2)
        self.fixed = out_width, self.height - out_width
        if self.out_rect is not None:
            self.coords(self.out_rect, out_width / 2, out_width / 2, self.width - (out_width / 2),
                        self.height - (out_width / 2))

        if self.in_rect is not None:
            _pix_ = self.get_pix()
            self.coords(self.in_rect, out_width, out_width, self.out_width + _pix_, self.fixed[1])

            if self.slider_w is not None:
                x0 = _pix_ + self.out_width - (self.height / 2) + 1
                x1 = x0 + self.height - 2
                self.coords(self.slider_w, x0, 1, x1, self.height - 1)

    def animate(self, boxv=20, time=4, stepp=5, loop_master=None):
        self.auto_ = True
        self.del_slider()
        boxp = self.get_pix(boxv)
        self.delete(self.in_rect)
        _step = stepp
        _time = round(((time * 1000) / (self.in_width + (2 * boxp))) * _step)

        if loop_master is None:
            loop_master = self.master

        if _time < 5:  # to avoid infinite recursion
            _time = 5
            _step = ((self.in_width + (2 * boxp)) * _time) / (time * 1000)

        print(_time, _step)

        self.in_rect = self.create_rectangle(self.out_width, self.out_width, self.out_width, self.fixed[1],
                                             fill=self.trough_color1, width=0)

        def gen(cur=self.out_width):
            if self.auto_:
                if cur - self.out_width < boxp:
                    self.coords(self.in_rect, self.out_width, self.out_width, cur + _step, self.fixed[1])
                    loop_master.after(_time, gen, cur + _step)
                else:
                    f(cur)

        def f(cur):
            if self.auto_:
                if cur < self.width - self.out_width - 1:
                    self.move(self.in_rect, _step, 0)
                    loop_master.after(_time, f, cur + _step)
                else:
                    des(cur - boxp)

        def des(cur):
            if self.auto_:
                if cur < self.width - self.out_width - 1:
                    self.coords(self.in_rect, cur + _step, self.out_width, self.width - self.out_width - 1,
                                self.fixed[1])
                    loop_master.after(_time, des, cur + _step)
                else:
                    gen()

        th__ = Thread(target=gen)
        th__.setDaemon(True)
        th__.start()


if __name__ == '__main__':
    a = RcStr('RC', 'NU')
    print(a[0])
