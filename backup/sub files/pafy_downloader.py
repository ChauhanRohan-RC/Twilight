import pafy
import sys
import requests
import tqdm

url = "https://www.youtube.com/watch?v=kJQP7kiw5Fk"

video = pafy.new(url)

video_streams = video.allstreams
audio_streams = video.audiostreams

print('.................VIDEOS')
for index_, stream in enumerate(video_streams):
    print(f'{index_ + 1} :: {stream}: {round(stream.get_filesize() / 1024 ** 2)} Mb')

print('.................AUDIO')
for index_, stream in enumerate(audio_streams):
    print(f'{index_ + 1 + len(video_streams)} :: {stream}: {round(stream.get_filesize() / 1024 ** 2)} Mb')

link__ = None
while link__ is None:
    i = int(input('Enter no to download : '))
    if 0 < i <= len(video_streams):
        ob_ = video_streams[i - 1]
        link__ = ob_.url, ob_.title, ob_.extension, ob_.get_filesize()
        break

    elif len(video_streams) < i <= len(audio_streams) + len(video_streams):
        ob_ = audio_streams[i - 1 - len(video_streams)]
        link__ = ob_.url, ob_.title, ob_.extension, ob_.get_filesize()
        break

    else:
        link__ = None
        print('invalid choice')
        continue


data_ = requests.get(link__[0], stream=True)

chunk_size = 1024

with open(f'{link__[1]}.{link__[2]}', 'wb') as file:
    for chunk in tqdm.tqdm(data_.iter_content(chunk_size), total=round(link__[3] / chunk_size), unit='KB'):
        file.write(chunk)
