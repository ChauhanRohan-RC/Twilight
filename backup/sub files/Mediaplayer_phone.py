# import sys
# import os.path
#
# main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
#     os.path.abspath(os.path.realpath(__file__)))
#
# sdk_dir = os.path.join(main_dir, 'sdk')
# run_file = os.path.join(sdk_dir, 'runfile.cc')
#
# if os.path.isfile(run_file):
#     from tkinter import messagebox, Tk
#
#     error_win = Tk()
#     error_win.withdraw()
#     in__bug = messagebox.askokcancel('Runtime error', 'Another instance already running : API RUNTIME WARNING\n'
#                                                       'CAUTION : in case of bug or crash press OK to fix it..... ')
#     if in__bug:
#         if os.path.isfile(run_file):
#             os.remove(run_file)
#         messagebox.showinfo('Repair RC MP', 'All set... Restart the program to verify ...')
#     sys.exit(2)
# else:
#     with open(run_file, 'x') as file:  # creating run file
#         file.close()
#
#     from tkinter import *
#     from tkinter import filedialog
#     from tkinter import messagebox
#     from pathlib import Path
#     from backup.filemanager import *
#     import PIL.Image, PIL.ImageTk
#     from io import BytesIO
#     import main_player
#     from threading import Thread
#     from __classes import *
#     from mutagen.mp3 import MP3
#     from mutagen.mp4 import MP4
#     import time
#
#
# def print_(str__=None):  # dummy function
#     pass
#
#
# # ....................................... filepath and vars ..................................................
# __media_paths__ = []
#
# default_settings = {'save_pos': 1, 'vol_rate': 5, 'seek_rate': 10, 'max_volume': 200, 'current_vol': 70, 'exit_check': 0,
#                     'refresh_time': 140, 'scan_sub': 0, 'fulltime_state': 0}
#
# default_past_info = {'past_media': [], 'play_count': 0, 'load_on_start': 1,
#                  'controller': 1, 'auto_play': 1, 'controller_coords': (None, None)}
#
# delay = 1000  # delay to play next/previous_call in ms
# thumbnail_info = [-1, (0, 0)]  # song thumbnail in form of [canvas id, (width, height)]
#
# audio_id = []
# exsub_list = []
#
# screenshot_dir = os.path.join(sdk_dir, 'screenshots')
#
# if not os.path.isdir(screenshot_dir):
#     os.mkdir(screenshot_dir)  # creating directory for screenshots if not present
#
# main_player_in = main_player.Instance()
# player = main_player_in.media_player_new()
#
# # previous media
# _past_file = os.path.join(sdk_dir, 'mpast.cc')
# _playlist_file = os.path.join(sdk_dir, 'playlists.cc')
# _playback_file = os.path.join(sdk_dir, 'playback.cc')
# _settings_file = os.path.join(sdk_dir, 'settings.cc')
#
# # file manager
# fmpast = FileManager(_past_file)
# fmplay = FileManager(_playlist_file)
# fmplayb = FileManager(_playback_file)
# fms = FileManager(_settings_file)
#
# # ....................................................... DIRECTORY .............................
# _sys_file = os.path.join(sdk_dir, 'sysplay.cc')
#
# fmsys = FileManager(_sys_file)
#
#
# # .................................................RC Classes.....................
#
# class SlideLabel(Label):
#     _id = 2
#     __name__ = 'SlideLabel'
#
#
# class Slide(Frame):
#     __name__ = 'Slide'
#     _id = 1
#     thumb_dim = (45, 38)
#     height = 40
#     dic = {}  # contains id : instances
#
#     def __init__(self, master, m_path, width=350, height=40, bd=3, fg='black', bg='white',
#                  activebg=rgb(235, 235, 235), activebd=0,**kwargs):
#         self.master = master
#         self.m_path = self.id = m_path
#         self.width = width
#         self.height = height
#         self.fg = fg
#         self.bg = bg
#         self.activebg = activebg
#         self.bd = bd
#         self.activebd = activebd
#
#         self.index = __media_paths__.index(self.m_path)
#
#         self.m_title, self.m_ext = os.path.splitext(os.path.basename(self.m_path))
#         self.artist = 'Unknown Artist'  # only for mp3 files
#         self.length = '--:--'
#         self.bitrate = '-'
#         self.channels = 1
#         self.thumb = daim if self.m_ext in song_format else dvim
#         self.l2_text = ''
#
#         self.set_m_info()
#
#         Frame.__init__(self, master=self.master, width=self.width, height=self.height, bg=self.bg, bd=self.bd, **kwargs)
#         self.title_l = SlideLabel(self, relief='flat', bd=0, text=self.m_title[:int(self.width / 10)] + '...',
#                                   bg=self.bg,
#                                   fg=self.fg,
#                                   font='Times 10 italic')
#         self.artist_l = SlideLabel(self, relief='flat', bd=0, text=self.l2_text, bg=self.bg, fg=self.fg,
#                                    font='comicsans 8')
#         # self.create_line(4, self.height / 3 + 4, 15, self.height / 3 + 4, fill=self.fg, width=2)
#         # self.create_line(4, self.height / 2 + 2, 15, self.height / 2 + 2, fill=self.fg, width=2)
#         # self.create_line(4, self.height / 1.5, 15, self.height / 1.5, fill=self.fg, width=2)
#
#         self.image_l = SlideLabel(self, image=self.thumb, bg='white', bd=0)
#         self.image_l.place(x=20, y=int((self.height - Slide.thumb_dim[1]) / 2))
#
#         self.title_l.place(x=Slide.thumb_dim[0] + 30, y=round(self.height / 5))
#         self.artist_l.place(x=Slide.thumb_dim[0] + 30, y=round(self.height / 2))
#
#         self.__class__.dic[self.id] = self
#
#     def activate(self):
#         self.configure(bd=self.activebd, bg=self.activebg)
#
#     def deactivate(self):
#         self.configure(bd=self.bd, bg=self.bg)
#
#     def __repr__(self):
#         return f'Slide({self.m_path})'
#
#     def set_bg(self, bg):
#         self['bg'] = bg
#         self.image_l['bg'] = bg
#         self.title_l['bg'] = bg
#         self.artist_l['bg'] = bg
#
#     def __str__(self):
#         return self.__repr__()
#
#     def set_m_info(self):
#         try:
#             if self.m_ext == '.mp3':
#                 _audio = MP3(self.m_path)
#                 _info, _tags = _audio.info, _audio.tags
#
#                 if 'TIT2' in _tags:
#                     self.m_title = str(_tags['TIT2'])
#
#                 if 'TPE1' in _tags:
#                     self.artist = str(_tags['TPE1'])
#
#                 self.length = format_mills(_info.length * 1000, _tuple=False, full=True)
#                 self.bitrate = _info.bitrate
#                 self.channels = _info.channels
#
#                 for key in _tags:
#                     if 'APIC' in key:
#                         _image = PIL.Image.open(BytesIO(_tags[key].data))
#                         _image = _image.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS)
#
#                         self.thumb = PIL.ImageTk.PhotoImage(_image)
#                         break
#
#             elif self.m_ext == '.mp4':
#                 _info = MP4(self.m_path).info
#                 self.length, self.bitrate, self.channels = format_mills(_info.length * 1000, _tuple=False, full=True), _info.bitrate, _info.channels
#         except Exception as e:
#             print(e)
#         finally:
#             self.l2_text = f'{self.artist[:int(self.width / 10)]}.. | {self.length}' if self.m_ext in song_format else self.length
#
#
# class PlayBox(Canvas):
#     """
#     only works for unique entries
#     """
#     def __init__(self, master, width=360, height=400, updatedelay=5, **kwargs):
#         self.master = master
#         self.width = width
#         self.height = height
#         self._delay = updatedelay  # in ms
#
#         self.LEN = 0  # len of current input
#         self.END = -1  # index of last entry
#         self.SELECTION = None  # index of current selection
#         # self.ids = []  # contains ids sequentially for faster search
#         # self.data = []  # contains objects sequentially
#
#         Canvas.__init__(self, master=self.master, width=self.width, height=self.height, **kwargs)
#         self.frame = Frame(self, width=self.width - 10, height=self.height, **kwargs)
#         self.yscroll = Scrollbar(self, orient='vertical', command=self.yview)
#         self.configure(yscrollcommand=self.yscroll.set)
#
#         self.yscroll.pack(side=RIGHT, fill=Y, expand='no', anchor='ne')
#         self.frame_id = self.create_window((0, 0), window=self.frame, anchor='nw')
#
#         # self.frame.pack(side=LEFT, expand='yes', fill='both', anchor='nw')
#         # self.master.bind('<Button-1>', self.on_click)
#         # self.master.bind('<B1-Motion>', self.on_drag)
#
#     def update_scroll(self):
#         self.frame['height'] = self.LEN * Slide.height
#
#         def _update_s():
#             self.configure(scrollregion=self.bbox(self.frame_id))
#
#         self.master.after(self._delay, _update_s)
#
#     def insert_pathseq(self, seq):
#         s = time.time()
#         self.clear()
#         for path_ in seq:
#             if path_ in Slide.dic:
#                 slide = Slide.dic[path_]
#             else:
#                 slide = self.create_slide(path_, bd=3)
#             slide.place(x=0, y=self.LEN * Slide.height)
#
#             self.update()   # lowers performance
#             self.LEN += 1
#             print('adding')
#
#         self.update_scroll()
#         if self.LEN > 0 and self.SELECTION is None:
#             self.activate(0)
#
#         e = time.time()
#         print(e - s)
#
#     def create_slide(self, m_path, **kwargs):
#         _slide = Slide(self.frame, m_path, width=self.width - 10, **kwargs)
#
#         _slide.bind('<Up>', lambda event: self.activate(self.SELECTION - 1))
#         _slide.bind('<Down>', lambda event: self.activate(self.SELECTION + 1))
#         _slide.bind('<Alt-Up>', self.up)
#         _slide.bind('<Alt-Down>', self.down)
#         _slide.bind('<Return>', active)
#         _slide.bind_all('<Button-1>', self.on_click)
#         _slide.bind_all('<Double-Button-1>', active)
#         _slide.bind_all('<B1-Motion>', self.on_drag)
#         _slide.bind_all('<Delete>', self.pop_active)
#
#         return _slide
#
#     def nearest(self, y):
#         """
#         returns nearest index
#         """
#         y = self.canvasy(y)  # gives y coord wrt to canvas upper left
#         print(y)
#         if 0 <= y < self.LEN * Slide.height:
#             return int(y // Slide.height)
#         return self.LEN
#
#     def get_slide(self, index):
#         """
#         returns (corrected index , slide) , or (None, None) in case of no slide
#         """
#         if self.LEN == 0:
#             return None, None
#         if -self.LEN <= index < self.LEN:
#             if index < 0:
#                 index += self.LEN
#             return index, Slide.dic[__media_paths__[index]]
#         elif index == self.LEN:
#             return 0, Slide.dic[__media_paths__[0]]
#         return None, None
#
#     def visiblebbox(self):
#         return self.canvasx(0), self.canvasy(0), self.canvasx(self.width), self.canvasy(self.winfo_height())
#
#     def get_mpos(self):
#         return self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty()
#
#     def on_click(self, event):
#         attr_ = getattr(event.widget, '_id', -1)
#         if attr_ == 1:
#             c_slide = event.widget
#         elif attr_ == 2:
#             c_slide = event.widget.master
#         else:
#             return
#         i = c_slide.index
#         if i != self.SELECTION:
#             if self.SELECTION is not None:
#                 p_slide_ = Slide.dic[__media_paths__[self.SELECTION]]
#                 if p_slide_:
#                     p_slide_.deactivate()
#
#             c_slide.activate()
#             c_slide.focus_force()
#             self.SELECTION = i
#             print('selected : ', i)
#             self.set_visible(i)
#
#     def activate(self, index):
#         if self.SELECTION is not None and index == self.SELECTION:
#             return
#
#         index, c_slide_ = self.get_slide(index)
#         if c_slide_:
#             if self.SELECTION is not None:
#                 p_slide_ = Slide.dic[__media_paths__[self.SELECTION]]
#                 p_slide_.deactivate()
#
#             c_slide_.activate()
#             c_slide_.focus_force()
#             self.SELECTION = index
#             print('selected : ', index)
#
#             self.set_visible(index)
#
#     def on_drag(self, event):
#         i = self.nearest(event.y_root - self.winfo_rooty())
#         if 0 <= i < self.LEN and i != self.SELECTION:
#             m_slide = Slide.dic[__media_paths__[self.SELECTION]]
#             if i < self.SELECTION:
#                 _y = i * Slide.height
#                 m_slide.place_configure(y=_y)
#                 Slide.dic[__media_paths__[i]].place_configure(y=_y + Slide.height)
#                 path_ = __media_paths__.pop(i)
#                 __media_paths__.insert(i + 1, path_)
#                 m_slide.activate()
#                 self.SELECTION = i
#
#             else:
#                 _y = i * Slide.height
#                 m_slide.place_configure(y=_y)
#                 Slide.dic[__media_paths__[i]].place_configure(y=_y - Slide.height)
#                 path_ = __media_paths__.pop(i)
#                 __media_paths__.insert(i - 1, path_)
#                 m_slide.activate()
#                 self.SELECTION = i
#
#     def set_visible(self, index):
#         y1 = index * Slide.height
#         y2 = y1 + Slide.height
#         vy1, vy2 = self.canvasy(0), self.canvasy(self.winfo_height())
#         _height = self.LEN * Slide.height
#         if vy1 < y1 < vy2 and vy1 < y2 < vy2:
#             print('visible')
#             return True
#         elif y1 < vy1:  # scroll down
#             self.yview_moveto(y1 / _height)
#         elif y2 > vy2:
#             self.yview_moveto((y2 - (vy2 - vy1) + 20) / _height)
#         self.update()
#
#     def clear(self):
#         if self.LEN > 0:
#             for _id in reversed(__media_paths__):
#                 slide = Slide.dic[_id]
#                 slide.place_forget()
#
#             if self.SELECTION is not None:
#                 Slide.dic[__media_paths__[self.SELECTION]].deactivate()
#                 self.SELECTION = None
#
#             self.LEN = 0
#             self.update_scroll()
#             self.update()
#
#     def pop(self, index):
#         if self.LEN > 0:
#             index, slide = self.get_slide(index)
#             if slide:
#                 slide.place_forget()
#                 if index == self.LEN - 1:
#                     __media_paths__.pop(index)
#                 else:
#                     for i in range(index + 1, self.LEN):
#                         i, slide = self.get_slide(i)
#                         if slide:
#                             slide.place_configure(y=(i - 1) * Slide.height)
#
#                     __media_paths__.pop(index)
#                 self.LEN -= 1
#                 self.update_scroll()
#                 self.update()
#
#     def pop_active(self, event=None):
#         # always called by slide
#         print('deltete')
#         pass
#
#     def get_active(self):
#         return self.SELECTION
#
#     # def destroy_(self):
#     #     """use withdraw instead"""
#     #     Slide.dic.clear()
#     #     self.ids.clear()
#     #     self.destroy()
#
#     def up(self, event=None):
#         if self.SELECTION is not None and 0 < self.SELECTION < self.LEN:
#             m_slide = Slide.dic[__media_paths__[self.SELECTION]]
#             i = self.SELECTION - 1
#             s_slide = Slide.dic[__media_paths__[i]]
#             path_ = __media_paths__.pop(i)
#             _y = i * Slide.height
#             m_slide.place_configure(y=_y)
#             s_slide.place_configure(y=_y + Slide.height)
#             __media_paths__.insert(i + 1, path_)
#             self.activate(i)
#             self.SELECTION = i
#
#     def down(self, event=None):
#         if self.SELECTION is not None and 0 <= self.SELECTION < self.LEN - 1:
#             m_slide = Slide.dic[__media_paths__[self.SELECTION]]
#             i = self.SELECTION + 1
#             s_slide = Slide.dic[__media_paths__[i]]
#             path_ = __media_paths__.pop(i)
#             _y = i * Slide.height
#             m_slide.place_configure(y=_y)
#             s_slide.place_configure(y=_y - Slide.height)
#             __media_paths__.insert(i - 1, path_)
#             self.activate(i)
#             self.SELECTION = i
#
#
# class PlayWin(Toplevel):
#     Instance = None
#
#     def __init__(self, master, title, size=(310, 410), minsize=(310, 190), pos=(0, 0)):
#         Toplevel.__init__(self, master)
#         self.geometry(f'{size[0]}x{size[1]}+{pos[0]}+{pos[1]}')
#         self.title_ = title
#         self.title(title)
#         self.iconbitmap(icon)
#         self.minsize_ = minsize
#         self.minsize(*minsize)
#         self.protocol('WM_DELETE_WINDOW', self.destroy_)
#         self.size = size
#         self.pos = pos
#         self['bg'] = 'white'
#
#         self.search_canvas = Canvas(self, bg='white', highlightthickness=0)  # for search widgets
#         self.play_canvas = Canvas(self, bg='white', highlightthickness=2)  # for listbox
#         self.canvas = Canvas(self)  # for dock buttons
#
#         self.current_indx = None
#         self.search_mode_ = False
#         self.search_results = []
#
#         self.yscroll = Scrollbar(self.play_canvas, orient='vertical')
#         self.xscroll = Scrollbar(self, orient='horizontal')
#         self.playlist = Listbox(self.play_canvas,
#                                 font='comicsans 9',
#                                 selectmode=SINGLE,
#                                 yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set, activestyle='dotbox')
#
#         self.yscroll.config(command=self.playlist.yview)
#         self.xscroll.config(command=self.playlist.xview)
#
#         self.save_b = Button(self.canvas, text=' Save ', font='comicsans 9 bold', command=save_playlist)
#         self.remove_b = Button(self.canvas, text=' Remove ', font='comicsans 9 bold', command=remove_media)
#         self.previous_b = Button(self.canvas, image=previous_image, command=previous_call)
#         self.next_b = Button(self.canvas, image=next_image, command=next_call)
#         self.shuffle_b = Button(self.canvas, text=' Shuffle ', font='comicsans 9 bold', command=shuffle)
#         self.clear_b = Button(self.canvas, text=' Clear ', font='comicsans 9 bold', command=clear_playlist)
#         self.organise_b = Button(self.canvas, text='Organise', font='comicsans 9 bold', command=self.organise)
#         self.up_b = Button(self.canvas, text=' Move Up ', font='comicsans 9 bold', command=self.up)
#         self.down_b = Button(self.canvas, text=' Move Down ', font='comicsans 9 bold', command=self.down)
#         self.exit_org_b = Button(self.canvas, text='>>>', font='comicsans 9 bold', command=self.exit_organise)
#
#         self.search_b = Button(self.search_canvas, text='Search', font='comicsans 8 bold italic', bg='white',
#                                activebackground='white', command=self.search_mode)
#         self.search_e = Entry(self.search_canvas, relief='flat', bg=rgb(230, 230, 230), font='comicsans 9 bold italic', fg='darkgreen')
#         self.cancel_search = Button(self.search_canvas, text='X', relief='flat', font='lucida 9 bold', bd=0, bg='white'
#                                     , command=self.cancel_search_mode, width=5)
#         self.search_b.pack(fill=BOTH, expand='yes')
#
#         self.yscroll.pack(side=RIGHT, fill=Y, expand='no', anchor='ne')
#         self.playlist.pack(side=LEFT, expand='yes', fill='both', anchor='nw')
#
#         # Bindings and scroll
#         self.bind('<Alt-Right>', next_call)
#         self.bind('<Alt-Left>', previous_call)
#         self.bind('<Alt-r>', set_playback)
#         self.bind('<Control-Up>', vol_in)
#         self.bind('<Control-Down>', vol_dec)
#         self.bind('<Control-p>', toogle_playlist)
#         self.bind('<Control-l>', load_playlist)
#         self.bind('<Control-w>', save_playlist)
#         self.bind('<Control-z>', shuffle)
#         self.bind('<Control-a>', set_aspect_ratio)
#         self.bind('<Alt-s>', screenshot)
#         self.bind('<Control-o>', openfile)
#         self.bind('<Control-f>', scan_folder_ui)
#
#         self.playlist.bind('<Delete>', remove_media)
#         self.playlist.bind('<Double-Button-1>', active)
#         self.playlist.bind('<Return>', active)
#         self.playlist.bind('<Button-1>', self.set_current)
#         self.playlist.bind('<B1-Motion>', self.drag)
#         self.playlist.bind('<Up>', self.search_init)
#
#         # theme
#         self.resizable(1, 1)
#         self['bg'] = 'white'
#         self.playlist['relief'] = 'flat'
#         self.playlist['borderwidth'] = 3
#         self.playlist['bg'] = rgb(65, 65, 65)
#         self.playlist['fg'] = rgb(190, 190, 190)
#         self.playlist['selectbackground'] = rgb(45, 45, 45)
#         self.playlist['selectforeground'] = rgb(240, 230, 240)
#
#         self.canvas['bg'] = 'white'
#         self.canvas['relief'] = 'flat'
#
#         self.save_b['bg'] = 'white'
#         self.shuffle_b['bg'] = 'white'
#         self.previous_b['bg'] = 'white'
#         self.next_b['bg'] = 'white'
#         self.remove_b['bg'] = 'white'
#         self.clear_b['bg'] = 'white'
#         self.organise_b['bg'] = 'white'
#         self.up_b['bg'] = 'white'
#         self.down_b['bg'] = 'white'
#         self.exit_org_b['bg'] = 'white'
#
#         self.save_b['relief'] = 'flat'
#         self.shuffle_b['relief'] = 'flat'
#         self.previous_b['relief'] = 'flat'
#         self.next_b['relief'] = 'flat'
#         self.remove_b['relief'] = 'flat'
#         self.clear_b['relief'] = 'flat'
#         self.organise_b['relief'] = 'flat'
#         self.up_b['relief'] = 'flat'
#         self.down_b['relief'] = 'flat'
#         self.exit_org_b['relief'] = 'flat'
#
#         self.bind_input_keys()
#         self.playlist.focus_set()
#         self.pack_w()
#
#         PlayWin.Instance = self
#
#     def __repr__(self):
#         return f'PlayWin({self.master},{self.title_}, {self.size}, {self.minsize_},{self.pos})'
#
#     def destroy_(self):
#         self.destroy()
#         win.focus_set()
#         playmenu.entryconfig(0, label="Show Playlist")
#         config_status('Playlist Hidden')
#         PlayWin.Instance = None
#
#     def bind_input_keys(self):
#         if player.get_state() in (3, 4):
#             self.bind('<space>', pause)
#         else:
#             self.bind('<space>', count)
#         self.bind('<Left>', backward)
#         self.bind('<Right>', forward)
#         self.bind('<Escape>', stop)
#
#     def unbind_input_keys(self):
#         self.unbind('<space>')
#         self.unbind('<Left>')
#         self.unbind('<Right>')
#         self.unbind('<Escape>')
#
#     def set_focus_on_playlist(self, event=None):
#         if self.search_mode_:
#             self.cancel_search_mode()
#         self.playlist.focus_set()
#
#     def search_init(self, event=None):
#         if self.get_active() == 0:
#             self.search_mode()
#
#     def search_mode(self, event=None):
#         self.search_b.pack_forget()
#         # self.search_e.pack(side=LEFT, fill=Y, anchor=NW)
#         # self.cancel_search.pack(side=RIGHT, anchor=NE)
#
#         self.cancel_search.pack(side=RIGHT, fill=Y, expand='no', anchor='ne', padx=5)
#         self.search_e.pack(side=LEFT, expand='yes', fill='both', anchor='nw', padx=10)
#
#         self.search_e.bind('<Return>', self.search_)
#         self.search_e.bind('<Escape>', self.cancel_search_mode)
#         self.search_e.bind('<Down>', self.set_focus_on_playlist)
#         self.search_e.focus_set()
#         self.unbind_input_keys()
#         self.search_mode_ = True
#         self.search_loop()
#
#     def search_(self, event=None):
#         text_ = self.search_e.get()
#         self.search_results = search_name_in_paths(text_, __media_paths__)  # in paths form
#         self.insert_pathseq(self.search_results)
#         if not self.search_results:
#             self.search_e['fg'] = 'red'
#         else:
#             self.search_e['fg'] = 'darkgreen'
#
#     def search_loop(self):
#         if self.search_mode_:
#             if self.focus_get() == self.search_e:  # if search box is in focus
#                 self.search_()
#             self.after(300, self.search_loop)
#
#     def insert_pathseq(self, seq):
#         self.playlist.delete(0, END)
#         for path_ in seq:
#             self.playlist.insert(END, f' >>>   {os.path.basename(path_)}')
#
#     def cancel_search_mode(self, event=None):
#         self.cancel_search.pack_forget()
#         self.search_e.pack_forget()
#         self.search_e.unbind('<Escape>')
#         self.search_e.unbind('<Return>')
#         self.search_b.pack(fill=BOTH, expand='yes')
#         self.search_results.clear()
#         self.search_mode_ = False
#         self.playlist.focus_set()
#         self.bind_input_keys()
#         self.insert_pathseq(__media_paths__)
#
#     def set_current(self, event):
#         self.current_indx = self.playlist.nearest(event.y)
#
#     def drag(self, event):
#         if not self.search_mode_:
#             i = self.playlist.nearest(event.y)
#             playing = __media_paths__[_play_count.v]
#             if i < self.current_indx:
#                 x = self.playlist.get(i)
#                 path_ = __media_paths__.pop(i)
#                 self.playlist.delete(i)
#                 self.playlist.insert(i + 1, x)
#                 __media_paths__.insert(i + 1, path_)
#                 self.current_indx = i
#                 self.playlist.activate(i)
#             elif i > self.current_indx:
#                 x = self.playlist.get(i)
#                 path_ = __media_paths__.pop(i)
#                 self.playlist.delete(i)
#                 self.playlist.insert(i - 1, x)
#                 __media_paths__.insert(i - 1, path_)
#                 self.current_indx = i
#                 self.playlist.activate(i)
#
#             _play_count.v = __media_paths__.index(playing)
#
#     def pack_w(self, all_=True):
#         # packing
#         if all_:
#             self.search_canvas.pack(anchor=NW, fill=X, expand='no')
#             self.play_canvas.pack(fill=BOTH, expand='yes', anchor=NW)
#             self.xscroll.pack(fill=X)
#             self.canvas.pack(side=LEFT, anchor=NW, expand='yes', fill=X)
#
#         self.save_b.pack(side=LEFT, anchor=S, padx=1, pady=9)
#         self.shuffle_b.pack(side=LEFT, anchor=S, padx=1, pady=9)
#         self.previous_b.pack(side=LEFT, anchor=S, padx=4, pady=5)
#         self.clear_b.pack(side=RIGHT, anchor=SE, padx=1, pady=9)
#         self.organise_b.pack(side=RIGHT, anchor=S, padx=1, pady=9)
#         self.next_b.pack(side=RIGHT, anchor=S, padx=4, pady=5)
#
#     def pack_f(self):
#         for widget in self.canvas.winfo_children():
#             widget.pack_forget()
#
#     def organise(self):
#         self.pack_f()
#         self.up_b.pack(side=LEFT, padx=10, pady=12)
#         self.down_b.pack(side=LEFT, padx=8, pady=12)
#
#         self.exit_org_b.pack(side=RIGHT, padx=10, pady=12)
#         self.remove_b.pack(side=RIGHT, padx=8, pady=12)
#
#     def up(self):
#         if not self.search_mode_:
#             in__up = self.playlist.index(ACTIVE)
#             if in__up is not None:
#                 if in__up > 0:
#                     x__ = self.playlist.get(in__up)
#                     self.pop(in__up)
#                     path_ = __media_paths__.pop(in__up)
#                     self.playlist.insert(in__up - 1, x__)
#                     __media_paths__.insert(in__up - 1, path_)
#                     self.playlist.activate(in__up - 1)
#
#     def down(self):
#         if not self.search_mode_:
#             in__down = self.playlist.index(ACTIVE)
#             if in__down is not None:
#                 if in__down < len(__media_paths__) - 1:
#                     x__ = self.playlist.get(in__down)
#                     self.pop(in__down)
#                     path_ = __media_paths__.pop(in__down)
#                     self.playlist.insert(in__down + 1, x__)
#                     __media_paths__.insert(in__down + 1, path_)
#                     self.playlist.activate(in__down + 1)
#
#     def exit_organise(self):
#         self.pack_f()
#         self.pack_w(all_=False)
#
#     def insert(self, m_paths):
#         for name in map(os.path.basename, m_paths):
#             self.playlist.insert(END, f' >>>   {name}')
#
#     def pop_active(self):
#         try:
#             n = self.playlist.curselection()
#             if n:
#                 n_in = n[0]
#                 self.playlist.delete(n_in[0])
#         except Exception as e:
#             print_(e)
#
#     def pop(self, index):
#         try:
#             self.playlist.delete(index)
#         except Exception as e:
#             print_(e)
#
#     def get_active(self):
#         try:
#             return self.playlist.index(ACTIVE) if not self.search_mode_ else __media_paths__.index(
#                 self.search_results[self.playlist.index(ACTIVE)])
#         except Exception as e:
#             print(e)
#             return None
#
#     def clear(self):
#         self.playlist.delete(0, END)
#
#
# class FsDock(Toplevel):
#     Instance = None
#
#     def __init__(self, master, canvas_, player_):
#         self.master = master
#         self.canvas = canvas_
#         self.player = player_
#         self.s_width = screen_width - 80
#         self.s_height = 28
#         Toplevel.__init__(self, master=master)
#         self.center()
#         self.protocol('WM_DELETE_WINDOW', exit_diag)
#         self.bind('<Button-1>', self.set_focus)
#         self.set_m_by_slider = False
#
#         self.m_scale = RcScale(self, slider=True, value=0, width=self.s_width - 120, height=16,
#                                troughcolor1=rgb(240, 123, 7),
#                                troughcolor2=rgb(206, 233, 234), outline=rgb(90, 90, 90), outwidth=6, relief='flat',
#                                bd=0,
#                                highlightthickness=0)
#
#         self.c_time = Label(self, text='--:--', font='comicsans 9')
#         self.f_time = Label(self, text='--:--', font='comicsans 9')
#
#         self.m_scale.bind("<ButtonRelease-1>", self.m_scale_release_call)
#         self.m_scale.bind("<Button-1>", self.m_scale_click_call)
#         self.m_scale.bind("<B1-Motion>", self.m_scale_motion_call)
#         self.destruct_time = 4000  # in ms
#         self.d_timer = self.master.after(self.destruct_time, self.destroy_)
#
#         # dock theme......................
#         self.c_time['bg'] = rgb(90, 90, 90)
#         self.f_time['bg'] = rgb(90, 90, 90)
#         self.c_time['fg'] = rgb(240, 240, 240)
#         self.f_time['fg'] = rgb(240, 240, 240)
#         self['bg'] = rgb(90, 90, 90)
#         self.wm_attributes('-alpha', 0.75)
#
#         self.overrideredirect(True)
#
#         self.place_widgets()
#         self.set_scale = True
#         self.auto_set()
#         self.at_top()
#
#         FsDock.Instance = self
#
#     def mouse_over(self, pos):
#         if self.winfo_rootx() < pos[0] < self.winfo_rootx() + self.s_width:
#             if self.winfo_rooty() < pos[1] < self.winfo_rooty() + self.s_height:
#                 return True
#         return False
#
#     def d_timer_cancel(self, event=None):
#         if self.d_timer is not None:
#             self.master.after_cancel(self.d_timer)
#             self.d_timer = None
#
#     def d_timer_reset(self, event=None):
#         self.d_timer_cancel()
#         self.d_timer = self.master.after(self.destruct_time, self.destroy_)
#
#     def destroy_(self):
#         self.set_scale = False
#         try:
#             self.destroy()
#         except Exception as e:
#             print(f'excption in fullscreen dock destroy_ : {e}')
#         FsDock.Instance = None
#
#     def place_widgets(self):
#         self.c_time.place(x=5, y=3)
#         self.m_scale.place(x=60, y=3)
#         self.f_time.place(x=self.s_width - 60, y=3)
#
#     def center(self, _pady_=7):
#         self.geometry(
#             f'{self.s_width}x{self.s_height}+{round((screen_width - self.s_width) / 2)}+{screen_height - self.s_height - _pady_}')
#
#     def m_scale_release_call(self, event=None):
#         self.set_scale = True
#
#     def m_scale_motion_call(self, event):
#         if self.set_m_by_slider:
#             _value_ = self.m_scale.get_value_from_x(event.x)
#             self.player.set_position(_value_ / 100)
#             self.m_scale.set(_value_)
#
#     def m_scale_click_call(self, event=None):
#         if player.get_state() in (3, 4):
#             self.set_scale = False
#             if self.m_scale.find_(event.x, event.y) == 'slider':
#                 self.set_m_by_slider = True
#             else:
#                 self.set_m_by_slider = False
#                 _value_ = self.m_scale.get_value_from_x(event.x)
#                 player.set_position(_value_ / 100)
#                 self.m_scale.set(_value_)
#         self.at_top()
#
#     def auto_set(self):
#         if self.set_scale:
#             self.m_scale.set(self.player.get_position() * 100)
#
#     def at_top(self, event=None):
#         self.attributes('-topmost', True)
#
#     def set_focus(self, event=None):
#         self.canvas.focus_force()
#
#
# class Controller(Toplevel):
#     Instance = None
#
#     def __init__(self, master, size=(200, 90), spadx=20, spady=40, override=True):
#         self.width = size[0]
#         self.height = size[1]
#         self.spadx = spadx
#         self.spady = spady
#         self.x, self.y = self.load_coordinates()
#         self.master = master
#         Toplevel.__init__(self, master)
#         self.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
#
#         self.overrideredirect(override)
#         self.override = override
#         self.attributes('-topmost', True)
#         self.resizable(0, 0)
#         self.wm_attributes('-alpha', 0.7)
#         self.protocol('WM_DELETE_WINDOW', self.exit_)
#
#         self.bg = 'white'
#         self['bg'] = self.bg
#
#         self.canvas = Canvas(self, bg=self.bg)
#         self.back_image = None
#
#         self.label = Label(self.canvas, bg=self.bg, font='comicsans 9 italic')
#         self.config_label(os.path.basename(__media_paths__[_play_count.v]))
#
#         self.play_button = Button(self.canvas, relief='flat', bg=self.bg, bd=0, activebackground=self.bg,
#                                   command=self.pause_)
#         if player.get_state() == 3:
#             self.play_button['image'] = pause_image
#         else:
#             self.play_button['image'] = play_image
#         self.previous_button = Button(self.canvas, relief='flat', image=previous_image, command=previous_call,
#                                       bg=self.bg,
#                                       bd=0, activebackground=self.bg)
#         self.next_button = Button(self.canvas, relief='flat', image=next_image, command=next_call, bg=self.bg, bd=0,
#                                   activebackground=self.bg)
#
#         self.scale = RcScale(self, slider=True, value=0, width=self.width - 20, height=16,
#                              troughcolor1=rgb(240, 123, 7),
#                              troughcolor2='lightgrey',
#                              outline=self.bg, outwidth=6, relief='flat', bd=0,
#                              highlightthickness=0)
#
#         self.set_scale = True
#         self.set_by_slider = False
#         self.scale.bind("<ButtonRelease-1>", self.m_scale_release_call)
#         self.scale.bind('<B1-Motion>', self.m_scale_motion_call)
#         self.scale.bind("<Button-1>", self.m_scale_click_call)
#
#         self.label.place(x=5, y=5)
#         self.scale.place(x=5, y=30)
#         self.play_button.place(x=round((self.width - im_dim) / 2), y=self.height - im_dim - 5)
#         self.previous_button.place(x=round((self.width - im_dim * 3 - 20) / 2), y=self.height - im_dim - 5)
#         self.next_button.place(x=round((self.width + im_dim + 20) / 2), y=self.height - im_dim - 5)
#
#         self.canvas.pack(fill=BOTH, expand='yes')
#
#         self.bind('<space>', self.pause_)
#         self.bind('<Alt-Right>', next_call)
#         self.bind('<Alt-Left>', previous_call)
#         self.bind('<Up>', vol_in)
#         self.bind('<Down>', vol_dec)
#         self.bind('<Right>', forward)
#         self.bind('<Left>', backward)
#         self.bind('<Control-Up>', self.raise_main)
#         self.bind('<Shift-Up>', self.toggle_titlebar)
#         self.focus_force()
#         Controller.Instance = self
#
#     def load_coordinates(self):
#         if controller_coordinates.v == (None, None):
#             return screen_width - self.width - self.spadx, self.spady
#         return controller_coordinates.v
#
#     def save_coordinates(self):
#         controller_coordinates.v = self.winfo_rootx(), self.winfo_rooty()
#
#     def config_label(self, text):
#         if len(text) < 25:
#             self.label['text'] = f'{text}...'
#         else:
#             self.label['text'] = f'{text[0: 26]}...'
#
#     def pause_(self, event=None):
#         if player.get_state() == 3:
#             self.play_button['image'] = play_image
#         else:
#             self.play_button['image'] = pause_image
#         pause()
#
#     def m_scale_release_call(self, event):
#         # if self.set_by_slider:
#         #     value = self.scale.get_value_from_x(event.x)
#         #     player.set_position(value / 100)
#         self.set_scale = True
#
#     def m_scale_motion_call(self, event=None):
#         if self.set_by_slider:
#             value = self.scale.get_value_from_x(event.x)
#             player.set_position(value / 100)
#             self.scale.set(value)
#
#     def m_scale_click_call(self, event):
#         if player.get_state() in (3, 4):
#             self.set_scale = False
#             if self.scale.find_(event.x, event.y) == 'slider':
#                 self.set_by_slider = True
#             else:
#                 self.set_by_slider = False
#                 value = self.scale.get_value_from_x(event.x)
#                 player.set_position(value / 100)
#                 self.scale.set(value)
#
#     def auto_set(self):
#         if self.set_scale:
#             self.scale.set(player.get_position() * 100)
#
#     def raise_main(self, event=None):
#         self.master.update()
#         self.master.deiconify()
#         self.save_coordinates()
#         self.destroy()
#         Controller.Instance = None
#
#     def toggle_titlebar(self, event=None):
#         if self.override:
#             self.override = False
#         else:
#             self.override = True
#         self.overrideredirect(self.override)
#
#     def exit_(self):
#         if not self.override:
#             self.raise_main()
#
#
# # .......................................................functions............................
#
#
# def get_ex(file_name):
#     return os.path.splitext(file_name)[1]
#
#
# def get_pastinfo():
#     if fmpast.exists():
#         return fmpast.read_bytes()
#     return default_past_info
#
#
# def save_pastinfo():
#     if __media_paths__:
#         all_ = __media_paths__ + mpast_['past_media']
#         if len(all_) >= 50:
#             all_ = all_[:50]
#
#         _past_info_ = {'past_media': all_, 'play_count': _play_count.v, 'load_on_start': load_on_start.get(),
#                  'controller': control_win_check.get(), 'auto_play': _auto_play.get(), 'controller_coords': controller_coordinates.v}
#     else:
#         if fmpast.exists():
#             _past_info_ = {'past_media': mpast_['past_media'], 'play_count': _play_count.v, 'load_on_start': load_on_start.get(),
#                      'controller': control_win_check.get(), 'auto_play': _auto_play.get(),
#                      'controller_coords': controller_coordinates.v}
#         else:
#             _past_info_ = {'past_media': [], 'play_count': _play_count.v,
#                      'load_on_start': load_on_start.get(),
#                      'controller': control_win_check.get(), 'auto_play': _auto_play.get(),
#                      'controller_coords': controller_coordinates.v}
#     fmpast.write_bytes(_past_info_)
#
#
# def get_settings():
#     if fms.exists():
#         return fms.read_bytes()
#     return default_settings
#
#
# def save_settings():
#     info_dic = {'save_pos': save_pos.get(), 'vol_rate': default_vol_rate.v, 'seek_rate': default_seek_rate.v,
#                 'max_volume': max_volume.v, 'current_vol': current_vol.v, 'exit_check': exit_check.get(),
#                 'refresh_time': refresh_time_ms.v, 'scan_sub': scan_sub_on_load.get(), 'fulltime_state': fulltime_state.v}
#
#     fms.write_bytes(info_dic)
#
#
# def load_set():
#     if load_on_start.get() == 1:
#         print('activating')
#         status['text'] = 'auto load media on startup ENABLED'
#     else:
#         print('deactivating')
#         status['text'] = 'auto load media on startup DISABLED'
#
#
# def autoplay_set():
#     if _auto_play.get() == 1:
#         print('activating')
#         status['text'] = '_auto_play ENABLED'
#     else:
#         print('deactivating')
#         status['text'] = '_auto_play DISABLED'
#
#
# def load_playback_file():
#     if fmplayb.exists():
#         return fmplayb.read_bytes()
#     return {}
#
#
# def check_sysupdate():
#     if fmsys.exists():
#         sys_data = fmsys.read_bytes()
#         for m__ in sys_data:
#             if m__ not in __media_paths__:
#                 __media_paths__.append(m__)
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#         fmsys.delete()
#
#
# def load_past():
#     len_temp__ = len(__media_paths__)
#     _p_paths = mpast_['past_media']
#
#     if _p_paths:
#         for path_ in _p_paths:
#             if os.path.isfile(path_) and path_ not in __media_paths__:
#                 __media_paths__.append(path_)
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#
#         change_ = len(__media_paths__) - len_temp__
#         if change_ == 0:
#             if len_temp__ == 0:
#                 status['text'] = 'Load Failed'
#                 messagebox.showinfo('Load Failed', 'Previous Media Load Failed : DATA NOT ON DISK LOCATION')
#         elif change_ > 0:
#             if len_temp__ == 0:
#                 status['text'] = 'Load complete'
#                 count()
#
#     else:
#         status['text'] = 'No previous media to load'
#
#
# def sys_load():
#     if len(sys.argv) > 1:
#         sys_paths = sys.argv[1:]
#         for path_ in sys_paths:
#             if get_ex(path_) in all_format:
#                 if path_ not in __media_paths__:
#                     __media_paths__.append(path_)
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#         status['text'] = 'Load complete'
#         force()
#     else:
#         if fmsys.exists():
#             check_sysupdate()
#             force()
#         else:
#             try:
#                 if load_on_start.get() == 1:
#                     load_past()
#             except Exception as e:
#                 print(e)
#
#
# def quit_(event=None):
#     status['text'] = 'QUITING'
#     system_on.v = False
#     try:
#         save_playback(_play_count.v)
#         player.release()
#         if os.path.isfile(run_file):
#             os.remove(run_file)
#         fmsys.delete()
#     except Exception as e:
#         print_(f'cannot release : {e}')
#     save_pastinfo()
#     save_settings()
#     save_playback_file()
#     win.destroy()
#     sys.exit()
#
#
# def exit_diag():
#     if _fullscreen.v and FsDock.Instance is not None:
#         FsDock.Instance.attributes('-topmost', False)
#
#     def no(event=None):
#         if _fullscreen.v and FsDock.Instance is not None:
#             FsDock.Instance.attributes('-topmost', True)
#         status['fg'] = 'black'
#         status['text'] = 'HI There'
#         m.destroy()
#
#     if exit_check.get() == 1:
#         status['fg'] = 'red'
#         status['text'] = 'Do you really wanna quit'
#
#         m = Toplevel(win)
#         m.overrideredirect(True)
#         m.focus_force()
#         m.bind('<FocusOut>', lambda event_: m.destroy())
#         m.geometry(
#             f'{250}x{100}+{win.winfo_rootx() + round((win_width.v / 2) - 125)}+{win.winfo_rooty() + round((win_height.v / 2) - 70)}')
#         m_cap = Label(m, text='Do you really want to exit', font='comicsans 10 bold', width=32, height=3)
#         b1 = Button(m, text='  Yes  ', command=quit_, fg=rgb(240, 100, 100), font='comicsans 11', bd=0)
#         b2 = Button(m, text='  No  ', command=no, fg=rgb(100, 200, 100), font='comicsans 11', bd=0)
#
#         # theme
#         m['bg'] = rgb(65, 65, 65)
#         m_cap['bg'] = rgb(65, 65, 65)
#         m_cap['fg'] = rgb(190, 190, 190)
#         b1['bg'] = rgb(65, 65, 65)
#         b2['bg'] = rgb(65, 65, 65)
#         m_cap['relief'] = 'flat'
#         b1['relief'] = 'flat'
#         b1['activebackground'] = rgb(65, 65, 65)
#         b2['activebackground'] = rgb(65, 65, 65)
#         b1['activeforeground'] = rgb(255, 255, 255)
#         b2['activeforeground'] = rgb(255, 255, 255)
#         b2['relief'] = 'flat'
#         m.bind('<Return>', quit_)
#         m.bind('<Escape>', no)
#
#         m_cap.pack()
#         b1.pack(side=LEFT, anchor=SE, padx=10, pady=8)
#         b2.pack(side=RIGHT, anchor=SW, padx=10, pady=8)
#         win.wait_window(m)
#     else:
#         quit_()
#
#
# def save_playlist(event=None):
#     rp = fmplay.read_bytes()
#     if __media_paths__:
#         box = EncryptionBox(win, title='Save Playlist', caption='Create Encrypted Playlist')
#         win.wait_window(box)
#         play_name = box.name
#         if play_name is not None:
#             if play_name == '':
#                 messagebox.showerror('Error', 'Could not save playlist : NO INPUT TITLE')
#             else:
#                 print(play_name)
#                 if rp is None:
#                     fmplay.write_bytes({play_name: (__media_paths__, box.pass_)})
#                     status['text'] = f'Playlist {play_name} Saved'
#                 else:
#                     if play_name in rp.keys():
#                         messagebox.showerror('Error', 'Could not save playlist : PLAYLIST ALREADY EXISTS')
#                     else:
#                         rp.update({play_name: (__media_paths__, box.pass_)})
#                         fmplay.write_bytes(rp)
#                         status['text'] = f'Playlist {play_name} Saved'
#     else:
#         messagebox.showerror('Error', 'Could not save playlist : NO MEDIA CURRENTLY')
#
#
# def load_playlist(event=None):
#     rp__ = fmplay.read_bytes()
#     if rp__:
#         names = [*rp__]
#
#         def load(event_=None):
#
#             def in_():
#                 global __media_paths__
#                 play_name = list_box.get(ACTIVE)
#
#                 var_, paths_ = check_pass(play_name)
#                 if var_:
#                     for path_ in paths_:
#                         if not os.path.isfile(path_):
#                             paths_.remove(path_)
#
#                     if len(paths_) == 0:
#                         messagebox.showinfo('Load Failed', 'Playlist Load Failed : DATA NOT ON DISK LOCATION')
#                     else:
#                         if len(__media_paths__) > 0:
#                             overwrite_in = messagebox.askyesno('Load Playlist',
#                                                                'Do you want to overwrite existing playlist sequence ?')
#                             if overwrite_in:
#                                 __media_paths__ = paths_
#                                 if PlayWin.Instance is not None:
#                                     PlayWin.Instance.insert_pathseq(__media_paths__)
#                                 status['text'] = 'Playlist load complete'
#                                 stop()
#                                 force()
#                             else:
#                                 for path_ in paths_:
#                                     if path_ not in __media_paths__:
#                                         __media_paths__.append(path_)
#                                 if PlayWin.Instance is not None:
#                                     PlayWin.Instance.insert_pathseq(__media_paths__)
#                                 status['text'] = 'Playlist load complete'
#                         else:
#                             __media_paths__ = paths_
#                             if PlayWin.Instance is not None:
#                                 PlayWin.Instance.insert_pathseq(__media_paths__)
#                             status['text'] = 'Playlist load complete'
#                             stop()
#                             force()
#                         box.destroy()
#
#             try:
#
#
#             except KeyError:
#                 print_('select a playlist to load first')
#                 status['text'] = 'Playlist load failed'
#
#         def del_(event_=None):
#             try:
#                 play_name = list_box.get(ACTIVE)
#                 var_ = check_pass(play_name)[0]
#                 if var_:
#                     del rp__[play_name]
#                     list_box.delete(names.index(play_name))
#                     fmplay.write_bytes(rp__)
#             except KeyError:
#                 print_('no playlist to delete')
#
#         def check_pass(key, callback):
#             paths__, password__ = rp__[key]
#             if password__ == '':
#                 callback(True, paths__)
#             else:
#                 def command(val=""):
#                     if val == password__:
#                         callback(True, paths__)
#                     else:
#                         box_.show_final_snack('Playlist Access Unauthorized', duration=4000)
#                         callback(False, None)
#
#                 box_ = RcDiag(win, 'Playlist Encrypted', f'Enter the password of playlist : {key}', command=command, retain_value=False)
#                 box_.entry['show'] = '*'
#
#         status['text'] = 'Select Playlist'
#         box_width = 200
#         box_height = 170
#         box = Toplevel(win)
#         box.geometry(
#             f'{box_width}x{box_height}+{win.winfo_rootx() + round((win_width.v - box_width) / 2)}+{win.winfo_rooty() + round((win_height.v - box_height) / 2) - 45}')
#         box.overrideredirect(True)
#         box.bind('<FocusOut>', lambda event_: box.destroy())
#         box.bind('<Escape>', lambda event_: box.destroy())
#         box['bg'] = rgb(90, 90, 90)
#
#         cap = Label(box, text='Select Playlist to load', font="comicsans 10 bold", borderwidth=16, relief="flat",
#                     bg=rgb(90, 90, 90), fg=rgb(240, 240, 240))
#         list_box = Listbox(box, borderwidth=5, relief='groove', width=10, height=5, highlightcolor=rgb(90, 90, 90),
#                            selectmode=SINGLE, bg=rgb(65, 65, 65), fg=rgb(200, 200, 200), activestyle='dotbox',
#                            selectbackground=rgb(45, 45, 45), selectforeground=rgb(240, 240, 240), bd=2,
#                            font='comicsans 9 bold')
#
#         list_box.bind('<Double-Button>', load)
#         load_button = Button(box, text='Load', font='comicsans 10 bold', relief='flat', borderwidth=0, command=load,
#                              bg=rgb(90, 90, 90), fg=rgb(240, 240, 240), activebackground=rgb(120, 120, 120),
#                              activeforeground=rgb(240, 240, 240))
#         del_button = Button(box, text='Delete', font='comicsans 10 bold', relief='flat', borderwidth=0, command=del_,
#                             bg=rgb(90, 90, 90), fg=rgb(240, 240, 240), activebackground=rgb(120, 120, 120),
#                             activeforeground=rgb(240, 240, 240))
#
#         for name in names:
#             list_box.insert(END, name)
#
#         list_box.focus_set()
#         list_box.bind('<Return>', load)
#         list_box.bind('<Delete>', del_)
#
#         # pack
#         cap.pack()
#         list_box.pack(fill='both')
#         load_button.pack(side=LEFT, anchor=SW, padx=10, pady=5)
#         del_button.pack(side=RIGHT, anchor=SE, padx=10, pady=5)
#         win.wait_window()
#     else:
#         config_status('No playlist to load, save one first')
#         messagebox.showwarning('No playlist', 'could not load : NO SAVED PLAYLIST')
#
#
# def openfile(event=None):
#     config_status('Trying to laod Media')
#     file_paths_of = filedialog.askopenfilenames(initialdir="C;\\", title="Open", filetypes=(
#         ('Media Files',
#          '*.wav *.3ga *.669 *.a52 *.aac *.ac3 *.adt *.adts *.aif *.aif *.aifc *.aiff *.amr *.aob *.ape *.awb '
#          '*.caf *.dts *.flac *.it *.m4a *.kar *.m4b *.m4p *.m5p *.mid *.mka *.mlp *.mod *.mpa *.mp1 *.mp2 *.mp3 *.mpc '
#          '*.ogg *.oga *.mus *.mpga *.mp4 *.mkv *.3g2 *.3gp *.3gp2 *.3gpp *.amv *.asf *.avi *.bik *.bin *.divx *.drc '
#          '*.dv *.f4v *.flv *.gvi *.gfx *.iso *.m1v *.m2v *.m2t *.m2ts *.m4v *.mov *.mp2 *.mp2v *.mp4v *.mpe *.mpeg '
#          '*.mpeg1 *.mpeg2 *.mpeg4 *.mpg *.gif *.webm'),
#         ('.Audio',
#          '*.wav *.3ga *.669 *.a52 *.aac *.ac3 *.adt *.adts *.aif *.aif *.aifc *.aiff *.amr *.aob *.ape *.awb '
#          '*.caf *.dts *.flac *.it *.m4a *.kar *.m4b *.m4p *.m5p *.mid *.mka *.mlp *.mod *.mpa *.mp1 *.mp2 *.mp3 *.mpc '
#          '*.ogg *.oga *.mus *.mpga'),
#         ('.Video',
#          '*.mp4 *.mkv *.3g2 *.3gp *.3gp2 *.3gpp *.amv *.asf *.avi *.bik *.bin *.divx *.drc *.dv *.f4v ''*.flv '
#          '*.gvi *.gfx *.iso *.m1v *.m2v *.m2t *.m2ts *.m4v *.mov *.mp2 *.mp2v *.mp4v *.mpe *.mpeg *.mpeg1 *.mpeg2'
#          ' *.mpeg4 *.mpg *.gif *.webm'), ('.all files', '*.*')))
#
#     if len(file_paths_of) > 0:
#         len_temp_ = len(__media_paths__)
#         for path_ in file_paths_of:
#             if get_ex(path_).lower() in all_format and path_ not in __media_paths__:
#                 __media_paths__.append(path_)
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#
#         change_ = len(__media_paths__) - len_temp_
#         if change_ > 0:
#             if len_temp_ == 0:
#                 stop()
#                 force()
#             config_status('Media load complete')
#
#
# def scan_folder_ui(event=None):
#     start_dir = filedialog.askdirectory(initialdir='C;\\', title='Open Folder', mustexist=True)
#
#     if start_dir:
#         config_status('Loading Media')
#         scanner_thread = Thread(target=scan_folder, args=(start_dir,))
#         scanner_thread.setDaemon(True)
#         scanner_thread.start()
#
#
# def scan_folder(start_dir):
#     files_in_dir = search_exts(ext_list=all_format, start=start_dir, mode='path')
#     if len(files_in_dir) > 0:
#         len_temp_ = len(__media_paths__)
#         for path_ in files_in_dir:
#             if path_ not in __media_paths__:
#                 __media_paths__.append(path_)
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#
#         change_ = len(__media_paths__) - len_temp_
#         if change_ > 0:
#             if len_temp_ == 0:
#                 stop()
#                 force()
#             config_status('Media load complete')
#     else:
#         messagebox.showinfo('Load Media', 'No Media found in specified directpry : NO MEDIA IN DIR')
#
#
# def _save_as_(event=None):
#     if PlayWin.Instance is None:
#         file_path__ = __media_paths__[_play_count.v]
#     else:
#         file_path__ = __media_paths__[PlayWin.Instance.get_active()]
#     if file_path__:
#         ext__ = os.path.splitext(file_path__)[1]
#         new_path__ = filedialog.asksaveasfilename(initialdir="C;\\", title="SAVE AS",
#                                                   filetypes=[(f'Default : {ext__}', ext__), ('All Files', '*')],
#                                                   defaultextension=ext__)
#         if new_path__:
#             p_ = Thread(target=fmpast.copy, args=(new_path__, file_path__))
#             p_.setDaemon(True)
#             p_.start()
#
#
# def set_playback_speed():
#     config_status('Set Playback Speed')
#     box_ = RcDiag(win, "playback Speed", "Enter the playback speed", size=(200, 120), retain_value=True)
#     win.wait_window(box_)
#     __speed_in__ = box_.value
#     if __speed_in__:
#         try:
#             speed = float(__speed_in__)
#         except Exception as e:
#             print_(e)
#             messagebox.showwarning("Wrong Input", 'Can only be float : INVALID INPUT DATA')
#             set_playback_speed()
#         else:
#             player.set_rate(speed)
#
#
# def remove_media(event=None):
#     if PlayWin.Instance is not None:
#         m_in = PlayWin.Instance.get_active()
#         if m_in is not None:
#             try:
#                 if _play_count.v == m_in or _play_count.v == (m_in - len(__media_paths__)):
#                     if player.get_state() in (3, 4):
#                         stop()
#                         path_temp = '/////'  # had to play again
#                     else:
#                         path_temp = '////////'  # no need to play
#                     config_status('Selected media removed')
#                 else:
#                     path_temp = __media_paths__[_play_count.v]
#
#                 __media_paths__.pop(m_in)
#                 PlayWin.Instance.pop(m_in)
#                 if path_temp == '/////':
#                     count()
#                 elif path_temp == '////////':
#                     if _play_count.v >= len(__media_paths__):
#                         _play_count.v = 0
#                 else:
#                     _play_count.v = __media_paths__.index(path_temp)
#
#             except Exception as e:
#                 print_(f'exception while removing media : {e}')
#
#
# def clear_playlist():
#     if __media_paths__:
#         if player.get_state() in (3, 4):
#             stop()
#
#         __media_paths__.clear()
#         canvas.delete('all')
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.clear()
#
#         config_status('Playlist Cleared')
#         nothing_special()
#
#
# def shuffle(event=None):
#     global __media_paths__
#     stop()
#     if __media_paths__:
#         config_status('Playlist Shuffled')
#         random.shuffle(__media_paths__)
#         canvas.delete('all')
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.insert_pathseq(__media_paths__)
#     force()
#
#
# def toogle_playlist(event=None):
#     if PlayWin.Instance is None:
#         if _fullscreen.v:
#             pos = (win_width.v - 320, win_height.v - 450)
#         else:
#             pos = (screen_width - 320, screen_height - 480)
#         PlayWin(master=win, title='Playlist', size=(310, 410),
#                 pos=pos)
#         PlayWin.Instance.insert_pathseq(__media_paths__)
#         PlayWin.Instance.focus_set()
#
#         playmenu.entryconfig(0, label="Hide Playlist")
#         config_status('Playlist Unhidden')
#     else:
#         PlayWin.Instance.destroy_()
#
#
# # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<     AUDIO AND SUBTITLE TRACKS    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
# def disable_sub():
#     player.video_set_spu(-1)
#
#
# def get_audio_sub_track():
#     global audio_id
#
#     exsub_list.clear()  # resetting exsub_list as media changes
#     audio_track.delete(0, END)
#     sub_menu.delete(0, END)
#     set_fulltime(fulltime)
#     if _fullscreen.v and FsDock.Instance is not None:
#         set_fulltime(FsDock.Instance.f_time)
#     sub_menu.add_command(label='Disable', command=disable_sub)
#
#     audio_list = player.audio_get_track_description()
#
#     if len(audio_list) > 0:
#         audio_id = list(list(zip(*audio_list))[0])
#     else:
#         audio_id = []
#
#     sub_list = player.video_get_spu_description()
#     for aid, audio in audio_list:
#         audio_track.add_command(label=audio, command=lambda arg=aid: set_audio_track(arg))
#     if sub_list:
#         video_menu.entryconfigure(0, state=NORMAL)
#         for sid, sub in sub_list:
#             if sid != -1:
#                 sub_menu.add_command(label=sub, command=lambda arg=sid: set_sub(arg))
#     else:
#         video_menu.entryconfigure(0, state=DISABLED)
#         video_menu.entryconfigure(3, state=DISABLED)
#
#     player.audio_set_volume(round(current_vol.v))
#
#     if scan_sub_on_load.get() == 1:
#         auto_scan_sub()
#
#
# def change_audio_track(event=None):
#     if len(audio_id) >= 3:
#         current_id_ = player.audio_get_track()
#         choice = random.choice(audio_id)
#         while choice == -1 or choice == current_id_:
#             choice = random.choice(audio_id)
#
#         set_audio_track(choice)
#
#
# def set_audio_track(value):
#     player.audio_set_track(value)
#
#
# def set_sub(value):
#     player.video_set_spu(value)
#     video_menu.entryconfigure(3, state=NORMAL)
#
#
# def set_sub_file(path_):
#     player.video_set_subtitle_file(path_)
#     video_menu.entryconfigure(3, state=NORMAL)
#     video_menu.entryconfigure(0, state=NORMAL)
#
#
# def add_sub():
#     if get_ex(__media_paths__[_play_count.v]) in video_format:
#         sub_path = filedialog.askopenfilename(initialdir="C;\\", title="Add Subtitle", filetypes=(
#             ('Subtitle file',
#              '*.srt *.aqt *.cvd *.dks *.jss *.sub *.ttxt *.mpl *.txt *.pjs *.psb *.rt *.smi *.ssf *.ssa *.svcd *.usf *.idx'),
#             ('all files', '*.*')))
#         sub_path = str(Path(sub_path))
#         if sub_path not in exsub_list:
#             exsub_list.append(sub_path)
#             sub_dir, sub_name = os.path.split(sub_path)
#             sub_menu.add_command(label=sub_name[0:30], command=lambda arg=sub_path: set_sub_file(arg))
#             set_sub_file(sub_path)
#     else:
#         messagebox.showerror("Invalid Format", 'Media file do not support subtitles : INVALID FORMAT')
#
#
# def auto_scan_sub(event=None):
#     if __media_paths__:
#         m_path = __media_paths__[_play_count.v]
#         if get_ex(m_path) in video_format:
#             start_dir = os.path.split(m_path)[0]
#             sub_files_ = [os.path.join(start_dir, f) for f in os.listdir(start_dir) if
#                           os.path.isfile(os.path.join(start_dir, f)) and os.path.splitext(f)[
#                               1].lower() in subtitles_format]
#
#             # sub_files_ = search_exts(subtitles_format, os.path.split(m_path)[0])
#
#             def set_sub_file__(sub_path):
#                 sub_path = str(Path(sub_path))
#                 if sub_path not in exsub_list:
#                     exsub_list.append(sub_path)
#                     sub_dir, sub_name = os.path.split(sub_path)
#                     sub_menu.add_command(label=sub_name[0:30], command=lambda arg=sub_path: set_sub_file(arg))
#                 set_sub_file(sub_path)
#                 box_.destroy()
#
#             def focus__(index):
#                 if index >= len(buttons):
#                     index = 0
#                 elif index == -1:
#                     index = len(buttons) - 1
#                 buttons[index].focus_set()
#
#             if len(sub_files_) > 0:
#                 print('subtitles found')
#                 box_ = Toplevel(win)
#                 # box_.attributes('-topmost', True)
#                 buttons = []
#                 box_width = 360
#                 button_h = 40
#                 pady = 7
#                 box_height = ((button_h + pady) * len(sub_files_)) + pady
#                 box_.geometry(
#                     f'{box_width}x{box_height}+{win.winfo_rootx() + round((win_width.v - box_width) / 2)}+{win.winfo_rooty() + round((win_height.v - box_height) / 2) - 45}')
#                 box_.overrideredirect(True)
#                 box_.resizable(0, 0)
#                 box_.title('Subtitles Scan Result')
#                 box_.focus_set()
#                 box_bg = rgb(90, 90, 90)
#                 box_['bg'] = box_bg
#                 for ind, path_ in enumerate(sub_files_):
#                     buttons.append(
#                         Button(box_, text=os.path.split(path_)[1][0:57], font='Times 11', bg=box_bg,
#                                fg=rgb(255, 255, 255),
#                                relief='flat', activebackground=box_bg, bd=0,
#                                command=lambda arg=path_: set_sub_file__(arg),
#                                activeforeground='white', anchor='w'))
#                     buttons[ind].place(x=10, y=(button_h * ind) + pady, height=button_h, width=box_width - 20)
#                     buttons[ind].bind('<Return>', lambda event_, arg_=path_: set_sub_file__(arg_))
#                     buttons[ind].bind('<Up>', lambda event_, arg_=ind - 1: focus__(arg_))
#                     buttons[ind].bind('<Down>', lambda event_, arg_=ind + 1: focus__(arg_))
#                 buttons[0].focus_set()
#
#                 def destroy_():
#                     f_widget = box_.focus_get()
#                     if f_widget not in buttons and f_widget != box_:
#                         box_.destroy()
#
#                 box_.bind('<FocusOut>', lambda event_: destroy_())
#             else:
#                 if event is not None:
#                     messagebox.showinfo('Scan Subtitles', 'No subtitles found in current media directory')
#
#         else:
#             if event is not None:
#                 messagebox.showwarning('Scan Subtitles', 'Media unsupported : INVALID FORMAT')
#
#
# def set_spu_delay():
#     if player.video_get_spu() != -1:
#         box = RcDiag(win, 'Subtitle Delay', 'Set Subtitle Delay (in milliseconds)', retain_value=True)
#         win.wait_window(box)
#
#         delay_ = box.value
#         if delay_:
#             try:
#                 delay_ = int(box.value) * 1000
#                 player.video_set_spu_delay(delay_)
#             except Exception as e:
#                 print_(e)
#                 messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT')
#                 set_spu_delay()
#     else:
#         messagebox.showerror("Error", 'Select a subtitle track first : SYNC ERROR')
#
#
# def default_aspect():
#     player.video_set_aspect_ratio(None)
#
#
# def set_aspect_ratio(event=None, string=None):
#     if event:
#         string = str(aspect_ratio_list[aspect_ratio_index.v])
#         if aspect_ratio_index.v < len(aspect_ratio_list) - 1:
#             aspect_ratio_index.v += 1
#         else:
#             aspect_ratio_index.v = 0
#     if string is None:
#         box = RcDiag(win, 'Set Aspect Ratio', 'Enter aspect ratio (like 16:9)', entry_size=None, retain_value=True)
#         win.wait_window(box)
#         value = str(box.value)
#         if value:
#             try:
#                 w, h = value.split(':')
#                 w = int(w)
#                 h = int(h)
#             except Exception as e:
#                 print_(e)
#                 messagebox.showerror("Error", 'video configuration failed : INVALID ASPECT RATIO')
#             else:
#                 player.video_set_aspect_ratio(value)
#     else:
#         player.video_set_aspect_ratio(string)
#
#
# # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  MAIN PLAY FUNCTION         >>>>>>>>
# def force(event=None):
#     if __media_paths__:
#         if player.get_state() in (3, 4):
#             save_playback(_play_count.v)
#         _play_count.v = 0
#         mediascale.set(0)
#         m_name_ = os.path.basename(__media_paths__[0])
#         media = main_player_in.media_new(__media_paths__[0])
#         player.set_media(media)
#         player.play()
#         win.title(f"{wintitle}               {m_name_}")
#         config_status(os.path.basename(m_name_))
#         print_(f"now playing {os.path.basename(m_name_)}")
#         set_()
#
#
# def count(event=None):
#     print('case of count : ' + str(_play_count.v))
#     if __media_paths__:
#         if _play_count.v >= len(__media_paths__):
#             _play_count.v = 0  # resetting _play_count
#
#         media = main_player_in.media_new(__media_paths__[_play_count.v])
#         m_name_ = os.path.basename(__media_paths__[_play_count.v])
#         player.set_media(media)
#         player.play()
#         win.title(f"{wintitle}               {m_name_}")
#         config_status(f'Now playing  {m_name_}')
#         print_(f"now playing {m_name_}")
#         set_()
#
#
# def active(event=None):
#     if PlayWin.Instance is not None:
#         try:
#             if player.get_state() in (3, 4):
#                 save_playback(_play_count.v)
#             m_index = PlayWin.Instance.get_active()
#             if m_index is not None:
#                 _play_count.v = m_index
#         except Exception as e:
#             print_(e)
#         count()
#
#
# def set_(mode='normal', stream_title='Streaming'):  # can be stream also
#     try:
#         mediascale.enable()
#         if _fullscreen.v and FsDock.Instance is not None:
#             FsDock.Instance.m_scale['state_'] = NORMAL
#         play_button['image'] = pause_image
#         play_button['command'] = pause
#         playback.entryconfigure(11, label="          Pause")
#         win.bind("<space>", pause)
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.bind("<space>", pause)
#
#         if mode == 'normal':
#             win.stream_title = None
#             m_path = __media_paths__[_play_count.v]
#             ex = get_ex(m_path)
#
#             if Controller.Instance is not None:
#                 Controller.Instance.config_label(os.path.basename(m_path))
#
#             if ex.lower() in song_format:
#                 set_image(__media_paths__[_play_count.v])
#                 video_menu.entryconfigure(6, state=DISABLED)
#                 video_menu.entryconfigure(8, state=DISABLED)
#             else:
#                 if thumbnail_info[0] != -1:
#                     canvas.delete(thumbnail_info[0])
#                     thumbnail_info[0] = -1
#
#                 video_menu.entryconfigure(6, state=NORMAL)
#                 video_menu.entryconfigure(8, state=NORMAL)
#
#             if save_pos.get() == 1:
#                 if m_path in playback_dict:
#                     if Playback_Win.Instance is None:
#                         Playback_Win(win, 'Do you want to resume where you left', callback=set_playback)
#                     else:
#                         Playback_Win.Instance.reset_timer()
#                 else:
#                     if Playback_Win.Instance is not None:
#                         Playback_Win.Instance.destroy_()
#         else:
#             win.stream_title = stream_title
#             if Controller.Instance is not None:
#                 Controller.Instance.config_label(stream_title)
#
#         win.after(700, get_audio_sub_track)
#
#         player.audio_set_volume(round(current_vol.v))
#         print_(f'player vol : {round(current_vol.v)}')
#
#     except Exception as e:
#         print_(e)
#
#
# # ..........................................................................................
# def set_image(file_path__):
#     if thumbnail_info[0] != -1:
#         canvas.delete(thumbnail_info[0])
#         thumbnail_info[0] = -1
#
#     im__ = fmpast.image_from_song(file_path__)
#     if im__ is not None:
#         thumbnail_info[1] = width, height = im__.size
#         win.im__ = im__ = PIL.ImageTk.PhotoImage(im__)
#         thumbnail_info[0] = canvas.create_image(round((win_width.v - width) / 2), round((win_height.v - height) / 2),
#                                                 image=im__, anchor=NW)
#
#
# def screenshot(event=None):
#     m_name, m_ext = os.path.splitext(os.path.basename(__media_paths__[_play_count.v]))
#     if m_ext in video_format:
#         hr_, min_, sec_ = format_mills(player.get_time())
#         name = f'{m_name} {hr_}:{min_}:{sec_}.jpg'
#         player.video_take_snapshot(0, os.path.join(screenshot_dir, name), player.video_get_size()[0],
#                                    player.video_get_size()[1])
#
#
# def stream_(event=None):
#     StreamBox(win, stream_call=player_set_url)
#
#
# def player_set_url(url=None, title='Streaming'):
#     """
#         info_object :tuple(type_, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
#     """
#     if url is None:
#         return
#     media = main_player_in.media_new(url)
#     media.get_mrl()
#     player.set_media(media)
#     win.title(f"{wintitle}               {title}")
#     config_status(f' {title}')
#     canvas.delete('all')
#
#     player.play()
#     set_(mode='stream', stream_title=title)
#
#
# def pause(event=False):
#     if len(__media_paths__) == 0:
#         config_status('Add media first')
#         messagebox.showinfo('Warning', 'Add Media First : NO MEDIA')
#
#     else:
#         if player.get_state() == 3:
#             play_button['image'] = play_image
#             playback.entryconfigure(11, label="          Resume", image=playi)
#             config_status('Paused')
#         else:
#             play_button['image'] = pause_image
#             config_status('Resumed')
#             playback.entryconfigure(11, label="          Pause", image=pausei)
#
#         play_button['command'] = pause
#         win.bind("<space>", pause)
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.bind("<space>", pause)
#     player.pause()
#
#
# #      ...............................MAIN THREAD .....................................................
# def __main_ui__():
#     try:
#         _state_ = player.get_state()
#         if _state_ == 6:
#             if _auto_play.get() == 1:
#                 if len(__media_paths__) == 1:
#                     force()
#                 elif len(__media_paths__) > 1:
#                     _play_count.v += 1
#                     config_status('Playing next')
#                     print_(f'next...{_play_count.v}')
#                     count()
#             else:
#                 nothing_special()
#
#         elif _state_ in (3, 4):
#             if _fullscreen.v:
#                 if FsDock.Instance is not None:
#                     set_ctime(FsDock.Instance.c_time, FsDock.Instance.f_time)
#                     FsDock.Instance.auto_set()
#                 Set_dock()
#             else:
#                 if _auto_mscale:
#                     pos = player.get_position()
#                     mediascale.set(pos * 100)
#                 set_ctime(currenttime, fulltime)
#
#             if win.state_() == 'iconic' and control_win_check.get() == 1:
#                 if Controller.Instance is None:
#                     if PlayWin.Instance is not None:
#                         toogle_playlist()
#                     Controller(win)
#                     if win.stream_title is None:
#                         Controller.Instance.config_label(os.path.basename(__media_paths__[_play_count.v]))
#                     else:
#                         Controller.Instance.config_label(win.stream_title)
#                     Controller.Instance.auto_set()
#                 else:
#                     Controller.Instance.auto_set()
#
#         if win.state_() != 'iconic' and Controller.Instance is not None:
#             Controller.Instance.raise_main()
#
#         if _resize.v:
#             __resize_ui__(win_width.v, win_height.v)
#             _resize.v = False
#
#         check_sysupdate()
#     except Exception as e:
#         print(f'exception in main_thread : {e}')
#     if system_on.v:
#         win.after(refresh_time_ms.v, __main_ui__)
#
#
# def set_ctime(label, label2=None):
#     c_time_ = player.get_time()
#     hr_, min_, sec_ = format_mills(c_time_)
#
#     if int(hr_):
#         label['text'] = f'{hr_}:{min_}:{sec_}'
#     else:
#         label['text'] = f'{min_}:{sec_}'
#
#     if fulltime_state == 1 and label2 is not None:
#         f_time = player.get_length()
#         hr_f, min_f, sec_f = format_mills(f_time - c_time_)
#         if f_time // 1000 >= 3600:
#             label2['text'] = f'-{hr_f}:{min_f}:{sec_f}'
#         else:
#             label2['text'] = f'-{min_f}:{sec_f}'
#
#
# def set_fulltime(label):
#     hr_, min_, sec_ = format_mills(player.get_length())
#
#     if int(hr_):
#         label['text'] = f'{hr_}:{min_}:{sec_}'
#     else:
#         label['text'] = f'{min_}:{sec_}'
#
#
# def __resize_ui__(width_, height_):
#     # resizing
#     if not _fullscreen.v:
#         canvas['height'] = height_ - dockh
#         placeconfig_w(width_)
#
#         if thumbnail_info[0] != -1:
#             width, height = thumbnail_info[1]
#             canvas.coords(thumbnail_info[0], int((width_ - width) / 2),
#                           int((height_ - play_button['height'] - 34 - height) / 2))
#
#         if Playback_Win.Instance is not None:
#             Playback_Win.Instance.place_config_w(width_)
#
#
# def __check_resize__(event):
#     if event.widget == win:
#         if win_width.v != event.width or win_height.v != event.height:
#             win_width.v, win_height.v = event.width, event.height
#             print_('you resize__')
#             _resize.v = True
#
#
# def nothing_special():
#     play_button['image'] = play_image
#     play_button['command'] = count
#     win.bind("<space>", count)
#     if PlayWin.Instance is not None:
#         PlayWin.Instance.bind("<space>", count)
#
#     currenttime['text'] = '--:--'
#     fulltime['text'] = '--:--'
#     mediascale.set(0)
#     mediascale.disable()
#     config_status('Ended , tap _auto_play to continue playback')
#
#     canvas.delete('all')
#     thumbnail_info[0] = -1
#
#
# def save_playback(index):
#     if save_pos.get() == 1:
#         try:
#             time = player.get_time()
#             if time and int(time) > 10000:  # saving playback only if played for more then 10000
#                 pos = player.get_position()
#                 path_ = __media_paths__[index]
#                 playback_dict[path_] = pos
#         except Exception as e:
#             print_(e)
#
#
# def stop(event=None):
#     def main_stop():
#         play_button['image'] = play_image
#         play_button['command'] = count
#         win.bind('<space>', count)
#
#         if PlayWin.Instance is not None:
#             PlayWin.Instance.bind("<space>", count)
#
#         save_playback(_play_count.v)
#
#         player.stop()
#         mediascale.set(0)
#         mediascale.disable()
#
#         currenttime['text'] = '--:--'
#         fulltime['text'] = '--:--'
#         config_status('Stopped')
#
#         if _fullscreen.v and FsDock.Instance is not None:
#             FsDock.Instance.c_time['text'] = '--:--'
#             FsDock.Instance.f_time['text'] = '--:--'
#             FsDock.Instance.m_scale.set(0)
#             FsDock.Instance.m_scale['state_'] = DISABLED
#
#         if thumbnail_info[0] != -1:
#             canvas.delete(thumbnail_info[0])
#             thumbnail_info[0] = -1
#
#     if event:
#         if not _stop:
#             _stop.v = True
#             main_stop()
#             win.after(delay, _stop)
#     else:
#         main_stop()
#
#
# def save_playback_file():
#     fmplayb.write_bytes(playback_dict)
#
#
# def set_playback(event=None):
#     try:
#         if save_pos.get() == 1:
#             pos = playback_dict[__media_paths__[_play_count.v]]
#             player.set_position(pos)
#             if event and Playback_Win.Instance is not None:
#                 Playback_Win.Instance.destroy_()
#     except KeyError:
#         print('no saved playback')
#
#
# def next_call(event=False):
#     if len(__media_paths__) > 1 and not _next:
#         _next.v = True
#         stop()
#         config_status('Playing next')
#         _play_count.v += 1
#         count()
#         win.after(delay, _next)  # resetting _next after delay
#
#
# def previous_call(event=False):
#     if len(__media_paths__) > 1 and not _previous:
#         _previous.v = True
#         stop()
#         config_status('Playing Previous')
#         _play_count.v -= 1
#         count()
#         win.after(delay, _previous)  # resetting _next after delay
#
#
# def forward(event=False):
#     if event:
#         player.set_time(player.get_time() + (default_seek_rate.v * 1000))
#     else:
#         box_ = RcDiag(win, "Seek Forward", "Enter the time to seek forward (in seconds)", size=(300, 120),
#                       retain_value=True)
#         win.wait_window(box_)
#         seek__ = box_.value
#         if seek__:
#             try:
#                 seek__ = int(seek__)
#             except Exception as e:
#                 print_(e)
#                 messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT')
#                 forward()
#             else:
#                 player.set_time(player.get_time() + (seek__ * 1000))
#
#
# def backward(event=False):
#     if event:
#         current_time_ = player.get_time()
#         if current_time_ <= default_seek_rate.v * 1000:
#             player.set_position(0)
#         else:
#             player.set_time(current_time_ - (default_seek_rate.v * 1000))
#     else:
#         box = RcDiag(win, "Seek Backward", "Enter the time to seek backward (in seconds)", size=(300, 120),
#                      retain_value=True)
#         win.wait_window(box)
#         seek__ = box.value
#         if seek__:
#             try:
#                 seek__ = int(seek__)
#             except Exception as e:
#                 print_(e)
#                 messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT')
#                 backward()
#             else:
#                 player.set_time(player.get_time() - (seek__ * 1000))
#
#
# def vol_in(event=None):
#     if event:
#         config_status('Volume increasing')
#         if default_vol_rate.v > 0:
#             current_ = int(player.audio_get_volume()) if player.get_state() in (3, 4) else (
#                                                                                                    audio_scale.value * max_volume.v) / 100
#             if current_ >= max_volume.v - default_vol_rate.v:
#                 current_vol.v = max_volume.v
#             else:
#                 current_vol.v = current_ + default_vol_rate.v
#             aset_(current_vol.get())
#
#
# def vol_dec(event=None):
#     if event:
#         config_status('Volume decreasing')
#         if default_vol_rate.v > 0:
#             current_ = int(player.audio_get_volume()) if player.get_state() in (3, 4) else (
#                                                                                                    audio_scale.value * max_volume.v) / 100
#             if current_ <= default_vol_rate.v:
#                 current_vol.v = 0
#             else:
#                 current_vol.v = current_ - default_vol_rate.v
#             aset_(current_vol.v)
#
#
# def setspecifictime():
#     box = RcDiag(win, "Jump to time", "Enter the time to jump on (in seconds)", size=(300, 120))
#     win.wait_window(box)
#     time = box.value
#     if time:
#         try:
#             ntime = int(time) * 100
#             player.set_time(ntime)
#         except Exception as e:
#             print_(f'exception in rendering specific time : {e}')
#             messagebox.showwarning("Wrong Input", 'Can only be integer : INVALID INPUT')
#             setspecifictime()
#
#
# def _mscale_release_call(event=None):
#     _auto_mscale.v = True
#
#
# def _mscale_motion_call(event):
#     if _set_by_slider.v:
#         value = mediascale.get_value_from_x(event.x)
#         player.set_position(value / 100)
#         mediascale.set(value)
#
#
# def _mscale_press_call(event):
#     if player.get_state() in (3, 4):
#         _auto_mscale.v = False
#         _part_ = mediascale.find_(event.x, event.y)
#         if _part_ == 'slider':
#             _set_by_slider.v = True
#         else:
#             _set_by_slider.v = False
#             value = mediascale.get_value_from_x(event.x)
#             player.set_position(value / 100)
#             mediascale.set(value)
#
#
# def _ascale_press_call(event):
#     part__ = audio_scale.find_(event.x, event.y)
#     if part__ == 'slider':
#         _set_a_by_slider.v = True
#     else:
#         current_vol.v = (audio_scale.get_value_from_x(event.x) * max_volume.v) / 100
#         aset_(current_vol.v)
#         _set_a_by_slider.v = False
#
#
# def _ascale_motion_call(event):
#     if _set_a_by_slider.v:
#         current_vol.v = (audio_scale.get_value_from_x(event.x) * max_volume.v) / 100
#         aset_(current_vol.v)
#
#
# def aset_(vol):
#     try:
#         player.audio_set_volume(round(vol))
#     except Exception as e:
#         print_(e)
#     if vol >= round(max_volume.v * .667):
#         audio_scale.itemconfig(audio_scale.in_rect, fill=rgb(205, 92, 92))
#     else:
#         audio_scale.itemconfig(audio_scale.in_rect, fill=audio_scale.trough_color1)
#     audio_scale.set((vol / max_volume.v) * 100)
#
#     # if VolWin.Instance is not None:
#     #     VolWin.Instance.update_(vol)
#     #     VolWin.Instance.attributes('-topmost', True)
#     # else:
#     #     VolWin(win, range_=max_volume.v)
#     #     VolWin.Instance.draw(vol)
#
#
# def mute(event=None):
#     status__ = player.audio_get_mute()
#     if not status__:
#         player.audio_set_mute(True)
#         audio_menu.entryconfigure(2, label='      Unmute', image=unmutei)
#     else:
#         player.audio_set_mute(False)
#         audio_menu.entryconfigure(2, label='      Mute', image=mutei)
#
#
# def hide_menu(event=None):
#     if _main_menu:
#         win.config(menu=empty_menu)
#         _main_menu.v = False
#
#
# def toggle_menu(event=None):
#     if _main_menu:
#         win.config(menu=empty_menu)
#         _main_menu.v = False
#     else:
#         win.config(menu=menubar)
#         _main_menu.v = True
#
#
# def Set_dock():
#     pos_ = win.winfo_pointerxy()
#
#     if _mouse_pos.v == -1:
#         _mouse_pos.v = pos_
#     else:
#         if _mouse_pos.v != pos_:  # mouse is in motion
#             if FsDock.Instance is not None:
#                 if FsDock.Instance.mouse_over(pos_):
#                     print('mouse_over')
#                     FsDock.Instance.d_timer_cancel()
#                 else:
#                     print('no mouse')
#                     FsDock.Instance.d_timer_reset()
#             else:
#                 FsDock(master=win, canvas_=canvas, player_=player)
#                 set_fulltime(FsDock.Instance.f_time)
#         _mouse_pos.v = pos_
#
#
# def toggle_fullscreen(event=None):
#     if _fullscreen.v:
#         win.attributes('-fullscreen', False)
#         win.attributes('-topmost', False)
#         try:
#             if FsDock.Instance is not None:
#                 FsDock.Instance.attributes('-topmost', False)
#                 FsDock.Instance.d_timer_cancel()
#                 FsDock.Instance.destroy_()
#
#         except Exception as e:
#             print_(e)
#         if not _main_menu:
#             toggle_menu()
#         video_menu.entryconfigure(5, label='Fullscreen')
#         win.update_idletasks()
#         w, h = win_width.v, win_height.v
#
#         canvas['height'] = h - dockh
#         dock.pack(fill=X, expand='yes', anchor=SW, side=BOTTOM)
#         _fullscreen.v = False
#     else:
#         win.attributes('-fullscreen', True)
#         hide_menu()
#         dock.pack_forget()
#         canvas['height'] = screen_height
#
#         if thumbnail_info[0] != -1:
#             width, height = thumbnail_info[1]
#             canvas.coords(thumbnail_info[0], int((screen_width - width) / 2), int((screen_height - height) / 2))
#
#         if Playback_Win.Instance is not None:
#             Playback_Win.Instance.place_config_w(screen_width)
#
#         video_menu.entryconfigure(5, label='Exit Fullscreen')
#         _fullscreen.v = True
#
#
# """
# SETTINGS CONFIGURATION ...........................................................
# """
#
#
# def set_playback_seek_rate():
#     box_ = RcDiag(win, 'Playback seek rate', 'playback seek rate (in secs)', retain_value=False)
#     box_.entry.delete(0, END)
#     box_.entry.insert(END, default_seek_rate.v)
#     win.wait_window(box_)
#     value_ = box_.value
#     if len(value_) > 0:
#         try:
#             value_ = int(value_)
#         except Exception as e:
#             print(e)
#             messagebox.showwarning("Wrong Input", 'Playback Seek Rate should be integer : INVALID INPUT')
#         else:
#             if value_ > 0:
#                 default_seek_rate.v = value_
#             else:
#                 messagebox.showwarning("Wrong Input", 'Playback Seek Rate should be absolute : INVALID INPUT')
#
#
# def set_vol_seek_rate():
#     box_ = RcDiag(win, 'Volume seek rate', 'Volume seek rate (in volume units)', retain_value=False)
#     box_.entry.delete(0, END)
#     box_.entry.insert(END, default_vol_rate.v)
#     win.wait_window(box_)
#     value_ = box_.value
#     if len(value_) > 0:
#         try:
#             value_ = int(value_)
#         except Exception as e:
#             print(e)
#             messagebox.showwarning("Wrong Input", 'Playback Seek Rate should be integer : INVALID INPUT')
#         else:
#             if value_ > 0:
#                 default_vol_rate.v = value_
#             else:
#                 messagebox.showwarning("Wrong Input", 'Volume Seek Rate should be absolute : INVALID INPUT')
#
#
# def set_max_volume():
#     box_ = RcDiag(win, 'Maximum Volume', 'Maximum playback volume', retain_value=False)
#     box_.entry.delete(0, END)
#     box_.entry.insert(END, max_volume.v)
#     win.wait_window(box_)
#     value_ = box_.value
#     if len(value_) > 0:
#         try:
#             value_ = int(value_)
#         except Exception as e:
#             print(e)
#             messagebox.showwarning("Wrong Input", 'Max Volume should be integer : INVALID INPUT')
#         else:
#             if value_ > 0 and value_ > current_vol.v:
#                 max_volume.v = value_
#                 aset_(current_vol.v)
#             else:
#                 messagebox.showwarning("Wrong Input",
#                                        'Maximum Volume should be absolute and greater than Current Playback Volume\n : RANGE ERROR')
#
#
# def set_refresh_rate():
#     box_ = RcDiag(win, 'Refresh rate',
#                   'Refresh rate of UI (in Frames per second)\n Warning : Higher FPS requires more resources',
#                   size=(350, 140), retain_value=False)
#     box_.entry.delete(0, END)
#     box_.entry.insert(END, (round(1000 / refresh_time_ms.v)))
#     win.wait_window(box_)
#     value_ = box_.value
#     if len(value_) > 0:
#         try:
#             value_ = int(value_)
#             if 5 <= value_ <= 60:
#                 refresh_time_ms.v = round(1000 / value_)
#             else:
#                 messagebox.showerror('Error', 'Refresh rate should be greater than 5 and less than 60 : RANGE ERROR')
#         except Exception as e:
#             print(e)
#             messagebox.showwarning("Wrong Input", 'Refresh Rate should be integer : INVALID INPUT')
#
#
# def toggle_fulltimestate():
#     if fulltime_state.v == 1:
#         fulltime_state.v = 0
#         set_fulltime(fulltime)
#
#         if FsDock.Instance is not None:
#             set_fulltime(FsDock.Instance.f_time)
#
#     else:
#         fulltime_state.v = 1
#
#     playback_settings_menu.entryconfigure(fulltime_menu_label.v, label=fulltime_menu_label.altv)
#     fulltime_menu_label.toggle()
#
#
# def reset_default_settings():
#     save_pos.set(default_settings['save_pos'])
#     exit_check.set(default_settings['exit_check'])
#     scan_sub_on_load.set(default_settings['scan_sub'])
#     default_vol_rate.v = default_settings['vol_rate']
#     default_seek_rate.v = default_settings['seek_rate']
#     max_volume.v = default_settings['max_volume']
#     refresh_time_ms.v = default_settings['refresh_time']
#     if current_vol.v >= max_volume.v:
#         current_vol.v = max_volume.v
#     aset_(current_vol.v)
#
#
# system_on = RcBool(True)
#
# mpast_ = get_pastinfo()
# settings_ = get_settings()
# playback_dict = load_playback_file()  # to save playback of media
#
# _play_count = RcInt(mpast_['play_count'])
#
# _next = RcBool(False)  # F for ideal and T for executing operation
# _previous = RcBool(False)  # F for ideal and T for executing operation
# _stop = RcBool(False)
#
# _auto_mscale = RcBool()
# _main_menu = RcBool()
# _fullscreen = RcBool(False)
#
# _set_by_slider = RcBool(False)
# _set_a_by_slider = RcBool(False)
#
# _resize = RcBool(False)
# _mouse_pos = RcInt(-1)  # mouse position (x, y) while fullscreen
# default_vol_rate = RcInt(settings_['vol_rate'])  # in vol units... loaded by setting config.......................
# default_seek_rate = RcInt(settings_['seek_rate'])  # in secs...# loaded by setting config.......................
# max_volume = RcInt(settings_['max_volume'])  # loaded by setting config................................
# current_vol = RcInt(settings_['current_vol'])  # loaded by setting config...................
# refresh_time_ms = RcInt(settings_['refresh_time'])  # loaded by setting config...................
# fulltime_state = RcInt(settings_['fulltime_state'])  # loaded by setting config...................
#
# if fulltime_state.v == 1:
#     fulltime_menu_label = RcStr('Show Full Media Length', 'Show Remaining Media Length')
# else:
#     fulltime_menu_label = RcStr('Show Remaining Media Length', 'Show Full Media Length')
#
# aspect_ratio_index = RcInt()
#
# controller_coordinates = RcVar(mpast_['controller_coords'])
#
# # ....................................... WINDOW INIT.....................................
# win = Tk()
#
# # images
# icon = os.path.join(sdk_dir, "icons\\app.ico")
# play_image = PhotoImage(file=os.path.join(sdk_dir, 'icons\\play_light.png'))
# pause_image = PhotoImage(file=os.path.join(sdk_dir, 'icons\\pause_light.png'))
# previous_image = PhotoImage(file=os.path.join(sdk_dir, 'icons\\previous_light.png'))
# next_image = PhotoImage(file=os.path.join(sdk_dir, 'icons\\next_light.png'))
# stop_image = PhotoImage(file=os.path.join(sdk_dir, 'icons\\stop_light.png'))
# im_dim = 32  # pixels
#
# daim_path = os.path.join(sdk_dir, 'icons\\file_audio.png')
# dvim_path = os.path.join(sdk_dir, 'icons\\file_video.png')
#
# with open(daim_path, 'rb') as afile:
#     daim = PIL.Image.open(BytesIO(afile.read()))
#     daim = PIL.ImageTk.PhotoImage(daim.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS))
# with open(dvim_path, 'rb') as vfile:
#     dvim = PIL.Image.open(BytesIO(vfile.read()))
#     dvim = PIL.ImageTk.PhotoImage(dvim.resize(Slide.thumb_dim, PIL.Image.ANTIALIAS))
#
# # .................................... mpast configurations........................
# load_on_start = IntVar(win, mpast_['load_on_start'])  # auto load on start var
# control_win_check = IntVar(win, mpast_['controller'])  # to check controller state_
# _auto_play = IntVar(win, mpast_['auto_play'])  # to check _auto_play state_
#
# # ............................................................SETTINGS LOAD.............................................
# save_pos = IntVar(win, settings_['save_pos'])  # to check playback save while stop() function # loaded by setting config.....
# exit_check = IntVar(win, settings_['exit_check'])  # loaded by setting config...................
# scan_sub_on_load = IntVar(win, settings_['scan_sub'])  # loaded by setting config...................
# # ......................................................................................................................
#
# screen_width = win.winfo_screenwidth()
# screen_height = win.winfo_screenheight()
#
# print(f'screen width : {screen_width},screen height : {screen_height}')
#
# win_width = RcInt(screen_width / 1.5)
# win_height = RcInt(screen_height / 1.5)
#
# win.geometry(
#     f'{win_width.v}x{win_height.v}+{round((screen_width - win_width.v) / 2)}+{round((screen_height - win_height.v) / 2)}')
# win.minsize(460, 100)
# win.title("RC MEDIA PLAYER ")
# win.protocol('WM_DELETE_WINDOW', exit_diag)
# wintitle = "RC MEDIA PLAYER"
# win.resizable(1, 1)
# win.iconbitmap(icon)
#
# menubar = Menu(win)
# empty_menu = Menu(win)
#
# dockh = 65
# displayh = win_height.v - dockh
#
# aspect_ratio_list = ['16:9', '4:3', '1:1', '16:10', '2.21:1', '2.35:1', '2.39:1', '5:4',
#                      f'{win_width.v}:{displayh}']
#
# # file
# file = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label="File", menu=file)
# file.add_command(label="Open File/Files     Cntr+o", command=openfile)
# file.add_command(label="Scan Folder          Cntr+f", command=scan_folder_ui)
# file.add_command(label="Save As                 Cntr+s", command=_save_as_)
# file.add_separator()
# file.add_command(label='Load previous media', command=load_past)
# file.add_checkbutton(label='Auto load on startup', onvalue=1, offvalue=0, variable=load_on_start, command=load_set)
# file.add_separator()
# file.add_checkbutton(label='Autoplay', onvalue=1, offvalue=0, variable=_auto_play, command=autoplay_set)
# file.add_checkbutton(label='Show controller when minimized', onvalue=1, offvalue=0, variable=control_win_check)
# file.add_separator()
# file.add_command(label='Network Stream', command=stream_)
# file.add_separator()
# file.add_command(label="Exit", command=exit_diag)
#
# # menu images
# playi = PhotoImage(file=os.path.join(sdk_dir, Path('icons\\play_menu.png')))
# pausei = PhotoImage(file=os.path.join(sdk_dir, Path('icons\\pause_menu.png')))
# stopi = PhotoImage(file=os.path.join(sdk_dir, Path('icons\\stop_menu.png')))
# mutei = PhotoImage(file=os.path.join(sdk_dir, Path('icons\\mute_menu.png')))
# unmutei = PhotoImage(file=os.path.join(sdk_dir, Path('icons\\unmute_menu.png')))
# # playback
# playback = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label="playback", menu=playback)
# playback.add_command(label="Set speed", command=set_playback_speed)
# playback.add_separator()
#
# playback.add_command(label="forward", command=forward)
# playback.add_command(label="backward", command=backward)
# playback.add_command(label="jump to time", command=setspecifictime)
# playback.add_separator()
# playback.add_command(label="Shuffle         Alt+s", command=shuffle)
# playback.add_command(label="Previous        Alt+Left", command=previous_call)
# playback.add_command(label="next               Alt+Right", command=next_call)
# playback.add_separator()
#
# playback.add_command(label="          Play", command=count, image=playi, compound=LEFT)
# playback.add_command(label="          Pause", command=pause, image=pausei, compound=LEFT)
#
# # playlistmenu
# playmenu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label="Playlist", menu=playmenu)
# playmenu.add_command(label="Show Playlist", command=toogle_playlist)
# playmenu.add_separator()
# playmenu.add_command(label="Add media", command=openfile)
# playmenu.add_command(label='Load playlists', command=load_playlist)
#
# audio_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label='Audio', menu=audio_menu)
# audio_track = Menu(audio_menu, activebackground='skyblue', activeforeground='black', tearoff=0)
# audio_menu.add_cascade(label='Audio Track', menu=audio_track)
# audio_menu.add_separator()
# audio_menu.add_command(label='      Mute', command=mute, image=mutei, compound=LEFT)
#
# video_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label='Video', menu=video_menu)
#
# sub_menu = Menu(video_menu, activebackground="skyblue", tearoff=0)
# video_menu.add_cascade(label='Subtitles', menu=sub_menu, state=DISABLED)
# sub_menu.add_command(label='Disable', command=disable_sub)
#
# video_menu.add_command(label='Add Subtitle', command=add_sub)
# video_menu.add_separator()
# video_menu.add_command(label='Subtitle Delay', command=set_spu_delay, state=DISABLED)
# video_menu.add_separator()
# video_menu.add_command(label='Fullscreen', command=toggle_fullscreen)
# aspect_menu = Menu(video_menu, activebackground="skyblue", tearoff=0)
# video_menu.add_cascade(label='Aspect Ratio', menu=aspect_menu, state=DISABLED)
# aspect_menu.add_command(label='Set Aspect Ratio', command=set_aspect_ratio)
# aspect_menu.add_separator()
# aspect_menu.add_radiobutton(label='Default', command=default_aspect)
# aspect_menu.add_radiobutton(label='16:9', command=lambda arg='16:9': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='4:3', command=lambda arg='4:3': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='1:1', command=lambda arg='1:1': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='16:10', command=lambda arg='16:10': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='2.21:1', command=lambda arg='2.21:1': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='2.35:1', command=lambda arg='2.35:1': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='2.39:1', command=lambda arg='2.39:1': set_aspect_ratio(arg))
# aspect_menu.add_radiobutton(label='5:4', command=lambda arg='5:4': set_aspect_ratio(arg))
# video_menu.add_separator()
# video_menu.add_command(label='Screenshot', command=screenshot, state=DISABLED)
#
# settings_menu = Menu(menubar, activebackground='skyblue', activeforeground='black', tearoff=0)
# menubar.add_cascade(label="Settings", menu=settings_menu)
#
# playback_settings_menu = Menu(settings_menu, activebackground='skyblue', activeforeground='black', tearoff=0)
# settings_menu.add_cascade(label='Playback settings', menu=playback_settings_menu)
#
# playback_settings_menu.add_command(label='Playback seek rate', command=set_playback_seek_rate)
# playback_settings_menu.add_command(label='Volume seek rate', command=set_vol_seek_rate)
# playback_settings_menu.add_command(label='Maximum playback volume', command=set_max_volume)
# playback_settings_menu.add_command(label=fulltime_menu_label.v, command=toggle_fulltimestate)
# playback_settings_menu.add_separator()
# playback_settings_menu.add_checkbutton(label='Scan subtitles automatically', onvalue=1, offvalue=0, variable=scan_sub_on_load)
# playback_settings_menu.add_checkbutton(label='Save playback', onvalue=1, offvalue=0, variable=save_pos)
#
# settings_menu.add_separator()
# settings_menu.add_command(label='Refresh rate of UI', command=set_refresh_rate)
# settings_menu.add_checkbutton(label='Confirm on Exit', onvalue=1, offvalue=0, variable=exit_check)
# settings_menu.add_separator()
# settings_menu.add_command(label='Reset default', command=reset_default_settings)
#
# # ................................WIDGETS..................................
#
# dock = Frame(win, width=win_width.v, height=dockh, bg='white')
# canvas = Canvas(win, width=win_width.v, height=displayh, bg='black')
# player.set_hwnd(canvas.winfo_id())
#
# # 90 pixels for time widgets
# mediascale = RcScale(dock, slider=True, value=0, width=win_width.v - 120, height=16, troughcolor1=rgb(240, 123, 7),
#                      troughcolor2=rgb(206, 233, 234),
#                      outline='white', outwidth=6, relief='flat', bd=0, highlightthickness=0)
#
# mediascale.bind("<ButtonRelease-1>", _mscale_release_call)
# mediascale.bind("<Button-1>", _mscale_press_call)
# mediascale.bind("<B1-Motion>", _mscale_motion_call)
#
# audio_scale = RcScale(dock, slider=True, value=0, width=round(win_width.v * .15), height=16,
#                       troughcolor1=rgb(240, 123, 7),
#                       troughcolor2=rgb(206, 233, 234),
#                       outline='white', outwidth=6, relief='flat', bd=0, highlightthickness=0)
#
# audio_scale.set((current_vol.v / max_volume.v) * 100)
# audio_scale.bind("<Button-1>", _ascale_press_call)
# audio_scale.bind("<B1-Motion>", _ascale_motion_call)
#
# # ............................................Buttons..............................................
#
# # buttons
# play_button = Button(dock, command=count, image=play_image, width=32, height=32, relief='flat', bd=0)
# win.bind("<space>", count)
#
# previous_button = Button(dock, command=previous_call, image=previous_image, width=32, height=32, relief='flat', bd=0,
#                          repeatdelay=600)
# next_button = Button(dock, command=next_call, image=next_image, width=32, height=32, relief='flat', bd=0)
# stop_button = Button(dock, command=stop, image=stop_image, width=32, height=32, relief='flat', bd=0)
#
# # time
# currenttime = Label(dock, text="--.--")
# fulltime = Label(dock, text='--.--')
#
# status = Label(dock, text='Hello', font='comicsans 9', width=round(win_width.v / 23))
# status.words = round(win_width.v / 23)
#
#
# def config_status(text):
#     status['text'] = text[0:status.words + 1]
#
#
# def place_widgets(width, padx=10, pady=7):
#     height = dockh
#     dock.pack(fill=X, expand='yes', anchor=SW, side=BOTTOM)
#     canvas.pack(fill=X, expand='yes', anchor=NW, side=TOP)
#
#     # .......................... Dock Widgets ...................
#     stop_button.place(x=padx, y=height - im_dim - pady)
#     previous_button.place(x=round((width / 2) - (im_dim * 1.5)) - padx, y=height - im_dim - pady)
#     play_button.place(x=round((width - im_dim) / 2), y=height - im_dim - pady)
#     next_button.place(x=round((width + im_dim) / 2) + padx, y=height - im_dim - pady)
#
#     currenttime.place(x=5, y=(pady / 2) - 2)
#     fulltime.place(x=width - 55, y=(pady / 2) - 2)
#
#     mediascale.place(x=60, y=pady / 2)
#     audio_scale.place(x=width - audio_scale.width - padx * 5, y=38)
#
#     if width > 500:
#         status.place(x=40 + stop_button['width'], y=38)
#     else:
#         try:
#             status.place_forget()
#         except Exception as e:
#             print_(f'exception in placing status bar {e}')
#
#
# def placeconfig_w(width, padx=10):
#     play_button.place_configure(x=round((width - im_dim) / 2))
#     previous_button.place_configure(x=round((width / 2) - (im_dim * 1.5)) - padx)
#     next_button.place_configure(x=round((width + im_dim) / 2) + padx)
#
#     mediascale.config_dim(round(width - 120))
#     audio_scale.config_dim(round(win_width.v * .15))
#     status['width'] = round(width / 23)
#
#     audio_scale.place_configure(x=width - audio_scale.width - padx * 5)
#     fulltime.place_configure(x=width - 55)
#     if width > 500:
#         status.place(x=40 + stop_button['width'], y=38)
#     else:
#         try:
#             status.place_forget()
#         except Exception as e:
#             print_(f'exception in placing status bar {e}')
#
#
# # theme
# win['bg'] = rgb(30, 30, 30)
#
# canvas['bg'] = rgb(10, 10, 10)
# dock['bg'] = 'white'
# # buttons theme
# play_button['bg'] = 'white'
# play_button['activebackground'] = 'white'
# previous_button['bg'] = 'white'
# previous_button['activebackground'] = 'white'
# next_button['bg'] = 'white'
# next_button['activebackground'] = 'white'
# stop_button['bg'] = 'white'
# stop_button['activebackground'] = 'white'
# stop_button['highlightcolor'] = 'white'
#
# # mediascale theme
# status['bg'] = 'white'
# status['relief'] = 'flat'
#
# currenttime['bg'] = 'white'
# fulltime['bg'] = 'white'
#
# # ....................................< BINDINGS >..................................
#
# win['menu'] = menubar
# win.bind('<Left>', backward)
# win.bind('<Right>', forward)
# win.bind('<Escape>', stop)
# win.bind('<Alt-Right>', next_call)
# win.bind('<Alt-Left>', previous_call)
# win.bind('<Up>', vol_in)
# win.bind('<Down>', vol_dec)
# win.bind('<Control-o>', openfile)
# win.bind('<Control-f>', scan_folder_ui)
# win.bind('<Control-s>', _save_as_)
# win.bind('<Control-z>', shuffle)
# win.bind('<Control-m>', toggle_menu)
# win.bind('<Control-p>', toogle_playlist)
# win.bind('<Control-Up>', toggle_fullscreen)
# win.bind('<Control-l>', load_playlist)
# win.bind('<Control-w>', save_playlist)
# win.bind("<Configure>", __check_resize__)
# win.bind('<Alt-r>', set_playback)
# win.bind('<Control-a>', set_aspect_ratio)
# win.bind('<Alt-s>', screenshot)
# win.bind('<b>', change_audio_track)
# win.bind('<q>', auto_scan_sub)
# win.bind('<Control-n>', stream_)
#
# place_widgets(win_width.v)  # main placing widgets callback
#
# sys_load()  # loading on Startup
#
# __main_ui__()  # initializing main ui loop
# # mainloop
# win.mainloop()
