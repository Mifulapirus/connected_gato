import sys
import telepot
from pprint import pprint
import time
from neopixel import *
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
#from flickrapi import FlickrAPI
from PIL import Image, ImageDraw
import urllib
from random import randrange
import requests
import json


#Google API
key = 'AIzaSyAHiMIKRaDbsgKmkY8rNjenuD8oFXXR1ME'
cx = '000645986483467971235:czxngi_yt_q'

#Flickr API setup
'''FLICKR_PUBLIC = '0da659bb6a06d1324db19da0524b3f06'
FLICKR_SECRET = '9b48d463e4a187ea'

flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
extras='url_m'
'''

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

#TelegramBot configuration: 
TOKEN = '347872193:AAFnHVo3Qw0GZgshMLW30vBUlRklpbq0giY'

#Command List
commands = {'commands': ['commands', 'command', '/command', '/commands'],
			'flickr': ['look like', 'make it', 'make the cat']}

color_list = {'white': [255, 255, 255] , 'red': [0, 255, 0], 'green': [255, 0, 0], 'blue': [0, 0, 255], 'off': [0, 0, 0,]}

def colorWipe(strip, color, wait_ms=20):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	if content_type == 'text':
		#convert to lowercase text
		message = msg['text'].lower()
		print "New message from:        " + msg['from']['first_name']
		print "Message content:         " + msg['text']

		process_command(msg)

def process_command(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	#Make it lowercase
	message = msg['text'].lower()

	print message

	if message in commands['commands']:
		print "List of commands"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='White', callback_data='white')],
			[InlineKeyboardButton(text='Red', callback_data='red')],
			[InlineKeyboardButton(text='Green', callback_data='green')],
			[InlineKeyboardButton(text='Blue', callback_data='blue')],
			[InlineKeyboardButton(text='Off', callback_data='off')],])
		bot.sendMessage(chat_id, 'Here is the list of commands', reply_markup=keyboard)

	elif any(word in message for word in commands['flickr']):
		google_color(chat_id, message)

	elif any(word in message for word in color_list):
		matching_color = [s for s in color_list if message in s]
		print matching_color 
		process_color(strip, message)
		print "Ok, connected Gato is now " + message

	else:
		bot.sendMessage(chat_id, 'Sorry, no entendi')


def process_color(strip, color_name):
	print color_list[color_name]

	red_channel = color_list[color_name][0]
	green_channel = color_list[color_name][1]
	blue_channel = color_list[color_name][2]

	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(red_channel, green_channel, blue_channel))
		strip.show()

def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	#print('Callback Query:', query_id, from_id, query_data)
	
	if query_data in colors:
		print query_data + " it's a color"
		process_color(strip, query_data)	

	bot.answerCallbackQuery(query_id, text="Connected Gato is now " + query_data)

def google_color(chat_id, message):
	for known_term in commands['flickr']:
			search_term = str(message.replace(known_term, ""))
		
	print search_term
	start_index = '1'

	search_url = "https://www.googleapis.com/customsearch/v1?q=" + search_term + "&start=" + start_index + "&key=" + key + "&cx=" + cx + "&searchType=image" + "&fileType=jpg"
	r = requests.get(search_url)
	response = r.content.decode('utf-8')
	result = json.loads(response)
	
	#pprint(search_url)
	#pprint(r)
	pprint(result['items'][0]['link'])

	selected_photo = result['items'][0]['link']

	print selected_photo
	urllib.urlretrieve(selected_photo, "img.jpg")

	get_image_colors('img.jpg', 'img2.png')
	img = open('img.jpg', 'rb')
	img2 = open('img2.png', 'rb')

	bot.sendPhoto(chat_id, img, caption="Here is what I found for" + search_term)
	bot.sendPhoto(chat_id, img2, caption="And this is all I can do with it")


def get_image_colors(infile, outfile, numcolors=2, swatchsize=20, resize=150):

	image = Image.open(infile)
	image = image.resize((resize, resize))
	result = image.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
	result.putalpha(0)
	colors = result.getcolors(resize*resize)
	pprint(colors)

	print "Obtained colors: " + str(len(colors))
	if len(colors)<numcolors:
		numcolors = len(colors)

	print "Resulting colors: "
	pprint(colors)
	LED_per_color = strip.numPixels()/numcolors

	print "Obtained colors"
	for i in range(0,numcolors):
		corrected_r = int(colors[i][1][0]*1)
		corrected_g = int(colors[i][1][1]*0.7)
		corrected_b = int(colors[i][1][2]*0.9)

		print "Block " + str(i)
		print "  R: " + str(corrected_r)
		print "  G: " + str(corrected_g)
		print "  B: " + str(corrected_b)

		for j in range((i*LED_per_color), (i*LED_per_color)+LED_per_color):
			strip.setPixelColor(j, Color(corrected_g, corrected_r, corrected_b))
			strip.show()
			
	# Save colors to file
	pal = Image.new('RGB', (swatchsize*numcolors, swatchsize))
	draw = ImageDraw.Draw(pal)

	posx = 0
	for count, col in colors:
		draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=col)
		posx = posx + swatchsize

	del draw
	pal.save(outfile, "PNG")


if __name__ == '__main__':
	# Intialize the library (must be called once before other functions).
	strip.begin()

	colorWipe(strip, Color(0, 0, 255))  # Blue wipe GRB
	colorWipe(strip, Color(0, 0, 0))  # Off wipe

	bot = telepot.Bot(TOKEN)
	#bot.message_loop(handle)
	bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})	

	#print "List of available colors"



	print ('Your Connected Gato is now listening ...')

	# Keep the program running.
	while 1:
		time.sleep(10)
