import sys
import telepot
from pprint import pprint
import time
from neopixel import *


# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

#TelegramBot configuration: 
TOKEN = '347872193:AAFnHVo3Qw0GZgshMLW30vBUlRklpbq0giY'

def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/500.0)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print msg
    
    if content_type == 'text':
    	print "New message from:	" + msg['chat_id']
    	print "Message content:		" + msg['text']
        bot.sendMessage(chat_id, msg['text'])



# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	colorWipe(strip, Color(0, 0, 255))  # Blue wipe GRB
	colorWipe(strip, Color(0, 0, 0))  # Off wipe

	bot = telepot.Bot(TOKEN)
	bot.message_loop(handle)
	print ('Your Connected Gato is now listening ...')

	# Keep the program running.
	while 1:
		time.sleep(10)