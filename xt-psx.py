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

# This script will handle multiple additional real joysticks as well as vJoy

# TO CONFIGURE FOR YOUR SYSTEM:
# Check the host and port assignments for PSX
#
# Provided the FreePie script is running and you have no other vJoy devices, X-Touch Mini support should work
# just "out of the box".

# Otherwise to add further joysticks:

# (b) go through the connect_joysticks() code and make sure it identifies and numbers your hardware correctly
# (c) go through the button_commands dict and assign the right commands to the right buttons
# 
#
# if host and port are set correctly just start the python script in a command window and it will output
# information on each joystick it finds to help you sort out connect_joysticks()
# then if you run the amended script again it will show what button numbers it detects on attached
# devices


import pygame
import telnetlib
import time
from pyautogui import press, hotkey, keyDown, keyUp

host = '127.0.0.1'          # hostname for PSX server, default is localhost                   
port = 10747                # which PSX server port to connect to
    
pygame.init()
pygame.joystick.init()
clock = pygame.time.Clock()

myjoy = {} # this will hold the translation table from physical to virtual joystick numbering set by connect_joysticks()

# button_commands defines each button on each joystick that we want to use
# The joystick numbering is set by connect_joysticks() later
# For each button define either a single character eg 't', two key hotkey combo as an array 
# to be sent as keyboard emulation eg ['alt', 'z'],
# or a PSX command byte string to be sent over the network client to server eg b"Qh69=1"

button_commands = {
# First Joystick : vjoy
0 : {                                           # This is our virtual joystick number 0, eg the X-Touch Mini via FreePie
    1: b"Qh26=1", # CTR
    2: b"Qh27=1", # TFC   
    3: b"Qh60=1", # SPD sel
    4: b"Qh61=1", # HDG sel
    5: b"Qh62=1", # ALT sel
    6: b"Qh69=1", # VS sel
    16: b"Qh25=1", # Baro STD (long press)
    17: b"Qh22=1", # FPV (long press)
    18: b"Qh23=1", # Meters (long press)
    19: b"Qh67=1", # FLCH (long press)
    20: b"Qh68=1", # HDG hold (long press)
    21: b"Qh70=1", # ALT hold (long press)
    23: b"Qh407=7", # switch standby and COM1 (long press)
    24: b"Qh267=1", # pull START1 (long press)
    25: b"Qh268=1", # pull START2 (long press)
    26: b"Qh269=1", # pull START3 (long press)
    27: b"Qh270=1", # pull START4 (long press)
    28: b"Qh392=1", # Fuel Cut-off1 (long press)
    29: b"Qh393=1", # Fuel Cut-off2 (long press)
    30: b"Qh394=1", # Fuel Cut-off3 (long press) 
    31: b"Qh395=1", # Fuel Cut-off4 (long press)
    32: b"Qh15=1", # WXR
    33: b"Qh63=1", # THR    
    34: b"Qh65=1", # LNAV
    35: 't',  # A/T ARM
    36: b"Qh71=1", # LOC
    38: b"Qs104=FWtMGaREFWTmG", # Weather WX+T on left map on right
    39: b"Qs104=FWTmGaREFWtMG", # Weather map on left WX+T on right
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
    70: ['alt','k'], # ND mode down
    71: ['alt','l'], # ND mode up
    72: ['alt','a'], # Range down
    73: ['alt','z'], # Range up
    74: b"Qh77=-1", # SPD down
    75: b"Qh77=1", # SPD up
    76: b"Qh78=-1", # HDG down
    77: b"Qh78=1", # HDG up
    78: b"Qh80=-1", # ALT down
    79: b"Qh80=1", # ALT up
    80: b"Qh79=-1", # VS down
    81: b"Qh79=1", # VS up
    82: b"Qs109=0;-1;0", # main COM1 down
    83: b"Qs109=0;1;0", # main COM1 up
    84: b"Qs109=0;0;-1", # small COM1 down
    85: b"Qs109=0;0;1", # small COM1 up
    },   
# Virpil 1
1 : {                                            # This is our virtual joystick number 1, in this example a Virpil CM3 
    0: b"Qh386=1", # Lt Thrust Disconnect
    1: b"Qi191=199359", # Start Pushback
    2: b"Qi191=120359", # Stop Pushback
    3: b"Qh397=1", # Park Brk Lever
    11: b"Qh170=1", # Gear down
    12: b"Qh170=3", # Gear up
    17: b"Qh61=1", # HDG sel
    18: b"Qh78=-1", # HDG down
    19: b"Qh78=1", # HDG up
    20: b"Qh70=1", # ALT hold
    21: b"Qh80=-1", # ALT down
    22: b"Qh80=1", # ALT up
    },
# Virpil 2
2 : {                                          # This is our virtual joystick number 2, in this example more of the CM3
    },   
# Virpil 3
3 : {                                          # This is our virtual joystick number 3, in this example even more of the CM3
    0: b"Qh60=1", # SPD sel
    1: b"Qh77=-1", # SPD down
    2: b"Qh77=1", # SPD up 
    13: b"Qh79=-1", # VS down
    14: b"Qh79=1", # VS up
    15: b"Qh69=1", # VS sel
    31: b"Qh387=1", # Lt Thrust TOGA
    }, 
# WinWing FCU
4 : {
    11: b"Qh60=1", # SPD sel activated by pushing SPD rotary
    15: b"Qh61=1", # HDG sel activated by pushing HDG rotary
    19: b"Qh62=1", # ALT sel activated by pushing ALT rotary
    23: b"Qh69=1", # VS sel activated by pushing VS rotary
    16: b"Qh68=1", # HDG hold activated by pulling HDG rotary
    20: b"Qh70=1", # ALT hold activated by pulling ALT rotary
    5: 't',  # A/T ARM
    1: b"Qh71=1", # LOC
    3: b"Qh73=1", # CMD L
    8: b"Qh72=1", # APP
    9: b"Qh77=-1", # SPD down
    10: b"Qh77=1", # SPD up
    13: b"Qh78=-1", # HDG down
    14: b"Qh78=1", # HDG up
    17: b"Qh80=-1", # ALT down
    18: b"Qh80=1", # ALT up
    21: b"Qh79=-1", # VS down
    22: b"Qh79=1", # VS up
    0: b"Qh66=1", # VNAV activated by SPD MACH button
    2: b"Qh65=1", # LNAV activated by HDG TRK VS FPA button
    6: b"Qh67=1", # FLCH activated by EXPED button
    12: b"Qh64=1", # SPD activated by pulling SPD rotary
    }
}

# The next routine works out which joysticks are connected to the PC,
# identifies them and connects them to our virtual joystick table in the correct order

def connect_joysticks():
    # Get the number of joysticks
    joystick_count = pygame.joystick.get_count()

    print(f"Number of joysticks: {joystick_count}\n")

# Print out the details of each stick to help identify them when setting up for the first time
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        print(f"Joystick {i}")
        print(f"\tName:      {joystick.get_name()}")
        print(f"\tAxes:      {joystick.get_numaxes()}")
        print(f"\tButtons:   {joystick.get_numbuttons()}")
        print(f"\tHats:      {joystick.get_numhats()}")
        print(f"\tBalls:     {joystick.get_numballs()}")
        print("\n")
# now try to identify each stick by defining characteristics
# in most cases the name will be enough but some complicated hardware will show
# as duplicate names, so we may need to check other features
        if joystick.get_name() == "vJoy Device":
            print(f"vJoy found!")
            vjoy = joystick
            myjoy.update({i : 0})   # the second argument corresponds to the joystick number in the button_commands dict
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
        if joystick.get_name() == "WINWING FCU-320":
            print(f"WinWing FCU found!")
            vp5 = joystick
            myjoy.update({i : 4})  
    joysticks = {vjoy, vp2, vp3, vp4, vp5}   # we will only pass the joysticks that we want to be "live" to the polling routine
    if not joysticks:
        print("No Joysticks found!")
        quit()
    return joysticks
    

# Connect to PSX as a client, wait 5s and try again if not ready

def connectPSX():

    while True :
        try:
            psx = telnetlib.Telnet(host, port)
            break
        except Exception as e:
            print(f"Failed to connect to PSX: check host and port are correct")
            print(f"and that PSX is activated in server mode. Will retry in 5 sec.")
            time.sleep(5)
    print(f"Connected")
    time.sleep(0.1)
    psx.read_very_eager()
    return psx
            
# This is the main polling loop. Poll for a button press, and then send it to PSX either
# as a client or via single or combination keypresses via keyboard emulation

def poll(psx, joysticks):
    pygame.event.get() #flush the joystick queue on first connection
    
    while True:      
        for event in pygame.event.get(): # User did something
            if event.type == pygame.JOYBUTTONDOWN:                
                j = myjoy.get(event.joy)    # find which joystick dict we should be using
                joy_dict = button_commands.get(j) # load the right joystick dictionary
                command = joy_dict.get(event.button) # find the command to be sent as client
                print("Joystick button pressed.", event.button, j, command)
                if command:                     # if that button is bound to something
                    match len(command):
                        case 1:                 # single character, send as keypress
                            keyDown(command)
                            keyUp(command)
                        case 2:                 # hotkey pair
                            hotkey(command) 
                        case _:                 # in that case it must be a Qh command             
                            try:
                                psx.write(command+b'\n')                                
                            except Exception as e:          # fail gracefully if lost connection
                                print(f"Lost connection")
                                return

# now flush the client input queue, fail gracefully if we have lost the PSX connection
        try:
            psx.read_very_eager()
        except Exception as e:
            print(f"Lost connection")
            return
        clock.tick(20)  # limit interactions with PSX to 20Hz
        

# Main loop
# connects the joysticks, connects to PSX as a client and then sits in the polling loop.
# If the polling loop exits it is because of a disconnection to PSX, so just loop and
# wait to be reconnected

joysticks = connect_joysticks()

while True:
    psx = connectPSX()
    poll(psx, joysticks)
    psx.close()
