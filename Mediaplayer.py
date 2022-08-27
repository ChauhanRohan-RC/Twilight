import os
import sys
from __c import C, U

# frozen_attr = getattr(sys, 'frozen', False)
# main_dir = os.path.dirname(sys.executable) if frozen_attr else os.path.dirname(
#     os.path.abspath(os.path.realpath(__file__)))
#
# sdk_dir = os.path.join(main_dir, 'sdk')
# C.sys_dir = os.path.join(sdk_dir, '__sys_dir')
# C.parallel_code_file = os.path.join(sdk_dir, '__parallel.cc')
# C.run_file = os.path.join(sdk_dir, '__run_file.cc')

_parallel_run_enabled = C.load_parallel_run_enabled()      # bool

if not _parallel_run_enabled and C.run_file_exists() and (not C.frozen or U.run_count(C.ExeName) > 1):
    # if paralel running is disabled and another instance is running
    if len(sys.argv) > 1:
        __paths = []
        for __p in sys.argv[1:]:
            if os.path.splitext(__p)[1] in C.all_format:
                __paths.append(__p)
        if __paths:
            from __classes import dump

            C.ensure_sys_dir()
            dump(__paths, os.path.join(C.sys_dir, f'{os.getpid()}.cc'))

    sys.exit(2)

C.ensure_run_file()
C.ensure_sys_dir()


from __classes import *
from __c import Ui, BinDings
from tkinter import filedialog, messagebox
import PIL.ImageTk, PIL.Image
import main_player
import shutil
import random
from itertools import chain
from subprocess import Popen

def print_(str__=None):  # dummy function
    pass


# C.icons_dir = os.path.join(C.sdk_dir, 'icons')
# screenshot_dir = os.path.join(sdk_dir, 'screenshots')

# if not os.path.isdir(C.default_screenshot_dir):
#     os.mkdir(C.default_screenshot_dir)  # creating directory for screenshots if not present


# exe_path = os.path.join(main_dir, f'{C.ExeName}.exe')
# win_icon_path = os.path.join(C.C.icons_dir, "app.ico")

# ....................................... filepath and vars ..................................................
__media_paths__ = []

delay = 1000  # delay to play next/previous_call in ms
thumbnail_info = [-1, (0, 0)]  # song thumbnail in form of [canvas id, (width, height)]

audio_list = []
sub_list = []
exsub_list = []

main_player_in = main_player.Instance()
player = main_player_in.media_player_new('--low-delay')
cursor_hide_timer = None


# previous media
# _past_file = os.path.join(sdk_dir, 'mpast.cc')
# _playlist_file = os.path.join(sdk_dir, 'playlists.cc')
# _playback_file = os.path.join(sdk_dir, 'playback.cc')
# _settings_file = os.path.join(sdk_dir, 'settings.cc')
# _bindings_file = os.path.join(sdk_dir, 'bindings.cc')
#

# .................................................RC Classes.....................


class SetName:
    func_dic = {}

    """ Decorator to set __name__ attr of functions used in bindings 
        func_dic : dic to hold  func.__name__ : func
    """

    def __init__(self, name=''):
        self.name = name

    def __call__(self, _func):
        if self.name: _func.__qualname__ = self.name
        self.__class__.func_dic[_func.__qualname__] = _func
        return _func


class PlayWin(Toplevel):

    def __init__(self, master, title, size=(310, 410), minsize=(310, 190), pos=(0, 0)):
        self.title_ = title
        self.bg = 'black'
        self.fg = 'white'
        self.abg = rgb(40, 40, 40)
        self.afg = 'white'

        self.w_init, self.h_init = size
        self.x_init, self.y_init = pos
        self.geometry_ = f'{self.w_init}x{self.h_init}+{self.x_init}+{self.y_init}'
        Toplevel.__init__(self, master)
        self.withdraw()  # hidden at startup ,stste_ = 0
        self.title(title)
        self.iconbitmap(C.app_icon_file)
        self.minsize_ = minsize
        self.minsize(*minsize)
        self.protocol('WM_DELETE_WINDOW', self.un_dock)

        self.search_canvas = Canvas(self, bg=self.bg, highlightthickness=0, bd=0, height=40)  # for search widgets
        self.play_canvas = Canvas(self, bg=self.bg, highlightthickness=2, bd=0)  # for listbox
        self.canvas = Canvas(self, bg=self.bg, bd=0, highlightthickness=0)  # for dock buttons

        self.current_indx = None
        self.search_mode_ = False
        self.search_results = []

        self.yscroll = Scrollbar(self.play_canvas, orient='vertical')
        self.xscroll = Scrollbar(self, orient='horizontal')
        self.playlist = Listbox(self.play_canvas,
                                font=('product sans', 10),
                                selectmode=SINGLE, height=2,
                                yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set, activestyle='dotbox')

        self.yscroll.config(command=self.playlist.yview)
        self.xscroll.config(command=self.playlist.xview)

        self.save_b = Button(self.canvas, text=' Save ', font=('product sans', 10), command=save_playlist,
                             activebackground=self.abg, bg=self.bg, bd=0, relief='flat', fg=self.fg,
                             activeforeground=self.afg)
        self.remove_b = Button(self.canvas, text=' Remove ', font=('product sans', 10), command=remove_media, bd=0,
                               relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                               activeforeground=self.afg)
        self.previous_b = Button(self.canvas, image=previous_image, command=previous_call, bd=0, relief='flat',
                                 activebackground=self.abg, bg=self.bg, fg=self.fg, activeforeground=self.afg,
                                 font=('product sans', 10))
        self.next_b = Button(self.canvas, image=next_image, command=next_call, bd=0, relief='flat',
                             activebackground=self.abg, bg=self.bg, fg=self.fg, activeforeground=self.afg,
                             font=('product sans', 10))
        self.shuffle_b = Button(self.canvas, text=' Shuffle ', font=('product sans', 10), command=shuffle, bd=0,
                                relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                                activeforeground=self.afg)
        self.clear_b = Button(self.canvas, text=' Clear ', font=('product sans', 10), command=clear_playlist, bd=0,
                              relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                              activeforeground=self.afg)
        self.organise_b = Button(self.canvas, text='Organise', font=('product sans', 10), command=self.organise, bd=0,
                                 relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                                 activeforeground=self.afg)
        self.up_b = Button(self.canvas, text=' Move Up ', font=('product sans', 10), command=self.up, bd=0,
                           relief='flat',
                           activebackground=self.abg, bg=self.bg, fg=self.fg, activeforeground=self.afg)
        self.down_b = Button(self.canvas, text=' Move Down ', font=('product sans', 10), command=self.down, bd=0,
                             relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                             activeforeground=self.afg)
        self.exit_org_b = Button(self.canvas, image=previous_image, font=('product sans', 10),
                                 command=self.exit_organise, bd=0,
                                 relief='flat', activebackground=self.abg, bg=self.bg, fg=self.fg,
                                 activeforeground=self.afg)

        self.search_b = Button(self.search_canvas, text='Search', font=('product sans', 10, 'italic'), bg=self.bg,
                               fg=self.fg, bd=0, relief='flat',
                               activebackground=self.abg, command=self.search_mode, activeforeground=self.afg)
        self.search_e = Entry(self.search_canvas, relief='flat', bg=rgb(230, 230, 230), font=('product sans', 10),
                              fg='darkgreen')
        self.cancel_search = Button(self.search_canvas, text='X', relief='flat', font=('product sans', 10, 'bold'),
                                    bd=0, bg=self.bg,
                                    fg=self.fg, activebackground=self.abg
                                    , command=self.cancel_search_mode, width=5, activeforeground=self.afg)
        self.search_b.pack(fill=BOTH, expand='yes', pady=10)

        self.yscroll.pack(side=RIGHT, fill=Y, expand='no', anchor='ne')
        self.playlist.pack(side=LEFT, expand='yes', fill='both', anchor='nw')

        self.bindings = chain(bindings_dict['playback'].items(), bindings_dict['playwin'].items())

        for __n, __s in self.bindings:
            self.bind(__s, SetName.func_dic[__n])

        self.playlist.bind('<Delete>', remove_media)
        self.playlist.bind('<Double-Button-1>', active)
        self.playlist.bind('<Return>', active)
        self.playlist.bind('<Button-1>', self.set_current)
        self.playlist.bind('<B1-Motion>', self.drag)
        self.playlist.bind('<Up>', self.search_init)

        # theme
        self.resizable(1, 1)
        self['bg'] = self.bg
        self.playlist['relief'] = 'flat'
        self.playlist['bd'] = 3
        self.playlist['bg'] = rgb(20, 20, 20)
        self.playlist['fg'] = rgb(225, 225, 225)
        self.playlist['selectbackground'] = 'white'  # rgb(80, 80, 80)
        self.playlist['selectforeground'] = 'black'  # rgb(255, 255, 255)

        self.bind_input_keys()
        self.playlist.focus_set()
        self.pack_w()
        self.playlist.focus_set()

    def __repr__(self):
        return f'PlayWin({self.master},{self.title_}, {self.size}, {self.minsize_})'

    def bind_input_keys(self):
        for __n, __s in self.bindings:
            if __s in ('<Left>', '<Right>', '<space>', '<Escape>'):
                if __n == count.__qualname__:
                    if player.get_state() in (3, 4):
                        self.bind(__s, pause)
                    else:
                        self.bind(__s, count)
                    continue
                self.bind(__s, SetName.func_dic[__n])

    def unbind_input_keys(self):
        try:
            self.unbind('<space>')
            self.unbind('<Left>')
            self.unbind('<Right>')
            self.unbind('<Escape>')
        except EXCEPTION:
            pass

    def set_focus_on_playlist(self, event=None):
        if self.search_mode_:
            self.cancel_search_mode()
        self.playlist.focus_set()

    def search_init(self, event=None):
        if self.get_active() == 0:
            self.search_mode()

    def search_mode(self, event=None):
        self.search_b.pack_forget()
        self.search_e.bind('<Return>', self.search_)
        self.search_e.bind('<Escape>', self.cancel_search_mode)
        self.search_e.bind('<Down>', self.set_focus_on_playlist)

        self.search_e.pack(side=LEFT, expand='yes', fill='both', anchor='nw', padx=10, pady=10)
        self.cancel_search.pack(side=RIGHT, fill=Y, expand='no', anchor='ne', padx=5)

        self.search_e.focus_set()
        self.unbind_input_keys()
        self.search_mode_ = True
        self.search_loop()

    def search_(self, event=None):
        text_ = self.search_e.get()
        self.search_results = search_name_in_paths(text_, __media_paths__)  # in paths form
        self.insert_pathseq(self.search_results)
        if not self.search_results:
            self.search_e['fg'] = 'red'
        else:
            self.search_e['fg'] = 'darkgreen'

    def search_loop(self):
        if self.search_mode_:
            if self.focus_get() == self.search_e:  # if search box is in focus
                self.search_()
            self.after(500, self.search_loop)

    def insert_pathseq(self, seq):
        self.playlist.delete(0, END)
        for path_ in seq:
            self.playlist.insert(END, self.display_name(os.path.basename(path_)))

    def cancel_search_mode(self, event=None):
        self.cancel_search.pack_forget()
        self.search_e.pack_forget()
        self.search_e.unbind('<Escape>')
        self.search_e.unbind('<Return>')
        self.search_b.pack(fill=BOTH, expand='yes', pady=10)
        self.search_results.clear()
        self.search_mode_ = False
        self.playlist.focus_set()
        self.bind_input_keys()
        self.insert_pathseq(__media_paths__)

    def set_current(self, event):
        self.current_indx = self.playlist.nearest(event.y)

    def drag(self, event):
        if not self.search_mode_:
            i = self.playlist.nearest(event.y)
            playing = __media_paths__[_play_count.v]
            if i < self.current_indx:
                x = self.playlist.get(i)
                path_ = __media_paths__.pop(i)
                self.playlist.delete(i)
                self.playlist.insert(i + 1, x)
                __media_paths__.insert(i + 1, path_)
                self.current_indx = i
                self.playlist.activate(i)
            elif i > self.current_indx:
                x = self.playlist.get(i)
                path_ = __media_paths__.pop(i)
                self.playlist.delete(i)
                self.playlist.insert(i - 1, x)
                __media_paths__.insert(i - 1, path_)
                self.current_indx = i
                self.playlist.activate(i)

            _play_count.v = __media_paths__.index(playing)

    def pack_w(self, all_=True):
        # packing
        if all_:
            self.search_canvas.pack(anchor=NW, fill=X, expand='no')
            self.play_canvas.pack(fill=BOTH, expand='yes', anchor=NW)
            self.xscroll.pack(fill=X)
            self.canvas.pack(side=LEFT, anchor=NW, expand='yes', fill=X)

        self.save_b.pack(side=LEFT, anchor=S, padx=1, pady=9)
        self.shuffle_b.pack(side=LEFT, anchor=S, padx=1, pady=9)
        self.previous_b.pack(side=LEFT, anchor=S, padx=4, pady=5)
        self.clear_b.pack(side=RIGHT, anchor=SE, padx=1, pady=9)
        self.organise_b.pack(side=RIGHT, anchor=S, padx=1, pady=9)
        self.next_b.pack(side=RIGHT, anchor=S, padx=4, pady=5)

    def pack_f(self):
        for widget in self.canvas.winfo_children():
            widget.pack_forget()

    def organise(self):
        self.pack_f()
        self.exit_org_b.pack(side=LEFT, padx=10, pady=12)
        self.up_b.pack(side=LEFT, padx=8, pady=12)
        self.remove_b.pack(side=RIGHT, padx=10, pady=12)
        self.down_b.pack(side=RIGHT, padx=8, pady=12)

    def up(self):
        if not self.search_mode_:
            in__up = self.playlist.index(ACTIVE)
            if in__up is not None:
                if in__up > 0:
                    x__ = self.playlist.get(in__up)
                    self.pop(in__up)
                    path_ = __media_paths__.pop(in__up)
                    self.playlist.insert(in__up - 1, x__)
                    __media_paths__.insert(in__up - 1, path_)
                    self.playlist.activate(in__up - 1)

    def down(self):
        if not self.search_mode_:
            in__down = self.playlist.index(ACTIVE)
            if in__down is not None:
                if in__down < len(__media_paths__) - 1:
                    x__ = self.playlist.get(in__down)
                    self.pop(in__down)
                    path_ = __media_paths__.pop(in__down)
                    self.playlist.insert(in__down + 1, x__)
                    __media_paths__.insert(in__down + 1, path_)
                    self.playlist.activate(in__down + 1)

    def exit_organise(self):
        self.pack_f()
        self.pack_w(all_=False)

    @staticmethod
    def display_name(name: str):
        return f'\u2022  {name}'

    def insert(self, m_paths):
        for name in map(os.path.basename, m_paths):
            self.playlist.insert(END, self.display_name(name))

    def pop_active(self):
        try:
            n = self.playlist.curselection()
            if n:
                n_in = n[0]
                self.playlist.delete(n_in[0])
        except Exception as e:
            print_(e)

    def pop(self, index):
        try:
            self.playlist.delete(index)
        except Exception as e:
            print_(e)

    def get_active(self):
        try:
            return self.playlist.index(ACTIVE) if not self.search_mode_ else __media_paths__.index(
                self.search_results[self.playlist.index(ACTIVE)])
        except Exception as e:
            print(e)
            return None

    def clear(self):
        self.playlist.delete(0, END)

    def dock(self):
        self.geometry(self.geometry_)
        self.insert_pathseq(__media_paths__)
        self.deiconify()
        self.update()
        self.attributes('-topmost', True)
        self.playlist.focus_force()

    def un_dock(self):
        self.geometry_ = self.winfo_geometry()
        # self.attributes('-topmost', False)
        self.withdraw()


class FsDock(Toplevel):
    def __init__(self, master, player_):
        self.master = master
        self.player = player_
        self.width = screen_width - (Ui.fsdock_screen_padx * 2)
        self.height = Ui.fsdock_h
        self.x, self.y = round((screen_width - self.width) / 2), screen_height - self.height - Ui.fsdock_screen_pady
        self.x2, self.y2 = self.x + self.width, self.y + self.height

        self.bg = rgb(150, 150, 150)
        self.obg = rgb(50, 51, 50)
        self.fg = 'white'

        Toplevel.__init__(self, master=master)
        self.withdraw()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.wm_attributes('-transparentcolor', self.bg)
        self.protocol('WM_DELETE_WINDOW', exit_diag)
        self.set_m_by_slider = False

        self.c_time = Label(self, text="--.--", bg=self.bg, fg=self.fg, font=('product sans', 10), width=10)
        self.f_time = Label(self, text="--.--", bg=self.bg, fg=self.fg, font=('product sans', 10), width=10)
        self.f_time.bind('<Button-1>', toggle_fulltime_state)

        self.m_scale = RcScale(self, slider=True, value=0, width=100, height=16,
                               slidercolor=rgb(240, 123, 7),
                               troughcolor1=rgb(240, 123, 7), troughcolor2='white', outline=self.obg, outwidth=6,
                               relief='flat', bd=0, highlightthickness=0)

        self.m_scale.bind("<ButtonRelease-1>", self.m_scale_release_call)
        self.m_scale.bind("<Button-1>", self.m_scale_click_call)
        self.m_scale.bind("<B1-Motion>", self.m_scale_motion_call)
        self.destruct_time = Ui.fsdock_hide_ms  # in ms
        self.d_timer = self.master.after(self.destruct_time, self.un_dock)

        self['bg'] = self.bg
        self.bind('<Motion>', motion_handler)

        self.place_widgets()
        self.set_scale = True
        self.auto_set()
        for __n, __seq in chain(bindings_dict['playback'].items(), bindings_dict['win'].items()):
            self.bind(__seq, SetName.func_dic[__n])

        self.anm_time = Ui.fsdock_anim_ms  # in ms
        self._alpha_step = Ui.fsdock_alpha_step  # transparency step
        self._anm_time = round(self.anm_time * self._alpha_step)

    def ctime_label_w(self, update=False):
        if update:
            self.master.update()
        return self.c_time.winfo_width()

    def calculate_mscale_w_del(self, update=False):
        return self.ctime_label_w(update) * 2

    def calculate_mscale_w(self, update=False):
        return self.width - self.calculate_mscale_w_del(update)

    def calculate_mscale_x(self, update=False):
        return self.ctime_label_w(update)

    def calculate_mscale_x_screen_offset(self, update=False):
        return self.x + self.calculate_mscale_x(update)

    def mscale_x(self, update=False):
        if update:
            self.master.update()
        return int(self.m_scale.place_info()['x'])

    def mouse_over(self, *pos):
        if self.x < pos[0] < self.x2 and self.y < pos[1] < self.y2:
            return True
        return False

    def d_timer_cancel(self, event=None):
        if self.d_timer is not None:
            try:
                self.master.after_cancel(self.d_timer)
            except Exception as e:
                print(e)
            self.d_timer = None

    def d_timer_reset(self, event=None):
        self.d_timer_cancel()
        self.d_timer = self.master.after(self.destruct_time, self.un_dock)

    def un_dock(self):
        self._anm_undock()

    def dock(self, reset_timer=True):
        self.auto_set()
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.deiconify()
        self.update()
        self.attributes('-topmost', True)
        show_cursor()
        self._anm_dock(reset_timer=reset_timer)

    def _anm_dock(self, cur_alpha=0.00, reset_timer=True):
        if cur_alpha < 1 - self._alpha_step:
            cur_alpha += self._alpha_step
            self.attributes('-alpha', cur_alpha)
            self.master.after(self._anm_time, self._anm_dock, cur_alpha, reset_timer)
        else:
            self.attributes('-alpha', 1.00)
            if reset_timer:
                self.d_timer_reset()

    def _anm_undock(self, cur_alpha=1.00):
        if cur_alpha > self._alpha_step:
            cur_alpha -= self._alpha_step
            self.attributes('-alpha', cur_alpha)
            self.master.after(self._anm_time, self._anm_undock, cur_alpha)
        else:
            reset_cursor_hide_timer()
            self.attributes('-alpha', 0.00)
            self.attributes('-topmost', False)
            self.withdraw()
            self.d_timer_cancel()

    def place_widgets(self):
        self.c_time.place(anchor='nw', x=0, y=Ui.fsdock_pady)
        self.f_time.place(anchor='ne', relx=1, y=Ui.fsdock_pady)

        self.m_scale.config_dim(width=self.calculate_mscale_w(update=True))
        self.m_scale.place(x=self.calculate_mscale_x(), y=Ui.fsdock_pady + 1)

    def m_scale_release_call(self, event=None):
        if self.set_m_by_slider:
            _value_ = self.m_scale.get_value_from_x(event.x)
            self.player.set_position(_value_ / 100)
            __in = PreDisplay.Instance
            if isinstance(__in, (PreDisplay,)) and __in.state == 1:
                __in.un_dock()
        self.set_scale = True

    def m_scale_motion_call(self, event):
        if self.set_m_by_slider:
            _pos = self.m_scale.get_value_from_x(event.x)
            if PreDisplay.m_path:
                _p_pos = _pos / 100
                PreDisplay.Instance.config_(_p_pos, event.x)
            self.m_scale.set(_pos)

    def m_scale_click_call(self, event=None):
        if player.get_state() in (3, 4):
            self.set_scale = False
            _pos = self.m_scale.get_value_from_x(event.x)
            _p_pos = _pos / 100
            if self.m_scale.find_(event.x, event.y) == 'slider':
                if PreDisplay.m_path:
                    __in = PreDisplay.Instance
                    __xoff = self.calculate_mscale_x_screen_offset()
                    if isinstance(__in, (PreDisplay,)):
                        __in.xoff = __xoff
                        PreDisplay.Instance.dock(_p_pos, event.x, self.y)
                    else:
                        PreDisplay(win, _p_pos, event.x, self.y, xoff=__xoff, yoff=10)

                self.set_m_by_slider = True
            else:
                self.set_m_by_slider = False
                player.set_position(_p_pos)
                self.m_scale.set(_pos)

    def auto_set(self):
        if self.set_scale:
            self.m_scale.set(self.player.get_position() * 100)


class Controller(Toplevel):
    Instance = None
    im_dim = 24

    def __init__(self, master, size=(200, 90), spadx=5, spady=60, override=True, **kwargs):
        self.width = size[0]
        self.height = size[1]
        self.spadx = spadx
        self.spady = spady
        self.x, self.y = self.load_coordinates()
        self.master = master

        super().__init__(master, **kwargs)
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')

        self.overrideredirect(override)
        self.override = override
        self.attributes('-topmost', True)
        self.resizable(0, 0)
        self.wm_attributes('-alpha', 0.9)
        self.protocol('WM_DELETE_WINDOW', self.raise_main)
        self.iconbitmap(C.app_icon_file)

        self.bg = 'black'
        self.abg = rgb(20, 20, 20)
        self.fg = 'white'
        self['bg'] = self.bg

        self.back_image = None

        self.label = Label(self, bg=self.bg, fg=self.fg, font=('product sans', 10))
        self.config_label(os.path.basename(__media_paths__[_play_count.v]))

        self.scale = RcScale(self, slider=True, value=0, width=self.width - 16, height=16,
                             troughcolor1=rgb(240, 123, 7),
                             troughcolor2=rgb(206, 233, 234),
                             outline=self.bg, outwidth=6, relief='flat', bd=0,
                             highlightthickness=0)

        self.b_frame = Frame(self, bg=self.bg)
        self.play_button = Button(self.b_frame, command=self.pause_, bg=self.bg,  activebackground=self.abg, relief='flat', bd=0)
        self.previous_button = Button(self.b_frame, image=previous_image_c, command=previous_call, bg=self.bg, activebackground=self.abg, relief='flat', bd=0)
        self.next_button = Button(self.b_frame, image=next_image_c, command=next_call, bg=self.bg, activebackground=self.abg, relief='flat', bd=0)

        self.set_scale = True
        self.set_by_slider = False
        self.scale.bind("<ButtonRelease-1>", self.m_scale_release_call)
        self.scale.bind('<B1-Motion>', self.m_scale_motion_call)
        self.scale.bind("<Button-1>", self.m_scale_click_call)

        self.label.pack(side='top', pady=5, anchor='center')
        self.scale.pack(side='top', pady=0, anchor='center')

        self.previous_button.pack(side='left')
        self.play_button.pack(side='left', padx=5)
        self.next_button.pack(side='left')
        self.b_frame.pack(side='top', pady=5, anchor='center')

        # self.play_button.place(x=round((self.width - self.im_dim) / 2), y=self.height - self.im_dim - 5)
        # self.previous_button.place(x=round((self.width - self.im_dim * 3 - 20) / 2), y=self.height - self.im_dim - 5)
        # self.next_button.place(x=round((self.width + self.im_dim + 20) / 2), y=self.height - self.im_dim - 5)

        self.sync_play_image()

        # General bindings
        for __n, __s in bindings_dict['playback'].items():
            if __n == stop.__qualname__:
                continue
            if __n == count.__qualname__:
                self.bind(__s, self.pause_)
                continue
            self.bind(__s, SetName.func_dic[__n])

        # Controller Specific Bindings
        for __n, __s in bindings_dict['controller_specific'].items():
            if __n == self.__class__.toggle_dock.__qualname__:
                self.bind(__s, self.toggle_dock)
            elif __n == self.__class__.raise_main.__qualname__:
                self.bind(__s, self.raise_main)

        self.focus_force()
        self.__class__.Instance = self

    def load_coordinates(self):
        if controller_coordinates.v == (None, None):
            return screen_width - self.width - self.spadx, screen_height - self.height - self.spady
        return controller_coordinates.v

    def save_coordinates(self):
        controller_coordinates.v = self.winfo_rootx(), self.winfo_rooty()

    def config_label(self, text):
        self.label['text'] = Ui.ellip(text, 24)

    def set_play_image(self, playing: bool):
        self.play_button['image'] = pause_image_c if playing else play_image_c

    def sync_play_image(self):
        self.set_play_image(player.get_state() == 3)

    def pause_(self, event=None):
        self.set_play_image(player.get_state() != 3)
        pause()

    def m_scale_release_call(self, event):
        self.set_scale = True

    def m_scale_motion_call(self, event=None):
        if self.set_by_slider:
            value = self.scale.get_value_from_x(event.x)
            player.set_position(value / 100)
            self.scale.set(value)

    def m_scale_click_call(self, event):
        if player.get_state() in (3, 4):
            self.set_scale = False
            if self.scale.find_(event.x, event.y) == 'slider':
                self.set_by_slider = True
            else:
                self.set_by_slider = False
                value = self.scale.get_value_from_x(event.x)
                player.set_position(value / 100)
                self.scale.set(value)

    def auto_set(self):
        if self.set_scale:
            self.scale.set(player.get_position() * 100)

    @SetName('Raise Main Window')
    def raise_main(self, event=None):
        self.master.update()
        self.master.deiconify()
        self.save_coordinates()
        self.destroy()
        self.__class__.Instance = None

    @SetName('Dock / UnDock Controller')
    def toggle_dock(self, event=None):
        self.override = not self.override
        self.overrideredirect(self.override)
        self.focus_force()


class LoadPlay(BasrCaptionDialogFrame):
    Instance = None

    def __init__(self, master, play_file_path, title='Load Playlist', caption='Select Playlist to load', data=None,
                 **kwargs):
        self.filepath = play_file_path
        self.dic_ = data if data else load(self.filepath)
        self.names = [*self.dic_]

        super().__init__(master, title=title, caption=caption, **kwargs)

        self.list_box = Listbox(self, borderwidth=5, relief='groove', width=10, height=5,
                                highlightcolor=self.bg_medium,
                                selectmode=SINGLE, bg=self.bg_dark, fg=self.fg_medium, activestyle='dotbox',
                                selectbackground=self.bg_medium, selectforeground=self.fg_dark, bd=2,
                                font=self.font)

        self.list_box.bind('<Double-Button>', self.load)

        # self.frame_b = Frame(self, bg=self.bg)
        self.load_button = Button(self, text='Load', font=self.font, relief='flat', bd=0,
                                  command=self.load,
                                  bg=self.bg_dark, fg=self.fg_medium, activebackground=self.bg_medium,
                                  activeforeground=self.fg_dark)
        self.del_button = Button(self, text='Delete', font=self.font, relief='flat', bd=0,
                                 command=self.del_,
                                 bg=self.bg_dark, fg=self.fg_medium, activebackground=self.bg_medium,
                                 activeforeground=self.fg_dark)

        for name in self.names:
            self.list_box.insert(END, name)

        self.list_box.bind('<Return>', self.load)
        self.list_box.bind('<Delete>', self.del_)
        # self.bind('<Escape>', self.destroy)

        self.pack_widgets()
        self.list_box.focus_set()

        self.__class__.Instance = self

    def pack_widgets(self):
        super().pack_widgets()
        # packing widgets
        self.list_box.pack(side='top', fill='x', padx=4, pady=6)
        self.load_button.pack(side='left', padx=10, pady=5)
        self.del_button.pack(side='right', padx=10, pady=5)

    def destroy(self):
        super().destroy()
        self.__class__.Instance = None

    def load(self, event_=None):

        def _main(info_):
            global __media_paths__
            var_, paths_ = info_
            if var_:
                for path_ in paths_:
                    if not os.path.isfile(path_):
                        paths_.remove(path_)

                if not paths_:
                    SnackBar.show_msg(self.master,
                                      f'Playlist load failed\n \"{play_name}\" could not be found on disk!')
                    # messagebox.showinfo('Load Failed', 'Playlist Load Failed : DATA NOT ON DISK LOCATION',
                    #                     parent=self)
                else:
                    if len(__media_paths__) > 0:
                        overwrite_in = messagebox.askyesno('Load Playlist',
                                                           'Do you want to overwrite existing playlist sequence ?',
                                                           parent=self)
                        if overwrite_in:
                            __media_paths__ = paths_
                            if playlist_win.state() == 'normal':  # docked
                                playlist_win.insert_pathseq(__media_paths__)
                            stop()
                            force()
                        else:
                            for path_ in paths_:
                                if path_ not in __media_paths__:
                                    __media_paths__.append(path_)
                            if playlist_win.state() == 'normal':  # docked
                                playlist_win.insert_pathseq(__media_paths__)
                    else:
                        __media_paths__ = paths_
                        if playlist_win.state() == 'normal':  # docked
                            playlist_win.insert_pathseq(__media_paths__)
                        stop()
                        force()

        try:
            play_name = self.list_box.get(ACTIVE)
            self.check_pass(play_name, command=_main)
        except KeyError:
            print_('select a playlist to load first')
            SnackBar.show_msg(self.master, "select a playlist to load first", 2000)

    def del_(self, event_=None):
        try:
            def _main(info_):
                if info_[0]:
                    del self.dic_[play_name]
                    self.list_box.delete(ACTIVE)
                    dump(self.dic_, self.filepath)

            play_name = self.list_box.get(ACTIVE)
            self.check_pass(play_name, _main)
        except KeyError:
            print('no playlist to delete')

    def check_pass(self, key, command):
        def __m(pass_):
            info_ = False, None
            if pass_:
                if pass_ == password__:
                    # self.deiconify()
                    # self.update()
                    box_.on_success()
                    info_ = True, paths__
                else:
                    box_.destroy()
                    SnackBar.show_msg(self.master, 'Playlist Access Unauthorized', duration=4000)
            command(info_)

        paths__, password__ = self.dic_[key]
        if password__ == '':
            command((True, paths__))
        else:
            # self.withdraw()
            box_ = RcDiag(self.master, 'Playlist Encrypted', f'Enter the password of playlist : {key}',
                          retain_value=False, command=__m)
            box_.entry['show'] = '*'
            box_.place_at_center()


class ScanDirUi(Toplevel):
    Instance = None

    def __init__(self, master, **kwargs):
        self.master = master
        self.width, self.height = 340, 190
        self.bg_dark = rgb(30, 30, 30)
        self.bg_medium = rgb(60, 60, 60)
        self.bg_light = rgb(100, 100, 100)
        self.fg_dark = rgb(255, 255, 255)
        self.fg_medium = rgb(245, 245, 245)
        self.fg_light = rgb(180, 180, 180)
        self.font = ('product sans', 10)
        self.font_big = ('product sans', 14)

        self.dirs = []
        self.x, self.y = (win.winfo_rootx() + round((win_width.v - self.width) / 2), win.winfo_rooty() + round(
            (win_height.v - self.height) / 2) - 25) if win.state() != 'iconic' else (
            round((screen_width - self.width) / 2), round((screen_height - self.height) / 2))

        super().__init__(master, **kwargs)
        self['bg'] = self.bg_dark
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.resizable(0, 0)
        self.title('Scan Directories')
        self.protocol('WM_DELETE_WINDOW', self.destroy_)
        self.iconbitmap(C.app_icon_file)
        # self.overrideredirect(True)

        self.frame1 = Frame(self, bg=self.bg_dark, relief='flat', bd=0)
        self.frame2 = Frame(self, bg=self.bg_dark, relief='flat', bd=0)
        self.scan_v_var = IntVar(self.frame2, 1)
        self.scan_a_var = IntVar(self.frame2, 1)

        self.list_box = Listbox(self.frame1, relief='groove', highlightcolor=self.bg_dark,
                                selectmode=SINGLE, bg=self.bg_medium, fg=self.fg_dark, activestyle='dotbox', bd=2,
                                font=self.font, selectbackground=self.bg_dark, selectforeground=self.fg_medium, height=6)

        self.list_box.bind('<Delete>', self.remove_dir)

        self.add_b = Button(self.frame1, text=" \u2295 ", command=self.add_dir, font=self.font_big,
                            bg=self.bg_medium, fg=self.fg_dark, activebackground=self.bg_light,
                            activeforeground=self.fg_dark, relief='flat', bd=0)

        self.remove_b = Button(self.frame1, text=" \u2296 ", command=self.remove_dir, font=self.font_big,
                               bg=self.bg_medium, fg=self.fg_dark, activebackground=self.bg_light,
                               activeforeground=self.fg_dark, relief='flat', bd=0)

        self.scan_b = Button(self.frame2, text="  Scan  ", command=self.scan, font=self.font,
                             bg=self.bg_medium, fg=Ui.fg_accent, activebackground=self.bg_light,
                             activeforeground=self.fg_dark, disabledforeground=self.fg_light,
                             relief='flat', bd=0, state=DISABLED)

        self.scan_v_b = Checkbutton(self.frame2, variable=self.scan_v_var, onvalue=1, offvalue=0,
                                    text='scan video files', font=self.font,
                                    bg=self.bg_dark, fg=self.fg_medium, activebackground=self.bg_medium,
                                    activeforeground=self.fg_dark, selectcolor=self.bg_medium, relief='flat', bd=0)

        self.scan_a_b = Checkbutton(self.frame2, variable=self.scan_a_var, onvalue=1, offvalue=0,
                                    text='scan audio files', font=self.font,
                                    bg=self.bg_dark, fg=self.fg_medium, activebackground=self.bg_medium,
                                    activeforeground=self.fg_dark, selectcolor=self.bg_medium, relief='flat', bd=0)

        self.list_box.grid(row=0, column=0, padx=8, sticky=NSEW, rowspan=2)
        self.add_b.grid(row=0, column=1, pady=5, sticky='s')
        self.remove_b.grid(row=1, column=1, pady=0, sticky='s')
        self.frame1.grid_rowconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)

        self.scan_v_b.pack(side=LEFT)
        self.scan_a_b.pack(side=LEFT)
        self.scan_b.pack(side=RIGHT, padx=8)

        self.frame1.pack(fill=X, expand='yes', padx=4, pady=4)
        self.frame2.pack(fill=X, expand='yes', padx=5, pady=6)

        self.bind("<plus>", self.add_dir)
        self.bind('<minus>', self.remove_dir)
        self.bind('<Return>', self.scan)
        self.bind('<Escape>', self.destroy_)

        self.focus_force()
        self.__class__.Instance = self

    def add_dir(self, event=None):
        print("asking dir")
        dir_path = filedialog.askdirectory(parent=self, initialdir="C;\\", title='Load Directory')
        if dir_path:
            self.dirs.append(dir_path)
            self.list_box.insert('end', dir_path)
            self.list_box.activate('end')

            for b in self.scan_b, self.remove_b:
                b['state'] = NORMAL
                b.update()

    def remove_dir(self, event=None):
        if self.dirs:
            i = self.list_box.index('active')
            self.dirs.pop(i)
            self.list_box.delete(i)
            if not self.dirs:
                for b in self.scan_b, self.remove_b:
                    b['state'] = DISABLED
                    b.update()

    def scan(self, event=None):
        if self.dirs:
            if self.scan_v_var.get() == 1 and self.scan_a_var.get() == 1:
                _exts_ = C.all_format
            elif self.scan_v_var.get() == 1:
                _exts_ = C.video_format
            elif self.scan_a_var.get():
                _exts_ = C.song_format
            else:
                messagebox.showwarning(parent=self, title='Invalid Input', message='Select at least one scan mode')
                return
            scanner_thread = Thread(target=scan_directories, kwargs={'dirs': self.dirs, '_exts_': _exts_})
            scanner_thread.setDaemon(True)
            scanner_thread.start()
            self.destroy_()
        else:
            if not event:
                messagebox.showinfo(parent=self, title='Warning',
                                    message='Add at least one directory to scan : NO INPUT BY USER')

    def destroy_(self, event=None):
        self.destroy()
        self.__class__.Instance = None


class ExitDiag(BasrCaptionDialogFrame):
    Instance = None

    def __init__(self, master, exit_call, cancel_call=None, title="Confirm Exit", caption='Do you really want to quit?',
                 exit_text="  Exit  ", cancel_text="  Cancel  ", **kwargs):

        self.exit_call = exit_call
        self.cancel_call = cancel_call

        super().__init__(master, title=title, caption=caption, **kwargs)

        self.check = Checkbutton(self, text="Do not ask again", font=self.font, bg=self.bg_dark, fg=self.fg_medium, relief='flat',
                                 bd=0,
                                 activebackground=self.bg_medium, activeforeground=self.fg_dark, selectcolor=self.bg_medium,
                                 onvalue=0, offvalue=1, variable=exit_check)

        self.exit_b = Button(self, text=exit_text, command=self.on_exit, font=self.font, bg=self.bg_dark, fg=self.fg_medium,
                             bd=0, relief='flat', activebackground=self.bg_medium,
                             activeforeground=self.fg_dark)
        self.cancel_b = Button(self, text=cancel_text, command=self.on_cancel, font=self.font, bg=self.bg_dark, fg=self.fg_medium,
                               bd=0, relief='flat', activebackground=self.bg_medium, activeforeground=self.fg_dark)

        # self.bind('<Return>', self.exit_call)
        # self.bind('<Escape>', self.cancel_callback)

        self.pack_widgets()
        self.__class__.Instance = self

    def pack_widgets(self):
        super().pack_widgets()
        self.check.pack(side='top', anchor='w', padx=10, pady=0)
        self.exit_b.pack(side="right", padx=10, pady=8)
        self.cancel_b.pack(side="left", padx=10, pady=8)

    def on_exit(self, event=None):
        self.destroy()
        if self.exit_call:
            self.exit_call()

    def on_cancel(self, event=None):
        self.destroy()
        if self.cancel_call:
            self.cancel_call()

    def destroy(self):
        super().destroy()
        self.__class__.Instance = None


class EncryptionBox(BasrCaptionDialogFrame):
    def __init__(self, master, title='Encrypt', caption='Enter Credentials', name_label='Name       ', pass_label='Password',
                 playlist_dic=None, file_path=C.playlist_file, **kwargs):
        self.name_label = name_label
        self.pass_label = pass_label
        self.play_dic = playlist_dic
        self.file_path = file_path

        super().__init__(master=master, title=title, caption=caption, **kwargs)

        self.name = ''
        self.pass_ = ''

        self.name_frame = Frame(self, bg=self.bg_dark)
        self.pass_frame = Frame(self, bg=self.bg_dark)
        self.name_l = Label(self.name_frame, text=self.name_label, font=self.font, fg=self.fg_medium, bg=self.bg_dark,
                            relief='flat', bd=0)
        self.pass_l = Label(self.pass_frame, text=self.pass_label, font=self.font, fg=self.fg_medium, bg=self.bg_dark,
                            relief='flat', bd=0)
        self.name_e = Entry(self.name_frame, font=self.font)
        self.pass_e = Entry(self.pass_frame, font=self.font, show='*')

        self.ok_b = Button(self, text="  OK  ", command=self.submit,
                           relief="flat", bd=0, bg=self.bg_dark, fg=self.fg_medium, font=self.font,
                           activebackground=self.bg_medium, activeforeground=self.fg_dark)

        self.pack_widgets()
        self.name_e.focus_set()
        self.name_e.bind('<Down>', self.fp)
        self.pass_e.bind('<Up>', self.fn)
        self.name_e.bind('<Up>', self.fp)
        self.pass_e.bind('<Down>', self.fn)
        # self.bind('<Escape>', lambda event: self.destroy())
        # self.bind('<Return>', self.submit)

        self.name_e.focus_force()

    def fp(self, event=None):
        self.pass_e.focus_set()

    def fn(self, event=None):
        self.name_e.focus_set()

    def pack_widgets(self, cap_padx=34, e_padx=12, e_pady=12):
        super().pack_widgets()
        self.name_l.pack(side='left', anchor='center', padx=8, fill='none')
        self.name_e.pack(side='left', fill='x')
        self.name_frame.pack(side='top', padx=e_padx, pady=e_pady, fill='x')

        self.pass_l.pack(side='left', anchor='center', padx=8, fill='none')
        self.pass_e.pack(side='left', fill='x')
        self.pass_frame.pack(side='top', padx=e_padx, pady=e_pady, fill='x')

        self.ok_b.pack(side='top', anchor='center', pady=10)

    def submit(self, event=None):
        pass_ = self.pass_e.get()
        play_name = self.name_e.get()

        if not play_name:
            SnackBar.show_msg(self.master, "Title is required", font=self.cap_font)
            # messagebox.showerror('Error', 'Could not save playlist : NO INPUT TITLE', parent=self)
        else:
            if not self.play_dic:
                dump({play_name: (__media_paths__, pass_)}, self.file_path)
                self.success_(play_name)
            else:
                if play_name in self.play_dic:
                    SnackBar.show_msg(self.master, "Playlist already exists\nTry a different name" + Ui.CHR_ELLIP,
                                      font=self.font)
                    # messagebox.showerror('Error', 'Could not save playlist : PLAYLIST ALREADY EXISTS', parent=self)
                else:
                    self.play_dic.update({play_name: (__media_paths__, pass_)})
                    dump(self.play_dic, self.file_path)
                    self.success_(play_name)

    def success_(self, play_name):
        self.destroy()
        SnackBar.show_msg(self.master, f'Playlist \"{play_name}\" saved', font=self.font)

        # self.bind('<Return>', lambda event: self.destroy())
        #
        # _c = Canvas(self, bg=rgb(90, 90, 90), bd=0, relief='flat')
        # _c.create_text(self.size[0] / 2, self.size[1] / 2, text=f'Playlist {play_name} saved successfully',
        #                fill='white', anchor=CENTER, font=('product sans', 12))
        # _c.place(x=0, y=0, relwidth=1, relheight=1)


class PreDisplay(Canvas):
    Instance = None
    _size = (180, 90)
    delay = 100  # in ms

    """ preview window players"""
    _player_in = main_player.Instance(' --aout=adummy')
    _player = _player_in.media_player_new()
    _player.video_set_aspect_ratio(f'{_size[0]}:{_size[1]}')
    m_path = None

    @staticmethod
    def set_media(mrl):
        PreDisplay._player.stop()
        PreDisplay._player.set_media(PreDisplay._player_in.media_new(mrl))
        # PreDisplay._player.video_set_aspect_ratio('%d:%d' % PreDisplay._size)
        PreDisplay.m_path = mrl

    @staticmethod
    def quit_():
        PreDisplay._player.stop()
        PreDisplay._player.release()
        PreDisplay._player_in.release()

    def __init__(self, master, p_pos, click_x, click_y, xoff=0, yoff=5):
        """
        click_x : x coordinate wrt to main window
        click_y : y coord wrt to main window

        """
        self.master = master
        self.p_pos = p_pos
        self.yoff = yoff
        self.xoff = xoff

        self.width, self.height = self.__class__._size
        self.del_click_x, self.del_click_y = round(self.width / 2) - self.xoff, self.height + self.yoff
        self._x, self._y = click_x - self.del_click_x, click_y - self.del_click_y
        self.check(True)

        """  muting playback  """
        self._busy = True
        Canvas.__init__(self, master=master, width=self.width, height=self.height, relief='flat', bd=0)
        self.__class__._player.set_hwnd(self.winfo_id())
        self.__class__._player.play()
        self.__class__._player.set_position(self.p_pos)

        self.place(x=self._x, y=self._y)
        self.state = 1  # 0 for hidden, 1 for on_display

        self.master.after(self.__class__.delay, self.release_busy)
        self.__class__.Instance = self

    def check(self, y=False):
        if self._x < 0:
            self._x = 0
        elif self._x >= win_width.v - self.width - 10:
            self._x = win_width.v - self.width - 10

        if y and self._y < 0:
            self._y = 0

    def config_(self, p_pos, event_x, event_y=None, set_play=False):
        self._x = event_x - round(self.width / 2) + self.xoff
        if event_y is not None:
            self._y = event_y - self.del_click_y
        self.check(True)

        self.place_configure(x=self._x, y=self._y)
        if not self._busy:
            self._busy = True
            if p_pos > .98:
                p_pos = .98
            if set_play:
                self.__class__._player.play()
            self.__class__._player.set_position(p_pos)
            self.master.after(self.__class__.delay, self.release_busy)

    def release_busy(self):
        self._busy = False

    def un_dock(self):
        if self.state == 1:
            self.place_forget()
            self.__class__._player.pause()
            self._busy = False
            self.state = 0

    def dock(self, p_pos, click_x, click_y):
        if self.state == 0:
            self.config_(p_pos, click_x, click_y, True)
            self.state = 1


class BindsUi(Toplevel):
    def __init__(self, master, size, bindings_dic, file_path, bg='white', fg='black', icon=None, pos=None, *args,
                 **kwargs):
        self.master = master
        self.width, self.height = size
        self.s_width, self.s_height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.x, self.y = pos if pos else (
            round((self.s_width - self.width) / 2), round((self.s_height - self.height) / 2))
        self.fg = fg
        self.bg = bg

        self.file_path = file_path
        self.binds = bindings_dic
        self.playback_binds, self.win_binds, self.playwin_binds, self.controller_binds = self.binds['playback'], \
                                                                                         self.binds['win'], self.binds[
                                                                                             'playwin'], self.binds[
                                                                                             'controller_specific']
        Toplevel.__init__(self, master, *args, **kwargs)
        self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        if icon:
            self.iconbitmap(icon)
        self['bg'] = self.bg
        self.focus_set()

        self.playback_frame = BindsFrame(self, text='Playback Bindings', font=('product sans medium', 11),
                                         labelanchor='n',
                                         bg=self.bg,
                                         fg=self.fg, width=round(self.width / 3), bd=2)
        self.win_frame = BindsFrame(self, text='Prefrences', font=('product sans medium', 11), labelanchor='n',
                                    bg=self.bg,
                                    fg=self.fg,
                                    width=round(self.width / 3), bd=2)
        self.controller_frame = BindsFrame(self, text='Controller Bindings', font=('product sans medium', 11),
                                           labelanchor='n',
                                           bg=self.bg, fg=self.fg, width=round(self.width / 3), bd=2)

        self._set_ui()  # parsing the data to setup ui

        self.dock = Frame(self, bg=bg, relief='flat', bd=0)
        self.save_b = Button(self.dock, text='Save', command=self.save_binds, bg=self.bg, fg=self.fg, relief='flat',
                             bd=0, width=7,
                             activebackground=self.bg, activeforeground=self.fg, font=('product sans', 10))
        self.cancel_b = Button(self.dock, text='Cancel', command=self.cancel, bg=self.bg, fg=self.fg, relief='flat',
                               bd=0, width=7,
                               activebackground=self.bg, activeforeground=self.fg, font=('product sans', 10))

        self.cancel_b.pack(side=RIGHT, padx=20, pady=4)
        self.save_b.pack(side=RIGHT, pady=4)
        self.dock.pack(side=BOTTOM, anchor='s', fill=X)

        self.playback_frame.pack(fill=Y, side=LEFT, anchor='nw')
        self.win_frame.pack(fill=Y, side=LEFT)
        self.controller_frame.pack(fill=Y, side=LEFT)

    def _set_ui(self):
        for key_, val_ in self.playback_binds.items():
            self.playback_frame.add_slide(key_, val_, font=('product sans', 10), fg=self.fg, bg=self.bg)

        for key_, val_ in self.win_binds.items():
            self.win_frame.add_slide(key_, val_, font=('product sans', 10), fg=self.fg, bg=self.bg)

        for key_, val_ in self.controller_binds.items():
            self.controller_frame.add_slide(key_, val_, font=('product sans', 10), fg=self.fg, bg=self.bg)

    def save_binds(self, event=None):
        self.win_binds = self.win_frame.get_info()
        self.controller_binds = self.controller_frame.get_info()
        self.playback_binds = self.playback_frame.get_info()

        self.playback_frame.test_binds(self.playback_binds.values())
        self.win_frame.test_binds(self.win_binds.values())
        self.controller_frame.test_binds(self.controller_binds.values())

        for func_, seq_ in self.win_binds.items():
            if func_ in self.playwin_binds:
                self.playwin_binds[func_] = seq_

        # had to dump the data in file
        dump({'playback': self.playback_binds, 'win': self.win_binds, 'playwin': self.playwin_binds,
              'controller_specific': self.controller_binds}, self.file_path)
        messagebox.showinfo(parent=self, title='Bindings',
                            message='Changes has been saved \nRestart the program to apply changes')
        self.destroy()

    def cancel(self, event=None):
        self.destroy()


class BindsFrame(LabelFrame):
    Slide_h = 40
    Entry_relw = .2
    Label_relw = .45
    rel_padx = (1 - Label_relw - (2 * Entry_relw)) / 4
    pady = 20

    def __init__(self, master, entry_font=('product sans', 10), *args, **kwargs):
        self.master = master
        self.entry_font = entry_font
        self.labels = []
        self.entries_1 = []
        self.entries_2 = []
        self.info = {}
        LabelFrame.__init__(self, master, *args, **kwargs)

    @staticmethod
    def parse(sym):
        sym_ = sym[1:-1]
        if '><' in sym_:
            return sym_.split('><')
        if '-' in sym_:
            return sym_.split('-')
        return sym_, None

    @staticmethod
    def join(sym_1, sym_2):
        if sym_1 in BinDings.special_keysym:
            return f'<{sym_1}><{sym_2}>'
        return f'<{sym_1}-{sym_2}>'

    def _prevent(self, e_widget):
        e_widget['stste_'] = 'disabled'
        self.master.after(1, lambda s='normal': e_widget.configure(state=s))

    def e1_call(self, event):
        if event.keysym in BinDings.special_keysym:
            event.widget.delete(0, END)
            event.widget.insert(END, event.keysym)
            if event.keysym in ('BackSpace', 'space'):
                self._prevent(event.widget)
        else:
            self._prevent(event.widget)

    def e2_call(self, event):
        if event.keysym in BinDings.special_keysym:
            # special keys
            if event.keysym in ('BackSpace', 'space'):
                self._prevent(event.widget)
        else:
            event.widget.delete(0, END)
            event.widget.insert(END, event.keysym)
            self._prevent(event.widget)

    def add_slide(self, caption, seq, font=('product sans', 10), bg=rgb(60, 60, 60),
                  fg=rgb(250, 250, 250)):  # ui need to be tuned
        l__ = Label(self, text=caption, font=font, bg=bg, fg=fg)
        e1__ = Entry(self, font=self.entry_font, disabledbackground='grey')
        e2__ = Entry(self, font=self.entry_font)
        indx__ = len(self.labels)

        __sym1, __sym2 = self.parse(seq)
        if __sym2:
            e1__.insert(END, __sym1)
            e2__.insert(END, __sym2)
        else:
            # e1__['stste_'] = 'disabled'
            if __sym1 in BinDings.special_keysym:
                e1__.insert(END, __sym1)
            else:
                e2__.insert(END, __sym1)
            # e2__.bind('<Key>', lambda event, _s=True: self.e2_call(event, _s))

        setattr(l__, 'index', indx__)
        setattr(e1__, 'index', indx__)
        setattr(e2__, 'index', indx__)

        e1__.bind('<Key>', self.e1_call)
        e2__.bind('<Key>', self.e2_call)

        l__.place(relx=self.__class__.rel_padx, y=(indx__ * self.__class__.Slide_h) + self.__class__.pady,
                  relwidth=self.__class__.Label_relw)
        e1__.place(relx=(self.__class__.rel_padx * 2) + self.__class__.Label_relw, relwidth=self.__class__.Entry_relw,
                   y=(indx__ * self.__class__.Slide_h) + self.__class__.pady)
        e2__.place(relx=1 - self.__class__.Entry_relw - self.__class__.rel_padx, relwidth=self.__class__.Entry_relw,
                   y=(indx__ * self.__class__.Slide_h) + self.__class__.pady)

        self.entries_1.append(e1__)
        self.entries_2.append(e2__)
        self.labels.append(l__)

    def get_info(self, event=None):
        self.info.clear()

        for e1_, e2_ in zip(self.entries_1, self.entries_2):
            # if e1_['stste_'] == 'normal':
            e1_seq, e2_seq = e1_.get(), e2_.get()
            if e1_seq and e2_seq:
                self.info[self.labels[e1_.index][
                    'text']] = f'<{e1_seq}><{e2_seq}>' if e1_seq in BinDings.special_keysym else f'<{e1_seq}-{e2_seq}>'
            elif e1_seq:
                self.info[self.labels[e1_.index]['text']] = f'<{e1_seq}>'
            elif e2_seq:
                self.info[self.labels[e1_.index]['text']] = f'<{e2_seq}>'

        return self.info

    def test_binds(self, seqs):
        for seq in seqs:
            try:
                self.bind(seq, lambda event: print('sda'))
            except Exception as e:
                print(f'invalid sequence : {seq}, error : {e}')
            else:
                self.unbind(seq)
                print(f'valid seq : {seq}')


class Dock(Frame):
    """ always undock or dock using methods """

    def __init__(self, master, win_width_var, *args, **kwargs):
        self.master = master
        self.win_width = win_width_var  # RcInt having v attr
        kwargs['height'] = 1  # initialising with 1 pix (un docked) height
        Frame.__init__(self, master=master, *args, **kwargs)

        # time
        self.current_time_l = Label(self, text="--.--", bg='black', fg='white', font=('product sans', 8), width=10,
                                    anchor='center')
        self.full_time_l = Label(self, text="--.--", bg='black', fg='white', font=('product sans', 8), width=10,
                                 anchor='center')
        self.full_time_l.bind('<Button-1>', toggle_fulltime_state)

        self.d_timer = None
        self.d_time = Ui.dock_hide_ms  # in ms

        # Media scale
        self.media_scale = RcScale(self, slider=True, value=0, width=100,  # will update width later
                                   height=16,
                                   troughcolor1=rgb(240, 123, 7),
                                   troughcolor2=rgb(206, 233, 234), outline='black', outwidth=6, relief='flat', bd=0,
                                   highlightthickness=0)

        self._set_by_slider = False
        self.auto_media_scale = True

        self.media_scale.bind("<ButtonRelease-1>", self._mscale_release_call)
        self.media_scale.bind("<Button-1>", self._mscale_press_call)
        self.media_scale.bind("<B1-Motion>", self._mscale_motion_call)

        # audio scale
        self.audio_scale = RcScale(self, slider=True, value=0,
                                   width=100,  # will update width later
                                   height=16,
                                   troughcolor1=rgb(240, 123, 7),
                                   troughcolor2=rgb(206, 233, 234),
                                   outline='black', outwidth=6, relief='flat', bd=0, highlightthickness=0)

        self._set_a_by_slider = False
        self.audio_scale.set((current_vol.v / max_volume.v) * 100)
        self.audio_scale.bind("<Button-1>", self._ascale_press_call)
        self.audio_scale.bind("<B1-Motion>", self._ascale_motion_call)

        # ............................................Buttons..............................................

        self.center_b_frame = Frame(self, bg='black')

        # buttons
        self.play_button = Button(self.center_b_frame, command=count, image=play_image, width=Ui.im_dim,
                                  height=Ui.im_dim,
                                  relief='flat',
                                  bd=0,
                                  bg='black', activebackground=rgb(60, 60, 60))
        self.previous_button = Button(self.center_b_frame, command=previous_call, image=previous_image, width=Ui.im_dim,
                                      height=Ui.im_dim,
                                      relief='flat', bd=0, repeatdelay=600, bg='black',
                                      activebackground=rgb(60, 60, 60))
        self.next_button = Button(self.center_b_frame, command=next_call, image=next_image, width=Ui.im_dim,
                                  height=Ui.im_dim,
                                  relief='flat', bd=0,
                                  bg='black', activebackground=rgb(60, 60, 60))
        self.stop_button = Button(self, command=stop, image=stop_image, width=Ui.im_dim, height=Ui.im_dim,
                                  relief='flat',
                                  bd=0,
                                  bg='black', activebackground=rgb(60, 60, 60))

        # animation constants
        self.anim_timer = None
        self.animate_time = Ui.dock_anim_ms  # in ms
        self._anm_step = Ui.dock_anim_step  # in pixels
        self._anm_time_per_pix = self.animate_time / (Ui.dock_h - 1)
        self._anm_time = int(self._anm_step * self._anm_time_per_pix)

        self.state = 0  # 0 for un docked, 1 for docked, 2 for busy animating
        self.place_widgets(self.win_width.v)

    def ctime_label_w(self, update=False):
        if update:
            self.master.update()
        return self.current_time_l.winfo_width()

    def calculate_mscale_w_del(self, update=False):
        return self.ctime_label_w(update) * 2

    def calculate_mscale_w(self, root_w, update=False):
        return root_w - self.calculate_mscale_w_del(update)

    def calculate_ascale_w(self, root_w):
        return round(root_w * Ui.audio_scale_relwidth)

    def calculate_mscale_x(self, update=False):
        return self.ctime_label_w(update)

    def mscale_x(self, update=False):
        if update:
            self.master.update()
        return int(self.media_scale.place_info()['x'])

    # @property
    # def calculate_ascale_x_del(self, update=False):
    #     return self.ctime_label_w(update)

    def _mscale_release_call(self, event):
        if self._set_by_slider:
            value = self.media_scale.get_value_from_x(event.x)
            player.set_position(value / 100)
            __in = PreDisplay.Instance
            if isinstance(__in, (PreDisplay,)):
                __in.un_dock()

        self.auto_media_scale = True

    def _mscale_motion_call(self, event):
        if self._set_by_slider:
            _pos = self.media_scale.get_value_from_x(event.x)
            if PreDisplay.m_path:
                _p_pos = _pos / 100
                PreDisplay.Instance.config_(_p_pos, event.x)
            self.media_scale.set(_pos)

    def _mscale_press_call(self, event):
        if player.get_state() in (3, 4):
            self.auto_media_scale = False
            _part_ = self.media_scale.find_(event.x, event.y)
            _pos = self.media_scale.get_value_from_x(event.x)
            _p_pos = _pos / 100

            if _part_ == 'slider':
                if PreDisplay.m_path:
                    __in = PreDisplay.Instance
                    # __xoff = Ui.media_scale_padx
                    __xoff = self.mscale_x()
                    if isinstance(__in, (PreDisplay,)):
                        __in.xoff = __xoff
                        PreDisplay.Instance.dock(_p_pos, event.x, win_height.v - Ui.dock_h)
                    else:
                        PreDisplay(win, _p_pos, event.x, win_height.v - Ui.dock_h, xoff=__xoff, yoff=10)

                self._set_by_slider = True
            else:
                self._set_by_slider = False
                player.set_position(_p_pos)
                self.media_scale.set(_pos)

    def _ascale_press_call(self, event):
        part__ = self.audio_scale.find_(event.x, event.y)
        if part__ == 'slider':
            self._set_a_by_slider = True
        else:
            current_vol.v = (self.audio_scale.get_value_from_x(event.x) * max_volume.v) / 100
            aset_(current_vol.v)
            self._set_a_by_slider = False

    def _ascale_motion_call(self, event):
        if self._set_a_by_slider:
            current_vol.v = (self.audio_scale.get_value_from_x(event.x) * max_volume.v) / 100
            aset_(current_vol.v, set_scale=True, show=True)

    def resize(self, width):
        # self.play_button.place_configure(x=(width - Ui.im_dim) / 2)
        # self.previous_button.place_configure(x=(width / 2) - (Ui.im_dim * 1.5) - Ui.dock_b_padx)
        # self.next_button.place_configure(x=((width + Ui.im_dim) / 2) + Ui.dock_b_padx)

        self.media_scale.config_dim(self.calculate_mscale_w(width))
        self.audio_scale.config_dim(self.calculate_ascale_w(width))

        # self.audio_scale.place_configure(x=width - self.audio_scale.width - Ui.del_audio_scale_x)
        # self.full_time_l.place_configure(x=width - Ui.dock_tl_w - Ui.dock_tl_padx)

    # def place_widgets(self, width):     # TODO
    #     self.stop_button.place(anchor='sw', x=Ui.dock_edge_padx, y=Ui.dock_h - Ui.dock_b_pady)
    #     self.previous_button.place(x=round((width / 2) - (Ui.im_dim * 1.5)) - Ui.dock_b_padx,
    #                                y=Ui.dock_h - Ui.im_dim - Ui.dock_b_pady)
    #     self.play_button.place(anchor='s', x=round((width - Ui.im_dim) / 2),
    #                            y=Ui.dock_h - Ui.im_dim - Ui.dock_b_pady)
    #     self.next_button.place(x=round((width + Ui.im_dim) / 2) + Ui.dock_b_padx,
    #                            y=Ui.dock_h - Ui.im_dim - Ui.dock_b_pady)
    #
    #     self.current_time_l.place(x=Ui.dock_tl_padx, y=Ui.dock_tl_pady)
    #     self.full_time_l.place(x=width - Ui.dock_tl_w - Ui.dock_tl_padx, y=Ui.dock_tl_pady)
    #
    #     self.media_scale.place(x=Ui.media_scale_padx, y=Ui.dock_edge_pady / 2)
    #     self.audio_scale.place(x=width - self.audio_scale.width - Ui.del_audio_scale_x,
    #                            y=Ui.dock_h - self.audio_scale.height - Ui.dock_edge_pady)

    def place_widgets(self, width):
        b_y = Ui.dock_h - Ui.dock_b_pady

        self.stop_button.place(anchor='sw', x=Ui.dock_edge_padx, y=b_y)

        self.previous_button.pack(side='left')
        self.play_button.pack(side='left')
        self.next_button.pack(side='left')
        self.center_b_frame.place(anchor='s', relx=0.5, y=b_y)

        #
        # self.previous_button.place(anchor='se', relx=round((width / 2) - (Ui.im_dim * 1.5)) - Ui.dock_b_padx, y=b_y)
        # self.play_button.place(anchor='s', relx=0.5, y=b_y)
        # self.next_button.place(x=round((width + Ui.im_dim) / 2) + Ui.dock_b_padx,
        #                        y=Ui.dock_h - Ui.im_dim - Ui.dock_b_pady)

        self.current_time_l.place(anchor='nw', x=0, y=Ui.dock_tl_pady)
        self.full_time_l.place(anchor='ne', relx=1, y=Ui.dock_tl_pady)

        self.media_scale.config_dim(width=self.calculate_mscale_w(width, update=True))
        self.media_scale.place(x=self.calculate_mscale_x(), y=Ui.dock_edge_pady / 2)

        self.audio_scale.config_dim(width=self.calculate_ascale_w(width))
        self.audio_scale.place(anchor='se', relx=0.98, y=Ui.dock_h - Ui.dock_edge_pady)

    def _cancel_anim(self):
        if self.anim_timer:
            self.master.after_cancel(self.anim_timer)
            self.anim_timer = None

    def _force_dock(self):
        self.d_timer_reset()
        self._cancel_anim()
        self.__set_height(Ui.dock_h)
        self.state = 1
        show_cursor()

    def _force_undock(self):
        self.d_timer_cancel()
        self._cancel_anim()
        self.__set_height(1)
        self.state = 0
        reset_cursor_hide_timer()

    def dock(self):
        # force dock
        if self.state in (0, 2):
            self._force_dock()

    def un_dock(self):
        # force undock
        if self.state in (1, 2):
            self._force_undock()

    def d_timer_cancel(self):
        if self.d_timer is not None:
            try:
                self.master.after_cancel(self.d_timer)
            except Exception as e:
                print(e)
            finally:
                self.d_timer = None

    def d_timer_reset(self):
        if self.d_timer is not None:
            try:
                self.master.after_cancel(self.d_timer)
            except Exception as e:
                print(e)
        self.d_timer = self.master.after(self.d_time, self.animate_undock)

    def is_over(self, *pos):
        if self.state == 1 and self.master.winfo_containing(*pos) == self:
            return True
        return False

    def __set_height(self, new_h: int):
        self['height'] = new_h
        self.update()

    def get_height(self, update=False):
        if update:
            self.update()
        return self.winfo_height()

    def __schedule_anim_call(self, call, h: int):
        self.anim_timer = self.master.after(self._anm_time, call, h)

    def _anm_dock(self, cur_h=1):
        if cur_h < Ui.dock_h - self._anm_step - 1:
            new_h = cur_h + self._anm_step
            self.__set_height(new_h)
            self.__schedule_anim_call(self._anm_dock, new_h)
        else:
            self._force_dock()

    def animate_dock(self):
        if self.state == 0:
            self.state = 2  # set busy
            self.__schedule_anim_call(self._anm_dock, self.get_height())

    def _anm_undock(self, cur_h):
        if cur_h > 1 + self._anm_step:
            new_h = cur_h - self._anm_step
            self.__set_height(new_h)
            self.__schedule_anim_call(self._anm_undock, new_h)
        else:
            self._force_undock()

    def animate_undock(self):
        if self.state == 1:
            self.state = 2  # set busy
            self.__schedule_anim_call(self._anm_undock, self.get_height())


# .......................................................functions............................


def __evenT_call_filter(event=None):
    """
    determines whether to call the base event callback
    :return: true to call the base, false otherwise
    """
    # 1. If there are some dialogs
    if BaseDialogFrame.has_instances():
        return False
    return True


def wrap_event_call(callback):
    return CallbackWrapper(callback, __evenT_call_filter)


def get_ex(file_name):
    return os.path.splitext(file_name)[1]


def save_pastinfo():
    if __media_paths__:
        all_ = __media_paths__ + mpast_['past_media']
        _past_info_ = {'past_media': all_[:50], 'play_count': _play_count.v}
    else:
        if os.path.isfile(C.past_file):
            _past_info_ = {'past_media': mpast_['past_media'], 'play_count': _play_count.v}
        else:
            _past_info_ = {'past_media': [], 'play_count': _play_count.v}
    dump(_past_info_, C.past_file)


def save_settings():
    info_dic = {'save_pos': save_pos.get(), 'vol_rate': default_vol_rate.v, 'seek_rate': default_seek_rate.v,
                'max_volume': max_volume.v, 'current_vol': current_vol.v, 'exit_check': exit_check.get(),
                'refresh_time': refresh_time_ms.v,
                'scan_sub': scan_sub_on_load.get(), 'fulltime_state': _full_time_info.key,
                'load_on_start': load_on_start.get(),
                'controller': control_win_check.get(), 'auto_play': _auto_play.get(),
                'controller_coords': controller_coordinates.v, 'mouse_gestures': _mouse_gestures.get()}

    dump(info_dic, C.settings_file)


def join_sys_paths(_n):
    return os.path.join(C.sys_dir, _n)


def sync_sys_paths(_sys_files=None):
    if not _sys_files and C.sys_dir_exists():
        _sys_files = os.listdir(C.sys_dir)
    if _sys_files:
        _sys_files = map(join_sys_paths, _sys_files)
        _len_temp = len(__media_paths__)
        for _sys_f in _sys_files:
            _sd = load(_sys_f, False, False)
            os.remove(_sys_f)
            if _sd:
                for m__ in _sd:
                    if m__ not in __media_paths__:
                        __media_paths__.append(m__)

        change_ = len(__media_paths__) - _len_temp
        if change_ > 0:
            if playlist_win.state() == 'normal':
                playlist_win.insert_pathseq(__media_paths__)
            if _len_temp == 0:
                force()


def load_past():
    len_temp__ = len(__media_paths__)
    _p_paths = mpast_['past_media']

    if _p_paths:
        for path_ in _p_paths:
            if os.path.isfile(path_) and path_ not in __media_paths__:
                __media_paths__.append(path_)

        change_ = len(__media_paths__) - len_temp__
        if change_ == 0:
            if len_temp__ == 0:
                messagebox.showinfo('Load Failed', 'Previous Media Load Failed : DATA NOT ON DISK LOCATION', parent=win)
        elif change_ > 0:
            if playlist_win.state() == 'normal':
                playlist_win.insert_pathseq(__media_paths__)
            if len_temp__ == 0:
                count()


def sys_load():
    if len(sys.argv) > 1:
        for path_ in sys.argv[1:]:
            if get_ex(path_) in C.all_format and path_ not in __media_paths__:
                __media_paths__.append(path_)
        force()
        return

    if C.sys_dir_exists():
        _s_p = os.listdir(C.sys_dir)
        if _s_p:
            sync_sys_paths(_s_p)
            force()
            return

    if load_on_start.get() == 1:
        load_past()


def quit_(event=None):
    system_on.v = False
    save_playback(_play_count.v)
    try:
        player.stop()
        player.release()
        main_player_in.release()
        PreDisplay.quit_()
        C.delete_run_file()
    except Exception as e:
        print(e)
    save_pastinfo()
    save_settings()
    dump(playback_dict, C.playback_file)
    win.quit()
    win.destroy()
    sys.exit()


def exit_diag():
    if exit_check.get() == 1:
        win.deiconify()
        win.update()

        if ExitDiag.Instance:
            ExitDiag.Instance.place(relx=0.5, rely=0.5, anchor='center')
        else:
            e = ExitDiag(win, exit_call=quit_, cancel_call=None)
            e.place(relx=0.5, rely=0.5, anchor='center')
    else:
        quit_()


def show_msg_no_media():
    SnackBar.show_msg(win, 'Media queue is empty')


def ensure_media_paths():
    if not __media_paths__:
        show_msg_no_media()
        return False
    return True


@SetName('Save Playlist')
def save_playlist(event=None):
    rp = load(C.playlist_file, None, None)
    win.deiconify()
    win.update()

    if ensure_media_paths():
        e = EncryptionBox(win, title='New Playlist',
                          caption='Create Playlist\n(Leave password blank for no encryption)', playlist_dic=rp,
                          file_path=C.playlist_file)
        e.place(anchor='center', relx=0.5, rely=0.5)


@SetName('Load Playlist')
def load_playlist(event=None):
    win.deiconify()
    win.update()

    if LoadPlay.Instance:
        LoadPlay.Instance.place(anchor='center', relx=0.5, rely=0.5)
    else:
        __rp = load(C.playlist_file, None, None)
        if __rp:
            l = LoadPlay(win, play_file_path=C.playlist_file, data=__rp)
            l.place(anchor='center', relx=0.5, rely=0.5)
        else:
            SnackBar.show_msg(win,
                              "No playlist saved yet! Go to Menu > Playlist > Show Playlist\n and click on \"Save Playlist\" to save one")
            # messagebox.showwarning('No playlist', 'could not load : NO SAVED PLAYLIST', parent=win)


@SetName('Load Media File')
def openfile(event=None):
    file_paths_of = filedialog.askopenfilenames(master=win, initialdir="C;\\", title="Open Media Files", filetypes=(
        ('Media Files',
         '*.wav *.3ga *.669 *.a52 *.aac *.ac3 *.adt *.adts *.aif *.aif *.aifc *.aiff *.amr *.aob *.ape *.awb '
         '*.caf *.dts *.flac *.it *.m4a *.kar *.m4b *.m4p *.m5p *.mid *.mka *.mlp *.mod *.mpa *.mp1 *.mp2 *.mp3 *.mpc '
         '*.ogg *.oga *.mus *.mpga *.mp4 *.mkv *.3g2 *.3gp *.3gp2 *.3gpp *.amv *.asf *.avi *.bik *.bin *.divx *.drc '
         '*.dv *.f4v *.flv *.gvi *.gfx *.iso *.m1v *.m2v *.m2t *.m2ts *.m4v *.mov *.mp2 *.mp2v *.mp4v *.mpe *.mpeg '
         '*.mpeg1 *.mpeg2 *.mpeg4 *.mpg *.gif *.webm'),
        ('Audio',
         '*.wav *.3ga *.669 *.a52 *.aac *.ac3 *.adt *.adts *.aif *.aif *.aifc *.aiff *.amr *.aob *.ape *.awb '
         '*.caf *.dts *.flac *.it *.m4a *.kar *.m4b *.m4p *.m5p *.mid *.mka *.mlp *.mod *.mpa *.mp1 *.mp2 *.mp3 *.mpc '
         '*.ogg *.oga *.mus *.mpga'),
        ('Video',
         '*.mp4 *.mkv *.3g2 *.3gp *.3gp2 *.3gpp *.amv *.asf *.avi *.bik *.bin *.divx *.drc *.dv *.f4v ''*.flv '
         '*.gvi *.gfx *.iso *.m1v *.m2v *.m2t *.m2ts *.m4v *.mov *.mp2 *.mp2v *.mp4v *.mpe *.mpeg *.mpeg1 *.mpeg2'
         ' *.mpeg4 *.mpg *.gif *.webm'),
        ('all files', '*.*')))

    if len(file_paths_of) > 0:
        len_temp_ = len(__media_paths__)
        for path_ in file_paths_of:
            if get_ex(path_).lower() in C.all_format and path_ not in __media_paths__:
                __media_paths__.append(path_)

        change_ = len(__media_paths__) - len_temp_
        if change_ > 0:
            if playlist_win.state() == 'normal':
                playlist_win.insert_pathseq(__media_paths__)
            if len_temp_ == 0:
                force()


@SetName('Scan Directories')
def scan_folder_ui(event=None):
    if not ScanDirUi.Instance:
        ScanDirUi(win)
    else:
        ScanDirUi.Instance.deiconify()
        ScanDirUi.Instance.update()


def scan_directories(dirs, _exts_=C.all_format):
    files_in_dirs = []
    for dir_ in dirs:
        files_in_dirs += search_exts(ext_list=_exts_, start=dir_, mode='path')
    if files_in_dirs:
        len_temp_ = len(__media_paths__)
        for path_ in files_in_dirs:
            if path_ not in __media_paths__:
                __media_paths__.append(path_)

        change_ = len(__media_paths__) - len_temp_
        if change_ > 0:
            if playlist_win.state() == 'normal':
                playlist_win.insert_pathseq(__media_paths__)
            if len_temp_ == 0:
                force()
    else:
        messagebox.showinfo('Load Media', 'No Media found in specified directpry : NO MEDIA IN DIR', parent=win)


@SetName('Save As')
def _save_as_(event=None):
    if not __media_paths__:
        messagebox.showerror('Error', 'No Media in Playlist currently : NO MEDIA TO SAVE', parent=win)
        return

    if playlist_win.state() == 'normal':  # docked
        file_path__ = __media_paths__[playlist_win.get_active()]
    else:
        file_path__ = __media_paths__[_play_count.v]

    if file_path__:
        ext__ = os.path.splitext(file_path__)[1]
        new_path__ = filedialog.asksaveasfilename(initialdir="C;\\", title="SAVE AS",
                                                  filetypes=[(f'Default : {ext__}', ext__), ('All Files', '*')],
                                                  defaultextension=ext__)
        if new_path__:
            p_ = Thread(target=shutil.copy, args=(file_path__, new_path__))
            p_.setDaemon(True)
            p_.start()


def set_playback_speed():
    def _main(__speed_in__):
        if __speed_in__:
            try:
                speed = float(__speed_in__)
            except Exception as e:
                print_(e)
                box_.clear_entry()
                messagebox.showwarning("Wrong Input", 'Can only be float : INVALID INPUT DATA', parent=box_)
            else:
                player.set_rate(speed)
                box_.on_success()
                SnackBar.show_msg(win, f'Playback Speed : {speed}')

    box_ = RcDiag(win, "playback Speed", "Enter the playback speed", retain_value=False, command=_main)
    box_.entry.insert(END, player.get_rate())
    box_.place_at_center()


@SetName('Remove Media')
def remove_media(event=None):
    if playlist_win.state() == 'normal':  # docked
        m_in = playlist_win.get_active()
        if m_in is not None:
            try:
                if _play_count.v == m_in or _play_count.v == (m_in - len(__media_paths__)):
                    if player.get_state() in (3, 4):
                        stop()
                        path_temp = '/////'  # had to play again
                    else:
                        path_temp = '////////'  # no need to play
                else:
                    path_temp = __media_paths__[_play_count.v]

                __media_paths__.pop(m_in)
                playlist_win.pop(m_in)
                if path_temp == '/////':
                    count()
                elif path_temp == '////////':
                    if _play_count.v >= len(__media_paths__):
                        _play_count.v = 0
                else:
                    _play_count.v = __media_paths__.index(path_temp)

            except Exception as e:
                print_(f'exception while removing media : {e}')


@SetName('Clear Playlist')
def clear_playlist():
    if __media_paths__:
        if player.get_state() in (3, 4):
            stop()

        __media_paths__.clear()
        _video_canvas_.delete('all')

        if playlist_win.state() == 'normal':  # docked
            playlist_win.insert_pathseq(__media_paths__)

        nothing_special()


@SetName('Shuffle Playlist')
def shuffle(event=None):
    if __media_paths__:
        save_playback(_play_count.v)
        random.shuffle(__media_paths__)
        _video_canvas_.delete('all')

        if playlist_win.state() == 'normal':  # docked
            playlist_win.insert_pathseq(__media_paths__)
        force()


@SetName('Show / Hide Playlist')
def toggle_playlist(event=None):
    if playlist_win.state() in ("iconic", "withdrawn"):
        playlist_win.dock()
        _playlist_menu_.entryconfig(0, label="Hide Playlist")
    else:
        playlist_win.un_dock()
        _playlist_menu_.entryconfig(0, label="Show Playlist")


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<     AUDIO AND SUBTITLE TRACKS    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_audio_sub_track():
    exsub_list.clear()  # resetting exsub_list as media changes
    audio_list.clear()
    sub_list.clear()

    audio_track.delete(0, END)
    sub_menu.delete(0, END)
    _m_len = set_fulltime(dock.full_time_l)
    setattr(_full_time_info, 'media_length', _m_len)
    set_fulltime(fsdock.f_time)
    sub_menu.add_command(label='Disable', command=disable_sub, font=Ui.menu_font)

    audio_list.extend(player.audio_get_track_description())
    sub_list.extend(player.video_get_spu_description())

    for aid, audio in audio_list:
        audio_track.add_command(label=audio, command=lambda arg=aid: set_audio_track(arg), font=Ui.menu_font)
    if sub_list:
        video_menu.entryconfigure(0, state=NORMAL)
        for sid, sub in sub_list:
            if sid != -1:
                sub_menu.add_command(label=sub, command=lambda arg=sid: set_sub(arg), font=Ui.menu_font)
    else:
        video_menu.entryconfigure(0, state=DISABLED)
        video_menu.entryconfigure(4, state=DISABLED)

    player.audio_set_volume(round(current_vol.v))

    if scan_sub_on_load.get() == 1:
        auto_scan_sub()


@SetName('Change Audio Track')
def change_audio_track(event=None):
    if player.get_state() in (3, 4):
        current_id = player.audio_get_track()
        des = None

        if len(audio_list) >= 3:
            choice = random.choice(audio_list)
            while choice[0] == -1 or choice[0] == current_id:
                choice = random.choice(audio_list)

            set_audio_track(choice[0])
            des = str(choice[1], 'utf-8')
        else:
            for aid, audio in audio_list:
                if aid == current_id:
                    des = str(audio, 'utf-8')
                    break

        if not des:
            des = "Unknown"
        TopRightSnackbar.show_audio_track(win, "Audio Track: " + des)


def set_audio_track(value):
    player.audio_set_track(value)


def set_sub(value):
    player.video_set_spu(value)
    video_menu.entryconfigure(4, state=NORMAL)

    if value == -1:
        msg = "Subtitles Disabled"
    else:
        for sid, sub in sub_list:
            if sid != -1 and sid == value:
                des = str(sub, 'utf-8')
                break
        else:
            des = 'Unknown'
        msg = 'Subtitle Track: ' + des

    TopRightSnackbar.show_sub_track(win, msg)


def disable_sub():
    set_sub(-1)


def set_sub_file(path_):
    player.video_set_subtitle_file(path_)
    video_menu.entryconfigure(4, state=NORMAL)
    video_menu.entryconfigure(0, state=NORMAL)

    msg = 'Subtitle Track: ' + os.path.basename(path_)[0:30]
    TopRightSnackbar.show_sub_track(win, msg)


def add_sub():
    if get_ex(__media_paths__[_play_count.v]) in C.video_format:
        sub_path = filedialog.askopenfilename(initialdir="C;\\", title="Add Subtitle", filetypes=(
            ('Subtitle file',
             '*.srt *.aqt *.cvd *.dks *.jss *.sub *.ttxt *.mpl *.txt *.pjs *.psb *.rt *.smi *.ssf *.ssa *.svcd *.usf *.idx'),
            ('all files', '*.*')))
        if sub_path:
            add_sub_file(sub_path)
    else:
        messagebox.showerror("Invalid Format", 'Media file do not support subtitles : INVALID FORMAT')


def add_sub_file(sub_path: str, set_now: bool = True):
    sub_path = sub_path.replace(r'/', r'\\')
    if sub_path not in exsub_list:
        exsub_list.append(sub_path)
        sub_dir, sub_name = os.path.split(sub_path)
        sub_menu.add_command(label=Ui.ellip(sub_name, 36), command=lambda arg=sub_path: set_sub_file(arg))
        if set_now:
            set_sub_file(sub_path)
        return True
    return False


class SubUi(BaseDialogFrame):
    INSTANCE = None

    @classmethod
    def destroy_instance(cls):
        if cls.INSTANCE:
            cls.INSTANCE.destroy()
            cls.INSTANCE = None
            return True
        return False

    @classmethod
    def show_instance(cls, master, m_path):
        cls.destroy_instance()
        cls.INSTANCE = cls(master, m_path)
        cls.INSTANCE.place_at_center()

    def __init__(self, master, m_path, title='Subtitle Tracks', **kwrags):
        self.m_path = m_path
        self.m_dir = os.path.dirname(m_path)
        self.ex_sub_files = [os.path.join(self.m_dir, f) for f in os.listdir(self.m_dir) if
                             os.path.isfile(os.path.join(self.m_dir, f)) and os.path.splitext(f)[
                                 1].lower() in C.subtitles_format]
        self.in_subs = [_tup for _tup in player.video_get_spu_description() if _tup[0] != -1]
        self.bg_dark = rgb(0, 0, 0)
        self.bg_medium = rgb(30, 30, 30)
        self.bg_light = rgb(50, 50, 50)
        self.fg_dark = rgb(255, 255, 255)
        self.fg_medium = rgb(245, 245, 245)
        self.fg_light = rgb(225, 225, 225)

        super().__init__(master, title=title, bg_dark=self.bg_dark, fg_medium=self.fg_dark, bg_medium=self.bg_light,
                         fg_dark=self.fg_light, **kwrags)

        self.pack_widgets()
        if len(self.ex_sub_files + self.in_subs):
            self.buttons = []
            self.b_padx, self.b_pady = Ui.sub_b_padx, Ui.sub_b_pady

            self.in_sub_l = Label(self, text=' Internal Tracks ', font=('product sans', 9), bg=self.bg_medium,
                                  fg=self.fg_light, bd=0, relief='flat')
            self.ex_sub_l = Label(self, text=' External Tracks ', font=('product sans', 9), bg=self.bg_light,
                                  fg=self.fg_light, bd=0, relief='flat')

            self.add_buttons()
            self.place(relx=.5, rely=.5, anchor='center')
        else:
            self.msg = Label(self,
                             text='No embedded subtitle track or subtitle file \nfound within the media folder !!',
                             font=('product sans', 9), bg=self.bg_dark,
                             fg=self.fg_dark, relief='flat', anchor='center')
            self.msg.pack(side=TOP, padx=24, pady=20, fill='x')

        self.bind("<Escape>", lambda event: self.destroy())

    def set_sub_file(self, sub_path):
        sub_path = sub_path.replace('/', '\\')
        add_sub_file(sub_path, set_now=False)
        set_sub_file(sub_path)
        self.destroy()

    def set_sub_id(self, sid):
        set_sub(sid)
        self.destroy()

    def focus__(self, index):
        if index >= len(self.buttons):
            index = 0
        elif index == -1:
            index = len(self.buttons) - 1
        self.buttons[index].focus_set()

    def add_buttons(self):
        if self.in_subs:
            self.in_sub_l.pack(padx=5, pady=self.b_pady, side='top', anchor='nw', fill='x', expand=True)
            for sid, sub in self.in_subs:
                _b = Button(self, text=sub, font=('product sans', 10), bg=self.bg_dark, fg=self.fg_medium,
                            relief='flat',
                            activebackground=self.bg_light, bd=0, command=lambda arg=sid: self.set_sub_id(arg),
                            activeforeground=self.fg_dark)

                _b.bind('<Return>', lambda event_, arg_=sid: self.set_sub_id(arg_))
                _b.bind('<Up>', lambda event_, arg_=len(self.buttons) - 1: self.focus__(arg_))
                _b.bind('<Down>', lambda event_, arg_=len(self.buttons) + 1: self.focus__(arg_))
                _b.pack(fill='x', padx=self.b_padx, pady=self.b_pady, side='top', anchor='n')
                self.buttons.append(_b)

        if self.ex_sub_files:
            self.ex_sub_l.pack(padx=5, pady=self.b_pady, side='top', anchor='nw', fill='x', expand=True)
            for sub_path in self.ex_sub_files:
                _b = Button(self, text=Ui.ellip(os.path.basename(sub_path), 57), font=('product sans', 10),
                            bg=self.bg_dark,
                            fg=self.fg_medium, relief='flat', activebackground=self.bg_light, bd=0,
                            command=lambda arg=sub_path: self.set_sub_file(arg), activeforeground=self.fg_dark)

                _b.bind('<Return>', lambda event_, arg_=sub_path: self.set_sub_file(arg_))
                _b.bind('<Up>', lambda event_, arg_=len(self.buttons) - 1: self.focus__(arg_))
                _b.bind('<Down>', lambda event_, arg_=len(self.buttons) + 1: self.focus__(arg_))
                _b.pack(fill='x', expand=True, padx=self.b_padx, pady=self.b_pady, side='top', anchor='n')
                self.buttons.append(_b)
        # self.buttons[0].focus_set()
        self.lift()

    def destroy(self):
        super().destroy()
        self.__class__.INSTANCE = None


@SetName('Scan Subtitles')
def auto_scan_sub(event=None):
    if SubUi.destroy_instance() and event:
        return

    if __media_paths__:
        m_path = __media_paths__[_play_count.v]
        if get_ex(m_path) in C.video_format:
            SubUi.show_instance(win, m_path)


def set_spu_delay():
    def _main(delay_ms):
        if delay_ms:
            try:
                delay_ms = int(delay_ms)
            except Exception as e:
                print_(e)
                messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT', parent=box)
                box.clear_entry()
            else:
                delay_ = delay_ms * 1000
                player.video_set_spu_delay(delay_)
                box.on_success()
                SnackBar.show_msg(win, f'Spu Delay : {delay_ms} ms')

    if player.video_get_spu() != -1:
        box = RcDiag(win, 'Subtitle Delay', 'Set Subtitle Delay (in milliseconds)', retain_value=False, command=_main)
        box.entry.insert(END, player.video_get_spu_delay() // 1000)
        box.place_at_center()
    else:
        messagebox.showerror("Error", 'Select a subtitle track first : SYNC ERROR')


def _set_aspect(asp):
    player.video_set_aspect_ratio(asp)
    TopCenterSnackbar.show_asp_ratio(win, asp)


@SetName('Change Aspect Ratio')
def set_aspect_ratio(event=None):
    def parse_aspect(_w, _h):
        if _w > _h:
            return round(_w / _h, 2), 1
        return 1, round(_h / _w, 2)

    def _main(_str):
        if _str:
            try:
                w, h = parse_aspect(*map(int, _str.split(':')))
                _str = f'{w}:{h}'
            except Exception as e:
                print_(e)
                box_.clear_entry()
                # messagebox.showerror("Error", 'video configuration failed : INVALID ASPECT RATIO', parent=box_)
                SnackBar.show_msg(win, f'Invalid Aspect Ratio')
            else:
                _set_aspect(_str)
                C.aspect_ratio_list.append(_str)
                aspect_ratio_index.v = len(C.aspect_ratio_list) - 1
                aspect_menu.add_radiobutton(label=_str, command=lambda arg=_str: _set_aspect(arg), font=Ui.menu_font)
                box_.on_success()

    if player.get_state() in (3, 4) and get_ex(__media_paths__[_play_count.v]) in C.video_format:
        if event:
            if aspect_ratio_index.v < len(C.aspect_ratio_list) - 1:
                aspect_ratio_index.v += 1
            else:
                aspect_ratio_index.v = 0

            string = C.aspect_ratio_list[aspect_ratio_index.v]
            _set_aspect(string)
        else:
            box_ = RcDiag(win, 'Set Aspect Ratio', 'Enter aspect ratio (like 16:9)', retain_value=True, command=_main)
            box_.place_at_center()


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  MAIN PLAY FUNCTION         >>>>>>>>
def set_wintitle(m_name: str = None, streaming: bool = False):
    C.WinTitleBarText = f'{C.WinTitle} {Ui.CHR_MIDDLE_DOT} {"Streaming" if streaming else "Playing"} {m_name}' if m_name else C.WinTitle
    win.title(C.WinTitleBarText)


@SetName('Play')
def force(event=None):
    if __media_paths__:
        save_playback(_play_count.v)
        _play_count.v = 0
        count()


@SetName('Play / Pause')
def count(event=None):
    if __media_paths__:
        _len = len(__media_paths__)
        if _play_count.v >= _len:
            _play_count.v = 0  # resetting _play_count
        elif _play_count.v < 0:
            _play_count.v += _len

        m_path_ = __media_paths__[_play_count.v]
        m_name_ = os.path.basename(m_path_)

        player.set_media(main_player_in.media_new(m_path_))
        player.play()
        set_normal(m_path_, m_name_)


@SetName('Play Selected Media')
def active(event=None):
    if playlist_win.state() == 'normal':
        try:
            if player.get_state() in (3, 4):
                save_playback(_play_count.v)
            m_index = playlist_win.get_active()
            if m_index is not None:
                _play_count.v = m_index
        except Exception as e:
            print_(e)
        count()


def set_normal(m_path, m_name):
    try:
        dock.media_scale.enable()
        fsdock.m_scale.enable()
        dock.play_button['image'] = pause_image
        dock.play_button['command'] = pause
        _playback_menu_.entryconfigure(11, label="Pause")
        play_seq = bindings_dict['playback'][count.__qualname__]
        win.bind(play_seq, wrap_event_call(pause))
        fsdock.bind(play_seq, pause)
        playlist_win.bind(play_seq, pause)
        set_wintitle(m_name)

        win.after(700, get_audio_sub_track)
        player.audio_set_volume(round(current_vol.v))

        setattr(win, 'stream_title', '')
        __ext = get_ex(m_name)

        if Controller.Instance:
            Controller.Instance.config_label(m_name)

        if __ext.lower() in C.song_format:
            PreDisplay.m_path = None
            set_image(m_path)
            video_menu.entryconfigure(7, state=DISABLED)
            video_menu.entryconfigure(9, state=DISABLED)
        else:
            if thumbnail_info[0] != -1:
                _video_canvas_.delete(thumbnail_info[0])
                thumbnail_info[0] = -1

            video_menu.entryconfigure(7, state=NORMAL)
            video_menu.entryconfigure(9, state=NORMAL)
            PreDisplay.set_media(m_path)

        if save_pos.get() == 1:
            # __in = PlaybackWin.INSTANCE
            if m_path in playback_dict:
                print("showing instance of playback restore snack")

                # if isinstance(__in, (PlaybackWin,)):
                #     __in.show()
                # else:
                #     PlaybackWin(win, 'Do you want to resume where you left', callback=set_playback)
                #

                RestorePlaynackSnackbar.show_instance(win, set_playback)
            else:
                print("hiding instance of playback restore snack")
                # if isinstance(__in, (PlaybackWin,)) and __in.state == 1:  # still docked
                #     __in.undock()
                RestorePlaynackSnackbar.hide_instance()

        SubUi.destroy_instance()
    except Exception as e:
        print_(e)


def set_stream(s_title):
    dock.media_scale.enable()
    fsdock.m_scale.enable()
    dock.play_button['image'] = pause_image
    dock.play_button['command'] = pause
    _playback_menu_.entryconfigure(11, label="          Pause")

    play_seq = bindings_dict['playback'][count.__qualname__]
    win.bind(play_seq, wrap_event_call(pause))
    fsdock.bind(play_seq, pause)
    playlist_win.bind(play_seq, pause)

    set_wintitle(s_title, streaming=True)

    win.after(700, get_audio_sub_track)
    player.audio_set_volume(round(current_vol.v))

    setattr(win, 'stream_title', s_title)
    PreDisplay.m_path = None
    if Controller.Instance:
        Controller.Instance.config_label(s_title)

    if thumbnail_info[0] != -1:
        _video_canvas_.delete(thumbnail_info[0])
        thumbnail_info[0] = -1

    SubUi.destroy_instance()


# ..........................................................................................
def sync_run_file_and_parallel_run():
    C.ensure_run_file()
    parallel_run_enabled = C.load_parallel_run_enabled()
    if _parallel_run_var.get() != parallel_run_enabled:
        _parallel_run_var.set(parallel_run_enabled)


def set_image(file_path__):
    if thumbnail_info[0] != -1:
        _video_canvas_.delete(thumbnail_info[0])
        thumbnail_info[0] = -1

    im__ = get_audio_thumb(file_path__)
    if im__ is not None:
        thumbnail_info[1] = width, height = im__.size
        win.im__ = im__ = PIL.ImageTk.PhotoImage(im__)
        thumbnail_info[0] = _video_canvas_.create_image(round((win_width.v - width) / 2),
                                                        round((win_height.v - height) / 2),
                                                        image=im__, anchor=NW)


@SetName('Capture Screen Shot')
def screenshot(event=None):
    if not os.path.isdir(C.user_app_screenshots_dir):
        os.makedirs(C.user_app_screenshots_dir)

        if not os.path.isdir(C.user_app_screenshots_dir):  # still not there
            if not os.path.isdir(C.default_screenshot_dir):
                os.makedirs(C.default_screenshot_dir)
            s_dir = C.default_screenshot_dir
        else:
            s_dir = C.user_app_screenshots_dir
    else:
        s_dir = C.user_app_screenshots_dir

    m_name, m_ext = os.path.splitext(os.path.basename(__media_paths__[_play_count.v]))
    if m_ext in C.video_format:
        _s_name = f'{m_name}_{Ui.format_secs(Ui.mills_to_sec(player.get_time()), full=True, full_delimiter="-")}.jpg'
        s_path = os.path.join(s_dir, _s_name)
        r = player.video_take_snapshot(0, s_path, 0, 0)
        snack = ScreenshotSnackbar(win, path=s_path, success=r == 0)
        snack.show_at_top_center()


@SetName('Stream media')
def stream_(event=None):
    StreamFrame.show_instance(win, stream_call=player_set_url)


def player_set_url(url=None, title=None):
    if not url:
        return
    media = main_player_in.media_new(url)
    media.get_mrl()
    player.set_media(media)

    player.play()

    if not title:
        title = url
    set_stream(title)


def pause(event=False):
    if ensure_media_paths():
        if player.get_state() == 3:
            dock.play_button['image'] = play_image
            _playback_menu_.entryconfigure(11, label="Resume", image=playi)
        else:
            dock.play_button['image'] = pause_image
            _playback_menu_.entryconfigure(11, label="Pause", image=pausei)

        dock.play_button['command'] = pause
    player.pause()


#      ...............................MAIN THREAD .....................................................
def __main_ui__():
    try:
        _state_ = player.get_state()
        if _state_ == 6:
            if _auto_play.get() == 1:
                _play_count.v += 1
                count()
            else:
                nothing_special()

        elif _state_ in (3, 4):
            if _fullscreen.v:
                set_ctime(fsdock.c_time, fsdock.f_time)
                fsdock.auto_set()
            else:
                if dock.auto_media_scale:
                    dock.media_scale.set(player.get_position() * 100)
                set_ctime(dock.current_time_l, dock.full_time_l)

            if win.state() == 'iconic' and control_win_check.get() == 1:
                if not Controller.Instance:
                    if playlist_win.state() == 'normal':
                        playlist_win.un_dock()
                    Controller(win)
                    if win.stream_title:
                        Controller.Instance.config_label(win.stream_title)
                    else:
                        Controller.Instance.config_label(os.path.basename(__media_paths__[_play_count.v]))
                    Controller.Instance.auto_set()
                else:
                    Controller.Instance.auto_set()

        if win.state() != 'iconic' and Controller.Instance:
            Controller.Instance.raise_main()

        if not _fullscreen.v and win.state() in ("normal", "zoomed"):
            __check_resize__()

        sync_run_file_and_parallel_run()
        if not _parallel_run_var.get():
            sync_sys_paths()
    except Exception as e:
        print(f'exception in main_thread : {e}')
    finally:
        if system_on.v:
            win.after(refresh_time_ms.v, __main_ui__)


def format_time_label(mills: int):
    hr_, min_, sec_ = Ui.mills_to_hms(mills)
    s = f'{min_:02d}:{sec_:02d}'
    return f'{hr_:02d}:{s}' if hr_ else s


def set_ctime(label, label2=None):
    c_time_ = player.get_time()
    label['text'] = format_time_label(c_time_)
    # label.update()

    if label2 and _full_time_info.key == 1:
        attr_ = getattr(_full_time_info, 'media_length', -1)
        f_time = attr_ if attr_ != -1 else player.get_length()
        label2['text'] = format_time_label(f_time - c_time_)
        # label2.update()


def set_fulltime(label):
    _length = player.get_length()
    label['text'] = format_time_label(_length)
    # label.update()

    return _length


def __resize_ui_width__(width):
    dock.resize(width)
    if thumbnail_info[0] != -1:
        _im_y = _video_canvas_.bbox(thumbnail_info[0])[1]
        _video_canvas_.coords(thumbnail_info[0], int((width - thumbnail_info[1][0]) / 2), _im_y)


def __resize_ui_height__(height):
    if thumbnail_info[0] != -1:
        _im_x = _video_canvas_.bbox(thumbnail_info[0])[0]
        _video_canvas_.coords(thumbnail_info[0], _im_x, int((height - thumbnail_info[1][1]) / 2))


def __check_resize__(event=None):
    _w, _h = win.winfo_width(), win.winfo_height()

    if win_width.v != _w:
        __resize_ui_width__(_w)
        win_width.v = _w

    if win_height.v != _h:
        print('resizing height')
        __resize_ui_height__(_h)
        win_height.v = _h


def nothing_special():
    dock.play_button['image'] = play_image
    dock.play_button['command'] = count

    play_seq = bindings_dict['playback'][count.__qualname__]
    win.bind(play_seq, wrap_event_call(count))
    playlist_win.bind(play_seq, count)
    fsdock.bind(play_seq, count)

    dock.current_time_l['text'] = '--:--'
    dock.full_time_l['text'] = '--:--'
    dock.media_scale.set(0)
    dock.media_scale.disable()

    _video_canvas_.delete('all')
    thumbnail_info[0] = -1


def save_playback(index):
    if save_pos.get() == 1 and player.get_state() in (3, 4):
        try:
            pos = player.get_position()
            if pos > .01:
                playback_dict[__media_paths__[index]] = pos
        except Exception as e:
            print(e)


@SetName('Stop Playback')
def stop(event=None):
    def main_stop():
        save_playback(_play_count.v)

        player.stop()
        setattr(_full_time_info, 'media_length', -1)
        dock.media_scale.set(0)
        dock.media_scale.disable()

        dock.current_time_l['text'] = '--:--'
        dock.full_time_l['text'] = '--:--'

        fsdock.c_time['text'] = '--:--'
        fsdock.f_time['text'] = '--:--'
        fsdock.m_scale.set(0)
        fsdock.m_scale.disable()

        if thumbnail_info[0] != -1:
            _video_canvas_.delete(thumbnail_info[0])
            thumbnail_info[0] = -1

        dock.play_button['image'] = play_image
        dock.play_button['command'] = count
        play_seq = bindings_dict['playback'][count.__qualname__]
        win.bind(play_seq, wrap_event_call(count))
        playlist_win.bind(play_seq, count)
        fsdock.bind(play_seq, count)

        PreDisplay.m_path = None
        set_wintitle(None)

    if event:
        if not _stop:
            _stop.v = True
            main_stop()
            win.after(delay, _stop)
    else:
        main_stop()


@SetName('Restore Playback')
def set_playback(event=None):
    try:
        if save_pos.get() == 1:
            pos = playback_dict[__media_paths__[_play_count.v]]
            player.set_position(pos)
            if event:
                RestorePlaynackSnackbar.hide_instance()
    except KeyError:
        print('no saved playback')


@SetName('Play Next Media')
def next_call(event=None):
    if len(__media_paths__) > 1 and not _next.v:
        _next.v = True
        save_playback(_play_count.v)
        _play_count.v += 1
        count()
        win.after(delay, _next)  # resetting _next after delay


@SetName('Play Previous Media')
def previous_call(event=None):
    if len(__media_paths__) > 1 and not _previous.v:
        _previous.v = True
        save_playback(_play_count.v)
        _play_count.v -= 1
        count()
        win.after(delay, _previous)  # resetting _previous after delay


@SetName('Seek Forward')
def forward(event=None):
    if player.get_state() in (3, 4):
        if event:
            if default_seek_rate.v > 0:
                ms = default_seek_rate.v * 1000
                player.set_time(player.get_time() + ms)
                # show_playback_notification("Jumped forward by " + Ui.format_mills(ms, _tuple=False, full=False))
                PlaybackSnackBar.instance_fw(win, ms)
        else:
            def _main(seek__):
                if seek__:
                    try:
                        seek__ = int(seek__)
                    except Exception as e:
                        print_(e)
                        SnackBar.show_msg(win, 'Invalid input: Can only be an integer')
                        # messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT', parent=box_)
                        box_.clear_entry()
                    else:
                        _n_time = player.get_time() + (seek__ * 1000)
                        player.set_time(_n_time)
                        box_.on_success()
                        SnackBar.show_msg(win, f'Jumped Forward : {seek__} s')

            box_ = RcDiag(win, "Seek Forward", "Enter the time to seek forward (in seconds)", retain_value=True,
                          command=_main)
            box_.place_at_center()


@SetName('Seek Backward')
def backward(event=False):
    if player.get_state() in (3, 4):
        if event:
            current_time_ = player.get_time()
            if current_time_ > 0 and default_seek_rate.v > 0:
                ms = min(current_time_, default_seek_rate.v * 1000)
                player.set_time(current_time_ - ms)
                # show_playback_notification("Jumped backward by " + Ui.format_mills(ms, _tuple=False, full=False))
                PlaybackSnackBar.instance_bw(win, ms)
        else:
            def _main(seek__):
                if seek__:
                    try:
                        seek__ = int(seek__)
                    except Exception as e:
                        print_(e)
                        SnackBar.show_msg(win, 'Invalid input: Can only be an integer')
                        # messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT', parent=box_)
                        box_.clear_entry()
                    else:
                        _n_time = player.get_time() - (seek__ * 1000)
                        if _n_time > 0:
                            player.set_time(_n_time)
                        else:
                            player.set_position(0)
                        box_.on_success()
                        SnackBar.show_msg(win, f'Jumped Backward : {seek__} s')

            box_ = RcDiag(win, "Seek Backward", "Enter the time to seek backward (in seconds)", retain_value=True,
                          command=_main)
            box_.place_at_center()


@SetName('Volume Up')
def vol_in(event=None):
    if event:
        if default_vol_rate.v > 0:
            current_ = int(player.audio_get_volume()) if player.get_state() in (3, 4) else (
                                                                                                   dock.audio_scale.value * max_volume.v) / 100
            if current_ >= max_volume.v - default_vol_rate.v:
                current_vol.v = max_volume.v
            else:
                current_vol.v = current_ + default_vol_rate.v
            aset_(current_vol.get())


@SetName("Volume Down")
def vol_dec(event=None):
    if event:
        if default_vol_rate.v > 0:
            current_ = int(player.audio_get_volume()) if player.get_state() in (3, 4) else (
                                                                                                   dock.audio_scale.value * max_volume.v) / 100
            if current_ <= default_vol_rate.v:
                current_vol.v = 0
            else:
                current_vol.v = current_ - default_vol_rate.v
            aset_(current_vol.v)


def setspecifictime():
    def _main(_in_sec):
        if _in_sec:
            try:
                int_sec = int(_in_sec)
                mills = int_sec * 1000
            except Exception as e:
                print_(f'exception in rendering specific time : {e}')
                # messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT', parent=box_)
                SnackBar.show_msg(win, 'Invalid input: Can only be an integer')
                box_.clear_entry()
            else:
                _l = player.get_length()
                if mills <= 0:
                    player.set_position(0)
                elif mills >= _l:
                    next_call()
                else:
                    player.set_time(mills)
                box_.on_success()
                SnackBar.show_msg(win, f'Jumped to time : {Ui.format_secs(int_sec, full=True)}')

    if player.get_state() in (3, 4):
        box_ = RcDiag(win, "Jump to time", "Enter the time to jump on (in seconds)", retain_value=True, command=_main)
        box_.place_at_center()


def aset_(vol, show=True, set_scale=True):
    if 0 <= vol <= max_volume.v:
        try:
            player.audio_set_volume(round(vol))
        except Exception as e:
            print_(e)

        if vol >= round(max_volume.v * .667):
            dock.audio_scale.itemconfig(dock.audio_scale.in_rect, fill=rgb(205, 92, 92))
        else:
            dock.audio_scale.itemconfig(dock.audio_scale.in_rect, fill=dock.audio_scale.trough_color1)

        vol_per = (vol / max_volume.v) * 100
        if set_scale:
            dock.audio_scale.set(vol_per)

        if show:
            TopRightSnackbar.show_volume(win, vol)
        else:
            TopRightSnackbar.hide_volume()

        ins_ = VolWin.Instance
        if ins_:
            if show and win.state() == 'iconic':
                ins_.update_((vol_per * ins_.range) / 100)
                ins_.attributes('-topmost', True)
            else:
                ins_.destroy()
        else:
            if show and win.state() == 'iconic':
                VolWin(win, range_=200).draw(vol_per * 2)


def mute(event=None):
    status__ = player.audio_get_mute()
    if not status__:
        player.audio_set_mute(True)
        audio_menu.entryconfigure(2, label='      Unmute', image=unmutei)
    else:
        player.audio_set_mute(False)
        audio_menu.entryconfigure(2, label='      Mute', image=mutei)


def hide_menu(event=None):
    if _main_menu.v:
        win.config(menu=empty_menu)
        _main_menu.v = False


@SetName('Show / Hide Menu Bar')
def toggle_menu(event=None):
    if _main_menu.v:
        win.config(menu=empty_menu)
        _main_menu.v = False
    else:
        win.config(menu=menubar)
        _main_menu.v = True


@SetName('Toggle Full Screen')
def toggle_fullscreen(event=None):
    if _fullscreen.v:
        win.attributes('-fullscreen', False)
        win.attributes('-topmost', False)
        fsdock.un_dock()
        if not _main_menu.v:
            win.config(menu=menubar)
            _main_menu.v = True
        video_menu.entryconfigure(6, label='Fullscreen')
        win.update()
        win.update_idletasks()
        win_width.v, win_height.v = win.winfo_width(), win.winfo_height()
        __resize_ui_height__(win_height.v)
        __resize_ui_width__(win_width.v)
        _fullscreen.v = False
    else:
        _fullscreen.v = True
        hide_menu()
        dock.un_dock()
        win.attributes('-fullscreen', True)
        win.attributes('-topmost', True)
        if thumbnail_info[0] != -1:
            width, height = thumbnail_info[1]
            _video_canvas_.coords(thumbnail_info[0], int((screen_width - width) / 2), int((screen_height - height) / 2))

        video_menu.entryconfigure(6, label='Exit Fullscreen')
        win_width.v, win_height.v = screen_width, screen_height


"""
SETTINGS CONFIGURATION ...........................................................
"""


def set_playback_seek_rate(event=None):
    def _main(value_):
        if value_:
            try:
                value_ = int(value_)
            except Exception as e:
                print_(e)
                # messagebox.showwarning("Wrong Input", 'Playback Seek Rate should be integer : INVALID INPUT',
                #                        parent=box_)
                SnackBar.show_msg(win, 'Invalid input: Playback Seek Rate should be a positive number')
                box_.clear_entry()
            else:
                if value_ > 0:
                    default_seek_rate.v = value_
                    box_.on_success()
                    SnackBar.show_msg(win, f'Playback seek rate : {value_} s')
                else:
                    # messagebox.showwarning("Wrong Input", 'Playback Seek Rate should be absolute : INVALID INPUT',
                    #                        parent=box_)
                    SnackBar.show_msg(win, 'Invalid input: Playback Seek Rate should be absolute')
                    box_.clear_entry()

    box_ = RcDiag(win, 'Playback Seek Rate', 'Playback Seek Rate (in secs)', retain_value=False, command=_main)
    box_.entry.insert(END, default_seek_rate.v)
    box_.place_at_center()


def set_vol_seek_rate(event=None):
    def _main(value_):
        if value_:
            try:
                value_ = int(value_)
            except Exception as e:
                print_(e)
                # messagebox.showwarning("Wrong Input", 'Volume Seek Rate should be integer : INVALID INPUT', parent=box_)
                SnackBar.show_msg(win, 'Invalid input: Volume Seek Rate should be a positive number')
                box_.clear_entry()
            else:
                if value_ > 0:
                    default_vol_rate.v = value_
                    box_.on_success()
                    SnackBar.show_msg(win, f'Volume seek rate : {value_} units')
                else:
                    # messagebox.showwarning("Wrong Input", 'Volume Seek Rate should be absolute : INVALID INPUT',
                    #                        parent=box_)
                    SnackBar.show_msg(win, 'Invalid input: Volume Seek Rate should be absolute')
                    box_.clear_entry()

    box_ = RcDiag(win, 'Volume Seek Rate', 'Volume Seek Rate (in volume units)', retain_value=False, command=_main)
    box_.entry.insert(END, default_vol_rate.v)
    box_.place_at_center()


def set_max_volume(event=None):
    def _main(value_):
        if value_:
            try:
                value_ = int(value_)
                if value_ <= 0:
                    raise ValueError
            except Exception as e:
                print(e)
                # messagebox.showwarning("Wrong Input", 'Max Volume should be integer : INVALID INPUT', parent=box_)
                SnackBar.show_msg(win, 'Maximum Volume should be a positive number')
                box_.clear_entry()
            else:
                if value_ > current_vol.v:
                    max_volume.v = value_
                    aset_(current_vol.v)
                    box_.on_success()
                    SnackBar.show_msg(win, f'Max Volume : {value_}%')
                else:
                    # messagebox.showwarning("Wrong Input",
                    #                        'Maximum Volume should be greater than Current Playback Volume : RANGE ERROR',
                    #                        parent=box_)
                    SnackBar.show_msg(win, f'Maximum Volume should be greater than the current volume ({current_vol.v})%')
                    box_.clear_entry()

    box_ = RcDiag(win, 'Maximum Volume', 'Maximum playback volume (in %)', retain_value=False, command=_main)
    box_.entry.insert(END, max_volume.v)
    box_.place_at_center()


def set_refresh_rate(event=None):
    def _main(value_):
        if value_:
            try:
                value_ = int(value_)
            except Exception as e:
                print(e)
                # messagebox.showwarning("Wrong Input", 'Refresh Rate should be integer : INVALID INPUT', parent=box_)
                SnackBar.show_msg(win, 'Invalid input: Refresh Rate should be a positive number')
                box_.clear_entry()
            else:
                if 5 <= value_ <= 60:
                    refresh_time_ms.v = round(1000 / value_)
                    box_.on_success()
                    SnackBar.show_msg(win, f'Refresh rate : {value_} fps')
                else:
                    # messagebox.showwarning('Invalid Input',
                    #                      'Refresh rate should be greater than 5 and less than 60 : RANGE ERROR',
                    #                      parent=box_)
                    SnackBar.show_msg(win, 'Refresh rate should be greater than 5 and less than 60')
                    box_.clear_entry()

    box_ = RcDiag(win, 'Refresh rate',
                  'Refresh rate of Ui (in Frames per second)\n ( warning : higher fps requires more resources )',
                  retain_value=False, command=_main)
    box_.entry.insert(END, (round(1000 / refresh_time_ms.v)))
    box_.place_at_center()


def toggle_fulltime_state(event=None):
    _f_state = _full_time_info.key
    if _f_state == 1:
        _full_time_info.key = 0
        set_fulltime(dock.full_time_l)
        set_fulltime(fsdock.f_time)
    else:
        _full_time_info.key = 1

    playback_settings_menu.entryconfigure(_full_time_info[_f_state], label=_full_time_info.get_keyv())


def change_bindings(event=None):
    BindsUi(win, (1200, 700), bindings_dict, C.bindings_file)


def update_call(event=None):
    # def _check(_up_file):
    #     # to check pickle load and version
    #     if os.path.isfile(_up_file) and os.path.splitext(_up_file)[1] == C.UpdateFileExt:
    #         try:
    #             with open(_up_file, 'rb') as _uf:
    #                 info_dic = pickle.load(_uf)
    #         except Exception as e:
    #             messagebox.showerror('Update Failed', 'File is either corrupt or invalid format\n error code : %s' % e,
    #                                  parent=win)
    #         else:
    #             if 'version' in info_dic:
    #                 _up_ver = info_dic['version']
    #                 _n_ver = U.get_new_ver(C.Version)
    #                 if _n_ver == _up_ver:
    #                     return True
    #                 messagebox.showerror('Update Failed',
    #                                      'Update package has invalid version signature : v%s\n\nDownload update patch having version %s' % (
    #                                          _up_ver, _n_ver), parent=win)
    #     return False

    # update_file = filedialog.askopenfilename(title='Browse Update file', initialdir="C;\\",
    #                                          filetypes=((f'Update File ({C.UpdateFileExt})', f'*{C.UpdateFileExt}'),),
    #                                          master=win)
    # if update_file:
    #     _code = _check(update_file)
    #     if _code:
    #         Popen([C.update_exe_path, update_file])
    #         quit_()

    p = Popen([C.update_exe_path])


def reset_default_settings():
    save_pos.set(C.default_settings['save_pos'])
    exit_check.set(C.default_settings['exit_check'])
    default_vol_rate.v = C.default_settings['vol_rate']
    default_seek_rate.v = C.default_settings['seek_rate']
    max_volume.v = C.default_settings['max_volume']
    refresh_time_ms.v = C.default_settings['refresh_time']
    _auto_play.set(C.default_settings['auto_play'])
    control_win_check.set(C.default_settings['controller'])
    scan_sub_on_load.set(C.default_settings['scan_sub'])
    load_on_start.set(C.default_settings['load_on_start'])

    if os.path.exists(C.bindings_file):
        os.remove(C.bindings_file)

    if _full_time_info.key != C.default_settings['fulltime_state']:
        toggle_fulltime_state()

    _parallel_run_var.set(C.default_parallel_run_enabled)

    if current_vol.v >= max_volume.v:
        current_vol.v = max_volume.v
    aset_(current_vol.v, show=False)


def set_fs_dock(event):
    # event is mouse motion without click
    if fsdock.state() in ("iconic", "withdrawn"):  # un docked
        fsdock.dock()
    else:
        if fsdock.mouse_over(event.x_root, event.y_root):
            fsdock.d_timer_cancel()
        else:
            fsdock.d_timer_reset()


def set_m_dock(event):
    # event is mouse motion without click
    if dock.state == 0:
        dock.animate_dock()
    elif dock.state == 1:
        if dock.is_over(event.x_root, event.y_root):
            dock.d_timer_cancel()
        else:
            dock.d_timer_reset()


def show_cursor():
    cancel_cursor_hide_timer()
    win.config(cursor='arrow')


def hide_cursor():
    win.config(cursor='none')


def cursor_hide_call():
    if player.get_state() in (3, 4):
        hide_cursor()
    else:
        show_cursor()


def cancel_cursor_hide_timer():
    global cursor_hide_timer

    if cursor_hide_timer:
        win.after_cancel(cursor_hide_timer)
        cursor_hide_timer = None


def reset_cursor_hide_timer():
    global cursor_hide_timer

    cancel_cursor_hide_timer()
    cursor_hide_timer = win.after(Ui.autohide_cursor_ms, cursor_hide_call)


# def show_playback_notification(msg):
#     SnackBar(master=win, msg=msg, height=30, show_cancel=False, undock_time=1000)


def double_click_handler(event=None):
    if _mouse_gestures.get() == 1:
        if event.x < win_width.v * .1:
            backward(True)
        elif event.x > win_width.v * .9:
            forward(True)
        else:
            toggle_fullscreen()
    else:
        toggle_fullscreen()


def left_click_handler(event=None):
    SubUi.destroy_instance()


def right_click_handler(event):
    if _mouse_gestures.get() == 1 and player.get_state() in (3, 4):
        _p_pos = player.get_position()
        if _fullscreen.v:
            fsdock.dock(reset_timer=False)
            fsdock.set_scale = False
            __dock = 1
            __xoff = fsdock.calculate_mscale_x_screen_offset()
            __pre_y = fsdock.y
            __pre_x = fsdock.m_scale.get_x_from_value(_p_pos * 100)
        else:
            dock.dock()
            dock.d_timer_cancel()
            dock.auto_media_scale = False
            __dock = 0
            __xoff = dock.calculate_mscale_x()
            __pre_y = win_height.v - Ui.dock_h
            __pre_x = dock.media_scale.get_x_from_value(_p_pos * 100)

        if PreDisplay.m_path:
            __in = PreDisplay.Instance
            if isinstance(__in, (PreDisplay,)):
                __in.xoff = __xoff
                PreDisplay.Instance.dock(_p_pos, __pre_x, __pre_y)
            else:
                PreDisplay(win, _p_pos, __pre_x, __pre_y, xoff=__xoff, yoff=10)
        _m_drag_cache.v = _p_pos, event.x, __dock  # in form (pos, mouse_x fpr calibaration, dock in action )
    else:
        _m_drag_cache.v = -1


def right_drag_handler(event):
    # mouse motion with click
    if _m_drag_cache.v != -1:
        _new = _m_drag_cache.v[0] + ((event.x - _m_drag_cache.v[1]) / win_width.v)
        _new_per = _new * 100
        __dock = _m_drag_cache.v[2]
        if __dock == 1:
            fsdock.m_scale.set(_new_per)
            __x = fsdock.m_scale.get_x_from_value(_new_per)
        else:
            dock.media_scale.set(_new_per)
            __x = dock.media_scale.get_x_from_value(_new_per)
        if PreDisplay.m_path:
            PreDisplay.Instance.config_(_new, event_x=__x)
        _m_drag_cache.v = _new, event.x, __dock


def motion_handler(event):
    # mouse motion without click
    if _fullscreen.v:
        set_fs_dock(event)
    else:
        set_m_dock(event)
    show_cursor()


def right_release_handler(event):
    if _m_drag_cache.v != -1:
        player.set_position(_m_drag_cache.v[0])
        if _m_drag_cache.v[2] == 1:
            fsdock.set_scale = True
            fsdock.d_timer_reset()
        else:
            dock.auto_media_scale = True
            dock.d_timer_reset()
        if PreDisplay.m_path:
            PreDisplay.Instance.un_dock()
        _m_drag_cache.v = -1


system_on = RcBool(True)

mpast_ = load(C.past_file, C.default_past_info)
settings_ = load(C.settings_file, C.default_settings)
playback_dict = load(C.playback_file, {})  # to save playback of media
bindings_dict = load(C.bindings_file, BinDings.default_bindings, BinDings.default_bindings)

_play_count = RcInt(mpast_['play_count'])

_next = RcBool(False)  # F for ideal and T for executing operation
_previous = RcBool(False)  # F for ideal and T for executing operation
_stop = RcBool(False)

_main_menu = RcBool(True)
_fullscreen = RcBool(False)

_set_by_slider = RcBool(False)
_set_a_by_slider = RcBool(False)

default_vol_rate = RcInt(settings_['vol_rate'])  # in vol units... loaded by setting config.......................
default_seek_rate = RcInt(settings_['seek_rate'])  # in secs...# loaded by setting config.......................
max_volume = RcInt(settings_['max_volume'])  # loaded by setting config................................
current_vol = RcInt(settings_['current_vol'])  # loaded by setting config...................
refresh_time_ms = RcInt(settings_['refresh_time'])  # loaded by setting config...................
_full_time_info = RcStr('Show Remaining Media Length', 'Show Full Media Length', key_var=settings_['fulltime_state'])
_m_drag_cache = RcInt(-1)
aspect_ratio_index = RcInt()

controller_coordinates = RcVar(settings_['controller_coords'])

"""
....................................... WINDOW initialise and attributse.....................................
"""

win = Tk()

screen_width, screen_height = win.winfo_screenwidth(), win.winfo_screenheight()
win_width, win_height = RcInt(screen_width / 1.5), RcInt(screen_height / 1.5)
print(f'screen width : {screen_width},screen height : {screen_height}')

win.geometry(
    f'{win_width.v}x{win_height.v}+{round((screen_width - win_width.v) / 2)}+{round((screen_height - win_height.v) / 2)}')
win.minsize(int(screen_width / 3), PreDisplay._size[1] + Ui.dock_h + 20)
win.title(C.WinTitle)
win.protocol('WM_DELETE_WINDOW', exit_diag)
win.resizable(1, 1)

# images
_play_image = PIL.Image.open(os.path.join(C.icons_dir, 'play_dark.png'))  # main raw play image
play_image = PIL.ImageTk.PhotoImage(_play_image)
play_image_c = PIL.ImageTk.PhotoImage(
    _play_image.resize((Controller.im_dim, Controller.im_dim), PIL.Image.ANTIALIAS))  # play image for controller

_pause_image = PIL.Image.open(os.path.join(C.icons_dir, 'pause_dark.png'))  # main raw pause image
pause_image = PIL.ImageTk.PhotoImage(_pause_image)
pause_image_c = PIL.ImageTk.PhotoImage(
    _pause_image.resize((Controller.im_dim, Controller.im_dim), PIL.Image.ANTIALIAS))  # pause image for controller

_previous_image = PIL.Image.open(os.path.join(C.icons_dir, 'previous_dark.png'))  # main raw previous image
previous_image = PIL.ImageTk.PhotoImage(_previous_image)
previous_image_c = PIL.ImageTk.PhotoImage(_previous_image.resize((Controller.im_dim, Controller.im_dim),
                                                                 PIL.Image.ANTIALIAS))  # previous image for controller

_next_image = PIL.Image.open(os.path.join(C.icons_dir, 'next_dark.png'))  # main raw next image
next_image = PIL.ImageTk.PhotoImage(_next_image)
next_image_c = PIL.ImageTk.PhotoImage(
    _next_image.resize((Controller.im_dim, Controller.im_dim), PIL.Image.ANTIALIAS))  # next image for controller

_stop_image = PIL.Image.open(os.path.join(C.icons_dir, 'stop_dark.png'))  # main raw stop image
stop_image = PIL.ImageTk.PhotoImage(_stop_image)
stop_image_c = PIL.ImageTk.PhotoImage(
    _stop_image.resize((Controller.im_dim, Controller.im_dim), PIL.Image.ANTIALIAS))  # stop image for controller

# menu images
playi = PhotoImage(file=os.path.join(C.icons_dir, 'play_menu.png'))
pausei = PhotoImage(file=os.path.join(C.icons_dir, 'pause_menu.png'))
stopi = PhotoImage(file=os.path.join(C.icons_dir, 'stop_menu.png'))
mutei = PhotoImage(file=os.path.join(C.icons_dir, 'mute_menu.png'))
unmutei = PhotoImage(file=os.path.join(C.icons_dir, 'unmute_menu.png'))

# .................................... settings | that depend upon tkinter vars | configurations........................
load_on_start = IntVar(win, settings_['load_on_start'])  # auto load on start var
control_win_check = IntVar(win, settings_['controller'])  # to check controller stste_
_auto_play = IntVar(win, settings_['auto_play'])  # to check _auto_play stste_
save_pos = IntVar(win,
                  settings_['save_pos'])  # to check playback save while stop() function # loaded by setting config.....
exit_check = IntVar(win, settings_['exit_check'])  # loaded by setting config...................
_mouse_gestures = IntVar(win, settings_['mouse_gestures'])
scan_sub_on_load = IntVar(win, settings_['scan_sub'])  # loaded by setting config...................
_parallel_run_var = BooleanVar(win, _parallel_run_enabled)
_parallel_run_var.trace_add(('write', 'unset'), lambda *args: C.save_parallel_run_enabled(_parallel_run_var.get()))

# ......................................................................................................................
win.iconbitmap(C.app_icon_file)
menubar = Menu(win, bg='black', fg='black')
empty_menu = Menu(win)

# file
file = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
file.add_command(label="Open File/Files", command=openfile, font=Ui.menu_font)
file.add_command(label="Scan Folder", command=scan_folder_ui, font=Ui.menu_font)
file.add_command(label="Save As", command=_save_as_, font=Ui.menu_font)
file.add_separator()
file.add_command(label='Load Recents', command=load_past, font=Ui.menu_font)
file.add_command(label='Network Stream', command=stream_, font=Ui.menu_font)
file.add_separator()
file.add_command(label="Exit", command=exit_diag, font=Ui.menu_font)

menubar.add_cascade(label="File", menu=file, font=Ui.menu_font_cascade)
# playback
_playback_menu_ = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
_playback_menu_.add_command(label="Set speed", command=set_playback_speed, font=Ui.menu_font)
_playback_menu_.add_separator()
_playback_menu_.add_command(label="forward", command=forward, font=Ui.menu_font)
_playback_menu_.add_command(label="backward", command=backward, font=Ui.menu_font)
_playback_menu_.add_command(label="jump to time", command=setspecifictime, font=Ui.menu_font)
_playback_menu_.add_separator()
_playback_menu_.add_command(label="Shuffle", command=shuffle, font=Ui.menu_font)
_playback_menu_.add_command(label="Previous", command=previous_call, font=Ui.menu_font)
_playback_menu_.add_command(label="Next", command=next_call, font=Ui.menu_font)
_playback_menu_.add_separator()
_playback_menu_.add_command(label="Play", command=count, image=playi, compound=LEFT, font=Ui.menu_font)
_playback_menu_.add_command(label="Pause", command=pause, image=pausei, compound=LEFT, font=Ui.menu_font)

menubar.add_cascade(label="playback", menu=_playback_menu_, font=Ui.menu_font_cascade)

# playlist menu
_playlist_menu_ = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
_playlist_menu_.add_command(label="Show Playlist", command=toggle_playlist, font=Ui.menu_font)
_playlist_menu_.add_separator()
_playlist_menu_.add_command(label="Add media", command=openfile, font=Ui.menu_font)
_playlist_menu_.add_command(label='Load playlists', command=load_playlist, font=Ui.menu_font)
menubar.add_cascade(label="Playlist", menu=_playlist_menu_, font=Ui.menu_font_cascade)

audio_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
audio_track = Menu(audio_menu, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
audio_menu.add_cascade(label='Audio Track', menu=audio_track, font=Ui.menu_font_cascade)
audio_menu.add_separator()
audio_menu.add_command(label='      Mute', command=mute, image=mutei, compound=LEFT, font=Ui.menu_font)
menubar.add_cascade(label='Audio', menu=audio_menu, font=Ui.menu_font_cascade)

video_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
menubar.add_cascade(label='Video', menu=video_menu, font=Ui.menu_font_cascade)

sub_menu = Menu(video_menu, activebackground="skyblue", tearoff=0, bg='white', activeforeground='black')
video_menu.add_cascade(label='Subtitles', menu=sub_menu, state=DISABLED, font=Ui.menu_font_cascade)
sub_menu.add_command(label='Disable', command=disable_sub, font=Ui.menu_font)

video_menu.add_command(label='Add Subtitle', command=add_sub, font=Ui.menu_font)
video_menu.add_command(label='Scan Subtitles', command=auto_scan_sub, font=Ui.menu_font)
video_menu.add_separator()
video_menu.add_command(label='Subtitle Delay', command=set_spu_delay, state=DISABLED, font=Ui.menu_font)
video_menu.add_separator()
video_menu.add_command(label='Fullscreen', command=toggle_fullscreen, font=Ui.menu_font)
aspect_menu = Menu(video_menu, activebackground="skyblue", tearoff=0, bg='white')
video_menu.add_cascade(label='Aspect Ratio', menu=aspect_menu, state=DISABLED, font=Ui.menu_font_cascade)
aspect_menu.add_command(label='Set Aspect Ratio', command=set_aspect_ratio, font=Ui.menu_font)
aspect_menu.add_separator()

for asp in C.aspect_ratio_list:
    aspect_menu.add_radiobutton(label=Ui.format_aspect(asp), command=lambda arg=asp: _set_aspect(arg), font=Ui.menu_font)
video_menu.add_separator()
video_menu.add_command(label='Screenshot', command=screenshot, state=DISABLED, font=Ui.menu_font)

settings_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
menubar.add_cascade(label="Settings", menu=settings_menu, font=Ui.menu_font_cascade)

playback_settings_menu = Menu(settings_menu, activebackground='skyblue', activeforeground='black', tearoff=0,
                              bg='white')
settings_menu.add_cascade(label='Playback settings', menu=playback_settings_menu, font=Ui.menu_font_cascade)

playback_settings_menu.add_command(label='Playback Seek Rate', command=set_playback_seek_rate, font=Ui.menu_font)
playback_settings_menu.add_command(label='Volume Seek Rate', command=set_vol_seek_rate, font=Ui.menu_font)
playback_settings_menu.add_command(label='Maximum Volume', command=set_max_volume, font=Ui.menu_font)
playback_settings_menu.add_command(label=_full_time_info.get_keyv(), command=toggle_fulltime_state, font=Ui.menu_font)
playback_settings_menu.add_checkbutton(label='Control Playback with Mouse', variable=_mouse_gestures, onvalue=1,
                                       offvalue=0, font=Ui.menu_font)
playback_settings_menu.add_separator()
playback_settings_menu.add_checkbutton(label='Auto load on startup', onvalue=1, offvalue=0, variable=load_on_start,
                                       font=Ui.menu_font)
playback_settings_menu.add_checkbutton(label='Autoplay', onvalue=1, offvalue=0, variable=_auto_play, font=Ui.menu_font)
playback_settings_menu.add_checkbutton(label='Show controller when minimized', onvalue=1, offvalue=0,
                                       variable=control_win_check, font=Ui.menu_font)
playback_settings_menu.add_checkbutton(label='Save playback', onvalue=1, offvalue=0, variable=save_pos,
                                       font=Ui.menu_font)
playback_settings_menu.add_separator()
playback_settings_menu.add_checkbutton(label='Scan subtitles automatically', onvalue=1, offvalue=0,
                                       variable=scan_sub_on_load, font=Ui.menu_font)

settings_menu.add_separator()
settings_menu.add_command(label='Refresh rate of Ui', command=set_refresh_rate, font=Ui.menu_font)
settings_menu.add_command(label='Keyboard Bindings', command=change_bindings, font=Ui.menu_font)
settings_menu.add_checkbutton(label='Parallel Run', font=Ui.menu_font, onvalue=True, offvalue=False, variable=_parallel_run_var)
settings_menu.add_checkbutton(label='Confirm on Exit', onvalue=1, offvalue=0, variable=exit_check, font=Ui.menu_font)
settings_menu.add_separator()
settings_menu.add_command(label='Reset default', command=reset_default_settings, font=Ui.menu_font)

about_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0, bg='white')
menubar.add_cascade(label='About', menu=about_menu, font=Ui.menu_font_cascade)


def copy_to_clipboard(label: str, text: str, append: bool = False):
    U.copy_to_clipboard(win, text, append=append)
    SnackBar.show_msg_copied_to_clipboard(win, label=label)

for label, val in (('Description', C.Description),
                   ('Version', C.Version),
                   ('Author', C.Author),
                   ('Contact', C.ContactEmail)):
    about_menu.add_command(label=f'{label}: {val}', font=Ui.menu_font,
                           command=lambda l=label, v=val: copy_to_clipboard(l, v))

# about_menu.add_command(label=f'Description: {C.Description}', font=Ui.menu_font_des, command=lambda a='Description', b=C.Description: copy_to_clipboard(a, b))
# about_menu.add_command(label=f'Version: {C.Version}', font=Ui.menu_font, command=lambda a='Version', b=C.Version: copy_to_clipboard(a, b))
# about_menu.add_command(label=f'Author: {C.Author}', font=Ui.menu_font)
# about_menu.add_command(label=f'Contact: {C.ContactEmail}', font=Ui.menu_font, command=lambda a='Contact', b=C.ContactEmail: copy_to_clipboard(a, b))
about_menu.add_separator()
about_menu.add_command(label='Update', command=update_call, font=Ui.menu_font)

# ................................WIDGETS..................................
""" MAIN VIDEO OUTPUT RENDERER CANVAS and mouse events """
_video_canvas_ = Canvas(win, width=win_width.v, height=win_height.v - Ui.dock_h, bg=rgb(10, 10, 10), bd=0,
                        highlightthickness=0)
player.set_hwnd(_video_canvas_.winfo_id())
player.video_set_mouse_input(False)
player.video_set_key_input(False)
player.video_set_marquee_int(0, 1)

""" Instances of main classes """
dock = Dock(win, win_width_var=win_width, bg='black')  # Dock instance
fsdock = FsDock(master=win, player_=player)
playlist_win = PlayWin(master=win, title='Playlist', size=Ui.playwin_size,
                       pos=(screen_width - Ui.playwin_w - 10, screen_height - Ui.playwin_h - 60))

# main window widgets placing
_video_canvas_.place(x=0, y=0, relwidth=1, relheight=1)  # placing video canvas
dock.place(x=0, rely=1, anchor='sw', relwidth=1)  # since it initialise with 1 pix height and state == 0

# theme
win['bg'] = rgb(30, 30, 30)
win['menu'] = menubar if _main_menu.v else empty_menu

# ....................................< BINDINGS >..................................
_video_canvas_.bind('<Button-1>', left_click_handler)
_video_canvas_.bind('<Button-3>', right_click_handler)  # for preview display init
_video_canvas_.bind('<B3-Motion>', right_drag_handler)  # for preview display calibration
_video_canvas_.bind('<ButtonRelease-3>', right_release_handler)  # for preview display release

_video_canvas_.bind('<Double-Button-1>', double_click_handler)  # for full screen toggle or mouse gestures
_video_canvas_.bind('<Motion>', motion_handler)  # for setting dock

dock.bind('<Motion>', motion_handler)  # binding dock to mouse motion call of dock itself

for _n, _seq in chain(bindings_dict['playback'].items(), bindings_dict['win'].items()):
    win.bind(_seq, wrap_event_call(SetName.func_dic[_n]))

sys_load()  # loading on Startup
__main_ui__()  # initializing custom ui loop

win.mainloop()  # main event loop
