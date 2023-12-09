# PSX-XTouchMini

This script for Windows searches for and connects multiple USB devices (joysticks, throttles etc) to AeroWinx PSX.
It does not matter which order they are discovered, as it builds an internal
table to identify devices correctly. As it can link to PSX server directly as a client, it can send a much wider set of control commands than
are offered by the USB interface in PSX, but it can also emulate single and multiple keypresses.

Provided that the X-Touch Mini MIDI device has been connected to a vjoy virtual joystick using
the FreePie script attached (not my authorship) then this script can deal with that too.

I am afraid there is no easy GUI here, you will need to customise the code to your system but I have tried to make that simple.

The precise button numbers on the vjoy device depend on how you have set up the X-Touch Mini in 
the Freepie script - they are not constant. </p>Eg I have defined two "virtual" rotary
encoders for the leftmost dial and this has pushed the numbering of all subsquent dials
by +2

# Prerequisites

1. Install Python https://www.python.org/downloads/windows/

1. `pip install telnetlib time pyautogui pygame==2.4.0` </p>(use pygame 2.4.0 as newer versions of pygame may contain a regression in which some connected USB devices are not recognised.)

1. Install Freepie from https://andersmalmgren.github.io/FreePIE/

1. Install Vjoy from https://github.com/shauleiz/vJoy

1. You may need the X-Touch Mini editor from Behringer if not already installed: find it in "Product Library -> Software" at https://www.behringer.com/product.html?modelCode=P0B3M

# Customisation

Out of the box the script will identify a single X-Touch Mini attached as a sole vjoy stick, and will connect it to PSX running on the same machine. A PDF is included of the default mappings. To change the mappings or to add any additional USB hardware you need to get into the code.

- Initialise the X-Touch Mini using layerA.bin and layerB.bin and the X-Touch Mini editor. Load Layer A and apply to the X-Touch, then repeat for Layer B. Then close the editor - it cannot run simultaneously with FreePie.
- Customise to your liking the accompanying FreePie script for the X-Touch Mini `xmini2vjoy_multi.py`
    written by Josep Zambrano and amended by trijet_arno. The FreePie script converts each button press and rotary movement on the X-Touch Mini to a button press on the
    vjoy virtual joystick. 
    The header in this allows you to redefine your X-Touch Mini layout
    e.g. each encoder can be 2, 3 or 4 virtual encoders should you so wish.<p>
    Full instructions in the script and on this page: 
    https://forums.x-plane.org/index.php?/files/file/81652-freepie-advanced-script-for-behringer-x-touch-mini/<p>
    The precise button numbers on the vjoy device will end up depending on how you have set up
the Freepie script - they are not constant. </p>Eg I have defined two "virtual" rotary
encoders for the leftmost dial (which I use for BARO) and this has bumped the numbering of all subsquent dials
by +2

- Edit `xt-psx.py`
  - Check that the PSX server host and port assignments are correct for your system. The defaults are localhost and the default PSX port.
  - go through the `connect_joysticks()` code and make sure it identifies and numbers your hardware correctly. The aim is to identify your hardware by name or other characteristics if name is ambiguous, and assign a device number 0, 1, 2... which corresponds to the mappings defined in `button_commands`
  - go through the `button_commands` dict and assign the right commands to the right buttons. You can use PSX client codes as binary strings  eg `b"Qh69=1"`, single keyboard keys eg `'t'`, or hotkey pairs eg `['alt','z']`. Please note that PSX needs to have keyboard focus (to be the foremost selected app) for keycodes / hotkeys to be passed on, not needed for commands sent client to server.
 
Setup can be made easier by starting FreePie with `xmini2vjoy_multi.py`, starting PSX as a server, and then running 
`python xt-psx.py` in a terminal window: it will show a list of USB devices it has found, and once these have been identified by altering the connect_joysticks() code, it will identify button presses
on the hardware
 
#  Usage

Start FreePie and from there load and start the `xmini2vjoy_multi.py` script, then in a terminal window run </p>
    `python xt-psx.py`

Once PSX is connected you should be able to test whether your X-Touch Mini inputs are being detected by the script.

 
