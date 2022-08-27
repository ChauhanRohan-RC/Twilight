from subprocess import Popen, STARTF_USESHOWWINDOW, STARTUPINFO
import requests
from threading import Thread
from backup.filemanager import *
import pickle

main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(os.path.realpath(__file__)))

sdk_dir = os.path.join(main_dir, 'sdk')
# bat_temp_dir = os.path.join(main_dir, r'sdk\temp\bat_temp')
temp_dir = os.path.join(sdk_dir, 'temp')
video_temp_dir = os.path.join(temp_dir, 'video_temp')
audio_temp_dir = os.path.join(temp_dir, 'audio_temp')
bat_temp_dir = os.path.join(temp_dir, 'bat_temp')
thumb_temp_dir = os.path.join(temp_dir, 'thumbnails')
ffmpeg_path = os.path.join(sdk_dir, r'ffmpeg\bin\ffmpeg.exe')


class DownMain:
    """
     info_object : list of tuples (type_, stream.url, stream.extension, stream.quality or bitrate, stream.get_filesize())
     """

    def __init__(self, info_dic, info_ob, final_save_dir, chunk_size=1024, on_progress_call=None):
        self.info_ob = info_ob
        self.info_dic = info_dic
        self.on_progress_call = on_progress_call

        self.chunk_size = chunk_size
        self.progress = 0  # in percent
        # states.........
        self.state = 0  # 0: No task yet, 1: downloading, 2: paused or completed, 3: error

        self._title = f'{self.info_dic["title"]} {self.info_ob[3]}'
        self.type = self.info_ob[0]  # 2: audio , 1 : video without audio , 0: normal
        self.thumb_url = self.info_dic['hdthumb_url']
        self.thumb_path = os.path.join(thumb_temp_dir, self.info_dic["title"] + self.thumb_url.split('/')[-1])

        self.main_temp_path = os.path.join(audio_temp_dir,
                                           f'{self._title}.{self.info_ob[2]}') if self.type == 2 else os.path.join(
            video_temp_dir, f'{self._title}.{self.info_ob[2]}')

        self.final_save_path = os.path.join(final_save_dir, os.path.basename(self.main_temp_path))

        self.main_data = None  # retrieved either on resume or download call
        self.sub_data = None
        self.thumb_data = None

        if self.type == 1:  # without audio
            self.sub_ob = self.info_dic["main_audio"]
            self.sub_temp_path = os.path.join(audio_temp_dir,
                                              f'{self.info_dic["title"]} {self.sub_ob[3]}.{self.sub_ob[2]}')
            self.total_size = self.info_ob[4] + self.sub_ob[4]
        else:
            self.total_size = self.info_ob[4]
            self.sub_ob = None
            self.sub_temp_path = None

        self.per_ = (self.chunk_size * 100) / self.total_size

    def analyse_data(self):
        try:
            self.main_data = requests.get(self.info_ob[1], stream=True)
            if self.type == 1:
                self.sub_data = requests.get(self.sub_ob[1], stream=True)
            self.thumb_data = requests.get(self.thumb_url, stream=True)
        except Exception as e:
            print(e)
            self.state = 3
            self.main_data = None
            self.sub_data = None
            self.thumb_data = None

    def is_downloaded(self):
        if self.type == 1:
            if os.path.isfile(self.main_temp_path) and os.path.isfile(self.sub_temp_path) and os.path.getsize(
                    self.main_temp_path) >= self.info_ob[4] and os.path.getsize(self.sub_temp_path) >= self.sub_ob[4]:
                return True
            return False
        if os.path.isfile(self.main_temp_path) and os.path.getsize(self.main_temp_path) >= self.info_ob[4]:
            return True
        return False

    def download(self, start=(0, None)):
        if not os.path.isdir(video_temp_dir):
            os.makedirs(video_temp_dir)
        if not os.path.isdir(audio_temp_dir):
            os.makedirs(audio_temp_dir)

        try:
            self.state = 1
            if start == (0, None):
                self.progress = 0
                f__ = 'wb'
            else:
                if start[0] == 0:
                    self.progress = (start[1] * 100 / self.total_size)
                    f__ = 'ab'
                else:
                    if start[1] is not None:
                        self.progress = ((self.info_ob[4] + start[1]) / self.total_size) * 100
                        f__ = 'ab'
                    else:
                        self.progress = (self.info_ob[4] / self.total_size) * 100
                        f__ = 'wb'

            if start[0] == 0:
                if self.main_data is None:
                    self.main_data = requests.get(self.info_ob[1], stream=True)
                with open(self.main_temp_path, f__) as main_file:
                    for chunk in self.main_data.iter_content(self.chunk_size):
                        if self.state != 1:
                            break
                        main_file.write(chunk)
                        self.progress += self.per_
                        print(self.progress)

            if self.type == 1 and self.state == 1:
                if self.sub_data is None:
                    self.sub_data = requests.get(self.sub_ob[1], stream=True)
                if start[0] == 1 and start[1] is not None:
                    f__ = 'ab'
                with open(self.sub_temp_path, f__) as sub_file:
                    for chunk in self.sub_data.iter_content(self.chunk_size):
                        if self.state != 1:
                            break
                        sub_file.write(chunk)
                        self.progress += self.per_
                        print(self.progress)

            self.state = 2
            if self.progress >= 100:
                # to merge or set thumb offline
                if self.type == 1:
                    merge_audio_and_meta(self.main_temp_path, self.sub_temp_path, self.thumb_path,
                                         output_path=self.final_save_path, delete_original=True)
                elif self.type == 2:
                    set_audio_meta(self.main_temp_path, output_path=self.final_save_path,
                                   thumbnail_path=self.thumb_path, delete_original=True)
        except Exception as e:
            print(e)
            self.state = 3

    def pause(self):
        self.state = 2

    def download_thumbnail(self):  # should be in a thread
        if not os.path.isdir(thumb_temp_dir):
            os.makedirs(thumb_temp_dir)

        if self.thumb_data is None:
            self.thumb_data = requests.get(self.thumb_url, stream=True)

        if os.path.isfile(self.thumb_path) and os.path.getsize(self.thumb_path) >= int(
                self.thumb_data.headers['Content-length']):
            return self.thumb_path

        with open(self.thumb_path, 'wb+') as thumb_file:
            for chunk in self.thumb_data.iter_content(self.chunk_size // 2):
                thumb_file.write(chunk)
        return self.thumb_path

    def resume_thread(self, start=None):
        if self.state != 1:
            if start is None:
                self.download_thumbnail()  # handles resuming itself
                if os.path.isfile(self.main_temp_path):
                    main_size_ = os.path.getsize(self.main_temp_path)
                    if main_size_ < self.info_ob[4]:
                        start = 0, main_size_
                        resume_header = {'Range': 'bytes=%d-' % start[1]}
                        self.main_data = requests.get(self.info_ob[1], headers=resume_header, stream=True,
                                                      verify=False,
                                                      allow_redirects=True)
                        self.download(start=start)
                    else:
                        # main file completed
                        if self.type == 1:
                            if os.path.isfile(self.sub_temp_path):
                                sub_size_ = os.path.getsize(self.sub_temp_path)
                                if sub_size_ < self.sub_ob[4]:
                                    start = 1, sub_size_
                                    resume_header = {'Range': 'bytes=%d-' % start[1]}
                                    self.sub_data = requests.get(self.sub_ob[1], headers=resume_header,
                                                                 stream=True,
                                                                 verify=False, allow_redirects=True)
                                    self.download(start=start)
                                else:
                                    self.state = 2
                                    # download complete
                                    self.progress = 100
                                    merge_audio_and_meta(self.main_temp_path, self.sub_temp_path,
                                                         self.thumb_path, output_path=self.final_save_path,
                                                         delete_original=True)
                            else:
                                start = 1, None
                                self.download(start)
                        else:
                            self.state = 2
                            # download complete
                            self.progress = 100
                            if self.type == 2:
                                set_audio_meta(self.main_temp_path, output_path=self.final_save_path,
                                               thumbnail_path=self.thumb_path, delete_original=True)
                else:
                    # no main_file
                    self.download(start=(0, None))

    def resume(self):
        th__ = Thread(target=self.resume_thread)
        th__.setDaemon(True)
        th__.start()

    def get_progress(self):
        return self.progress

    def get_state(self):
        return self.state

    def save(self, file_path):
        with open(file_path, 'wb+') as _file_:
            try:
                pickle.dump(self, file)
            except Exception as e:
                print(e)
                pickle.dump(self, file)


def set_audio_meta(a_path, output_path=None, thumbnail_path=None, title_='Rc Media Player', artist_='Rc',
                   album_='Rc Productions', comment_='Rc Mp', genre_='Classic', language_='hindi', ext_='.mp3',
                   delete_original=False):
    """
    it will convert audio to mp3 automatically
    """
    if not os.path.isdir(bat_temp_dir):
        os.makedirs(bat_temp_dir)
    if output_path is None:
        dir_, full_name_ = os.path.split(a_path)
        name_ = os.path.splitext(full_name_)[0]
        output_path = os.path.join(dir_, f'{name_}__temp__{ext_}')
    else:
        output_path = os.path.join(os.path.dirname(output_path),
                                   f'{os.path.splitext(os.path.basename(output_path))[0]}{ext_}')
    if thumbnail_path is None:
        __cmd__ = f'{ffmpeg_path} -y -i "{a_path}" -map 0:a:0 -acodec libmp3lame -id3v2_version 3 -metadata title="{title_}" -metadata artist="{artist_}" -metadata album="{album_}" -metadata comment="{comment_}" -metadata genre="{genre_}" -metadata language="{language_}" "{output_path}"'
    else:
        __cmd__ = f'{ffmpeg_path} -y -i "{a_path}" -i "{thumbnail_path}" -map 0 -map 1 -acodec mp3 -id3v2_version 3 -metadata title="{title_}" -metadata artist="{artist_}" -metadata album="{album_}" -metadata comment="{comment_}" -metadata genre="{genre_}" -metadata language="{language_}" "{output_path}"'

    _bat_path_ = os.path.join(bat_temp_dir, f'{os.path.basename(a_path)}.bat')
    with open(_bat_path_, 'w+') as bat_file:
        bat_file.write(__cmd__)

    si = STARTUPINFO()
    si.dwFlags |= STARTF_USESHOWWINDOW
    _p_ = Popen([_bat_path_], startupinfo=si)
    _p_.wait()
    if delete_original and _p_.returncode == 0:
        os.remove(a_path)
    return _p_.returncode


def merge_audio_and_meta(v_path, a_path, thumbnail_path=None, title_='Rc Media Player', artist_='Rc',
                         album_='Rc Productions', output_path=None, delete_original=False):
    if not os.path.isdir(bat_temp_dir):
        os.makedirs(bat_temp_dir)
    if output_path is None:
        dir_, full_name_ = os.path.split(v_path)
        name_, ext_ = os.path.splitext(full_name_)
        output_path = os.path.join(dir_, f'{name_}__merged__{ext_}')

    if thumbnail_path is None:
        __cmd__ = f'"{ffmpeg_path}" -y -i "{v_path}" -i "{a_path}" -c:v copy -c:a aac -shortest -map 0:v:0 -map 1:a:0 -id3v2_version 3 -metadata title="{title_}" -metadata artist="{artist_}" -metadata album="{album_}" "{output_path}"'
    else:
        __cmd__ = f'"{ffmpeg_path}" -y -i "{v_path}" -i "{a_path}" -i "{thumbnail_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -map 2 -disposition:2 attached_pic -id3v2_version 3 -metadata title="{title_}" -metadata artist="{artist_}" -metadata album="{album_}" "{output_path}"'

    _bat_path_ = os.path.join(bat_temp_dir, f'{os.path.basename(v_path)}.bat')
    with open(_bat_path_, 'w+') as bat_file:
        bat_file.write(__cmd__)

    si = STARTUPINFO()
    si.dwFlags |= STARTF_USESHOWWINDOW
    _p_ = Popen([_bat_path_], startupinfo=si)
    _p_.wait()
    if delete_original and _p_.returncode == 0:
        os.remove(v_path)
        os.remove(a_path)
    return _p_.returncode


with open('t.cc', 'rb') as file:
    d = pickle.load(file)

print('done')
print(d.progress)

url = "https://www.youtube.com/watch?v=HhjHYkPQ8F0"
"https://www.youtube.com/watch?v=hoNb6HuNmU0"


