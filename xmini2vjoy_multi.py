
##########################################################################################
#                                                                            
#                                   xmini2vjoy_multi.py                            
#                                                                            
#                                   FreePIE Script                           
#                                     v.1.1                             
#                                                                            
#                                                                            
#            Midi Controller Behringer X-Touch Mini ---> X-Plane, FSX, ...   
#                      1x vJoy: 16 Encoders, 2 Sliders, 48 Buttons           
#                                                                            
#                                                                            
#               This script will let you take control of your sim's axes,    
#               knobs and buttons easily using the Behringer X-Touch Mini    
#                                                                            
#                                     Installation:                          
#                                                                            
#                   1. Download and run vJOY v2.1.9 & FreePIE v1.11.724.0    
#                                                                            
#     http://vjoystick.sourceforge.net/site/index.php/download-a-install/download   
#                       https://andersmalmgren.github.io/FreePIE/            
#                                                                            
#                                                                            
#                   2. Use Behringer's X-Touch Editor to set the encoders    
#                   of your Mini to CC, Relative2 mode.                      
#                                                                            
#                   3. Use vJoyConf to generate 1 virtual joystick           
#                   with 1 axis and 128 buttons (no POVs are needed.)         
#                   That's all we will need to model X-Touch Mini's          
#                   layers A and B.                                          
#                                                                            
#                   4. Place this script on FreePIE's data  folder:           
#                   C:\ProgramData\Freepie Data\                     
#                                                                            
#                   5. Start windows Task Scheduler (taskschd.msc)           
#                                                                            
#                   6. Create a new task "start freepie" , choose your user account,
#                     choose independent of user logon (makes it invisible)
#                    Trigger: "on user logon"
#                    Action: Start program "C:\Program Files (x86)\FreePIE\FreePIE.exe" with
#                    argument  "C:\PROGRA~3\FREEPI~1\xmini2vjoy_multi.py /r /t" (no quotes)
#                                                                            
#                                                                            
#                          Josep Zambrano, December 30, 2019                    
#                          Modified by trijet_arno April 2022                     
#                                                                             
#                                                                            
##########################################################################################
import time

if starting:

###########################################     CUSTOMIZATION   CONFIGURATION    ####################################
    # choose for slider as windows volume up/down key emulation in stead of vjoy axis
    volume_slider = 0   # 0 means vjoy slider axis, 1 means slider adjusts volume

    #define properties of rotary encoders
    #                  ---------------BANK A-------------------     --------------------BANK B----------------
    #                 BAR, MOD, RNG, SPD, HDG,  ALT,  V/S,   NAV, NAV1, NAV2, ADF , DME , HSI , key , XPDR, COM1
    encoder_levels = (2  , 1  , 1  , 1  , 1   , 1   , 1    , 2   , 0   , 0   , 0   , 0   , 2   , 0   , 0   , 0    )  #maximum 31 in total
    encoder_reset =  (5  , 0  , 0  , 0  , 0   , 0   , 0    , 5   , 10  , 10  , 10  , 10  , 0   , 0   , 10  , 10   )  #focus time-out in seconds
    encoder_speed =  (1.0, 1.0, 1.0, 1.5, 1.5 , 1.8 , 1.0  , 1.3 , 1.8 , 1.8 , 1.8 , 1.8 , 1.8 , 1.0 , 1.0 , 1.8  )  #twist acceleration factor

    long_press_time = 0.50    # minimum duration of long press in seconds

######################################################################################################################

    speed = 64  # type: int
    drive = 0   # type: int
    times = 0   # type: int
    axis = 0    # type: int
    t_start = 0
    last_volume = -1
    cycle_counter = 20
    long_press_latch = 0
    
    # Delays ~0.013, depends on your CPU, adjust if you find trouble reading encoders, axes and buttons.    
    loop_delay = 0.03   # type: float , duration of press and pause between repeats
    cycle_delay = 0.01  # type: float
       
    #intitalize working variables and define button range per encoder
    encoder_base = [66]
    encoder_focus = [0]
    encoder_time = [0]
    for i in range(len(encoder_levels)):
       if i:
           encoder_focus.append(0)
           encoder_time.append(0)
           encoder_base.append( encoder_base[i-1] + encoder_levels[i-1] * 2 )
       if encoder_base[i] + encoder_levels[i] * 2 > 128:
           levels_found = str( (encoder_base[i] - encoder_base[0]) / 2 + encoder_levels[i] )
           diagnostics.debug("Too many encoder levels, maximum is 31 levels combined for all encoders. You have "+levels_found)
     
    vJoy[0].setButton(64,1) #always signal gear down on startup until the silder moves
           
def check_timer(used_encoder):
    if (encoder_time[used_encoder] + encoder_reset[used_encoder] < time.clock()) and encoder_reset[used_encoder]:   #x seconds have expired
        encoder_focus[used_encoder] = 0
    encoder_time[used_encoder] = time.clock()    #update usage
         
    
def  short_press(used_encoder):
    if encoder_levels[used_encoder] < 2:
        vJoy[0].setButton(used_encoder, 1)     # pass button to game 
        time.sleep(loop_delay)
        vJoy[0].setButton(used_encoder, 0)
    else:
        encoder_time[used_encoder] = time.clock()    #update usage
        encoder_focus[used_encoder] += 1   #switch focus
        if encoder_focus[used_encoder] == encoder_levels[used_encoder]:
            encoder_focus[used_encoder] = 0
      
def long_press(used_encoder):
    global long_press_latch
    if long_press_latch == 0:
        vJoy[0].setButton(used_encoder + 16, 1)
        time.sleep(loop_delay)
        vJoy[0].setButton(used_encoder + 16, 0)
        if encoder_reset[used_encoder]:
            encoder_time[used_encoder] = time.clock()    #update usage
            encoder_focus[used_encoder] += 1   #switch focus
            if encoder_focus[used_encoder] == encoder_levels[used_encoder]:
                encoder_focus[used_encoder] = 0
        long_press_latch = 1


def map_cc_buttons(cc, encoder1):

    """ maps an X-Mini's relative encoder to two vJoy buttons, back and forth.

        X-Mini's relative encoder mode 2 works like this: when you move an
        encoder to your left, it will give you cc messages 63, 62, 61...
        depending on how fast you turn it. When you move it to your right,
        will send cc messages 65, 66, 67, etc.

         This function gives one or more button presses of button1 or button2
         depending on the direction and speed of turn of the encoder """
         

    if (midi[0].data.buffer[0] == cc) and (midi[0].data.status == MidiStatus.Control):
        check_timer( encoder1)
        button1 = encoder_base[encoder1] + 2*encoder_focus[encoder1]
        button2 = button1 + 1
    
        speed = midi[0].data.buffer[1]
        drive = speed - 64
        times = int(pow(abs(drive),encoder_speed[encoder1]))
        if encoder_levels[encoder1] == 0:
            drive = 0    # no button action when levels are zero
        if drive < 0:
            for i in range(times):
                vJoy[0].setButton(button1, 1)
                midi[0].data.buffer[0] = 99
                time.sleep(loop_delay)
                vJoy[0].setButton(button1, 0)
                time.sleep(loop_delay)
        elif drive > 0:
            for i in range(times):
                vJoy[0].setButton(button2, 1)
                midi[0].data.buffer[0] = 99
                time.sleep(loop_delay)  # CC    ENCODER     BTNS 1,2
                vJoy[0].setButton(button2, 0)
                time.sleep(loop_delay)

def map_cc_press(note, button):

    """ maps an X-Mini's midi note to a vJoy button, long press maps button + 16 """
    global t_start
    global long_press_latch
    if (midi[0].data.buffer[0] == note and midi[0].data.buffer[1] == 127
                       and (midi[0].data.status == MidiStatus.NoteOn)):
        if t_start == 0:
            t_start = time.clock()
        if ( time.clock() - t_start) >= long_press_time: # long press
            long_press(button)
    elif (midi[0].data.buffer[0] == note and midi[0].data.buffer[1] == 0
                       and (midi[0].data.status == MidiStatus.NoteOff) and t_start > 0):
            # on release, check for short press depending on time runing since start of press
            if ( time.clock() - t_start) >= cycle_delay and ( time.clock() - t_start) < long_press_time:
                short_press(button)
            t_start = 0
            long_press_latch = 0
            
    
def map_note_button(note, button):

    """ maps an X-Mini's midi note to a vJoy button """

    vJoy[0].setButton(button, midi[0].data.buffer[0] == note and midi[0].data.buffer[1] == 127
                       and (midi[0].data.status == MidiStatus.NoteOn))



#      Layer A: Rotary Encoders        #######################################  MIDI ## CONTROL ### X-PLANE ###

encoder_num = 0    # type: int
base_cc = 1         # type: int

for n in range(8):
    map_cc_buttons(base_cc + n, encoder_num + n )  # CC  Encoders 1-8 



#      Layer B: Rotary Encoders        #######################################  MIDI  ## CONTROL ### X-PLANE ###

encoder_num = 8   # type: int
base_cc = 11        # type: int

for n in range(8):
    map_cc_buttons(base_cc + n, encoder_num + n )   # CC  Encoders 9-16  


#      Layer A/B: Slider     ######################################  MIDI  ## CONTROL ### X-PLANE ###
#        Modified to output gear commands to buttons 64 and 65

if  ((midi[0].data.buffer[0] == 9) or (midi[0].data.buffer[0] == 10)) and (midi[0].data.status == MidiStatus.Control):

    if volume_slider:
        new_volume = round(filters.mapRange(midi[0].data.buffer[1], 0, 127, 0, 50))
        
        if last_volume == -1: # first call, just set reference position to prevent jumps
            last_volume = new_volume
        
        while new_volume > last_volume:
            keyboard.setKeyDown(Key.VolumeUp)
            keyboard.setKeyUp(Key.VolumeUp)
            last_volume += 1
            
        while new_volume < last_volume:
            keyboard.setKeyDown(Key.VolumeDown)
            keyboard.setKeyUp(Key.VolumeDown)
            last_volume -= 1
        
    else:
        if (midi[0].data.buffer[1] < 32):
            vJoy[0].setButton(65,0) #gear hydrauilics on
            vJoy[0].setButton(64,1) #gear down 
            
        elif (midi[0].data.buffer[1] > 95):
            vJoy[0].setButton(65,0) #gear hydrauilics on
            vJoy[0].setButton(64,0) #gear up 
 
        else:
            vJoy[0].setButton(65,1)  #gear hydrauilics off, no gear operation
            
        vJoy[0].x = filters.mapRange(midi[0].data.buffer[1], 0, 127, -16382, 16382)



#      Layer A: Encoder Buttons        #######################################  MIDI  ## CONTROL ### X-PLANE ###

base_button = 0     # type: int
base_note = 0       # type: int

for n in range(8):
    map_cc_press(base_note + n, base_button + n)                  #Note  Encoders 1-8  Buttons 1-8 long press 17-24

#      Layer B: Encoder Buttons        #######################################  MIDI  ## CONTROL ### X-PLANE ###

base_button = 8    # type: int
base_note = 24      # type: int

for n in range(8):
    map_cc_press(base_note + n, base_button + n)                  #Note  Encoders 9-16 Buttons 9-16 long press 25-32


#      Layer A: Square Buttons         #######################################  MIDI  ## CONTROL ### X-PLANE ###

base_button = 32     # type: int
base_note = 8       # type: int

for n in range(16):
    map_note_button(base_note + n, base_button + n)                  #Note Sqr Button 9-24 Buttons 32-47


#      Layer B: Square Buttons         #######################################  MIDI  ## CONTROL ### X-PLANE ###

base_button = 48    # type: int
base_note = 32      # type: int

for n in range(16):
    map_note_button(base_note + n, base_button + n)                  #Note Sqr Button 33-48 Buttons 48-63


#      Midi Monitor for FreePIE's Console      ###############

def update():

    diagnostics.watch(midi[0].data.channel)
    diagnostics.watch(midi[0].data.status)
    diagnostics.watch(midi[0].data.buffer[0])
    diagnostics.watch(midi[0].data.buffer[1])


if starting:
    midi[0].update += update

# every fifth cycle check for volume 0 or 50 and keep pressing volume if so (self-calibration)
if cycle_counter:
    cycle_counter -= 1
else:
    cycle_counter = 5
    if last_volume == 0:
        keyboard.setKeyDown(Key.VolumeDown)
        keyboard.setKeyUp(Key.VolumeDown)
    if last_volume == 50:
        keyboard.setKeyDown(Key.VolumeUp)
        keyboard.setKeyUp(Key.VolumeUp)
     
#      Stabilizing Delay to allow time for getting encoder and button data      #############
time.sleep(cycle_delay)

