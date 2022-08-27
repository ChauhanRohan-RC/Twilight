import os
import sys
import requests
import pafy
import threading
from subprocess import Popen, STARTF_USESHOWWINDOW, STARTUPINFO

main_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(os.path.realpath(__file__)))
sdk_dir = os.path.join(main_dir, 'sdk')

temp_dir = os.path.join(sdk_dir, 'temp')
video_temp_dir = os.path.join(temp_dir, 'video_temp')
audio_temp_dir = os.path.join(temp_dir, 'audio_temp')
bat_temp_dir = os.path.join(temp_dir, 'bat_temp')
thumb_temp_dir = os.path.join(temp_dir, 'thumbnails')
ffmpeg_path = os.path.join(sdk_dir, r'ffmpeg\bin\ffmpeg.exe')


class DownMain:
    def __init__(self, pafy_object, stream_object, final_save_dir, chunk_size=1024):
        self.pafy_ob = pafy_object  # to extract title and audio if not present
        self.main_ob = stream_object

        self.main_size = int(self.main_ob.get_filesize())
        self.main_type = self.main_ob.mediatype

        if self.main_type == "audio":
            self.main_title = f'{self.pafy_ob.title} {self.main_ob.bitrate}'
        else:
            self.main_title = f'{self.pafy_ob.title} {self.main_ob.resolution}'

        self.info_dic = {'title': self.main_title, 'main_ext': self.main_ob.extension, 'main_size': self.main_size,
                         'main_type': self.main_type, 'main_url': self.main_ob.url, 'thumb_url': self.pafy_ob.bigthumbhd,
                         'total_size': self.main_size}
        self.info_dic['thumb_path'] = os.path.join(thumb_temp_dir, self.info_dic['thumb_url'].split('/')[-1])

        self.main_temp_path = os.path.join(audio_temp_dir, f'{self.info_dic["title"]}.{self.info_dic["main_ext"]}') if self.main_type == 'audio' else os.path.join(
            video_temp_dir, f'{self.info_dic["title"]}.{self.info_dic["main_ext"]}')

        self.final_save_path = os.path.join(final_save_dir, os.path.basename(self.main_temp_path))

        self.main_data = None  # retrieved either on resume or download call
        self.sub_data = None
        self.thumb_data = None

        if self.info_dic['main_type'] == 'video':  # without audio
            self.sub_ob = self.pafy_ob.audiostreams[0]
            self.sub_size = int(self.sub_ob.get_filesize())
            self.info_dic['sub_url'] = self.sub_ob.url
            self.info_dic['sub_size'] = self.sub_size
            self.info_dic['sub_ext'] = self.sub_ob.extension
            self.info_dic['total_size'] += self.sub_size
            self.sub_temp_path = os.path.join(audio_temp_dir, f'{self.info_dic["title"]}.{self.info_dic["sub_ext"]}')
        else:
            self.sub_ob = None
            self.sub_temp_path = None

        self.chunk_size = chunk_size
        self.per_ = (self.chunk_size * 100) / self.info_dic['total_size']
        self.progress = 0

        # states.........
        self.state = 0  # 0: No task yet, 1: downloading, 2: paused or completed, 3: error

    def analyse_data(self):
        try:
            self.main_data = requests.get(self.info_dic['main_url'], stream=True)
            if self.info_dic['main_type'] == 'video':
                self.sub_data = requests.get(self.info_dic['sub_url'], stream=True)
            self.thumb_data = requests.get(self.info_dic['thumb_url'], stream=True)
        except Exception as e:
            print(e)
            self.state = 3
            self.main_data = None
            self.sub_data = None
            self.thumb_data = None

    def is_downloaded(self):
        if self.sub_ob is None:
            if os.path.isfile(self.main_temp_path) and os.path.getsize(self.main_temp_path) >= self.main_size:
                return True
            return False
        if os.path.isfile(self.main_temp_path) and os.path.isfile(self.sub_temp_path) and os.path.getsize(
                self.main_temp_path) >= self.main_size and os.path.getsize(self.sub_temp_path) >= self.sub_size:
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
                    self.progress = (start[1] * 100 / self.info_dic['total_size'])
                    f__ = 'ab'
                else:
                    if start[1] is not None:
                        self.progress = ((self.main_size + start[1]) / self.info_dic['total_size']) * 100
                        f__ = 'ab'
                    else:
                        self.progress = (self.main_size / self.info_dic['total_size']) * 100
                        f__ = 'wb'
            if start[0] == 0:
                if self.main_data is None:
                    self.main_data = requests.get(self.info_dic['main_url'], stream=True)
                with open(self.main_temp_path, f__) as main_file:
                    for chunk in self.main_data.iter_content(self.chunk_size):
                        if self.state != 1:
                            break
                        main_file.write(chunk)
                        self.progress += self.per_
                        print(self.progress)

            if self.info_dic['main_type'] == 'video' and self.state == 1:
                if self.sub_data is None:
                    self.sub_data = requests.get(self.info_dic['sub_url'], stream=True)
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
                self.resume()  # to merge or set thumb offline
        except Exception as e:
            print(e)
            self.state = 3

    def pause(self):
        self.state = 2

    def download_thumbnail(self):  # should be in a thread
        if not os.path.isdir(thumb_temp_dir):
            os.makedirs(thumb_temp_dir)
        if self.thumb_data is None:
            self.thumb_data = requests.get(self.info_dic['thumb_url'], stream=True)

        if os.path.isfile(self.info_dic["thumb_path"]) and os.path.getsize(self.info_dic['thumb_path']) >= int(self.thumb_data.headers['Content-length']):
            return True
        with open(self.info_dic['thumb_path'], 'wb+') as thumb_file:
            for chunk in self.thumb_data.iter_content(self.chunk_size//2):
                thumb_file.write(chunk)

    def resume_thread(self, start=None):
        if self.state != 1:
            if start is None:
                self.download_thumbnail()  # handles resuming itself
                if os.path.isfile(self.main_temp_path):
                    main_size_ = os.path.getsize(self.main_temp_path)
                    if main_size_ < self.main_size:
                        start = 0, main_size_
                        resume_header = {'Range': 'bytes=%d-' % start[1]}
                        self.main_data = requests.get(self.info_dic['main_url'], headers=resume_header, stream=True, verify=False,
                                                      allow_redirects=True)
                        self.download(start=start)
                    else:
                        # main file completed
                        if self.info_dic['main_type'] == 'video':
                            if os.path.isfile(self.sub_temp_path):
                                sub_size_ = os.path.getsize(self.sub_temp_path)
                                if sub_size_ < self.sub_size:
                                    start = 1, sub_size_
                                    resume_header = {'Range': 'bytes=%d-' % start[1]}
                                    self.sub_data = requests.get(self.info_dic['sub_url'], headers=resume_header, stream=True,
                                                                 verify=False, allow_redirects=True)
                                    self.download(start=start)
                                else:
                                    self.state = 2
                                    # download complete
                                    self.progress = 100
                                    merge_audio_and_meta(self.main_temp_path, self.sub_temp_path, self.info_dic['thumb_path'], output_path=self.final_save_path, delete_original=True)
                            else:
                                start = 1, None
                                self.download(start)
                        else:
                            self.state = 2
                            # download complete
                            self.progress = 100
                            set_audio_meta(self.main_temp_path, output_path=self.final_save_path, thumbnail_path=self.info_dic['thumb_path'], delete_original=True)
                else:
                    # no main_file
                    self.download(start=(0, None))

    def resume(self):
        th__ = threading.Thread(target=self.resume_thread)
        th__.setDaemon(True)
        th__.start()

    def get_progress(self):
        return self.progress

    def get_state(self):
        return self.state


def set_audio_meta(a_path, output_path=None, thumbnail_path=None, title_='Rc Media Player', artist_='Rc', album_='Rc Productions', comment_='Rc Mp', genre_='Classic', language_='hindi', ext_='.mp3', delete_original=False):
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
        output_path = os.path.join(os.path.dirname(output_path), f'{os.path.splitext(os.path.basename(output_path))[0]}{ext_}')
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


def merge_audio_and_meta(v_path, a_path, thumbnail_path=None, title_='Rc Media Player', artist_='Rc', album_='Rc Productions', output_path=None, delete_original=False):
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


if __name__ == '__main__':
    url = r"https://www.youtube.com/watch?v=kJQP7kiw5Fk"
    yt = pafy.new(url)
    video_streams = [i for i in yt.allstreams if i.mediatype in ('video', 'normal') and i.extension == 'mp4']
    audio_streams = yt.audiostreams
    all_streams = video_streams + audio_streams
    for i, stream in enumerate(all_streams, start=1):
        print(i, stream)

    in_ = int(input('enter a no : '))
    stream_selected = all_streams[in_ - 1]
    d = DownMain(yt, stream_selected, final_save_dir=r"E:\songs\english songs")
    d.resume()


