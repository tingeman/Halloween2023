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


KNOWN_HOSTS = ['10.67.1.250']

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

chromecasts, browser = pychromecast.get_listed_chromecasts(
    friendly_names=[args.cast], known_hosts=KNOWN_HOSTS
)
if not chromecasts:
    print(f'No chromecast with name "{args.cast}" discovered')
    sys.exit(1)

cast = chromecasts[0]
# Start socket client's worker thread and wait for initial status update
cast.wait()
print(f'Found chromecast with name "{args.cast}", attempting to play "{args.url}"')
cast.media_controller.play_media(args.url, "audio/mp3")

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