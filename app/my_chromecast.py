

import time
import asyncio
import colorsys
import pychromecast
from pychromecast.const import MESSAGE_TYPE
import threading
import random


CHROMECASTS = {'Udendørs':   {'IP': '10.67.1.250'},
               'Udendørs 2': {'IP': '10.67.1.251'},
               'Udendørs 3': {'IP': '10.67.1.252'}}

CHROMECAST_VOLUME = 0.3


CHROMECAST_IP_ADDRESSES = [val['IP'] for key,val in CHROMECASTS.items()]


def seek(castunit, position, resumeState="PLAYBACK_PAUSE"):
    """Seek the media to a specific location."""
    castunit.media_controller._send_command(
        {
            MESSAGE_TYPE: "SEEK",
            "currentTime": position,
            "resumeState": resumeState,
        }
    )

class ChromecastGroup:
    def __init__(self, host_list):
        chromecast_devices, browser = pychromecast.get_chromecasts(known_hosts=host_list)
        if not chromecast_devices:
            print(f'No chromecasts discovered')
            return
        else:
            print('Found {0} devices.'.format(browser.count))
        self.browser = browser
        self.chromecasts = list(filter(lambda item: item.cast_info.host in host_list, chromecast_devices))

        for id, cast in enumerate(self.chromecasts):
            # Start socket client's worker thread and wait for initial status update
            cast.wait()
            cast.media_controller.stop()
            cast.set_volume(CHROMECAST_VOLUME)
            print(f'Found chromecast with name "{cast.cast_info.friendly_name}"')

    def load_media(self, url_list):
        for cid, cast in enumerate(self.chromecasts):
            if cid >= len(url_list):
                url = url_list[-1]  # take last item, if there is not enough
            else:
                url = url_list[cid]
            print("Loading media: "+cast.cast_info.host)
            cast.media_controller.play_media(url, "audio/mp3", autoplay=False)
            print("Waiting for paused status: "+cast.cast_info.host)
            while cast.media_controller.status.player_state in ['UNKNOWN', 'IDLE', 'BUFFERING']:
                print(cast.media_controller.status.player_state)
                cast.media_controller.update_status()
                time.sleep(0.5)
            if cast.media_controller.status.player_state == 'PAUSED':
                print("Paused status reported: "+cast.cast_info.host)
            else:
                print('Host: '+cast.cast_info.host)
                print(cast.media_controller.status)
                raise ValueError('Unknown player state')

    def stop(self):
        for cast in self.chromecasts: 
            print("stop playing: "+cast.cast_info.host)
            cast.media_controller.stop()

    def play(self):
        for cast in self.chromecasts: 
            print("start playing: "+cast.cast_info.host)
            cast.media_controller.play()

    def pause(self):
        for cast in self.chromecasts: 
            print("pausing: "+cast.cast_info.host)
            cast.media_controller.pause()

    def seek(self, position=0, resume_state='PLAYBACK_PAUSE'):
        for cast in self.chromecasts: 
            seek(cast, position, resumeState=resume_state)

    def refresh(self):
        for cast in self.chromecasts: 
            cast.media_controller.update_status()

    def play_halloween2023(self, volume=39):
        url = 'http://10.67.1.254:8000/Halloween%20soundtrack2023.mp3'
        self.load_media([url])
        time.sleep(3)
        self.play()

    #def play_thriller2022(self, volume=39):
    #    url = 'http://10.67.1.254:32469/object/d463b8bdaf56cc8c9aea/file.mp3'
    #    await self.play_url(url, volume=volume)

    #def play_laugh2022(self, volume=39):
    #    url = 'http://10.67.1.254:32469/object/feee8acf6e41a67b3ba9/file.mp3'
    #    await self.play_url(url, volume=volume)



if __name__ == "__main__":
    # Connect to heos system and get player
    print('Connecting to Chromecasts...')
    
    group = ChromecastGroup(KNOWN_HOSTS)
    group.play_halloween2023()
