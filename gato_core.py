import sys
import telepot
from pprint import pprint
import time
from neopixel import *
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

#TelegramBot configuration: 
TOKEN = '347872193:AAFnHVo3Qw0GZgshMLW30vBUlRklpbq0giY'

def colorWipe(strip, color, wait_ms=20):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    pprint (msg)
    
    if content_type == 'text':
    	print "New message from:	" + msg['from']['first_name']
    	print "Message content:		" + msg['text']
        bot.sendMessage(chat_id, msg['text'])

def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	#pprint (msg)
	if content_type == 'text':
		#convert to lowercase text
		message = msg['text'].lower()
		print "New message from:        " + msg['from']['first_name']
		print "Message content:         " + message

	if ('commands' or '/commands') in message:
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='White', callback_data='white')],
			[InlineKeyboardButton(text='Red', callback_data='red')],
			[InlineKeyboardButton(text='Green', callback_data='green')],
			[InlineKeyboardButton(text='Blue', callback_data='blue')],
			[InlineKeyboardButton(text='Off', callback_data='off')],])
		bot.sendMessage(chat_id, 'Here is the list of commands', reply_markup=keyboard)
	else:
		bot.sendMessage(chat_id, 'Sorry, no entendi')

def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	print('Callback Query:', query_id, from_id, query_data)
	bot.answerCallbackQuery(query_id, text=query_data)

# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	colorWipe(strip, Color(0, 0, 255))  # Blue wipe GRB
	colorWipe(strip, Color(0, 0, 0))  # Off wipe

	bot = telepot.Bot(TOKEN)
	#bot.message_loop(handle)
	bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})	

	print ('Your Connected Gato is now listening ...')

	# Keep the program running.
	while 1:
		time.sleep(10)
