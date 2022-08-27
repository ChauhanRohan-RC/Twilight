from tkinter import *
import os
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from io import BytesIO
from backup.filemanager import format_mills, search_exts, rgb
from __classes import all_format
import time

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
    _id = 'Rc'


class Slide(Frame):
    __name__ = 'Slide'
    _id = 'Rc'
    thumb_dim = (45, 38)
    height = 40
    dic = {}  # contains id : instances

    def __init__(self, master, m_path, width=350, height=40, fg='black', bg='white', up_call=None, down_call=None,
                 **kwargs):
        self.master = master
        self.m_path = self.id = m_path
        self.width = width
        self.height = height
        self.up_call = up_call
        self.down_call = down_call
        self.fg = fg
        self.bg = bg

        self.m_title, self.m_ext = os.path.splitext(os.path.basename(self.m_path))
        self.artist = 'Unknown Artist'  # only for mp3 files
        self.length = '--:--'
        self.bitrate = '-'
        self.channels = 1
        self.thumb = daim if self.m_ext in song_format else dvim
        self.l2_text = ''

        self.set_m_info()

        Frame.__init__(self, master=self.master, width=self.width, height=self.height, bg=self.bg, **kwargs)
        self.title_l = SlideLabel(self, relief='flat', bd=0, text=self.m_title[:int(self.width / 10)] + '...',
                                  bg=self.bg,
                                  fg=self.fg,
                                  font='Times 10 italic')
        self.artist_l = SlideLabel(self, relief='flat', bd=0, text=self.l2_text, bg=self.bg, fg=self.fg,
                                   font='comicsans 8')
        # self.create_line(4, self.height / 3 + 4, 15, self.height / 3 + 4, fill=self.fg, width=2)
        # self.create_line(4, self.height / 2 + 2, 15, self.height / 2 + 2, fill=self.fg, width=2)
        # self.create_line(4, self.height / 1.5, 15, self.height / 1.5, fill=self.fg, width=2)

        self.image_l = SlideLabel(self, image=self.thumb, bg='white', bd=0)
        self.image_l.place(x=20, y=int((self.height - Slide.thumb_dim[1]) / 2))

        self.title_l.place(x=Slide.thumb_dim[0] + 30, y=round(self.height / 5))
        self.artist_l.place(x=Slide.thumb_dim[0] + 30, y=round(self.height / 2))

        if self.up_call is not None:
            self.bind('<Up>', self.up_call)
        if self.down_call is not None:
            self.bind('<Down>', self.down_call)

        self.__class__.dic[self.id] = self

    def __repr__(self):
        return f'Slide({self.m_path})'

    def set_bg(self, bg):
        self['bg'] = bg
        self.image_l['bg'] = bg
        self.title_l['bg'] = bg
        self.artist_l['bg'] = bg

    def __str__(self):
        return self.__repr__()

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
                        _image = Image.open(BytesIO(_tags[key].data))
                        _image = _image.resize(Slide.thumb_dim, Image.ANTIALIAS)

                        self.thumb = ImageTk.PhotoImage(_image)
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
    def __init__(self, master, width=360, height=400, updatedelay=5, **kwargs):
        self.master = master
        self.width = width
        self.height = height
        self._delay = updatedelay  # in ms

        self.LEN = 0  # len of current input
        self.END = -1  # index of last entry
        self.SELECTION = None  # index of current selection
        self.ids = []  # contains ids sequentially for faster search
        # self.data = []  # contains objects sequentially

        Canvas.__init__(self, master=self.master, width=self.width, height=self.height, **kwargs)
        self.frame = Frame(self, width=self.width - 10, height=self.height, **kwargs)
        self.yscroll = Scrollbar(self, orient='vertical', command=self.yview)
        self.configure(yscrollcommand=self.yscroll.set)

        self.yscroll.pack(side=RIGHT, fill=Y, expand='no', anchor='ne')
        self.frame_id = self.create_window((0, 0), window=self.frame, anchor='nw')
        # self.frame.pack(side=LEFT, expand='yes', fill='both', anchor='nw')

        # self.master.bind('<Button-1>', self.on_click)
        self.master.bind('<B1-Motion>', self.on_drag)

    def update_scroll(self):
        self.frame['height'] = self.LEN * Slide.height

        def _update_s():
            self.configure(scrollregion=self.bbox(self.frame_id))

        self.master.after(self._delay, _update_s)

    def insert_pathseq(self, seq):
        s = time.time()
        self.clear()
        for path_ in seq:
            if path_ in Slide.dic:
                slide = Slide.dic[path_]
                self.ids.append(slide.id)
                # if _slide.master == self.frame:
                #     self.ids.append(_slide.id)
                #     _slide.place(x=0, y=self.LEN * Slide.height)
                # else:
                #     slide = self.create_slide(path_, bd=3)
                #     slide.place(x=0, y=self.LEN * Slide.height)
            else:
                slide = self.create_slide(path_, bd=3)
            slide.place(x=0, y=self.LEN * Slide.height)

            self.update()   # lowers performance
            self.LEN += 1
            print('adding')

        # self.update()
        self.update_scroll()
        if self.LEN > 0 and self.SELECTION is None:
            self.activate(0)

        e = time.time()
        print(e - s)

    def create_slide(self, m_path, **kwargs):
        _slide = Slide(self.frame, m_path, width=self.width - 10,
                       up_call=lambda event: self.activate(self.SELECTION - 1),
                       down_call=lambda event: self.activate(self.SELECTION + 1), **kwargs)
        self.ids.append(_slide.id)
        _slide.bind_all('<Alt-Up>', self.up)
        _slide.bind_all('<Alt-Down>', self.down)
        _slide.bind_all('<Button-1>', self.on_click)
        _slide.bind_all('<B1-Motion>', self.on_drag)

        return _slide

    def nearest(self, y):
        """
        returns nearest index
        """
        y = self.canvasy(y)  # gives y coord wrt to canvas upper left
        print(y)
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
            return index, Slide.dic[self.ids[index]]
        elif index == self.LEN:
            return 0, Slide.dic[self.ids[0]]
        return None, None

    def visiblebbox(self):
        return self.canvasx(0), self.canvasy(0), self.canvasx(self.width), self.canvasy(self.winfo_height())

    def get_mpos(self):
        return self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty()

    def on_click(self, event):
        if self.LEN == 0 or not getattr(event.widget, '_id', False):
            return
        indx_ = self.nearest(event.y_root - self.winfo_rooty())
        if indx_ != self.SELECTION:
            indx_, c_slide_ = self.get_slide(indx_)
            if c_slide_:
                if self.SELECTION is not None:
                    _, p_slide_ = self.get_slide(self.SELECTION)
                    if p_slide_:
                        p_slide_.configure(bd=3)
                        p_slide_.set_bg('white')
                c_slide_.configure(bd=0)
                c_slide_.set_bg(rgb(230, 230, 230))
                c_slide_.focus_force()
                self.SELECTION = indx_
                print('selected : ', indx_)
                self.set_visible(indx_)

    def activate(self, index):
        if self.LEN == 0:
            return
        print('call')
        print('index :', index)
        if index != self.SELECTION:
            index, c_slide_ = self.get_slide(index)
            if c_slide_:
                if self.SELECTION is not None:
                    _, p_slide_ = self.get_slide(self.SELECTION)
                    if p_slide_:
                        p_slide_.configure(bd=3)
                        p_slide_.set_bg('white')
                c_slide_.configure(bd=0)
                c_slide_.set_bg(rgb(230, 230, 230))
                c_slide_.focus_force()
                self.SELECTION = index
                print('selected : ', index)

                self.set_visible(index)

    def on_drag(self, event):
        if self.LEN == 0 or self.SELECTION is None or not getattr(event.widget, '_id', False):
            return
        i = self.nearest(event.y_root - self.winfo_rooty())
        if i < self.LEN and i != self.SELECTION:
            m_slide = Slide.dic[self.ids[self.SELECTION]]
            if m_slide:
                if i < self.SELECTION:
                    s_slide = Slide.dic[self.ids[i]]
                    if s_slide:
                        self.ids.pop(i)
                        _y = i * Slide.height
                        m_slide.place_configure(y=_y)
                        s_slide.place_configure(y=_y + Slide.height)
                        self.ids.insert(i + 1, s_slide.id)
                        self.activate(i)
                        self.SELECTION = i

                elif i > self.SELECTION:
                    i, s_slide = self.get_slide(i)
                    if s_slide:
                        self.ids.pop(i)
                        _y = i * Slide.height
                        m_slide.place_configure(y=_y)
                        s_slide.place_configure(y=_y - Slide.height)
                        self.ids.insert(i - 1, s_slide.id)
                        self.activate(i)
                        self.SELECTION = i

    def set_visible(self, index):
        self.update_idletasks()
        y1 = index * Slide.height
        y2 = y1 + Slide.height
        vy1, vy2 = self.canvasy(0), self.canvasy(self.winfo_height())
        _height = self.LEN * Slide.height
        if vy1 < y1 < vy2 and vy1 < y2 < vy2:
            print('visible')
            return True
        elif y1 < vy1:  # scroll down
            self.yview_moveto(y1 / _height)
        elif y2 > vy2:
            self.yview_moveto((y2 - (vy2 - vy1) + 20) / _height)
        self.update()

    def clear(self):
        if self.LEN > 0:
            for i, _id in reversed(list(enumerate(self.ids))):
                slide = Slide.dic[_id]
                slide.place_forget()

            self.LEN = 0
            self.ids.clear()
            self.update_scroll()
            self.update()

    def pop(self, index):
        if self.LEN > 0:
            index, slide = self.get_slide(index)
            if slide:
                slide.place_forget()
                if index == self.LEN - 1:
                    self.ids.pop(index)
                else:
                    for i in range(index + 1, self.LEN):
                        i, slide = self.get_slide(i)
                        if slide:
                            slide.place_configure(y=(i - 1) * Slide.height)

                    self.ids.pop(index)
                self.LEN -= 1
                self.update_scroll()
                self.update()

    def get_active(self):
        return self.SELECTION

    def destroy_(self):
        """use withdraw instead"""
        Slide.dic.clear()
        self.ids.clear()
        self.destroy()

    def up(self, event=None):
        if self.SELECTION is not None and 0 < self.SELECTION < self.LEN:
            m_slide = Slide.dic[self.ids[self.SELECTION]]
            i = self.SELECTION - 1
            s_slide = Slide.dic[self.ids[i]]
            self.ids.pop(i)
            _y = i * Slide.height
            m_slide.place_configure(y=_y)
            s_slide.place_configure(y=_y + Slide.height)
            self.ids.insert(i + 1, s_slide.id)
            self.activate(i)
            self.SELECTION = i

    def down(self, event=None):
        if self.SELECTION is not None and 0 <= self.SELECTION < self.LEN - 1:
            m_slide = Slide.dic[self.ids[self.SELECTION]]
            i = self.SELECTION + 1
            s_slide = Slide.dic[self.ids[i]]
            self.ids.pop(i)
            _y = i * Slide.height
            m_slide.place_configure(y=_y)
            s_slide.place_configure(y=_y - Slide.height)
            self.ids.insert(i - 1, s_slide.id)
            self.activate(i)
            self.SELECTION = i


paths = search_exts(all_format, 'E:\\')

win = Tk()
win.geometry('370x410')
win.minsize(310, 100)
win.maxsize(2000, 900)

with open(daim_path, 'rb') as afile:
    daim = Image.open(BytesIO(afile.read()))
    daim = ImageTk.PhotoImage(daim.resize(Slide.thumb_dim, Image.ANTIALIAS))
with open(dvim_path, 'rb') as vfile:
    dvim = Image.open(BytesIO(vfile.read()))
    dvim = ImageTk.PhotoImage(dvim.resize(Slide.thumb_dim, Image.ANTIALIAS))
#
# paths = ["E:\hollywood\Cars (2006) 480p BluRay (Dual Audio) (Hindi-English) ESub (MKVMovies7.Com).mkv",
#          "E:\hollywood\Inception 2010 720p[Dual-Audio][Eng-Hindi]~BONIIN.mkv",
#          "E:\hollywood\Kingsman_The_Golden_Circle_2017_Bluray.mp4",
#          "E:\hollywood\Kingsman_The_Secret_Service_2014_Bluray.mp4",
#          "E:\hollywood\Oblivion_2013_Bluray.mp4",
#          "E:\songs\english songs\Alan Walker - Unity (Lyrics) ft. Walkers(MP3_160K).mp3",
#          "E:\songs\english songs\Alan Walker ignite.mp3",
#          "E:\songs\english songs\Alan Walker_ Sabrina Carpenter _ Farruko  - On My(MP3_128K).mp3",
#          "E:\songs\english songs\Charlie Puth - Attention [Official Video](MP3_128K).mp3",
#          "E:\songs\english songs\Dan   Shay_ Justin Bieber - 10_000 Hours (Official(MP3_160K).mp3",
#          "E:\songs\english songs\Despacito.mp3",
#          "E:\songs\english songs\Despacito__temp__.mp3",
#          "E:\songs\english songs\Ed Sheeran - Perfect (Official Music Video)(MP3_128K).mp3",
#          "E:\songs\english songs\Ed Sheeran - South of the Border (feat. Camila Cab(MP3_160K).mp3",
#          "E:\songs\english songs\hold on(MP3_160K).mp3",
#          "E:\songs\english songs\Imagine Dragons - Believer(MP3_128K).mp3",
#          "E:\songs\english songs\Justin Bieber - Sorry (Official Lyric Video)(MP3_160K).mp3",
#          "E:\songs\english songs\Liam Payne   Strip That Down Lyrics ft Quavo(MP3_160K).mp3"]


def show():
    win.update()
    win.deiconify()
    win.after(1000, p.insert_pathseq, paths)


p = PlayBox(win, width=370)
p.pack(fill='both', expand='yes', pady=30)
print(len(paths))


# p.insert_pathseq(paths)
# win.after(2050, p.destroy())
#
# win.after(3000, win.withdraw)
win.after(1000, p.insert_pathseq, paths)

win.after(3000, win.withdraw)


win.after(5000, show)
win.mainloop()
