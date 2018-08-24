"""
 Title: LED Driver
 Description: LED related stuff
""" 

import time
import neopixel
import threading


# LED strip configuration:
LED_COUNT      = 30       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


neopixel_led = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
neopixel_led.begin()

neopixel_led.setPixelColor(20, neopixel.Color(255, 0, 0))
neopixel_led.show()
