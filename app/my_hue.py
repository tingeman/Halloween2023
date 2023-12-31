
import time
import colorsys
from phue import Bridge
import threading
import random

hue_bridge_ip = '10.67.1.54'
light_pattern = 'halloween'
sensor_pattern = 'bryggers'   # 'halloween'

run_disco = True


class HueBridge:
    def __init__(self, bridge_ip):
        self.bridge_ip = bridge_ip
        self.b = Bridge(hue_bridge_ip)        


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




def main():
    global run_disco

    b = Bridge(hue_bridge_ip)

    # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
    b.connect()

    # Get the bridge state (This returns the full dictionary that you can explore)
    my_api = b.get_api()
    groups = b.get_group()



    # Connect to Hue system
    print('Connecting to Hue...')
    sensor = HueSensor(hue_bridge_ip, sensor_pattern)
    lights = HueLights(hue_bridge_ip, light_pattern)
    
    

    lights.send_command('off')
    
    lights.send_command('red')
    time.sleep(5)
    
    if run_disco:
        lights.start_disco()

    time.sleep(30)
    lights.lights_off(transitiontime=50)


if __name__ == "__main__":
    try:
        main()
    except:
        print('Caught an error in outer loop')
        pass
