# This uses the vjoy device which has been bound 
# from the X-Touch Mini by the accompanying FreePie script. 
# Each button press and rotary movement are translated to a button press on the 
# virtual joystick.
#
# It sets up a telnet connection to PSX to send client commands directly. 
# Some commands are better sent as virtual keypresses and it handles these also.
# The connection to PSX is "write-only".
# The layout of the X-Touch Mini is handled by the FreePie script.
#
# The precise button numbers on the vjoy device depend on how you have set up
# the Freepie script - they are not constant. Eg I have defined two "virtual" rotary
# encoders for the leftmost dial and this has pushed the numbering of all subsquent dials
# by +2

# Experiment freely, This script will show the number of each X-Touch Mini
# input as it is made.

# NB needs 'pip install pygame==2.4.0' as newer versions of pygame may contain a regression
# in which some connected devices are not recognised.


import pygame
import telnetlib
import time
from pyautogui import press, hotkey, keyDown, keyUp

pygame.init()

pygame.joystick.init()

# First section is for commands to be sent directly to PSX as a client
myjoy = {}

button_commands = [{
# First Joystick : vjoy
    1: b"Qh26=1", # CTR
    2: b"Qh27=1", # TFC   
    3: b"Qh60=1", # SPD sel
    4: b"Qh61=1", # HDG sel
    5: b"Qh62=1", # ALT sel
    6: b"Qh69=1", # VS sel
    16: b"Qh25=1", # Baro STD (long press)
    19: b"Qh67=1", # FLCH (long press)
    20: b"Qh68=1", # HDG hold (long press)
    21: b"Qh70=1", # ALT hold (long press)
    32: b"Qh15=1", # WXR
    33: b"Qh63=1", # THR    
    34: b"Qh65=1", # LNAV
    36: b"Qh71=1", # LOC
    40: b"Qh21=1", # TERR
    41: b"Qh64=1", # SPD
    42: b"Qh66=1", # VNAV
    43: b"Qh73=1", # CMD L
    44: b"Qh72=1", # APP
    45: b"Qh111=1", # EICAS canc
    46: b"Qh112=1", # EICAS recall
    47: b"Qh55=0", # AP DISCONNECT
    66: b"Qh30=-1", # Baro down
    67: b"Qh30=1", # Baro up
    68: b"Qh31=0", # Baro inches
    69: b"Qh31=1", # Baro hpa
    74: b"Qh77=-1", # SPD up
    75: b"Qh77=1", # SPD down
    76: b"Qh78=-1", # HDG up
    77: b"Qh78=1", # HDG down
    78: b"Qh80=-1", # ALT up
    79: b"Qh80=1", # ALT down
    80: b"Qh79=-1", # VS up
    81: b"Qh79=1", # VS down
},   
# Virpil 2
{
    
    11: b"Qh170=1", # Gear down
    12: b"Qh170=3", # Gear up
    17: b"Qh61=1", # HDG sel
    18: b"Qh78=1", # HDG down
    19: b"Qh78=-1", # HDG up
    20: b"Qh70=1", # ALT hold
    21: b"Qh80=1", # ALT down
    22: b"Qh80=-1", # ALT up
},
# Virpil 3
{
},   
# Virpil 4
{
    0: b"Qh60=1", # SPD sel
    1: b"Qh77=-1", # SPD up
    2: b"Qh77=1", # SPD down 
    13: b"Qh79=-1", # VS up
    14: b"Qh79=1", # VS down
    15: b"Qh69=1", # VS sel
} 
]

# next section is for commands to be sent as hotkey combinations

button_keys = [{
    70: ['alt','k'], # ND mode down
    71: ['alt','l'], # ND mode up
    72: ['alt','a'], # Range down
    73: ['alt','z'], # Range up
},   
# Virpil 2
{
},
# Virpil 3
{
},   
# Virpil 4
{
}     
]

# next section is for commands to be send as single keypresses

button_press = [{
    23: 'q', # switch standby and COM1 (long press)
    35: 't',  # A/T ARM
    82: 's', # main COM1 down
    83: 'w', # main COM1 up
    84: 'd', # small COM1 down
    85: 'e', # small COM1 up
},   
# Virpil 2
{
},
# Virpil 3
{
},   
# Virpil 4
{
}     
]

# Connect to PSX as a client, wait 5s and try again if not ready

def connectPSX():
    host = '127.0.0.1'                         
    port = 10747
    while True :
        try:
            psx = telnetlib.Telnet(host, port)
            break
        except Exception as e:
            print(f"Failed to connect: {e}")
            time.sleep(5)
    print(f"Connected")
    time.sleep(0.1)
    psx.read_very_eager()
    return psx
            
# This is the main polling loop. Poll for a button press, and then send it to PSX either
# as a client or via single or combination keypresses

def poll(psx, joysticks):
    pygame.event.get() #flush the joystick queue on first connection
    print("got here")
    while True:      
        for event in pygame.event.get(): # User did something
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.", event.button, event.joy)
                j = myjoy.get(event.joy)
# we have something to send, go through the options

                command = button_commands[j].get(event.button) # to be sent as client
                
                if command:
                    try:
                        psx.write(command+b'\n')
                        print(f"wrote something from joystick ",event.joy)
                    except Exception as e:          # fail gracefully if lost connection
                        print(f"Lost connection")
                        return

                key = button_keys[j].get(event.button) # to be sent as hotkey
                if key:
                    hotkey(key) 

                key = button_press[j].get(event.button) # to be sent as single keypress
                if key:                    
                    keyDown(key)
                    keyUp(key)

# now flush the client input queue, fail gracefully if we have lost the PSX connection
        try:
            psx.read_very_eager()
        except Exception as e:
            print(f"Lost connection")
            return
        

# Routine to find the vJoy stick out of the list of attached devices

def connect_joysticks():
    # Get the number of joysticks
    joystick_count = pygame.joystick.get_count()

    print(f"Number of joysticks: {joystick_count}\n")

    # For each joystick
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)

        print(f"Joystick {i}")
        print(f"\tName:      {joystick.get_name()}")
        print(f"\tAxes:      {joystick.get_numaxes()}")
        print(f"\tButtons:   {joystick.get_numbuttons()}")
        print(f"\tHats:      {joystick.get_numhats()}")
        print(f"\tBalls:     {joystick.get_numballs()}")
        print("\n")
        if joystick.get_name() == "vJoy Device":
            print(f"vJoy found!")
            vjoy = joystick
            myjoy.update({i : 0})
        if joystick.get_name() == "LEFT VPC Throttle MT-50CM3" and joystick.get_numaxes() == 0 and joystick.get_numbuttons() == 32:
            print(f"Virpil 2 found!")
            vp2 = joystick
            myjoy.update({i : 1})
        if joystick.get_name() == "LEFT VPC Throttle MT-50CM3" and joystick.get_numaxes() == 0 and joystick.get_numbuttons() == 19:
            print(f"Virpil 3 found!")
            vp3 = joystick
            myjoy.update({i : 2})
        if joystick.get_name() == "LEFT VPC Throttle MT-50CM3" and joystick.get_numaxes() > 0:
            print(f"Virpil 4 found!")
            vp4 = joystick
            myjoy.update({i : 3})  
    joysticks = {vjoy, vp2, vp3, vp4}
    if not joysticks:
        print("No Joysticks found!")
        quit()
    return joysticks
    
    

# MAIN LOOP
# connects the vjoy device, connects as a client and then sits in the polling loop.
# If the polling loop exits it is because of a disconnection, so just loop and
# wait to be reconnected

pygame.init()
joysticks = connect_joysticks()

while True:
    psx = connectPSX()
    poll(psx, joysticks)
    psx.close()
