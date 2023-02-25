#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import threading
import random
import sys


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    print ("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    sys.exit()

def GetMBNumber(name):
    global MBNumber
    
    print ("thread start")
    uid = [[0]*10]
    HexUID = [[0]*10]

    while True:
    # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
        if status == MIFAREReader.MI_OK:
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            HexUID = format(int(uid[0]),'02X') + format(int(uid[1]),'02X') + format(int(uid[2]),'02X') + format(int(uid[3]),'02X') + format(int(uid[4]),'02X')
            #print(int(HexUID,16))
            MBNumber = int(HexUID,16) + random.randint(1,101)

if __name__ == "__main__":
    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()
    GPIO.cleanup()
    MIFAREReader = MFRC522.MFRC522()

    # Welcome message
    print ("Welcome to the MFRC522 data read example")
    print ("Press Ctrl-C to stop.")

    global MBNumber
    MBNumber = "start"
    oldMBNumber = MBNumber

    MB_value = threading.Thread(target=GetMBNumber, args=(1,), daemon=True).start()
    while True:
        if oldMBNumber != MBNumber:
            oldMBNumber = MBNumber
            print(":::::",MBNumber,":::::")

