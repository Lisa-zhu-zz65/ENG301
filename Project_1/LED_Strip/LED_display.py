# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------
LED Music Visualizer & Vibrator
--------------------------------------------------------------------------
License:   
Copyright 2021 Lisa Zhu

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
--------------------------------------------------------------------------
Control LED strip and vibration motors with WAV file data
  
LED lights and vibrations according to tuple values extracted from wav file

--------------------------------------------------------------------------
Background Information: 
 
  * Setting up the LED strip:
  https://markayoder.github.io/PRUCookbook/01case/case.html#_neopixels_5050_rgb_leds_with_integrated_drivers_ledscape (Section 1.3. NeoPixels - 5050 RGB LEDs with Integrated Drivers (LEDScape))
  
  * Unpacking and analyzing wav file:
  https://stackoverflow.com/questions/2226853/interpreting-wav-data (Comment by SapphireSun on Feb 9 '10 at 6:18)
  
Copyright Information:
    Adopted from code by Juliana Wang:
    https://www.hackster.io/juliana-wang/pocketbeagle-led-music-visualizer-3e6c7c
"""

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# PART 1: READ/UNPACK WAV FILE DATA
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

import time
import wave
import struct

import opc
import vibration as vibration
from multiprocessing import Process
# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

ADDRESS = 'localhost:7890'

# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------
integer_data = []



# ------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------


def pcm_channels(wave_file):
    """Given a file-like object or file path representing a wave file,
    decompose it into its constituent PCM data streams.

    Input: A file like object or file path
    Output: A list of lists of integers representing the PCM coded data stream channels
        and the sample rate of the channels (mixed rate channels not supported)
    """
    global integer_data
    stream = wave.open(wave_file,"rb")

    num_channels = stream.getnchannels()
    sample_rate  = stream.getframerate()
    sample_width = stream.getsampwidth()
    num_frames   = stream.getnframes()
    
    raw_data = stream.readframes( num_frames ) # Returns byte data
    stream.close()

    total_samples = num_frames * num_channels
 

    if sample_width == 1: 
        fmt = "%iB" % total_samples # read unsigned chars
    elif sample_width == 2:
        fmt = "%ih" % total_samples # read signed 2 byte shorts
    else:
        raise ValueError("Only supports 8 and 16 bit audio formats.")

    integer_data = struct.unpack(fmt, raw_data)
    del raw_data # Keep memory tidy (who knows how big it might be)

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# PART 2: TRIGGER LED LIGHT STRIP WITH WAV DATA
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
    
def led_strip(wave_file):
    global integer_data
    
    pcm_channels(wave_file)
    
    vib1 = vibration.Vibration("P2_1")
    vib2 = vibration.Vibration("P2_3")
    vib3 = vibration.Vibration("P1_33")
    vib4 = vibration.Vibration("P1_36")

    client = opc.Client(ADDRESS)

    stop_time = time.time() + 60
    STR_LEN = 10
    
    offset      = 0
    data_length = len(integer_data)
    
    # Test if it can connect
    if client.can_connect():
        print ('connected to %s' % ADDRESS)
    else:
        # We could exit here, but instead let's just print a warning
        # and then keep trying to send pixels in case the server
        # appears later
        print ('WARNING: could not connect to %s' % ADDRESS)
        
    leds = [(0, 0, 0)] * STR_LEN
    
    while time.time() < stop_time:
        vib_freq = 0
        
        for i in range(STR_LEN):
            datavalue = abs(integer_data[(i+offset)])//16
            vib_freq += datavalue
            leds[i]  = (datavalue,datavalue,datavalue)

        offset = offset + STR_LEN   #Leaves remainder numebr of pixels to shift
        vib_freq = vib_freq // STR_LEN

        if vib_freq == 0: # frequency can't be zero
            vib_freq = 1
        
        if offset > data_length:
            break
        
        if not client.put_pixels(leds, channel=0):
            print('not connected')
        
        # Do vibration
        
        process_1 = Process(target=vib1.vibrate,args=(vib_freq,))
        process_2 = Process(target=vib2.vibrate,args=(vib_freq,))
        process_3 = Process(target=vib3.vibrate,args=(vib_freq,))
        process_4 = Process(target=vib4.vibrate,args=(vib_freq,))

        processes = [process_1, process_2, process_3, process_4]
        for process in processes:
            process.start() #start vibration
        
        process_1.join()
        process_2.join()
        process_3.join()
        process_4.join()
        
        time.sleep(0.001)
    
    vib1.end()
    vib2.end()
    vib3.end()
    vib4.end()