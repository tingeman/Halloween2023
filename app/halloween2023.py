import time
import copy
import colorsys
from phue import Bridge
from my_chromecast import *
from my_hue import *
try:
    import getchlib
except:
    import msvcrt
import threading
import random

motion_timeout = 10    # how long to keep playing after no motion

HALLOWEEN2023_URL = 'http://10.67.1.254:8000/Halloween%20soundtrack2023.mp3'



class RunState:
    def __init__(self):
        self.counter = 0
        self.state = 'stop'
        self.last_key_pressed = None
    
    def get_last_keypress(self, clear=True):
        tmp = copy.copy(self.last_key_pressed)
        if clear:
            self.key_pressed = None
        return tmp

    @staticmethod
    def set_state(instance, var, val):
        print('setting state ({0})'.format(val))
        instance.__dict__[var] = val



def main(run_state=None):
    global run_disco, cc_group

    if run_state is None:
        run_state = RunState()

    # define hotkeys
    #keys = ['x', '+', '-', 'd', 's']

    #listener = getchlib.HotKeyListener()
    #for key in keys:
    #    listener.add_hotkey('', functools.partial(run_state.set_state, 
                                                #   run_state, 
                                                #   'last_key_pressed', 
                                                #   key))

    

    # Connect to sound system
    print('Connecting to sound system...')
    cc_group = ChromecastGroup(host_list=CHROMECAST_IP_ADDRESSES)

    # Connect to Hue system
    print('Connecting to Hue...')
    sensor = HueSensor(hue_bridge_ip, sensor_pattern)
    #lights = HueLights(hue_bridge_ip, light_pattern)
    #lights.send_command('off')
    
    # Connect to Tesla
    #tesla = TeslaCar(email)
    #print('Locking Tesla...')
    #result = tesla.lock(update_trunk_state=True)
    #print('Result of lock action is: {0}'.format(result))

    #if tesla.trunk_open:
    #    print('Trunk is open, closing trunk...')
    #    tesla.close_trunk(lock_test=False)
    #else:
    #    print('Trunk is (presumably) closed...')

    # ==============================================================================================
    # =  LOOPING
    # ==============================================================================================

    print('Initiating loop...')
    # Start the loop
    run_state.state = 'run'
    #listener.start()

    cc_group.load_media(url_list=[HALLOWEEN2023_URL])
    print('Media loaded and ready...')

    while 'run' in run_state.state:

        # get motion sensor state
        sensor.refresh()
        print('Software state: {0}'.format(run_state.state))
        print('Activation counter: {0}'.format(run_state.counter))
        print('Motion sensor state: {0}    ({1})'.format(sensor.presence, sensor.updated))

        if sensor.presence or 'play' in run_state.state:
            
            # ======================================================================================
            # =  START OF ACTION
            # ======================================================================================
    
            # Motion sensor senses presence in the area
            print('Start playing...')
            run_state.counter += 1
            #lights.send_command('red')
            cc_group.play()
            time.sleep(5)

            #if run_disco:
            #    lights.start_disco()

            #if use_tesla:
            #    tesla.open_trunk()
            
            # ======================================================================================
            # =  LOOP WHILE ACTION ONGOING
            # ======================================================================================
            timeout_counter = 0
            run_state.state = 'run'
            while 'run' in run_state.state:
                cc_group.refresh()
                sensor.refresh()
                out_str = 'Player: {0}  state: {1}    Sensor presence: {2}   Timeout counter: {3}/{4}    (Type "h" for options)'
                print(out_str.format(cc_group.chromecasts[0].cast_info.friendly_name, 
                                     cc_group.chromecasts[0].media_controller.status.player_state, 
                                     sensor.presence,
                                     timeout_counter, motion_timeout))
                

                time.sleep(1)
                print('waiting 1 sec')
                ch = ''
                try:
                    ch = getchlib.getkey(False, tout=1)
                except:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch().decode()
                if ch != '':
                    print('you pressed: {0}'.format(ch))
                    
                    if ch == 'h':
                        print('  x: Exit script')
                        print('  +: Volume +')
                        print('  -: Volume -')
                        print('  d: Toggle disco')
                        print('  s: Stop play loop (and enter waiting state)')
                    
                    elif ch == 'x':
                        run_state.state = 'exit'
                        print('Exiting script...')
                    elif ch == '+':
                        print('Not implemented')
                        # heos_volume += 5
                        # if heos_volume > 100: heos_volume = 100
                        # print('Heos volume: {0}'.format(heos_volume))
                        # await heos.player.set_volume(heos_volume)
                    elif ch == '-':
                        print('Not implemented')
                        # heos_volume -= 5
                        # if heos_volume < 0: heos_volume = 0
                        # print('Heos volume: {0}'.format(heos_volume))
                        # await heos.player.set_volume(heos_volume)
                    elif ch == 's':
                        run_state.state = 'stop'
                        print('Stopping play-loop...')
                    elif ch == 'd':
                        print('Not implemented')
                        # if lights.disco_on:
                        #     lights.disco_on = False
                        #     run_disco = False
                        #     lights.send_command('red')
                        #     print('Stopping disco...')
                        # else:
                        #     run_disco = True
                        #     lights.start_disco()
                        #     print('Starting disco...')
                
                if cc_group.chromecasts[0].media_controller.status.player_state != 'PLAYING':
                    run_state.state = 'stop'
                    
                if sensor.presence:
                    timeout_counter = 0
                else:   
                    timeout_counter += 1
                
                if timeout_counter >= motion_timeout:
                    run_state.state = 'fade-out laugh'
                    break
            
            
            # ======================================================================================
            # =  TURN OFF ACTION
            # ======================================================================================

            #lights.disco_on = False
            #lights.send_command('red', transitiontime=30)
            
            if run_state.state == 'fade-out laugh':
                # Fade out music, fade lights over 7 seconds
                # Play end-laugh
                # Wait for playback to complete
                # Wait 10 seconds then go back into normal run mode awaiting new trigger
                
                print('Fading out music...')
                # await heos.fade_to_stop(duration=3)
                # await heos.play_laugh2022(volume=heos_volume)
                
                #cc_group.paus()
                cc_group.fade_to_stop()

                # if use_tesla:
                #     print('Closing trunk...')
                #     tesla.close_trunk()

                # print('Fading out lights...')
                # lights.lights_off(transitiontime=10)

                # await heos.player.set_play_mode('off', 'off')
                # time.sleep(2)
                # while True:
                #     time.sleep(1)
                #     await heos.refresh()
                #     if heos.player.state != 'play':
                #         break

                time.sleep(5)
                cc_group.stop()
                time.sleep(5)
                # run_state.state = 'run'
            elif run_state.state == 'stop':
                # Fade out lights over 5 seconds
                # Fade out music over 5 seconds
                # Wait 10 seconds then go back into normal run mode awaiting new trigger
                #lights.lights_off(transitiontime=50)
                cc_group.pause()

                # if use_tesla:
                #     tesla.close_trunk()

                # await heos.player.set_play_mode('off', 'off')
                time.sleep(10)
                run_state.state = 'run'
            elif run_state.state == 'exit':            
                # Fade out lights over 5 seconds
                # Fade out music over 5 seconds
                # Then break loops
                #lights.lights_off(transitiontime=50)
                cc_group.pause()

                # if use_tesla:
                #     tesla.close_trunk()

                # await heos.player.set_play_mode('off', 'off')
            
            # try:
            #     await heos.player.stop()
            # except:
            #     await heos.connect()
            #     await heos.get_player()

            # if use_tesla:
            #     tesla.close_trunk()

            # time.sleep(1)
            # try:
            #     await heos.clear_queue()
            # except:
            #     pass
            
        else:
            
            # ======================================================================================
            # =  NO ACTION
            # ======================================================================================

            # If no presence detected, wait one second...
            time.sleep(1)
            print('waiting 1 sec')
            ch = ''
            try:
                ch = getchlib.getkey(False, tout=1)
            except:
                if msvcrt.kbhit():
                    ch = msvcrt.getch().decode()
            if ch != '':
                #ch = run_state.get_last_keypress()
                print('you pressed: {0}'.format(ch))
                if ch == 'h':
                    print('  x: Exit script')
                    print('  +: Volume +')
                    print('  -: Volume -')
                    print('  d: Toggle disco')
                    print('  p: Start play loop')
                elif ch == 'x':
                    run_state.state = 'exit'
                    print('Exiting script...')
                elif ch == '+':
                    print('Not implemented')
                    # heos_volume += 5
                    # if heos_volume > 100: heos_volume = 100
                    # print('Heos volume: {0}'.format(heos_volume))
                    # await heos.player.set_volume(heos_volume)
                elif ch == '-':
                    print('Not implemented')
                    # heos_volume -= 5
                    # if heos_volume < 0: heos_volume = 0
                    # print('Heos volume: {0}'.format(heos_volume))
                    # await heos.player.set_volume(heos_volume)
                elif ch == 'p':
                    run_state.state = 'run-play'
                elif ch == 'd':
                    print('Not implemented')
                    # if lights.disco_on:
                    #     lights.disco_on = False
                    #     run_disco = False
                    #     lights.send_command('red')
                    #     print('Stopping disco...')
                    # else:
                    #     run_disco = True
                    #     lights.start_disco()
                    #     print('Starting disco...')                
    
    # lights.disco_on = False



if __name__ == "__main__":
    run_state = RunState()

    while run_state.state != 'exit':
        try:
            main(run_state)
        except Exception as e:
            print('Caught an error in outer loop')
            print(e)
        
        if run_state.state != 'exit':
            print('Sleeping 5 sec')
            time.sleep(5)
