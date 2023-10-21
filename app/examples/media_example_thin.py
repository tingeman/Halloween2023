"""
Example on how to use the Media Controller to play an URL.

"""
# pylint: disable=invalid-name

import argparse
import logging
import sys
import time

import zeroconf
import numpy as np

import pychromecast

from pychromecast.const import MESSAGE_TYPE

def seek(castunit, position, resumeState="PLAYBACK_PAUSE"):
    """Seek the media to a specific location."""
    castunit.media_controller._send_command(
        {
            MESSAGE_TYPE: "SEEK",
            "currentTime": position,
            "resumeState": resumeState,
        }
    )


KNOWN_HOSTS = ['10.67.1.250', '10.67.1.251', '10.67.1.252']

# Change to the friendly name of your Chromecast
CAST_NAME = "Udendørs"

# Change to an audio or video url
MEDIA_URL = "http://10.67.1.254:8000/Halloween%20soundtrack2023.mp3"

parser = argparse.ArgumentParser(
    description="Example on how to use the Media Controller to play an URL."
)
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument(
    "--show-zeroconf-debug", help="Enable zeroconf debug log", action="store_true"
)
parser.add_argument(
    "--cast", help='Name of cast device (default: "%(default)s")', default=CAST_NAME
)
parser.add_argument(
    "--known-host",
    help="Add known host (IP), can be used multiple times",
    action="append",
)
parser.add_argument(
    "--url", help='Media url (default: "%(default)s")', default=MEDIA_URL
)
args = parser.parse_args()

try:
    KNOWN_HOSTS.extend(args.known_hosts)
except:
    pass

if args.show_debug:
    logging.basicConfig(level=logging.DEBUG)
if args.show_zeroconf_debug:
    print("Zeroconf version: " + zeroconf.__version__)
    logging.getLogger("zeroconf").setLevel(logging.DEBUG)

chromecasts, browser = pychromecast.get_chromecasts(known_hosts=KNOWN_HOSTS)

if not chromecasts:
    print(f'No chromecasts discovered')
    sys.exit(1)

# remove any chromecasts not in KNOWN_HOSTS
chromecasts = list(filter(lambda item: item.cast_info.host in KNOWN_HOSTS, chromecasts))

for id, cast in enumerate(chromecasts):
    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    cast.media_controller.stop()
    cast.set_volume(0.3)
    cast.wait()
    print(f'Found chromecast with name "{cast.cast_info.friendly_name}", attempting to play "{args.url}"')

for cast in chromecasts:
    cast.media_controller.play_media(args.url, "audio/mp3", autoplay=False)

for cast in chromecasts:
    print("Waiting for paused status: "+cast.cast_info.host)
    while cast.media_controller.status.player_state != "PAUSED":
        cast.media_controller.update_status()
        time.sleep(0.1)
    print("Paused status reported: "+cast.cast_info.host)

#time.sleep(1)
#for cast in chromecasts:    
#    seek(cast, 0)
#    print('Pausing...')

#time.sleep(1)
#for cast in chromecasts:    
#    cast.set_volume(0.4)

time.sleep(1)

for cast in chromecasts: 
    print("start playing: "+cast.cast_info.host)
    cast.media_controller.play()

1/0

# Wait for player_state PLAYING
player_state = None
t = 30
has_played = False
while t >= 0:
    try:
        if player_state != cast.media_controller.status.player_state:
            player_state = cast.media_controller.status.player_state
            print("Player state:", player_state)
        if player_state == "PLAYING":
            has_played = True
        if cast.socket_client.is_connected and has_played and player_state != "PLAYING":
            has_played = False
            cast.media_controller.play_media(args.url, "audio/mp3")

        time.sleep(0.1)
        t = t - 0.1
        if np.round(t % 1, 2) == 0:
            print(t)
    except KeyboardInterrupt:
        break

cast.media_controller.pause()
time.sleep(3)
cast.media_controller.play()

# Shut down discovery
browser.stop_discovery()