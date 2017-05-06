'''--------------------
TODO:
	Log the output of the script
	Split it in different files
	Fix the style
	Send Angel who sent a message
	Install Zerotier
'''

import sys
from pprint import pprint
import time
import Adafruit_BMP.BMP085 as BMP085
from neopixel import *
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw
import urllib
from random import randrange
import requests
import json
import os.path
import datetime

print str(datetime.datetime.now()) + "  Starting Connected Gato"

#Time Variables
start_time = time.time()
elapsed_time = 0


SUCCESS = True
FAIL = False

#Google API
key = 'AIzaSyAHiMIKRaDbsgKmkY8rNjenuD8oFXXR1ME'
cx = '000645986483467971235:czxngi_yt_q'

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_RED_CORRECTION 		= 0.95
LED_GREEN_CORRECTION 	= 1
LED_BLUE_CORRECTION 	= 0.85	

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
simplified_color_blocks = 1
current_brightness = 1
current_r = 0
current_g = 0
current_b = 0

#TelegramBot configuration: 
TOKEN = '347872193:AAFnHVo3Qw0GZgshMLW30vBUlRklpbq0giY'	#gatogatobot
#TOKEN = '377513945:AAHXHnH1jmDVtPvt1luhB0zSN1equJivY58'	#ConnectedYellowGatoBot
OWNER_CHAT_ID = 17186779

#Pressure Sensor:
sensor = BMP085.BMP085()
standard_pressure = 0
pressure_threshold = 50.0
pressure_timer = 5*60
pressure_last_update = 0

#Command List
commands = {'commands': ['commands', 'command', '/command', '/commands'],
			'google': ['look like', 'make it', 'make the cat'],
			'color blocks': ['color blocks', 'simplify colors', '/colorblocks'], 
			'brightness': ['brightness', '/brightness'],
			'temperature': ['temperature', '/temperature', 'temp', '/temp']}

color_list = {'white': [255, 255, 255] , 'red': [255, 0, 0], 'green': [0, 255, 0], 'blue': [0, 0, 255], 'off': [0, 0, 0,]}


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
	print "Received Message: "
	pprint(msg)
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

	elif message in commands['color blocks']:
		print "Set number of color blocks"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='1', callback_data='set simplified_color_blocks = 1')],
			[InlineKeyboardButton(text='2', callback_data='set simplified_color_blocks = 2')],
			[InlineKeyboardButton(text='3', callback_data='set simplified_color_blocks = 3')],
			[InlineKeyboardButton(text='4', callback_data='set simplified_color_blocks = 4')],])
		bot.sendMessage(chat_id, 'How many block should I use?', reply_markup=keyboard)
	
	elif message in commands['brightness']:
		print "Set the brightness"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='Low', callback_data='set brightness = 0.2')],
			[InlineKeyboardButton(text='Medium', callback_data='set brightness = 0.5')],
			[InlineKeyboardButton(text='High', callback_data='set brightness = 1')],])
		bot.sendMessage(chat_id, 'How bright shall I get?', reply_markup=keyboard)

	elif message in commands['temperature']:
		bot.sendMessage(chat_id, "It's " + str(get_temperature()) + " degrees")


	elif any(word in message for word in commands['google']):
		google_color(chat_id, message)

	elif any(word in message for word in color_list):
		matching_color = [s for s in color_list if message in s]
		print matching_color 
		process_color_name(strip, message)
		print "Ok, connected Gato is now " + message
		bot.sendMessage(chat_id, 'Connected gato is now ' + message)


	else:
		bot.sendMessage(chat_id, 'Sorry, no entendi')

def on_callback_query(msg):
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	#print('Callback Query:', query_id, from_id, query_data)
	
	if query_data in color_list:
		print query_data + " it's a color"
		process_color_name(strip, query_data)
		bot.answerCallbackQuery(query_id, text="Connected Gato is now " + query_data)

	if "set simplified_color_blocks = " in query_data:
		print "Change number of simplified blocks"
		global simplified_color_blocks 
		simplified_color_blocks = int(str(query_data.replace("set simplified_color_blocks = ", "")))
		print "  New number of blocks: " + str(simplified_color_blocks)
		bot.answerCallbackQuery(query_id, text="I will use " + str(simplified_color_blocks) + " LED blocks")

	elif "set brightness = " in query_data:
		print "Set a new brightness value"
		global current_brightness 
		current_brightness = float(str(query_data.replace("set brightness = ", "")))
		print "  New brightness level: " + str(current_brightness)
		bot.answerCallbackQuery(query_id, text="My brightness level is now " + str(current_brightness*100) + "%")

def process_color_name(strip, color_name):
	print "Turning " + str(color_list[color_name])
	red_channel = int(color_list[color_name][0])
	green_channel = int(color_list[color_name][1])
	blue_channel = int(color_list[color_name][2])

	set_all_leds(red_channel, green_channel, blue_channel)

def colorWipe(strip, color, wait_ms=20):
	#Wipe color across display a pixel at a time
	for i in range(strip.numPixels()+1):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def set_single_led(led_number, r, g, b, brightness=current_brightness, override=True):
	global current_brightness
	global current_r
	global current_g
	global current_b
	brightness = current_brightness

	#print "Current brightness: " + str(brightness)
	
	red_channel = int(r*LED_RED_CORRECTION*brightness)
	green_channel = int(g*LED_GREEN_CORRECTION*brightness)
	blue_channel = int(b*LED_BLUE_CORRECTION*brightness)

	#print "  R: " + str(red_channel)
	#print "  G: " + str(green_channel)
	#print "  B: " + str(blue_channel)
	if override == True:
		current_r = red_channel
		current_g = green_channel
		current_b = blue_channel

	strip.setPixelColor(led_number, Color(green_channel, red_channel, blue_channel))
	strip.show()
	
def set_all_leds(r, g, b, brightness=current_brightness, override=True):
	for i in range(strip.numPixels()+1):
		set_single_led(i, r, g, b, brightness, override)

def google_color(chat_id, message):
	for known_term in commands['google']:
			search_term = str(message.replace(known_term, ""))
		
	print search_term
	start_index = '1'

	bot.sendMessage(chat_id, 'Let me see what I can find for ' + search_term)

	search_url = "https://www.googleapis.com/customsearch/v1?q=" + search_term + "&start=" + start_index + "&key=" + key + "&cx=" + cx + "&searchType=image" + "&fileType=png"
	r = requests.get(search_url)
	response = r.content.decode('utf-8')
	result = json.loads(response)
	
	#pprint(search_url)	
	if r.status_code == 200:
		print "success!"
		for i in range(0, 5):
			selected_photo = result['items'][i]['link']

			print selected_photo
			try:
				urllib.urlretrieve(selected_photo, 'img.png')
				
				os.path.isfile('img.png')
				print "Image has been created"
				if get_image_colors('img.png', 'img2.png', simplified_color_blocks):
					img = open('img.png', 'rb')
					img2 = open('img2.png', 'rb')
					bot.sendPhoto(chat_id, img, caption="Here is what I found for" + search_term)
					bot.sendPhoto(chat_id, img2, caption="And this is all I can do with it")

					img.close()
					img2.close()
					break
				
				else:
					bot.sendMessage(chat_id, "I found an image, but it didn't work very well, let me try again (" + str(i+1) + " out of 5 tries)")

			except Exception as err:
				print "Image not downloaded %s" % err

	else:
		print "Something went wrong"
		print r.status_code
		#pprint(response)

def get_image_colors(infile, outfile, numcolors=simplified_color_blocks, swatchsize=20, resize=150):
	try:
		image = Image.open(infile)
		image = image.resize((resize, resize))
		#result = image.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
		
		result = image.quantize(colors=simplified_color_blocks)
		result.putalpha(0)
		colors = result.getcolors(resize*resize)
		#colors = result.getcolors(16)
		print(colors)
		print "Reducing the image to " + str(numcolors) + " colors"
		print "Obtained colors in image: " + str(len(colors))
		if len(colors)<numcolors:
			numcolors = len(colors)

		#print "Resulting colors: "
		#pprint(colors)
		LED_per_color = strip.numPixels()/numcolors

		print "Simplified " + str(numcolors) + " color blocks:"
		for i in range(0,numcolors):
			r = int(colors[i][1][0])
			g = int(colors[i][1][1])
			b = int(colors[i][1][2])

			print "Block " + str(i) + ": " + str(r) + " ," + str(g) + " ," + str(b)

			for j in range((i*LED_per_color), (i*LED_per_color)+LED_per_color):
				set_single_led(j, r, g, b)
				
		# Save colors to file
		pal = Image.new('RGB', (swatchsize*numcolors, swatchsize))
		draw = ImageDraw.Draw(pal)

		posx = 0
		for count, col in colors:
			draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=col)
			posx = posx + swatchsize

		del draw
		pal.save(outfile, "PNG")
		return SUCCESS

	except Exception as err:
		print "ERROR: Can't open " + str(infile)
		return FAIL

def get_pressure(samples = 10):
	cumulative_pressure = 0.0
	for i in range(0, samples):
		cumulative_pressure += sensor.read_pressure()
	
	current_pressure = cumulative_pressure/samples
	#print "Current Pressure: " + str(current_pressure)
	return current_pressure

def get_temperature(samples = 1):
	cumulative_temp = 0.0
	for i in range(0, samples):
		_current_temp = sensor.read_temperature()
		cumulative_temp += _current_temp
		print " Temp " + str(i) + ": " + str(_current_temp) + " --> " + str(cumulative_temp)
		time.sleep(0.01)
	
	print " Cumulative = " + str(cumulative_temp)
	print " Samples =    " + str(samples)
	current_temp = cumulative_temp/samples
	#print "Current Pressure: " + str(current_pressure)
	return current_temp

def get_ambient_pressure():
	global standard_pressure
	global _min_pressure_threshold
	global _max_pressure_threshold

	standard_pressure = get_pressure(10)
	_min_pressure_threshold = int(standard_pressure - pressure_threshold)
	_max_pressure_threshold = int(standard_pressure + pressure_threshold)
	
	print str(datetime.datetime.now()) + "  Reading initial pressure..."
	print str(datetime.datetime.now()) + "    Current Pressure: " + str(standard_pressure)
	print str(datetime.datetime.now()) + "    Threshold:        " + str(pressure_threshold)
	print str(datetime.datetime.now()) + "    Min Threshold:    " + str(_min_pressure_threshold)
	print str(datetime.datetime.now()) + "    Max Threshold:    " + str(_max_pressure_threshold)


if __name__ == '__main__':
	print "----------------------------"
	print "|     Connected Gato       |"
	print "----------------------------"

	print str(datetime.datetime.now()) + "  Starting LED strip..."
	strip.begin()
	print str(datetime.datetime.now()) + "    ... Done"

	print str(datetime.datetime.now()) + "  Starting Telegram Bot"
	bot = telepot.Bot(TOKEN)
	bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})	
	print str(datetime.datetime.now()) + "    ... Done"
	
	print str(datetime.datetime.now()) + "  Temperature: " + str(get_temperature())
	print str(datetime.datetime.now()) + "  Your Connected Gato is now listening"
	#Text Angel when Connected gato is ready
	bot.sendMessage(OWNER_CHAT_ID, "I'm up! It's like " + str(get_temperature()) + " degrees in here!")
	colorWipe(strip, Color(0, 0, 255))  # Blue wipe GRB
	colorWipe(strip, Color(0, 0, 0))  # Off wipe

	# Keep the program running.
	_min_pressure_delta = 0.0
	_pressure_delta = 0.0
	_100_division = 0.0
	_compressing = False
	_decompressing = False

	while 1:
		_current_pressure = get_pressure(5)
		_pressure_delta = standard_pressure - _current_pressure
		
		if pressure_last_update < (time.time() - pressure_timer):
			print "Time to update the pressure"
			get_ambient_pressure()
			pressure_last_update = time.time()
			print "  Next pressure update in " + str((pressure_timer)/60) + " minutes" 

		if (_min_pressure_threshold < _current_pressure < _max_pressure_threshold):
			if _decompressing == True:
				_min_pressure_delta = 0.0
				_decompressing = False

				colorWipe(strip, Color(255, 0, 0))  # Blue wipe GRB
				colorWipe(strip, Color(0, 0, 0))  # Off wipe
				bot.sendMessage(OWNER_CHAT_ID, "I've just been squished")
				colorWipe(strip, Color(current_g, current_r, current_b))  # Blue wipe GRB

		elif _current_pressure < _max_pressure_threshold:
			print "Decompressing: " + str(_pressure_delta)
			if _compressing == True:
				_compressing = False
				_decompressing = True
				colorWipe(strip, Color(255, 255, 0))  # Blue wipe GRB

		else:
			print "Compressing: " + str(_pressure_delta)
			_compressing = True
			set_all_leds(255, 0, 0, 1, False)	


		
