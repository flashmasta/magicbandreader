# magicbandreader
Reads magic bands and plays sounds and lights up leds, just like the real thing.
Use webhook URLS to turn on lights or unlock locks.

# Fork Updates
This forks works with NON-USB RFID readers--the cheap US$3 ones found on aucton sites.  It requires modified installation activities and hardware connections.  Those changes are made in the rest of this README.  This was done on a RPi 3B running the FULL Raspbian load on a 64GB memory card.  I am sure that much space is not necessary.

# NOTE
Sound files are no longer included. Either supply your own mp3 sound files or contact us through youtube for more information.

# 3D Printer pieces:
Find the pieces to make this model on thingiverse:
https://www.thingiverse.com/thing:4271417

# Upgrade
If you are upgrading from a previous version, be sure to re-run the install script to pick up the new required files:
sudo sh install.sh. 

BACKUP YOUR magicband.py BEFORE UPGRADING so you don't lose you sequences configurations! You'll need to migrate any old configurations that were stored in the magicband.py file to the new settings.conf file.

# New Features in this Fork
* If you scan the same magic band 3 times (after each light sequence has completed) within 60 seconds it will toggle on-and-off the spinning white light.  The reader will still function as expected when a band is read.
* If you scan the same magic band 5 times (after each light sequence has completed) within 60 seconds it will start the RPi shutdown process.

# New Features (From previous fork)
* All configurations are now stored in settings.conf file instead of editing the python file directly.
* New color support including rainbow (see example config for details) Make sure you are using the newest color names.
* Webhook support for turning on lights or opening locks when a magic band is played
* Multiple sequence support per individual magic bands. (A single magicband can have multiple sequences assigned to it.)

#Basic wiring:
* Connect PIXEL LEDS to  DATA on GPIO-18 (pin 12), pixel GnD to GND (pin 6) and pixel positive to +5v (pin 2)
* Connect cheap RFID reader to RPi BUS as described in my MFRC522 repository.  Its 7 wires, and soldering is encouraged.
* Connect Speaker via HDMI connector (ONBOARD SPEAKER WILL NOT WORK DUE TO Pixel LEDS!)

# Installation

* Install Raspbian onto pi 
* use 'sudo raspi-config' to enable SSH, SPI, and your wireless network.
* sudo apt-get update
* sudo apt-get upgrade
* install the SPI library:  sudo pip3 sudo pip3 install git+https://github.com/lnaleefer/SPI-py
* pull down this git repository: git clone https://github.com/texasmouse/magicbandreader.git
* and you need two files (MFRC522.py and MyReader.py) from this repository: git clone https://github.com/texasmouse/MFRC522.git.  Put those two files in the same directory as the MagicBandReader files.
* cd magicbandreader
* sudo sh install.sh  (this will take awhile)
* cp * /home/pi/.
* sudo reboot now
* log back into pi
* vi /home/pi/settings.conf. and edit the led counts for your build
* sudo vi /etc/rc.local
  * Before the exit 0 line add:
  * (cd /home/pi; sudo python3 magicband.py &)
* sudo reboot now

See videos for more details
Note: if you are using the older videos to follow along, the main difference with the latest code is the settings.conf. Updated videos coming soon. 

# Config

* Set the ring_pixels and mickey_pixel counts to the correct value
* If you have any magic bands and want special lights and sounds, update the settigns file.  Use the MyReader.py file to get the magicband ID.  Read it a couple times.  Notice that the last 2-3 digits change.  Ignore those and just use the ones that don't change.

# Troubleshooting

If the install fails, try running this command first:
sudo apt-get update



