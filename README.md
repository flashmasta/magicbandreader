# magicbandreader
Reads magic bands and plays sounds and lights up leds, just like the real thing.
Use webhook URLS to turn on lights or unlock locks.

# Fork Updates
This forks works with NON-USB RFID readers--the cheap US$3 ones found on auction sites.  It requires modified installation activities and hardware connections.  Those changes are made in the rest of this README.  This was done on a RPi 3B running the FULL Raspbian load on a 64GB memory card.  I am sure that much space is not necessary.  This version also does NOT require the HDMI port for sound. Yup!!  Use the on-board 3.5mm headphone jack and don't buy the HDMI-to-Audio cable.

# NOTE
Sound files are no longer included. Either supply your own mp3 sound files or contact us through youtube for more information.

# 3D Printer pieces
Find the pieces to make this model on thingiverse:
https://www.thingiverse.com/thing:4271417

# Upgrade
If you are upgrading from a previous version, be sure to re-run the install script to pick up the new required files:
sudo sh install.sh. 

BACKUP YOUR magicband.py BEFORE UPGRADING so you don't lose you sequences configurations! You'll need to migrate any old configurations that were stored in the magicband.py file to the new settings.conf file.

# New Features in this Fork
* No need for HDMI sound.  Use the onboard 3.5mm headphone port.
* If you scan the same magic band 3 times (after each light sequence has completed) within 60 seconds it will toggle on-and-off the spinning white light.  The reader will still function as expected when a band is read.
* If you scan the same magic band 5 times (after each light sequence has completed) within 60 seconds it will start the RPi shutdown process.
* If you are going to play with the code, turn on and off debug messages by changing the value of DEBUG at the top of the code.
* So, you want to make your magic bands turn on and off your house lights or something else???  So did I!!  This fork now includes details on how to get there.  See below!

# New Features (From previous fork)
* All configurations are now stored in settings.conf file instead of editing the python file directly.
* New color support including rainbow (see example config for details) Make sure you are using the newest color names.
* Webhook support for turning on lights or opening locks when a magic band is played
* Multiple sequence support per individual magic bands. (A single magicband can have multiple sequences assigned to it.)

#Basic wiring:
* Connect PIXEL LEDS to  DATA on GPIO-18 (pin 12), pixel GnD to GND (pin 6) and pixel positive to +5v (pin 2)
* Connect cheap RFID reader to RPi BUS as described in my MFRC522 repository.  Its 7 wires, and soldering is encouraged.
* Connect Speaker via 3.5mm headphone connector

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
* Make monitor hot-plug and force HMDI sound with: sudo vi /boot/config.txt
  * remove # from the front of hdmi_force_hotplug=1
  * remove # from the front of hdmi_drive=2
  * at the end, add: enable_hdmi_sound 
* sudo vi /etc/rc.local
  * Before the exit 0 line add:
  * (cd /home/pi; sudo python3 magicband.py &)
* sudo reboot now

See videos for more details
Note: if you are using the older videos to follow along, the main difference with the latest code is the settings.conf. Updated videos coming soon. 

# Config

* Set the ring_pixels and mickey_pixel counts to the correct value
* If you have any magic bands and want special lights and sounds, update the settigns file.  Use the MyReader.py file to get the magicband ID.  Read it a couple times.  Notice that the last 2-3 digits change.  Ignore those and just use the ones that don't change.

# Home Assistant and Node Red

The coolest part of this is that you can make it actually do something in your home.  You just need to have the right setup.  I accomplished this with a second RPi (an RPI4) running Home Assistant and the NodeRed addon.  To save you some work, I am including some details to help you out.  Getting HA and NodeRed setup and running are beyond the scope of this effort.
* Import the flows.json file from this fork into NodeRed.  The key part here is that I figured out how to recieve the webhook.  You will still need to tweak a few things, like changin an IP address or two and BandID's.  The nice thing here is that once you get it up and running, if it reads a bandId it doesn't know, you can look in the debugger for the number and code it to do something.
* You also need to update the settings.conf file.  In each of the band profiles, there is a 'webhook:' entry.  Notice there is nothing else on that line.  You need to change every instance where you want an action to occur.  Change all of them (with your Home Assistant IP address) to look something like:   webhooks = http://[HA IP ADDRESS]:1800/endpoint/MBReader

# Troubleshooting

If the install fails, try running this command first:
sudo apt-get update



