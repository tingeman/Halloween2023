"""

Have some problems with errors, see below:

...
Player: Soveværelse  state: play    Sensor presence: False   Timeout counter: 26/30    (Type "h" for options)
Player: Soveværelse  state: play    Sensor presence: False   Timeout counter: 27/30    (Type "h" for options)
Player: Soveværelse  state: play    Sensor presence: False   Timeout counter: 28/30    (Type "h" for options)
Player: Soveværelse  state: play    Sensor presence: False   Timeout counter: 29/30    (Type "h" for options)
stopping disco (uid: 28)
stopping disco (uid: 12)
Player: Soveværelse    (available: True)
Player: Soveværelse    state: play
Player: Soveværelse    state: play
Player: Soveværelse    play_url     http://10.67.1.65:32469/object/5b2a08ea6087e8e26562/file.flac
Task exception was never retrieved
future: <Task finished name='Task-113837' coro=<HeosConnection._handle_event() done, defined at C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\connection.py:280> exception=CommandError('Command timed out')>
Traceback (most recent call last):
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\connection.py", line 331, in wait
    await self._event.wait()
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\asyncio\locks.py", line 226, in wait
    await fut
asyncio.exceptions.CancelledError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\asyncio\tasks.py", line 487, in wait_for
    fut.result()
asyncio.exceptions.CancelledError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\connection.py", line 265, in command
    response = await asyncio.wait_for(event.wait(), self.timeout)
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\asyncio\tasks.py", line 489, in wait_for
    raise exceptions.TimeoutError() from exc
asyncio.exceptions.TimeoutError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\connection.py", line 285, in _handle_event
    if player and (await player.event_update(
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\player.py", line 356, in event_update
    await self.refresh_now_playing_media()
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\player.py", line 227, in refresh_now_playing_media
    payload = await self._commands.get_now_playing_state(self._player_id)
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\command.py", line 75, in get_now_playing_state
    response = await self._connection.command(
  File "C:\Users\thin\AppData\Local\Continuum\anaconda3\envs\halloween3p9\lib\site-packages\pyheos\connection.py", line 271, in command
    raise CommandError(command, message) from error
pyheos.error.CommandError: Command timed out

"""







import time
import asyncio
import colorsys
import pyheos
from phue import Bridge
from telnetlib import Telnet
import msvcrt
import threading
import random

hue_bridge_ip = '10.67.1.54'
heos_ip = '10.67.1.85'
player_name = 'Soveværelse'
heos_volume = 70
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
                await self.connect()
                await self.get_player()
                try:
                    await self.player.refresh()
                except:
                    await self.connect()
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


async def send_to_arduino(ip, port, command):
    with Telnet(ip, port) as tn:
        tn.write(command.encode('ascii')+b"\n")



class HueLights:

    commands = {'red':         {'transitiontime': 70, 'on':  True, 'bri' : 90, 'hue': 65535, 'sat': 255},
                'yellow':      {'transitiontime': 70, 'on':  True, 'bri':  58, 'hue': 13539, 'sat': 252},
                'pink':        {'transitiontime': 70, 'on':  True, 'bri':  58, 'hue': 58294, 'sat': 253},
                'purple':      {'transitiontime': 70, 'on':  True, 'bri': 136, 'hue': 58294, 'sat': 253},
                'normal':      {'transitiontime': 70, 'on':  True, 'bri': 144, 'hue': 13524, 'sat': 200},
                'normal_lstr': {'transitiontime': 70, 'on':  True, 'bri': 144, 'hue':  7676, 'sat': 199},
                'dimmed':      {'transitiontime': 70, 'on':  True, 'bri':   0}, 
                'off':         {'transitiontime':  0, 'on': False},
                }
                
    disco_cmds = ['red', 'red', 'red', 'red', 'red', 'yellow', 'yellow', 'yellow', 'pink', 'purple']
    disco_durations =  [1,2,3,4]   # in seconds
    disco_brightness = [0, 0, 0, 50, 50, 50, 100, 150]   # in seconds

    def __init__(self, bridge_ip, light_pattern):
        self.run_disco = False
        self.bridge_ip = bridge_ip
        self.b = Bridge(hue_bridge_ip)
                
        # get lights
        lights = self.b.get_light_objects('name')
                
        # Get the appropriate lights
        self.lights = {}
        self.lights_uids = []
        light_pattern = light_pattern.lower()
        
        for light_name in lights.keys():
            if light_pattern in light_name.lower():
                #print('{0}'.format(light_name))
                self.lights[light_name] = lights[light_name]

        self.lights_uids = [l.light_id for l in self.lights.values()]
        self.list_lights()
        
        
    def lights_off(self, transitiontime=50):
        cmd = self.commands['dimmed']
        cmd['transitiontime'] = transitiontime
        self.b.set_light(self.lights_uids, cmd)
        
        timer = threading.Timer(transitiontime/10., self.b.set_light, args=[self.lights_uids, self.commands['off']])
        timer.start()  # after 60 seconds, 'callback' will be called
    
    def send_command(self, cmd=None, uids=None,  **kwargs):
        if uids is None:
            uids = self.lights_uids
            
        if cmd is not None:
            cmd_dict = self.commands[cmd]
            cmd_dict.update(**kwargs)
        else:
            cmd_dict = kwargs
        
        self.b.set_light(uids, cmd_dict)
            
    def list_lights(self):
        for id, (n, l) in enumerate(self.lights.items()):
            print("{0})  {1:30}     'on': {2:>5s}, 'bri': {3:>3d}, 'hue': {4:>5d}, 'sat': {5:>3d}".format(id, n, (lambda x: 'True' if x else 'False')(l.on), l.brightness, l.hue, l.saturation))  

    def start_disco(self, uids=None):
        self.disco_on = True
        
        if uids is None:
            uids = self.lights_uids
        
        for uid in uids:
            self._disco_callback(uid)
   
    def _disco_callback(self, uid):
        #print(self.disco_on)
        if not self.disco_on:
            print('stopping disco (uid: {0})'.format(uid))
            return     # return without scheduling new
        
        rcmd = random.choice(self.disco_cmds)
        rtransition = random.choice(self.disco_durations)
        rbri = random.choice(self.disco_brightness)
        
        #print('changing color to {0}  bri: {1}  duration: {2}s       (uid {0})'.format(rcmd,rbri, rtransition, uid))
        self.send_command(uids=[uid], cmd=rcmd, transitiontime=rtransition*5, bri=rbri)
        
        # schedule next light change
        timer = threading.Timer(rtransition, self._disco_callback, args=[uid])
        timer.start()

class HueSensor:
    def __init__(self, bridge_ip, sensor_pattern):
        self.bridge_ip = bridge_ip
        self.b = Bridge(hue_bridge_ip)
                
        # get sensors and lights
        sensors = self.b.get_sensor_objects('name')

        sensor_pattern = sensor_pattern.lower()

        # Get the motion sensor
        self.sensor = None
        for sname in sensors.keys():
            if sensor_pattern in sname.lower():
                print('{0}'.format(sname))
                self.sensor = sensors[sname]
        
        self.refresh()
    
    def refresh(self):
        self.sensor_state = self.b.get_sensor(sensor_id=self.sensor.sensor_id)['state']
        self.presence = self.sensor_state['presence']
        self.updated = self.sensor_state['lastupdated']



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

    # Connect to Hue system
    print('Connecting to Hue...')
    sensor = HueSensor(hue_bridge_ip, sensor_pattern)
    lights = HueLights(hue_bridge_ip, light_pattern)
    
    lights.send_command('off')
    
    # check connection to arduino (manually check LED is on
    print('Connecting to Arduino...')
    await send_to_arduino(arduino_ip, arduino_port, 'LED=ON')
    time.sleep(5)
    await send_to_arduino(arduino_ip, arduino_port, 'LED=OFF')
    
    print('Initiating loop...')
    # Start the loop
    state = 'run'
    while 'run' in state:
        # get motion sensor state
        #sensor_state = b.get_sensor(sensor_id=mysensor.sensor_id)
        sensor.refresh()
        print('Software state: {0}'.format(state))
        print('Sensor state: {0}    ({1})'.format(sensor.presence, sensor.updated))
        
        if sensor.presence or 'play' in state:
            # Motion sensor senses presence in the area
            print('Start playing...')
            #b.set_light(CurrentLights_uids, lights_on_command)
            lights.send_command('red')
            await heos.play_halloween(volume=heos_volume)
            await send_to_arduino(arduino_ip, arduino_port, monster_rise_cmd)
            time.sleep(5)
            
            if run_disco:
                lights.start_disco()
            
            timeout_counter = 0
            state = 'run'
            while 'run' in state:
                time.sleep(1)
                await heos.refresh()
                sensor.refresh()
                print('Player: {0}  state: {1}    Sensor presence: {2}   Timeout counter: {3}/{4}    (Type "h" for options)'.format(heos.player.name, heos.player.state, 
                                                                                                          sensor.presence,
                                                                                                          timeout_counter, motion_timeout))
                
                if msvcrt.kbhit() > 0:
                    ch = msvcrt.getch()
                    print('you pressed: {0}'.format(ch))
                    
                    if ch == b'h':
                        print('  x: Exit script')
                        print('  +: Heos volume +')
                        print('  -: Heos volume -')
                        print('  d: Toggle disco')
                        print('  s: Stop play loop (and enter waiting state)')
                    
                    elif ch == b'x':
                        state = 'exit'
                        print('Exiting script...')
                    elif ch == b'+':
                        heos_volume += 5
                        if heos_volume > 100: heos_volume = 100
                        print('Heos volume: {0}'.format(heos_volume))
                        await heos.player.set_volume(heos_volume)
                    elif ch == b'-':
                        heos_volume -= 5
                        if heos_volume < 0: heos_volume = 0
                        print('Heos volume: {0}'.format(heos_volume))
                        await heos.player.set_volume(heos_volume)
                    elif ch == b's':
                        state = 'stop'
                        print('Stopping play-loop...')
                    elif ch == b'd':
                        if lights.disco_on:
                            lights.disco_on = False
                            run_disco = False
                            lights.send_command('red')
                            print('Stopping disco...')
                        else:
                            run_disco = True
                            lights.start_disco()
                            print('Starting disco...')
                            
                    while msvcrt.kbhit() > 0:
                        ch = msvcrt.getch()
                
                if heos.player.state != 'play':
                    state = 'stop'
                    
                if sensor.presence:
                    timeout_counter = 0
                else:   
                    timeout_counter += 1
                
                if timeout_counter >= motion_timeout:
                    state = 'fade-out laugh'
                    break
            
            
            await send_to_arduino(arduino_ip, arduino_port, monster_down_cmd)
            lights.disco_on = False
            lights.send_command('red', transitiontime=30)
            
            if state == 'fade-out laugh':
                # Fade out music, fade lights over 7 seconds
                # Play end-laugh
                # Wait for playback to complete
                # Wait 10 seconds then go back into normal run mode awaiting new trigger
                await heos.fade_to_stop(duration=10)
                lights.lights_off(transitiontime=70)
                await heos.play_laugh(volume=heos_volume)
                await heos.player.set_play_mode('off', 'off')
                time.sleep(4)
                while True:
                    time.sleep(1)
                    await heos.refresh()
                    if heos.player.state != 'play':
                        break
                time.sleep(10)
                state = 'run'
            elif state == 'stop':
                # Fade out lights over 5 seconds
                # Fade out music over 5 seconds
                # Wait 10 seconds then go back into normal run mode awaiting new trigger
                lights.lights_off(transitiontime=50)
                await heos.fade_to_stop(duration=5)
                await heos.player.set_play_mode('off', 'off')
                time.sleep(10)
                state = 'run'
            elif state == 'exit':            
                # Fade out lights over 5 seconds
                # Fade out music over 5 seconds
                # Then break loops
                lights.lights_off(transitiontime=50)
                await heos.fade_to_stop(duration=5)
                await heos.player.set_play_mode('off', 'off')
            
            try:
                await heos.player.stop()
            except:
                await heos.connect()
                await heos.get_player()
                            
            time.sleep(1)
            try:
                await heos.clear_queue()
            except:
                pass
            
        else:
            # If no presence detected, wait one second...
            time.sleep(1)
            
            if msvcrt.kbhit() > 0:
                ch = msvcrt.getch()
                print('you pressed: {0}'.format(ch))
                if ch == b'h':
                    print('  x: Exit script')
                    print('  +: Heos volume +')
                    print('  -: Heos volume -')
                    print('  d: Toggle disco')
                    print('  p: Start play loop')
                elif ch == b'x':
                    state = 'exit'
                    print('Exiting script...')
                elif ch == b'+':
                    heos_volume += 5
                    if heos_volume > 100: heos_volume = 100
                    print('Heos volume: {0}'.format(heos_volume))
                    await heos.player.set_volume(heos_volume)
                elif ch == b'-':
                    heos_volume -= 5
                    if heos_volume < 0: heos_volume = 0
                    print('Heos volume: {0}'.format(heos_volume))
                    await heos.player.set_volume(heos_volume)
                elif ch == b'p':
                    state = 'run-play'
                elif ch == b'd':
                    if lights.disco_on:
                        lights.disco_on = False
                        run_disco = False
                        lights.send_command('red')
                        print('Stopping disco...')
                    else:
                        run_disco = True
                        lights.start_disco()
                        print('Starting disco...')                

                while msvcrt.kbhit() > 0:
                    ch = msvcrt.getch()
    
    lights.disco_on = False



if __name__ == "__main__":
    while True:
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.run(main())
        except:
            print('Caught an error in outer loop')
            pass
