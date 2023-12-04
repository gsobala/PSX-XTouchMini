# PSX-XTouchMini

This uses the vjoy device which has been bound
from the X-Touch Mini by the accompanying FreePie script.
Each button press and rotary movement are translated to a button press on the
virtual joystick.

It sets up a telnet connection to PSX to send client commands directly.
Some commands are better sent as virtual keypresses and it handles these also.
The connection to PSX is "write-only".
The layout of the X-Touch Mini is handled by the FreePie script.

The precise button numbers on the vjoy device depend on how you have set up
the Freepie script - they are not constant. </p>Eg I have defined two "virtual" rotary
encoders for the leftmost dial and this has pushed the numbering of all subsquent dials
by +2

Experiment freely, This script will show the number of each X-Touch Mini input as it is made.

# Requirements

(1) Freepie from https://andersmalmgren.github.io/FreePIE/

(2) The accompanying script for the X-Touch Mini xmini2vjoy_multi.py
    written by Josep Zambrano and amended by trijet_arno.</p>
    The header in this allows you to redefine your X-Touch Mini layout
    e.g. each encoder can be 2, 3 or 4 virtual encoders should you so wish.
    Full instructions in the script and on this page: 
    https://forums.x-plane.org/index.php?/files/file/81652-freepie-advanced-script-for-behringer-x-touch-mini/

(3) Vjoy from https://github.com/shauleiz/vJoy

(4) Python

(5) `pip install pygame==2.4.0` </p>(as newer versions of pygame may contain a regression in which some connected devices are not recognised.)

    pip install telnetlib time pyautogui

Start FreePie and from there load and start the xmini2vjoy_multi.py script, then run </p>
    `python xt-psx.py`

Once PSX is connected you should be able to test whether your X-Touch inputs are being detected by the script.

 
