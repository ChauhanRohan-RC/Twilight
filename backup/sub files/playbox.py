from tkinter import *
import os
import PIL.Image, PIL.ImageTk
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from io import BytesIO
from backup.filemanager import format_mills, rgb

main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, 'sdk')
icons_dir = os.path.join(sdk_dir, 'icons')

daim_path = os.path.join(icons_dir, 'file_audio.png')
dvim_path = os.path.join(icons_dir, 'file_video.png')

song_format = {'.wav', '.3ga', '.669', '.a52', '.aac', '.ac3', '.adt', '.adts', '.aif', '.aif', '.aifc', '.aiff',
               '.amr', '.aob', '.ape', '.awb', 'caf', '.dts', '.flac', '.it', '.m4a', '.kar', '.m4b', '.m4p', '.m5p',
               '.mid', '.mka', '.mlp', '.mod', '.mpa', '.mp1', '.mp2', '.mp3', '.mpc ', '.ogg', '.oga', '.mus', '.mpga'}

video_format = {'.mp4', '.vob', '.mkv', '.mkv', '.3g2', '.3gp', '.3gp2', '.3gpp', '.amv', '.asf', '.avi',
                '.bik', '.bin', '.divx', '.drc', '.dv', '.f4v', '.flv ', '.gvi', '.gfx', '.iso', '.m1v,', '.m2v',
                '.m2t', '.m2ts', '.m4v', '.mov', '.mp2', '.mp2v', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg2',
                '.mpeg4', '.mpg', '.gif', '.webm'}


class SlideLabel(Label):
    _id = 2
    __name__ = 'SlideLabel'


class Slide(Frame):
    __name__ = 'Slide'
    _id = 1
    thumb_dim = (40, 35)
    height = 100
    width = 350
    active_slide = None
    dic = {}  # contains id : instances

    def __init__(self, master, m_path, bd=4, fg='black', bg='white',
                 activebg=rgb(235, 235, 235), activebd=0, **kwargs):
        self.master = master
        self.m_path = self.id = m_path
        self.fg = fg
        self.bg = bg
        self.activebg = activebg
        self.bd = bd
        self.activebd = activebd

        kwargs['width'] = self.width
        kwargs['height'] = self.height
        kwargs['bd'] = bd
        kwargs['bg'] = bg

        self.m_title, self.m_ext = os.path.splitext(os.path.basename(self.m_path))
        self.artist = 'Unknown Artist'  # only for mp3 files
        self.length = '--:--'
        self.bitrate = '-'
        self.channels = 1
        self.thumb = default_audio_image if self.m_ext in song_format else default_video_image
        self.l2_text = ''

        self.set_m_info()

        Frame.__init__(self, master=self.master, **kwargs)
        self.title_l = SlideLabel(self, relief='flat', bd=0, text=self.m_title[:round(self.width / 10)] + '...',
                                  bg=self.bg,
                                  fg=self.fg,
                                  font='Times 11 italic')
        self.artist_l = SlideLabel(self, relief='flat', bd=0, text=self.l2_text, bg=self.bg, fg=self.fg,
                                   font='comicsans 8')
        # self.create_line(4, self.height / 3 + 4, 15, self.height / 3 + 4, fill=self.fg, width=2)
        # self.create_line(4, self.height / 2 + 2, 15, self.height / 2 + 2, fill=self.fg, width=2)
        # self.create_line(4, self.height / 1.5, 15, self.height / 1.5, fill=self.fg, width=2)

        self.image_l = SlideLabel(self, image=self.thumb, bg='white', bd=0)
        self.image_l.place(x=20, y=int((self.height - Slide.thumb_dim[1]) / 2))

        self.title_l.place(x=Slide.thumb_dim[0] + 30, y=int(self.height / 6))
        self.artist_l.place(x=Slide.thumb_dim[0] + 30, y=round(self.height / 2))

        self.__class__.dic[self.id] = self

    def activate(self):
        self['bd'] = self.activebd
        self.set_bg(self.activebg)
        self.focus_force()
        self.__class__.active_slide = self

    def deactivate(self):
        if self.__class__.active_slide == self:
            self['bd'] = self.bd
            self.set_bg(self.bg)
            self.__class__.active_slide = None

    def __repr__(self):
        return f'Slide({self.m_path})'

    def set_bg(self, bg):
        self['bg'] = bg
        self.image_l['bg'] = bg
        self.title_l['bg'] = bg
        self.artist_l['bg'] = bg

    def __str__(self):
        return self.__repr__()

    def bind_all_(self, seq, call):
        self.bind(seq, call)
        self.title_l.bind(seq, call)
        self.artist_l.bind(seq, call)
        self.image_l.bind(seq, call)

    def set_m_info(self):
        try:
            if self.m_ext == '.mp3':
                _audio = MP3(self.m_path)
                _info, _tags = _audio.info, _audio.tags

                if 'TIT2' in _tags:
                    self.m_title = str(_tags['TIT2'])

                if 'TPE1' in _tags:
                    self.artist = str(_tags['TPE1'])

                self.length = format_mills(_info.length * 1000, out='str')
                self.bitrate = _info.bitrate
                self.channels = _info.channels

                for key in _tags:
                    if 'APIC' in key:
                        _image = PIL.Image.open(BytesIO(_tags[key].data))
                        _image = _image.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS)

                        self.thumb = PIL.ImageTk.PhotoImage(_image)
                        break

            elif self.m_ext == '.mp4':
                _info = MP4(self.m_path).info
                self.length, self.bitrate, self.channels = format_mills(_info.length * 1000,
                                                                        out='str'), _info.bitrate, _info.channels
        except Exception as e:
            print(e)
        finally:
            self.l2_text = f'{self.artist[:int(self.width / 10)]}.. | {self.length}' if self.m_ext in song_format else self.length


class PlayBox(Canvas):
    """
    only works for unique entries
    """

    def __init__(self, master, width=360, height=400, updatedelay=5, relheight=.1, **kwargs):
        self.master = master
        self.width = width
        Slide.width = width - 10
        self.height = height
        Slide.height = round(height * relheight)
        Slide.thumb_dim = Slide.height + 5, Slide.height - 4
        self._delay = updatedelay  # in ms
        self._busy = False

        self.LEN = 0  # len of current input
        self.END = -1  # index of last entry
        self.SELECTION = -1  # index of current selection
        # self.ids = []  # contains ids sequentially for faster search
        # self.data = []  # contains objects sequentially

        Canvas.__init__(self, master=self.master, width=self.width, height=self.height, **kwargs)
        self.frame = Frame(self, width=self.width - 10, height=self.height, **kwargs)
        self.yscroll = Scrollbar(self, orient='vertical', command=self.yview)
        self.configure(yscrollcommand=self.yscroll.set)

        self.yscroll.pack(side=RIGHT, fill=Y, expand='no', anchor='ne')
        self.frame_id = self.create_window((0, 0), window=self.frame, anchor='nw')

        # self.frame.pack(side=LEFT, expand='yes', fill='both', anchor='nw')
        # self.master.bind('<Button-1>', self.on_click)
        # self.master.bind('<B1-Motion>', self.on_drag)

    def update_scroll(self):
        self.frame['height'] = self.LEN * Slide.height

        def _update_s():
            self.configure(scrollregion=self.bbox(self.frame_id))

        self.master.after(self._delay, _update_s)

    def insert_pathseq(self, seq):
        self.clear()
        for path_ in seq:
            if path_ in Slide.dic:
                slide = Slide.dic[path_]
            else:
                slide = self.create_slide(path_)
            slide.place(x=0, y=self.LEN * Slide.height)

            self.update()  # lowers performance
            self.LEN += 1

        self.update_scroll()
        if self.LEN > 0 and self.SELECTION == -1:
            self.activate(0)

    def create_slide(self, m_path, **kwargs):
        _slide = Slide(self.frame, m_path, **kwargs)

        _slide.bind('<Up>', lambda event: self.activate(self.SELECTION - 1))
        _slide.bind('<Down>', lambda event: self.activate(self.SELECTION + 1))
        _slide.bind('<Shift-Up>', self.up)
        _slide.bind('<Shift-Down>', self.down)
        _slide.bind('<Return>', active)
        _slide.bind_all_('<Button-1>', self.on_click)
        _slide.bind_all('<Double-Button-1>', active)
        # _slide.bind_all_('<B1-Motion>', self.on_drag)
        _slide.bind_all_('<Delete>', self.pop_active)

        return _slide

    def nearest(self, y):
        """
        returns nearest index
        """
        y = self.canvasy(y)  # gives y coord wrt to canvas upper left
        if 0 <= y < self.LEN * Slide.height:
            return int(y // Slide.height)
        return self.LEN

    def get_slide(self, index):
        """
        returns (corrected index , slide) , or (None, None) in case of no slide
        """
        if self.LEN == 0:
            return None, None
        if -self.LEN <= index < self.LEN:
            if index < 0:
                index += self.LEN
            return index, Slide.dic[__media_paths__[index]]
        elif index == self.LEN:
            return 0, Slide.dic[__media_paths__[0]]
        return None, None

    def visiblebbox(self):
        return self.canvasx(0), self.canvasy(0), self.canvasx(self.width), self.canvasy(self.winfo_height())

    # def get_mpos(self):
    #     return self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty()

    def on_click(self, event):

        if Slide.active_slide:
            Slide.active_slide.deactivate()
            self.SELECTION = -1

        i = self.nearest(event.y_root - self.winfo_rooty())
        if 0 <= i < self.LEN:
            c_slide = Slide.dic[__media_paths__[i]]
            c_slide.activate()
            self.SELECTION = i
            print('selected : ', i)
            self.set_visible(i)

    def activate(self, index):

        index, c_slide_ = self.get_slide(index)
        if c_slide_:
            if Slide.active_slide:
                Slide.active_slide.deactivate()

            c_slide_.activate()
            self.SELECTION = index
            print('selected : ', index)
            self.set_visible(index)

    # def on_drag(self, event):
    #     if self._busy:
    #         print('busy < drag >')
    #         return
    #     i = int(self.canvasy(event.y_root - self.winfo_rooty()) // Slide.height)
    #     if 0 <= i < self.LEN and i != self.SELECTION:
    #         self._busy = True
    #         m_slide = Slide.active_slide
    #         s_slide = Slide.dic[__media_paths__[i]]
    #         _y = i * Slide.height
    #         m_slide.place_configure(y=_y)
    #         if i < self.SELECTION:
    #             s_slide.place_configure(y=_y + Slide.height)
    #             path_ = __media_paths__.pop(i)
    #             __media_paths__.insert(i + 1, path_)
    #
    #         else:
    #             s_slide.place_configure(y=_y - Slide.height)
    #             path_ = __media_paths__.pop(i)
    #             __media_paths__.insert(i - 1, path_)
    #         # m_slide.activate()
    #         # s_slide.deactivate()
    #         self.set_visible(i)
    #         self.SELECTION = i
    #         self.update_idletasks()
    #         self._busy = False

    def set_visible(self, index):
        y1 = index * Slide.height
        y2 = y1 + Slide.height
        vy1, vy2 = self.canvasy(0), self.canvasy(self.winfo_height())
        _height = self.LEN * Slide.height
        if vy1 < y1 < vy2 and vy1 < y2 < vy2:
            return True
        elif y1 < vy1:  # scroll down
            self.yview_moveto(y1 / _height)
        elif y2 > vy2:
            self.yview_moveto((y2 - (vy2 - vy1) + 20) / _height)
        self.update()

    def clear(self):
        if self.LEN > 0:
            for _id in reversed(__media_paths__):
                slide = Slide.dic[_id]
                slide.place_forget()

            if Slide.active_slide:
                Slide.active_slide.deactivate()
                self.SELECTION = -1

            self.LEN = 0
            self.update_scroll()
            self.update()

    def pop(self, index):
        if self.LEN > 0:
            index, slide = self.get_slide(index)
            if slide:
                slide.place_forget()
                if index == self.LEN - 1:
                    __media_paths__.pop(index)
                else:
                    for i in range(index + 1, self.LEN):
                        i, slide_ = self.get_slide(i)
                        if slide_:
                            slide_.place_configure(y=(i - 1) * Slide.height)

                    __media_paths__.pop(index)
                if index == self.SELECTION:
                    slide.deactivate()
                    self.activate(index)
                self.LEN -= 1
                self.update_scroll()
                self.update()

    def pop_active(self, event=None):
        m_slide = Slide.active_slide
        if m_slide:
            m_slide.place_forget()
            m_slide.deactivate()
            if self.SELECTION == self.LEN - 1:
                __media_paths__.pop(self.SELECTION)
            else:
                for i in range(self.SELECTION + 1, self.LEN):
                    slide_ = Slide.dic[__media_paths__[i]]
                    slide_.place_configure(y=(i - 1) * Slide.height)
                __media_paths__.pop(self.SELECTION)
            self.LEN -= 1
            self.update_scroll()
            self.update()
            self.activate(self.SELECTION)

    def get_active(self):
        return self.SELECTION

    def up(self, event=None):
        if self._busy:
            return
        if self.SELECTION > 0:
            self._busy = True
            i = self.SELECTION - 1
            s_slide = Slide.dic[__media_paths__[i]]
            path_ = __media_paths__.pop(i)
            _y = i * Slide.height
            Slide.active_slide.place_configure(y=_y)
            s_slide.place_configure(y=_y + Slide.height)
            __media_paths__.insert(i + 1, path_)
            self.set_visible(i)
            self.SELECTION = i
            self._busy = False

    def down(self, event=None):
        if self._busy:
            return
        if self.SELECTION < self.LEN - 1:
            self._busy = True
            i = self.SELECTION + 1
            s_slide = Slide.dic[__media_paths__[i]]
            path_ = __media_paths__.pop(i)
            _y = i * Slide.height
            Slide.active_slide.place_configure(y=_y)
            s_slide.place_configure(y=_y - Slide.height)
            __media_paths__.insert(i - 1, path_)
            self.set_visible(i)
            self.SELECTION = i
            self._busy = False

    # def destroy_(self):
    #     """use withdraw instead"""
    #     Slide.dic.clear()
    #     self.ids.clear()
    #     self.destroy()


win = Tk()
width, height = 400, 600
min_w, min_h = 200, 100
screen_w, screen_h = win.winfo_screenwidth(), win.winfo_screenheight()
win.geometry(f'{width}x{height}')
win.minsize(min_w, min_h)
win.maxsize(screen_w, screen_h)

# _daim = PIL.Image.open(daim_path)
# default_audio_image = PIL.ImageTk.PhotoImage(_daim.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS))

_daim = PhotoImage(file=daim_path)
default_audio_image = _daim.zoom(Slide.width // 32, Slide.height // 32)

# _dvim = PIL.Image.open(dvim_path)
# default_video_image = PIL.ImageTk.PhotoImage(_dvim.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS))


_dvim = PhotoImage(file=dvim_path)
default_video_image = _dvim.zoom(round(Slide.thumb_dim[0] / _dvim.width()), round(Slide.thumb_dim[1] / _dvim.height()))

__media_paths__ = ["E:\hollywood\Cars (2006) 480p BluRay (Dual Audio) (Hindi-English) ESub (MKVMovies7.Com).mkv",
                  "E:\hollywood\Inception 2010 720p[Dual-Audio][Eng-Hindi]~BONIIN.mkv",
                  "E:\hollywood\Kingsman_The_Golden_Circle_2017_Bluray.mp4",
                  "E:\hollywood\Kingsman_The_Secret_Service_2014_Bluray.mp4",
                  "E:\hollywood\Oblivion_2013_Bluray.mp4",
                  "E:\songs\english songs\Alan Walker - Unity (Lyrics) ft. Walkers(MP3_160K).mp3",
                  "E:\songs\english songs\Alan Walker ignite.mp3",
                  "E:\songs\english songs\Alan Walker_ Sabrina Carpenter _ Farruko  - On My(MP3_128K).mp3",
                  "E:\songs\english songs\Charlie Puth - Attention [Official Video](MP3_128K).mp3",
                  "E:\songs\english songs\Dan   Shay_ Justin Bieber - 10_000 Hours (Official(MP3_160K).mp3",
                  "E:\songs\english songs\Despacito.mp3",
                  "E:\songs\english songs\Despacito__temp__.mp3",
                  "E:\songs\english songs\Ed Sheeran - Perfect (Official Music Video)(MP3_128K).mp3",
                  "E:\songs\english songs\Ed Sheeran - South of the Border (feat. Camila Cab(MP3_160K).mp3",
                  "E:\songs\english songs\hold on(MP3_160K).mp3",
                  "E:\songs\english songs\Imagine Dragons - Believer(MP3_128K).mp3",
                  "E:\songs\english songs\Justin Bieber - Sorry (Official Lyric Video)(MP3_160K).mp3",
                  "E:\songs\english songs\Liam Payne   Strip That Down Lyrics ft Quavo(MP3_160K).mp3",
                  "E:\songs\english songs\Luis Fonsi - Despacito ft. Daddy Yankee 160k.mp3",
                  "E:\songs\english songs\Maroon 5 - Girls Like You ft. Cardi B(MP3_160K).mp3",
                  "E:\songs\english songs\Maroon 5 - Memories(MP3_160K).mp3",
                  "E:\songs\english songs\Mind is a prison -Alec_Benjamin.mp3",
                  "E:\songs\english songs\Phillip Phillips - Gone_ Gone_ Gone(MP3_128K).mp3"]


def active(event=None):
    print(__media_paths__[p.SELECTION])


# __media_paths__ = search_exts(song_format, r'/storage/emulated/0/songs')
#
# print(paths)
p = PlayBox(win, bg='white', width=screen_w, updatedelay=10, height=500, relheight=.09)
p.pack(fill='both', expand='yes')
p.insert_pathseq(__media_paths__)


win.mainloop()
