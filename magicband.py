#!/usr/bin/env python
from __future__ import print_function
import pygame
import argparse
import binascii
import logging
import hashlib
import struct
#import ndef
import hmac
import cli
import sys
import os
import time
import board
import neopixel
import time
import os.path
from os import path
import random
import configobj
from json import dumps
from httplib2 import Http
import threading
import atexit
import RPi.GPIO as GPIO
import MFRC522
import signal

DEBUG = True

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
config = configobj.ConfigObj('settings.conf')
print_band_id = config['Settings']['print_band_id']
reverse_circle = config['Settings']['reverse_circle']
ring_pixels = int(config['Settings']['ring_pixels'])
mickey_pixels = int(config['Settings']['mickey_pixels'])

# Format is (R, G, B)
COLORS = {
    "red": (255, 0, 0),
    "electricred": (228, 3, 3),
    "orange": (255, 165, 0),
    "dark orange": (255, 140, 0),
    "yellow": (255, 255, 0),
    "canaryyellow": (255, 237, 0),
    "green": (0, 255, 0),
    "lasallegreen": (0, 128, 38),
    "teal": (0, 128, 128),
    "blue": (0, 0, 255),
    "patriarch": (117, 7, 135),
    "lightblue": (153, 204, 255),
    "white": (255, 255, 255),
    "purple": (0, 153, 153),
    "gray": (128, 128, 128),
    "pink": (255, 105, 180),
    "stitch": (0, 39, 144),
    "rainbow": (0, 0, 0),
    "pride": (0, 0, 1),
}
sequences = config['sequences']
# GPIO Pin (Recommend GPIO18) GPIO13 is also a good choice
pixel_pin = board.D21

if sys.version_info.major < 3:
    sys.exit("This script requires Python 3")

log = logging.getLogger('main')

log.setLevel(logging.CRITICAL)

# Pre init helps to get rid of sound lag
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()

totalPixels = ring_pixels+mickey_pixels

currentBandId = ""
repeatCount = 0
repeatBandId = ""
repeatTime = time.time()
whiteIdleActive = True

pixels = neopixel.NeoPixel(pixel_pin, totalPixels, brightness=0.9, auto_write=False, pixel_order=neopixel.GRB)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    if (DEBUG):
        print ("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    sys.exit()

def playLightSequence(magicBandScannedEvent, successEvent, ringPixels, totalPixels):
    lightSpeed = .1
    pixelRingArray = list(range(0, ringPixels-1))
    if reverse_circle == 'True':
        pixelRingArray.reverse()
    global pixels
    if (DEBUG):
        print("Playing light sequence")
    
    global whiteIdleActive
    while True:
        if (not whiteIdleActive) and (not magicBandScannedEvent.isSet()):
            continue
        if not magicBandScannedEvent.isSet():
            lightSpeed = .1
        else:
            if lightSpeed == .1:
                lightSpeed = lightSpeed * .50
            else:
                lightSpeed = lightSpeed * .95

        if lightSpeed < 0.001:
            successEvent.set()

        if lightSpeed < 0.000001:
            global currentBandId
            sequence = getSequence(currentBandId)
            runSuccess(magicBandScannedEvent, successEvent, sequence)
            lightSpeed = .1
        else:
            leadingIndex = pixelRingArray[4]
            trailingIndex = pixelRingArray[0]
            color = COLORS['white']
            if magicBandScannedEvent.isSet():
                sequence = getSequence(currentBandId)
                color = COLORS[sequence.get('color_ring')]
            if color == COLORS['rainbow']:
                rainbowCycle(1, 1)
                successEvent.set()
                runSuccess(magicBandScannedEvent, successEvent, sequence)
            else:
                pixels[leadingIndex] = fadePixel(False, pixels[leadingIndex], color)
                pixels[trailingIndex] = fadePixel(True, pixels[trailingIndex], color)
                pixels.show()
                pixelRingArray = rotateArray(pixelRingArray)
                time.sleep(lightSpeed)

def runSuccess(bandEvent, successEvent, sequence):
    showAllColored(pixels, COLORS[sequence.get('color_mouse')])
    time.sleep(int(sequence.get('hold_seconds')))
    magicBandScannedEvent.clear()
    successEvent.clear()
    doLightFadeOff(pixels)
    pixels.brightness = 0.9

def wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbowCycle(wait, iterations):
    for j in range(256 * iterations):
        for i in range(ring_pixels):
            pixels[i] = wheel((int(i * 256 / ring_pixels) + j) & 255)
        pixels.show()
        time.sleep(wait/1000)

def theaterChase(wait, iterations):
    for j in range(256 * iterations):
        for i in range(ring_pixels):
            if (i + j) % 3 == 0:
                pixels[i] = (255, 0, 0)
            else:
                pixels[i] = (0, 255, 0)
        pixels.show()
        time.sleep(wait/1000)

def doLightFadeOff(pixels):
    brightness = 1.01
    for x in range(100):
        brightness = brightness - .01
        pixels.brightness = brightness
        pixels.show()
        time.sleep(.0005)
    doLightsOff(pixels)

def doLightsOff(pixels):
    for i in range(totalPixels):
        pixels[i] = 0 
    pixels.show()

def showAllColored(pixels, color):
    for i in range(totalPixels):
        pixels[i] = color

    pixels.show()

def rotateArray(arr):
    firstValue = arr.pop(0)
    arr.append(firstValue)
    return arr

def exit_handler():
    doLightsOff(pixels)

def printArray(arr):
    for i in range(len(arr)):
        if (DEBUG):
            print ("%d"% arr[i],end=" ")

def fadePixel(out, pixel, color):
    if out:
        return (0, 0, 0)
    if not out:
        return color

def getSequence(bandid):
    sequences = config['bands'].get(str(bandid)) or config['bands']['unknown']
    if sequences:
        sequences = sequences if type(sequences) == list else [sequences,]
        sequence = config['sequences'][random.choice(sequences)]
        if (DEBUG):
            print("getsequences = " + str(sequences))
        return sequence

class MagicBand():
    def __init__(self):
        self.success = True
        self.successSequence = []

class BandScannerAndSound():
    def __init__(self, scannedEvent, successEvent):     
        if (DEBUG):
            print("Scanning")
        self.scannedEvent = scannedEvent
        self.successEvent = successEvent

        # Scan for cards
        uid = [0,0,0,0,0]
        bandid = 0
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            HexUID = format(int(uid[0]),'02X') + format(int(uid[1]),'02X') + format(int(uid[2]),'02X') + format(int(uid[3]),'02X') + format(int(uid[4]),'02X')
            bandid = int(HexUID,16)
            if (DEBUG):
                print("MagicBandId = " + str(bandid))

        if self.scannedEvent.isSet():
            return
        if (bandid != 0):
            global repeatBandId
            global repeatTime
            global repeatCount
            if (repeatBandId == str(bandid)):
                if (time.time()-repeatTime <60):
                    repeatCount = repeatCount + 1
                if (time.time()-repeatTime >=60):
                    repeatTime = time.time()
                    repeatCount = 1
                if (repeatCount == 3):
                    print ("Still Running - Toggle White Spinner")
                    global whiteIdleActive
                    whiteIdleActive = not whiteIdleActive
                if (repeatCount == 5):
                    print ("Powering Down System")
                    repeatCount = 0
            else:
                repeatTime = time.time()
                repeatCount = 1
                repeatBandId = str(bandid)
            global currentBandId
            currentBandId = bandid
            self.scannedEvent.set()
            sequence = getSequence(bandid)
            if (DEBUG):
                print("Playing sound")
            self.playSound(sequence.get('spin_sound'))
            while not self.successEvent.isSet():
                continue
            self.playSound(sequence.get('sound'))
            self.runWebHook(sequence)

    def runWebHook(self, sequence):
        webhooks = sequence.get('webhooks', [])
        if webhooks:
            webhooks = webhooks if type(webhooks) == list else [webhooks,]
            for hook in webhooks:
                message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
                http_obj = Http()
                response = http_obj.request(
                    uri=hook,
                    method='POST',
                    headers=message_headers,
                )
                print(response)

    # Preload sound
    def loadSound(self, fname):
        if fname == '':
            return False
        if not path.exists(fname):
            print("Missing sound file :" + fname)
            return False
        if (DEBUG):
            print("Found file: " + fname)
        return True

    # play sound
    def playSound(self, fname):
        if self.loadSound(fname) == True:
            if (DEBUG):
                print("Playing sound now")
            pygame.mixer.music.load(fname)
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play()
#           while pygame.mixer.get_busy() == True:
#               time.sleep(1)

class ArgparseError(SystemExit):
    def __init__(self, prog, message):
        super(ArgparseError, self).__init__(2, prog, message)

    def __str__(self):
        return '{0}: {1}'.format(self.args[1], self.args[2])

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgparseError(self.prog, message)

if __name__ == '__main__':
    atexit.register(exit_handler)

    # Hook the SIGINT and create an object of MFRC522 for the card reader
    signal.signal(signal.SIGINT, end_read)
    MIFAREReader = MFRC522.MFRC522()

    magicBandScannedEvent = threading.Event()
    successEvent = threading.Event()
    magicBandObject = MagicBand()
    
    try:
        lightsThread = threading.Thread(name='lights',
            target=playLightSequence, args=(magicBandScannedEvent, successEvent, ring_pixels, ring_pixels+mickey_pixels), daemon = True)
        lightsThread.start()
        while True:
            bandAndSound = BandScannerAndSound(magicBandScannedEvent, successEvent)
        lightsThread.join()

    except ArgparseError as e:
        print("exception")
        print(e)
        _prog = e.args[1].split()

    else:
        sys.exit(0)

