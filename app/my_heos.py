

import time
import asyncio
import colorsys
import pyheos
from phue import Bridge
import threading
import random

hue_bridge_ip = '10.67.1.54'
heos_ip = '10.67.1.80'
player_name = 'Soveværelse'
#heos_volume = 70
heos_volume = 40
light_pattern = 'halloween'
sensor_pattern = 'halloween'
arduino_ip = '10.67.1.100'
arduino_port = 80
monster_rise_cmd = 'TURNS=-8'
monster_down_cmd = 'TURNS=8'

run_disco = True

motion_timeout = 30    # how long to keep playing after no motion


class HeosSpeaker:
    @classmethod
    async def create(cls, heos_ip, player_name):
        self = HeosSpeaker()
        self.heos = None
        self.ip = heos_ip
        self.name = player_name
        self.player = None
        
        await self.connect()
        await self.get_player()
        return self
    
    async def connect(self):
        if self.heos is None:
            self.heos = pyheos.Heos(self.ip)
        
        if not self.heos.connection_state == 'connected':
            await self.heos.connect(auto_reconnect=True)

    async def get_player(self):
        await self.connect()
        players = await self.heos.get_players()

        for pid, ply in players.items():
            if ply._name.lower() == self.name.lower():
                self.player = ply
                break
    
    async def refresh(self):
        if self.player is not None:
            try: 
                await self.player.refresh()
            except:
                await self.get_player()
                try:
                    await self.player.refresh()
                except:
                    await self.get_player()
        
        if not self.player.available:
            #if not self.heos.connection_state == 'connected':
            await self.heos.connect(auto_reconnect=True)
            await self.get_player()
    
    async def clear_queue(self):
        await self.refresh()
        try:
            await self.player.clear_queue()
        except:
            await self.connect()

    async def fade_to_stop(self, duration=5):
        await self.refresh()
        
        await self.player.refresh_state()
                    
        if self.player.state == 'play':
            vol = self.player._volume
            current_vol = vol
            while current_vol > 0:
                current_vol -= 1
                await self.player.set_volume(current_vol)
                await self.player.refresh()
                time.sleep(duration/vol)

            try:
                await self.player.stop()
            except:
                await self.connect()
                await self.get_player()
                
            await self.player.set_volume(vol)

    async def play_url(self, url, volume=39):
        await self.refresh()
        
        print('Player: {0}    (available: {1})'.format(self.player.name, self.player.available))
        print('Player: {0}    state: {1}'.format(self.player.name, self.player.state))
        
        if self.player.state == 'play':
            try:
                await self.player.stop()
            except:
                await self.connect()
                await self.get_player()
                
            time.sleep(0.5)
            print('Player: {0}    state: {1}'.format(self.player.name, self.player.state))

        try:
            await self.player.clear_queue()
        except:
            await self.connect()

        await self.player.set_volume(volume)

        print('Player: {0}    play_url     {1}'.format(self.player.name, url))
        try:
            await self.player.play_url(url)     # Andreas soundtrack
            
             # find the media id by starting the track on a heos player and do:
             #
             # heos = await tom.heos_connect()
             # player = await tom.get_player(heos, player_name)
             # player._now_playing_media._media_id
            
        except:
            print('Player: {0}    exception raised'.format(self.player.name))
            await self.connect()

    async def play_thriller(self, volume=39):
        url = 'http://10.67.1.65:32469/object/808f12599985e18e594c/file.flac'   # Thriller
        await self.play_url(url, volume=volume)

    async def play_halloween(self, volume=39):
        url = 'http://10.67.1.65:32469/object/1bae2ea8f529f6523d6f/file.flac'     # Andreas soundtrack
        await self.play_url(url, volume=volume)

    async def play_laugh(self, volume=39):
        url = 'http://10.67.1.65:32469/object/5b2a08ea6087e8e26562/file.flac' 
        await self.play_url(url, volume=volume)

    async def play_halloween2022(self, volume=39):
        url = 'http://10.67.1.254:32469/object/30dfb1bff981fa19903d/file.mp3'
        await self.play_url(url, volume=volume)

    async def play_thriller2022(self, volume=39):
        url = 'http://10.67.1.254:32469/object/d463b8bdaf56cc8c9aea/file.mp3'
        await self.play_url(url, volume=volume)

    async def play_laugh2022(self, volume=39):
        url = 'http://10.67.1.254:32469/object/feee8acf6e41a67b3ba9/file.mp3'
        await self.play_url(url, volume=volume)



async def main():
    global heos_volume, run_disco
    # Connect to heos system and get player
    print('Connecting to Heos...')
    
    heos = await HeosSpeaker.create(heos_ip, player_name)
    
    await heos.clear_queue()
    #try:
    #    await player.clear_queue()
    #except:
    #    pass
        
    await heos.player.set_volume(heos_volume)
    await heos.player.set_play_mode('off', 'off')
    
    await heos.play_halloween2022(volume=heos_volume)
    time.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.run(main())
    except:
        print('Caught an error in outer loop')
        pass
