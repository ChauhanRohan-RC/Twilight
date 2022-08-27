import main_player
from backup.filemanager import FileManager
import os
import os.path
from tkinter import *
from tkinter import filedialog
from threading import Thread

# ...................MAIN FILEMANAGER..........................

if getattr(sys, 'frozen', False):
    main_dir = os.path.dirname(sys.executable)
else:
    main_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, 'sdk')
icons_dir = os.path.join(sdk_dir, 'icons')

past_file = os.path.join(sdk_dir, 'mpast.cc')
play_file = os.path.join(sdk_dir, 'mplay.cc')

fm = FileManager()
fmpast = FileManager(past_file)
fmplay = FileManager(play_file)

platform = fm.platform()
if platform == 'win':
    initialdir = 'C;//'
else:
    initialdir = '/'


# ................................................................................

# vlc init
vlc_in = main_player.Instance()
player = vlc_in.media_player_new()

# .................................STATIC  FUNCTIONS...............................

# Static vars
default_seek_rate = 10  # in secs
default_vol_rate = 10  # in range of 0 - max_volume
max_volume = 200


def rgb(RGB):
    return '#%02x%02x%02x' % RGB


class RcScale(Scale):
    def __init__(self, master, **kwargs):
        Scale.__init__(self, master=master, **kwargs)

    def get_value_from_x(self, x, range_=100):
        x0, y0 = self.coords(0)
        x1, y1 = self.coords(100)

        pix = x1 - x0
        pix_per_value = pix / range_

        return (x - x0) / pix_per_value

    def find(self, x, y):
        return self.identify(x, y)


class Win(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)

        self.resizable(1, 1)
        self.sw, self.sh = self.s_info()
        self.geometry(f"{round(self.sw * .75)}x{round(self.sh * .75)}")
        self.minsize(width=round(self.sw * .25), height=round(self.sh * .25))
        self.protocol('WM_DELETE_WINDOW', self.exit_)

        # ............................. MENU........................
        self.menubar = Menu(self)
        self.file = Menu(self.menubar, tearoff=0, bd=1, activebackground='skyblue', activeborderwidth=2)

        # .............................RESIZING VARS................
        self.resize_ = False
        self.rwidth = None
        self.rheight = None

        # .................................Images..........................
        self.icon = os.path.join(icons_dir, 'play_light.png')
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=self.icon))

        self.playi = PhotoImage(file=os.path.join(icons_dir, 'play_light.png'))
        self.pausei = PhotoImage(file=os.path.join(icons_dir, 'pause_light.png'))
        self.previousi = PhotoImage(file=os.path.join(icons_dir, 'previous_light.png'))
        self.nexti = PhotoImage(file=os.path.join(icons_dir, 'next_light.png'))
        self.stopi = PhotoImage(file=os.path.join(icons_dir, 'stop_light.png'))
        self.im_dim = 32

        self.dockh = 65
        self.displayh = self.w_info()[1] - self.dockh

        self.dock = Frame(self, width=self.winfo_width(), height=self.dockh, bg='white')
        self.canvas = Canvas(self, width=self.winfo_width(), height=self.displayh, bg='black')

        # ................................ Dock WIDGETS..........................................
        self.play_b = Button(self.dock, bg='white', image=self.playi, activebackground='white', command=self.force)
        self.stop_b = Button(self.dock, bg='white', image=self.stopi, activebackground='white', command=self.stop)
        self.previous_b = Button(self.dock, bg='white', image=self.previousi, activebackground='white',
                                 command=self.previous)
        self.next_b = Button(self.dock, bg='white', image=self.nexti, activebackground='white', command=self.next)

        self.ctime = Label(self.dock, text="--:--:--", font='timesnewroman 10 italic')
        self.ftime = Label(self.dock, text="--:--:--", font='timesnewroman 10 italic')

        self.mediascale = RcScale(self.dock, from_=0, to=100, orient=HORIZONTAL, length=self.w_info()[0] - 100,
                                  showvalue=0,
                                  width=10,
                                  sliderlength=20,
                                  resolution=.0001)

        # ............................... PLAY DATA..................
        self.mediapath = []
        self.medianame = []

        self.video_format = ['.mp4', '.mkv', '.mpeg', '.avi', '.mov']
        self.audio_format = ['.mp3', '.m4a', '.wav', '.ogg']
        self.all_format = self.video_format + self.audio_format

        # ...... PLAYBACK VARS...
        self.playcount = 0
        self.firstopen = False

        self.busy = False
        self.delay = 400  # in milli seconds
        self.do_next = False
        self.do_previous = False

        self.autoplay = True  # Auto Play by default
        self.setmscale = True  # config media scale continously
        self.setm_by_s = True  # setting mediascale by slider

        # volume
        self.default_vol = 70
        self.current_vol = self.default_vol

        # ...................... Executing All functions .............
        self.center(self)
        self.place(self.w_info()[0])
        self.main_menu()
        self.set_screen()

        self.mainthread()  # also contain __check_resize__ thraed ,loop after every 5 millisecs

        self.set_theme()
        self.load()  # auto load on startup
        # ............................ BINDINGS ................
        self.bind('<Configure>', self.resize)

        # playback bindings
        self.bind('<Alt-Right>', self.next)
        self.bind('<Alt-Left>', self.previous)
        self.bind('<Escape>', self.stop)
        self.bind('<space>', self.force)
        self.bind('<Control-Right>', self.forward)
        self.bind('<Control-Left>', self.backward)
        self.bind('<Control-Up>', self.volin)
        self.bind('<Control-Down>', self.voldec)

        # mediascale bindings
        self.mediascale.bind('<Button-1>', self.stopset_m)
        self.mediascale.bind('<ButtonRelease-1>', self.setscale_m)

    # ..................................... EXIT , AND LOADING ON START....................

    def exit_(self):
        if len(self.mediapath) > 0:
            past_dic = {'paths': self.mediapath}
            fmpast.write_bytes(past_dic)

        player.release()
        self.quit()

    def load(self):
        if fmpast.exists():
            past_dic = fmpast.read_bytes()
            paths_past = past_dic['paths']
            paths_past = self.check_media(paths_past)
            if paths_past is not None:
                if len(self.mediapath) == 0:
                    self.firstopen = True
                else:
                    self.firstopen = False
                for p in paths_past:
                    self.mediapath.append(p)
                    self.medianame.append(fm.dir_name(p)[1])

                if self.firstopen:
                    self.playcount = 0
                    self.force()

    # ..................................... LOAD MEDIA .........................

    def check_media(self, paths):
        cpaths = []
        for path in paths:
            if fm.name_ex(path)[1].lower() in self.all_format:
                if path not in self.mediapath:
                    if fm.dir_name(path)[1] not in self.medianame:
                        cpaths.append(path)

        if cpaths:
            return cpaths
        return None

    def open(self):

        paths = filedialog.askopenfilenames(initialdir=initialdir,
                                            filetypes=(('Media Files', '*.mp3 *.mp4 *.mkv *.MP3'
                                                                       ' *.MP4 *.MKV *.ogg '
                                                                       '*.wav *.mpeg'),
                                                       ('All Files', '*')),
                                            title='Open Media Files')
        if paths:
            paths = self.check_media(paths)
            if paths is not None:
                if len(self.mediapath) == 0:
                    self.firstopen = True
                else:
                    self.firstopen = False
                for path in paths:
                    self.mediapath.append(path)
                    self.medianame.append(fm.dir_name(path)[1])

                if self.firstopen:
                    self.playcount = 0
                    self.force()

    def scan_dir(self):
        dir_ = filedialog.askdirectory(initialdir=initialdir,
                                       title='Scan Media Files in a Directory')
        if dir_:
            def scan():
                paths, names = fm.scan(self.all_format, start=dir_, mode='dono')

                paths = self.check_media(paths)
                if paths is not None:
                    if len(self.mediapath) == 0:
                        self.firstopen = True
                    else:
                        self.firstopen = False
                    for path in paths:
                        self.mediapath.append(path)
                        self.medianame.append(fm.dir_name(path)[1])

                    if self.firstopen:
                        self.playcount = 0
                        self.force()

            scan_thread = Thread(target=scan)
            scan_thread.start()

    # ............................... PLAY FUNCTIONS ....................
    def force(self, event=None):
        if self.mediapath:
            media = vlc_in.media_new(self.mediapath[self.playcount])
            player.set_media(media)
            player.play()
            self.set()

    def play(self, count):
        if len(self.mediapath) != 0:
            try:

                if count >= len(self.mediapath):
                    count = 0
                elif count < 0:
                    count = len(self.mediapath) + count

                media = vlc_in.media_new(self.mediapath[count])
                player.set_media(media)
                player.play()
                self.playcount = count

                self.set()

            except Exception as e:
                print(e, f'in play with count : {count}')

    def set(self):  # with every play function
        try:
            self.play_b['image'] = self.pausei
            self.bind('<space>', self.pause)
            self.play_b['command'] = self.pause

            self.mediascale['state_'] = NORMAL

            player.audio_set_volume(self.current_vol)
            if platform == 'win':
                self.after(10, self.set_fulltime)
            else:
                self.after(400, self.set_fulltime)  # takes time to calculate full time in linux and mac
        except Exception as e:
            print(e, 'set')

    def set_fulltime(self):
        fsecs = player.get_length()
        min_, sec = fm.mills_to_time(fsecs)

        if len(str(min_)) < 2:
            min_ = f'0{min_}'
            hr = '00'

        else:
            if min_ > 60:
                hr = min_ // 60
                min_ = min_ % 60
            else:
                hr = '00'

        if len(str(sec)) == 1:
            sec = f'0{sec}'

        if int(hr):
            self.ftime['text'] = f'{hr}:{min_}:{sec}'
        else:
            self.ftime['text'] = f'{min_}:{sec}'

    def pause(self, event=None):
        if player.get_state() == 3:  # Playing
            self.play_b['image'] = self.playi
            player.pause()

        elif player.get_state() == 4:  # Paused
            self.play_b['image'] = self.pausei
            player.pause()

    # ...............................PLAYBACK FUNCTIONS...................
    def next(self, event=None):
        if not self.busy:
            self.stop()
            self.do_next = True

    def previous(self, event=None):
        if not self.busy:
            self.stop()
            self.do_previous = True

    def forward(self, event=None):
        if player.get_state() in (3, 4):
            if event:
                ctime = player.get_time()
                ntime = ctime + default_seek_rate * 1000
                player.set_time(ntime)

    def backward(self, event=None):
        if player.get_state() in (3, 4):
            if event:
                ctime = player.get_time()
                if ctime > default_seek_rate * 1000:
                    ntime = ctime - default_seek_rate * 1000
                    player.set_time(ntime)

    def volin(self, event=None):
        if event:
            if max_volume - self.current_vol >= default_vol_rate:
                self.current_vol += default_vol_rate
            else:
                self.current_vol = max_volume
            if player.get_state() in (3, 4):
                player.audio_set_volume(self.current_vol)

            print(self.current_vol)

    def voldec(self, event=None):
        if event:
            if self.current_vol >= default_vol_rate:
                self.current_vol -= default_vol_rate
            else:
                self.current_vol = 0
            if player.get_state() in (3, 4):
                player.audio_set_volume(self.current_vol)

            print(self.current_vol)

    def revoke_busy(self):
        def f():
            self.busy = False

        if self.busy:
            self.after(self.delay, f)

    def stop(self, event=None):
        self.play_b['image'] = self.playi
        self.bind('<space>', self.force)
        self.play_b['command'] = self.force
        player.stop()

        self.ctime['text'] = '--:--:--'
        self.ftime['text'] = '--:--:--'

        self.mediascale.set(0)

    # ................main place function......................

    def place(self, width, padx=10, pady=10):
        height = self.dockh
        self.dock.pack(fill=X, expand='yes', anchor=SW, side=BOTTOM)
        self.canvas.pack(fill=X, expand='yes', anchor=NW, side=TOP)

        # .......................... Dock Widgets ...................
        self.stop_b.place(x=padx, y=height - self.im_dim - pady / 2)
        self.previous_b.place(x=round((width / 2) - (self.im_dim * 1.5)) - padx, y=height - self.im_dim - pady / 2)
        self.play_b.place(x=round((width - self.im_dim) / 2), y=height - self.im_dim - pady / 2)
        self.next_b.place(x=round((width + self.im_dim) / 2) + padx, y=height - self.im_dim - pady / 2)

        self.ctime.place(x=5, y=(pady / 2) - 2)
        self.ftime.place(x=width - 43, y=(pady / 2) - 2)

        self.mediascale.place(x=50, y=pady / 2)

    # ......... configuring dock according to width of window.......................

    def placeconfig_w(self, width, padx=10):
        self.play_b.place_configure(x=round((width - self.im_dim) / 2))
        self.previous_b.place_configure(x=round((width / 2) - (self.im_dim * 1.5)) - padx)
        self.next_b.place_configure(x=round((width + self.im_dim) / 2) + padx)

        self.mediascale['length'] = width - 100
        self.ftime.place_configure(x=width - 43)

    def main_menu(self):
        # ............................... MENU .......................................

        self.menubar.add_cascade(label='File', menu=self.file)
        self.file.add_command(label='Open File/Files', command=self.open)
        self.file.add_command(label='Scan Folder', command=self.scan_dir)
        self.file.add_command(label='Load Recents', command=self.load)
        self.file.add_checkbutton(label='Auto load on startup')
        self.file.add_separator()
        self.file.add_command(label='Network Stream')
        self.file.add_separator()
        self.file.add_command(label='Exit')

        self.configure(menu=self.menubar)

    def center(self, window):
        self.update_idletasks()
        window.update_idletasks()
        sw, sh = self.s_info()
        ww, wh = window.winfo_width(), window.winfo_height()
        window.geometry(f'+{round((sw - ww) / 2)}+{round((sh - wh) / 2)}')

    def w_info(self):
        self.update_idletasks()
        w_width, w_height = self.winfo_width(), self.winfo_height()
        return w_width, w_height

    def s_info(self):
        self.update_idletasks()
        s_width, s_height = self.winfo_screenwidth(), self.winfo_screenheight()
        return s_width, s_height

    def set_screen(self):
        if sys.platform.startswith('win'):
            player.set_hwnd(self.canvas.winfo_id())
        else:
            player.set_xwindow(self.canvas.winfo_id())

    def stopset_m(self, event):
        part = self.mediascale.find(event.x, event.y)  # part of mscale under mouse focus
        if part == 'slider':
            self.setm_by_s = True
        else:
            self.setm_by_s = False
        self.setmscale = False

    def setscale_m(self, event):
        if player.get_state() in (3, 4):
            if self.setm_by_s:  # for slider click
                player.set_position(self.mediascale.get() / 100)

            else:  # for click on trough
                value = self.mediascale.get_value_from_x(event.x)
                player.set_position(value / 100)

            self.setmscale = True

        else:
            self.mediascale.set(0)

    def mainthread(self):
        state = player.get_state()

        if state == 3:  # Playing
            # configuring time labels
            min_, sec = fm.mills_to_time(player.get_time())
            if len(str(min_)) < 2:
                min_ = f'0{min_}'
                hr = '00'

            else:
                if min_ > 60:
                    hr = min_ // 60
                    min_ = min_ % 60
                else:
                    hr = '00'

            if len(str(sec)) == 1:
                sec = f'0{sec}'

            if int(hr):
                self.ctime['text'] = f'{hr}:{min_}:{sec}'
            else:
                self.ctime['text'] = f'{min_}:{sec}'

            # configuring mediascale
            if self.setmscale:
                pos = player.get_position()
                self.mediascale.set(pos * 100)

        if state == 5:  # Stopped
            if self.do_next:
                self.busy = True
                self.play(count=self.playcount + 1)
                self.do_next = False
                self.revoke_busy()

            if self.do_previous:
                self.busy = True
                self.play(count=self.playcount - 1)
                self.do_previous = False
                self.revoke_busy()

        if state == 6:  # Ended
            if self.autoplay:
                self.next()

        self.resizethread()

        self.after(10, self.mainthread)

    def resizethread(self):
        if self.resize_:
            w, h = self.w_info()
            self.canvas['height'] = h - self.dockh
            self.placeconfig_w(w)

        # self.after(5, self.resizethread)

    def resize(self, event=None):
        if event.widget == self:
            if self.rwidth != event.width or self.rheight != event.height:
                self.resize_ = True
                self.rwidth, self.rheight = event.width, event.height
            else:
                self.resize_ = False

    def set_theme(self):
        #   ....................... reliefs and texture................
        self.play_b['relief'] = 'flat'
        self.previous_b['relief'] = 'flat'
        self.next_b['relief'] = 'flat'
        self.stop_b['relief'] = 'flat'

        self.play_b['bd'] = 0
        self.play_b['highlightthickness'] = 0
        self.previous_b['bd'] = 0
        self.previous_b['highlightthickness'] = 0
        self.next_b['bd'] = 0
        self.next_b['highlightthickness'] = 0
        self.stop_b['bd'] = 0
        self.stop_b['highlightthickness'] = 0

        self.mediascale['bd'] = 2
        self.mediascale['relief'] = 'flat'

        self.ctime['relief'] = 'flat'
        self.ftime['relief'] = 'flat'

        # .........................COLORS.................
        self['bg'] = 'black'
        self.mediascale['troughcolor'] = 'skyblue'
        self.mediascale['bg'] = 'white'
        self.mediascale['activebackground'] = 'lightgreen'

        self.ctime['bg'] = 'white'
        self.ftime['bg'] = 'white'


win = Win()
win['bg'] = 'black'
win.mainloop()
