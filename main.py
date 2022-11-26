import pypresence
import configparser
import time
from yandex_music import Client
import psutil
import os.path

# ----- necessary info -----
client_id = '978995592736944188'

# ----- automated cfg creation -----
configCreate = configparser.ConfigParser()
if os.path.isfile("config.ini"):
    configCreate.read("config.ini")
    if not configCreate.sections():
        configCreate['token'] = {'token': 'None'}
        file = open("config.ini", "w")
        configCreate.write(file)
        file.close()
else:
    configCreate['token'] = {'token': 'None'}
    file = open("config.ini", "w")
    configCreate.write(file)
    file.close()


def getToken() -> str:
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.get('token', 'token') == 'None':
        token_ = input("[YandexMusicRPC] -> Please, input your token which you've given from link in README: ")
        config.set('token', 'token', token_)
        with open('config.ini', 'w') as f:
            config.write(f)
    else:
        print('[YandexMusicRPC] -> Token was successfully got from config')
    return config.get('token', 'token')


class Presence:
    def __init__(self) -> None:
        self.token = getToken()
        self.client = None
        self.currentTrack = None
        self.rpc = None
        self.running = False

    def start(self) -> None:
        if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
            print("[YandexMusicRPC] -> Discord is not launched")
            return

        self.currentTrack = self.getTrack()
        self.rpc = pypresence.Presence(client_id)
        self.rpc.connect()
        self.client = Client(self.token).init()

        self.running = True
        while self.running:
            if "Discord.exe" not in (p.name() for p in psutil.process_iter()):
                print("[YandexMusicRPC] -> Discord was closed")
                return
            if self.currentTrack != (ongoing_track := self.getTrack()):
                print(f"[YandexMusicRPC] -> Changed track to {ongoing_track['label']}")
                if ongoing_track['success']:
                    self.rpc.update(
                        details=ongoing_track['label'],
                        state=ongoing_track['duration'],
                        large_image=ongoing_track['og-image'],
                        large_text='Y.M',
                        buttons=[{'label': 'Go to the track', 'url': ongoing_track['link']}]
                    )
                else:
                    self.rpc.update(
                        details=ongoing_track['label'],
                        state=ongoing_track['duration'],
                        large_image=ongoing_track['og_image'],
                        large_text='Y.M'
                    )
                self.currentTrack = ongoing_track
            time.sleep(10)

    def getTrack(self) -> dict:
        try:
            queues = self.client.queues_list()
            last_queue = self.client.queue(queues[0].id)
            track_id = last_queue.get_current_track()
            track = track_id.fetch_track()
        except AttributeError:
            return {
                'success': False,
                'label': "No track",
                'duration': "Duration: None",
                'link': "",
                'og-image': "og-image"
            }
        except Exception as exception:
            print(f"[YandexMusicRPC] -> Something happened: {exception}")
            return {
                'success': False,
                'label': "No track",
                'duration': "Duration: None",
                'link': "",
                'og-image': "og-image"
            }
        return {
            'success': True,
            'label': f"{', '.join(track.artists_name())} - {track.title}",
            'duration': f'Duration: {0 if track.duration_ms // 60000 < 10 else ""}{track.duration_ms // 60000}'
                        f':{0 if track.duration_ms % 60000 // 1000 < 10 else ""}{track.duration_ms % 60000 // 1000}',
            'link': f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/",
            'og-image': "https://" + track.og_image[:-2] + "400x400"
        }


if __name__ == "__main__":
    presence = Presence()
    presence.start()
