# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
--------------------------------------------------------------------------
Song Name Display & Music Player
--------------------------------------------------------------------------
License:   
Copyright 2021 <Lisa Zhu>

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Reference of SPI display related code: Melissa LeBlanc-Williams for Adafruit Industries
--------------------------------------------------------------------------

Use the ili9341 Display, a button, five vibration motors, a led strip and a speaker to 
create a music player with selectable songs, with led color change and vibrations to
enhance the experience.

Requirements:
  - Display all selectable songs on the screen
  - Increment the counter by one each time the button is pressed
  - Stop incrementing the counter 5 seconds after the button is released
  - Play the song corresponding to the counter
  - Sync vibrations and LEDs with the music
Uses:
  - digitalio, board, busio, PIL, adafruit_rgb_display.ili9341 libraries are used to control the display
  - time library is used to time the program and exit when appropriate
  - Adafruit_BBIO.GPIO library is used to take input from the button
  - os library is used to play the music
  - multiprocessing library is used to sync vibration and led with the music
"""

import digitalio
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

import time

import Adafruit_BBIO.GPIO as GPIO
import os
from multiprocessing import Process

import led_display as led
import vibration as vibration

# First define some constants to allow easy resizing of shapes.
BORDER = 20
FONTSIZE = 18
class SongNames():
    vib1       = None
    vib2       = None
    vib3       = None
    vib4       = None
    button     = None
    display    = None
    
    def __init__(self, reset_time=5.0, button="P1_26", spi = busio.SPI(board.SCLK_1, board.MOSI_1, board.MISO_1)):
        """ intialize variables and set up display """
        self.vib1 = vibration.Vibration("P2_1")
        self.vib2 = vibration.Vibration("P2_3")
        self.vib3 = vibration.Vibration("P1_33")
        self.vib4 = vibration.Vibration("P1_36")

        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.P2_31)
        dc_pin = digitalio.DigitalInOut(board.P2_33)
        reset_pin = digitalio.DigitalInOut(board.P2_35)
        
        # Config for display baudrate (default max is 24mhz):
        BAUDRATE = 24000000

        self.button    =button
        self.display   =ili9341.ILI9341(
                        spi,
                        rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
                        cs=cs_pin,
                        dc=dc_pin,
                        rst=reset_pin,
                        baudrate=BAUDRATE,
                    )
        self._setup()

   
    def _setup(self):
       
        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        if self.display.rotation % 180 == 90:
            height = self.display.width  # we swap height/width to rotate it to landscape!
            width = self.display.height
        else:
            width = self.display.width  # we swap height/width to rotate it to landscape!
            height = self.display.height
        
        image = Image.new("RGB", (width, height))
        
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        
        # Draw a black box as the background
        draw.rectangle((0, 0, width, height), fill=0)
        self.display.image(image)
        
        # Draw a smaller inner purple rectangle
        draw.rectangle(
            (BORDER, BORDER, width - BORDER - 1, height - BORDER - 1), fill=(170, 0, 136)
        )
        # Initialize Button
        GPIO.setup(self.button, GPIO.IN)
        
        # Load a TTF Font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
        padding = BORDER+1
        x= BORDER+2
        # Display song names
        song1 = "Stay with Me -- Press Once"
        song2 = "Glassy Sky    -- Press Twice"
        song3 = "Verona          -- Press 3 Times"
        song4 = "Aimer           -- Press 4 Times"
        y=padding+15
        draw.text(
            (x, y),
            song1,
            font=font,
            fill=(255, 255, 0),
        )
        y+=font.getsize(song1)[1]+15
        draw.text(
            (x, y),
            song2,
            font=font,
            fill=(255, 255, 0),
        )
        y+=font.getsize(song2)[1]+15
        draw.text(
            (x, y),
            song3,
            font=font,
            fill=(255, 255, 0),
        )
        y+=font.getsize(song3)[1]+15
        draw.text(
            (x, y),
            song4,
            font=font,
            fill=(255, 255, 0),
        )

        # Display image.
        self.display.image(image)
        
    def run(self):
        """Execute the main program."""
        press_count         = 0      # Number of times button was pressed
        button_press_done   = False
        timeout             = False
        
        while(not button_press_done):
            
            while(GPIO.input(self.button) == 1):
                if press_count != 0:
                    if (time.time() - initial_time) > 5: #stop counting if the button remains unpressed for 5 seconds
                        button_press_done = True
                        timeout = True
                        break
                time.sleep(0.1)
            
            if press_count == 0:
                initial_time = time.time()

            if not timeout:            
                press_count += 1
                print(press_count)
                
            # Wait for button release
            while(GPIO.input(self.button) == 0):
                if (button_press_done):
                    break
                time.sleep(0.1)
            
        #Each button press count corresponds to a different set of music, vibration and led effects
        if (press_count ==1):
            process1=Process(target=os.system, args=("mplayer ../speaker/music/stay_with_me.mp3",))
            process2=Process(target=led.led_strip, args=("/var/lib/cloud9/ENGI301/Project_1/speaker/music/stay_with_me.wav",))
        if (press_count ==2):
            process1=Process(target=os.system, args=("mplayer ../speaker/music/glassy_sky.mp3",))
            process2=Process(target=led.led_strip, args=("/var/lib/cloud9/ENGI301/Project_1/speaker/music/glassy_sky.wav",))
        if (press_count ==3):
            process1=Process(target=os.system, args=("mplayer ../speaker/music/verona.mp3",))
            process2=Process(target=led.led_strip, args=("/var/lib/cloud9/ENGI301/Project_1/speaker/music/verona.wav",))
        if (press_count ==4):
            process1=Process(target=os.system, args=("mplayer ../speaker/music/aimer.mp3",))
            process2=Process(target=led.led_strip, args=("/var/lib/cloud9/ENGI301/Project_1/speaker/music/aimer.wav",))
            
        processes = [process1, process2]
        
        for process in processes:
            process.start() #start vibration, music and led effects
        
        process1.join()
        process2.join()
        
    def cleanup(self):
        self.vib1.end()
        self.vib2.end()
        self.vib3.end()
        self.vib4.end()

if __name__ == '__main__':
    print("Program Start")
    
    # Create instantiation of song name display
    song_name=SongNames()
    try:
        # Run the song name display
        song_name.run()
    except KeyboardInterrupt:
        # Clean up hardware when exiting
        song_name.setup()

    song_name.cleanup()

    print("Program Complete")    
    