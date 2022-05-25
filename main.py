import pypresence
from yandex_music import Client
import configparser
client_id = '978995592736944188'

def get_track():
    try:
        queues = client.queues_list()
        last_queue = client.queue(queues[0].id)
        track_id = last_queue.get_current_track()
        track = track_id.fetch_track()
        return track
    except Exception as e:
        return 0


def get_label():
    try:
        track = get_track()
        artists = ', '.join(track.artists_name())
        title = track.title
        return f"{artists} - {title}"
    except Exception as e:
        return 'No track'


def get_duration():
    try:
        track = get_track()
        return f'Duration: {0 if track["duration_ms"] // 60000 < 10 else ""}{track["duration_ms"] // 60000}:{0 if track["duration_ms"] % 60000 // 1000 < 10 else ""}{track["duration_ms"] % 60000 // 1000}'
    except Exception as e:
        return "Duration: None"


def get_link():
    try:
        track = get_track()
        return f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/"
    except Exception as e:
        return 'https://music.yandex.ru/'


config = configparser.ConfigParser()
config.read('config.ini')
if config.get('token', 'token') == 'None':
    token_ = input("[YandexMusicRPC] - Please, input your token which you've given from link in README: ")
    config.set('token', 'token', token_)
    with open('config.ini', 'w') as f:
        config.write(f)
else:
    print('[YandexMusicRPC] - Token was successfully got from config!')
TOKEN = config.get('token', 'token')

client = Client(TOKEN).init()
curr = get_label()

RPC = pypresence.Presence(client_id)
RPC.connect()
RPC.update(
        details=get_label(),
        state=get_duration(),
        large_image='og-image',
        large_text='Y.M',
        buttons=[{'label': 'Go to the track', 'url': get_link()}] if get_link() != '' else [{}]
        )
print(f"[YandexMusicRPC] - RPC was successfully updated with track {get_label()}!")

while True:
    if get_label() != curr:
        RPC.update(
            details=get_label(),
            state=get_duration(),
            large_image='og-image',
            large_text='Y.M',
            buttons=[{'label': 'Go to the track', 'url': get_link()}] if get_link() != '' else [{}]
        )
        print(f"[YandexMusicRPC] - RPC was successfully updated with track {get_label()}!")
        curr = get_label()
