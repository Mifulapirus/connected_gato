#!/usr/bin/env python

"""
 Title: Connected Gato Core
 Description: This is the heart of your Connected Gato
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

"""--------------------
TODO:
	Split it in different files
	Fix the style
	Send Angel who sent a message
	Make it a hotspot
	Add new Wifi on line 180 or so
"""

import sys
from pprint import pprint
import time
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw
import urllib
from random import randrange
import json
import os.path
import os
import dateutil.tz
import datetime
import httplib
import requests
import BMP180
import wifi_driver
import led_driver
import thingspeak_driver
import telegram_driver
import p2p_driver
import ConfigParser
import update_cat
import psutil

print str(datetime.datetime.now()) + "  Starting Connected Gato"

config_file_path = "/home/pi/connected_gato/connected_gato.conf"

#Time Variables
start_time = time.time()
elapsed_time = 0

SUCCESS = True
FAIL = False

thingspeak = thingspeak_driver.thingspeak_driver()
thingspeak_delay = 60
thingspeak_last_update = 0

# LED strip configuration:
strip = led_driver.led_driver()

#TelegramBot configuration:
telegram_bot = telegram_driver.telegram_driver()
TOKEN = telegram_bot.token
OWNER_CHAT_ID = telegram_bot.owner_id
user_interactions = 0	#Number of user interactions to be updated on ThingSpeak

#Pressure Sensor:
pressure_sensor = BMP180.BMP180()

#Wifi Stuff
wifi_driver = wifi_driver.wifi_driver()
wifi_setup_started = False

#Alarm stuff
global alarm_time
alarm_time = None

#Command List
commands = {'commands': ['commands', 'command', '/command', '/commands'],
			'google': ['look like', 'make it', 'make the cat'],
			'color blocks': ['color blocks', 'simplify colors', '/colorblocks'],
			'top': ['top', '/top', 'top ', '/top '],
			'bottom': ['bottom', '/bottom', 'bot', '/bot', 'bottom ', '/bottom ', 'bot ', '/bot '], 
			'brightness': ['brightness', '/brightness'],
			'temperature': ['temperature', '/temperature', 'temp', '/temp'], 
			'wifi': ['scan', 'connect', '/scan'], 
			'heartbeat': ['/heartbeat', 'heartbeat'], 
			'set alarm': ['/set_alarm', 'set alarm', 'set the alarm for', 'wake me up at', 'wake up at'],
			'check alarm': ['/check_alarm', 'check alarm', 'is there any alarm?', 'when are you waking up', 'when are you waking me up'],
			'time': ['/time', 'time', "what's the time", "What time is it?"],
			'update': ['/update'],
			'trump': ['trump', '/trump', 'trump quote']}

def on_chat_message(msg):
	global user_interactions
	content_type, chat_type, chat_id = telepot.glance(msg)
	user_interactions += 1

	if content_type == 'text':
		#convert to lowercase text
		message = msg['text'].lower()
		print "New message from:        " + msg['from']['first_name']
		print "Message content:         " + msg['text']
		process_command(msg)

def restart_gato_core():
	#Restarts the current program, with file objects and descriptors cleanup
    
	'''try:
		p = psutil.Process(os.getpid())
		for handler in p.get_open_files() + p.connections():
			os.close(handler.fd)
	except Exception, e:
		print e

	python = sys.executable
	os.execl(python, python, *sys.argv)'''
	
	#this seems to work, but I need to clean up all objects
	#os.execv('/home/pi/connected_gato/gato_core.py', [''])  
	print "Can't reboot by myself yet"
	
	
def process_command(msg):
	global wifi_setup_started
	content_type, chat_type, chat_id = telepot.glance(msg)
	print "Received Message: "
	pprint(msg)
	#Make it lowercase
	original_msg = msg['text']
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
		telegram_send(chat_id, 'Here is the list of commands', keyboard)

	elif message in commands['heartbeat']:
		print "Do you want to see my heart beating?"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text='Yes', callback_data='set heartbeat = 1')],
				[InlineKeyboardButton(text='No', callback_data='set heartbeat = 0')],])

		telegram_send(chat_id, 'Do you want to see my heart beating?', keyboard)

	elif message in commands['color blocks']:
		print "Set number of color blocks"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='1', callback_data='set simplified_color_blocks = 1')],
			[InlineKeyboardButton(text='2', callback_data='set simplified_color_blocks = 2')],
			[InlineKeyboardButton(text='3', callback_data='set simplified_color_blocks = 3')],
			[InlineKeyboardButton(text='4', callback_data='set simplified_color_blocks = 4')],])

		telegram_send(chat_id, 'How many blocks should I use?', keyboard)
	
	elif message in commands['brightness']:
		print "Set the brightness"
		keyboard = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text='Low', callback_data='set brightness = 0.05')],
			[InlineKeyboardButton(text='Medium', callback_data='set brightness = 0.3')],
			[InlineKeyboardButton(text='High', callback_data='set brightness = 1')],])

		telegram_send(chat_id, 'How bright shall I get?', keyboard)
	
	elif message in commands['update']:
		print "Start Updating"
		result = update_cat.update_firmware()
		if result == "Already up-to-date.":
			telegram_send(chat_id, "I'm already up to date... I like that you keep an eye on my health!")
			print "Restarting anyway"
			restart_gato_core()
		else:
			telegram_send(chat_id, "I have been updated.\n Here is the result:")
			telegram_send(chat_id, str(result))
			telegram_send(chat_id, "I'm gonna restart now... see you in a minute!")
			restart_gato_core()

	elif any(word in message for word in commands['set alarm']):
		print "Setting up a wake up time"
		global alarm_time

		for known_term in commands['set alarm']:
			message = str(message.replace(known_term, ""))
		message = message.replace(" ", "")

		#Check if the remaining of the message is in time format
		try:
			alarm_time = time.strptime(message, '%H:%M')			
			telegram_send(chat_id, 'It is ' + time.strftime("%H:%M", time.localtime()))
			telegram_send(chat_id, 'I will light up at ' + time.strftime("%H:%M", alarm_time))
		
		except ValueError:
			telegram_send(chat_id, 'Sorry, can you send me the time in HH:MM format, please?\n I got ' + message)
			alarm_time = None
			return False
			
	elif any(word in message for word in commands['check alarm']):
		print "Checking Alarm"
		global alarm_time
		if alarm_time == None:
			telegram_send(chat_id, "I don't have any alarm set right now. Send me any of the following commands to set up an alarm: \n" + str(commands['check alarm']))
		else:
			telegram_send(chat_id, 'I have an alarm set at ' + str(alarm_time))
		
		
	elif any(word in message for word in commands['time']):
		print "Timer Requested"
		telegram_send(chat_id, "It's " + time.strftime("%H:%M", time.localtime()))
		
	elif message in commands['wifi']:
		if message == 'scan':
			wifi_list = wifi_driver.scann_wifi()			
			i = 0
			_inline_keyboard=[]
			for i, ap in enumerate(wifi_list):
				print str(i) + ". " + str(ap)
				_inline_keyboard.append([InlineKeyboardButton(text = str(i) + " " + str(ap.ssid) + " " + str(ap.signal), callback_data=str('wifi_id = ' + str(i)))])
			
			keyboard = InlineKeyboardMarkup(inline_keyboard=_inline_keyboard)
			telegram_send(chat_id, "Here are the WiFis I can see: ", keyboard)

	elif message in commands['temperature']:
		telegram_send(chat_id, "It's " + str(pressure_sensor.get_temperature()) + " degrees")

	elif any(word in message for word in commands['top']):
		for known_term in commands['top']:
			message = str(message.replace(known_term, ""))

		message = message.replace(" ", "")

		print "Resulting Color: " + str(message)

		red_channel = int(strip.color_list[message][0])
		green_channel = int(strip.color_list[message][1])
		blue_channel = int(strip.color_list[message][2])
		strip.wipe_top(red_channel, green_channel, blue_channel)

		print "Top part is now " + message
		telegram_send(chat_id, 'Connected gato is half ' + message)

	elif any(word in message for word in commands['bottom']):
		for known_term in commands['bottom']:
			message = str(message.replace(known_term, ""))

		message = message.replace(" ", "")

		print "Resulting Color: " + str(message)

		red_channel = int(strip.color_list[message][0])
		green_channel = int(strip.color_list[message][1])
		blue_channel = int(strip.color_list[message][2])
		strip.wipe_bottom(red_channel, green_channel, blue_channel)

		print "Bottom part is now " + message
		telegram_send(chat_id, 'Connected gato is half ' + message)

	elif any(word in message for word in commands['google']):
		google_color(chat_id, message)
	
	elif any(word in message for word in commands['trump']):
		hair = [0, 0, 0]
		face = [255, 120, 2]
		jacket = [0, 0, 60]
		jacket_intense = [0, 0, 160]
		shirt = [70, 70, 70]
		tie = [70, 0, 0]
		no_color = [0,0,0]
		trump_leds = [hair, hair, no_color, 
                              no_color, face, face, face, face, face, face, no_color,
			      no_color, no_color, no_color, no_color, hair, 
			      jacket, jacket, jacket, jacket, jacket_intense, jacket_intense, 
			      shirt, 
			      tie, tie,
			      shirt, 
			      jacket_intense, jacket_intense, jacket, jacket, jacket]			      

		fade = 1
                for j in range(0, len(trump_leds)-1):
			strip.set_single_led(j, trump_leds[j][0]*fade, trump_leds[j][1]*fade, trump_leds[j][2]*fade)
                        strip.show()


		url = "https://api.whatdoestrumpthink.com/api/v1/quotes/random"
		resp = requests.get(url=url, params=dict())
		pprint(resp)
		data = json.loads(resp.text)
		pprint(data)
		telegram_send(chat_id, data["message"])

	elif any(word in message for word in strip.color_list):
		matching_color = [s for s in strip.color_list if message in s]
		print matching_color 
		process_color_name(strip, message)
		print "Ok, connected Gato is now " + message
		telegram_send(chat_id, 'Connected gato is now ' + message)

	else:
		if wifi_setup_started == True:
			print "Wifi Password: " + original_msg
			wifi_driver.connect_wifi(original_msg)
			wifi_setup_started = False


def on_callback_query(msg):
	global wifi_setup_started
	global user_interactions
	user_interactions += 1
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
	
	if query_data in strip.color_list:
		print query_data + " it's a color"
		process_color_name(strip, query_data)
		bot.answerCallbackQuery(query_id, text="Connected Gato is now " + query_data)

	if "set simplified_color_blocks = " in query_data:
		print "Change number of simplified blocks"
		strip.simplified_color_blocks = int(str(query_data.replace("set simplified_color_blocks = ", "")))
		print "  New number of blocks: " + str(strip.simplified_color_blocks)
		bot.answerCallbackQuery(query_id, text="I will use " + str(strip.simplified_color_blocks) + " LED blocks")

	elif "set brightness = " in query_data:
		print "Set a new brightness value"
		strip.current_brightness = float(str(query_data.replace("set brightness = ", "")))
		print "  New brightness level: " + str(strip.current_brightness)
		bot.answerCallbackQuery(query_id, text=("My brightness level is now " + str(strip.current_brightness*100) + "%"))

	elif "wifi_id = " in query_data:
		wifi_id = int(str(query_data.replace("wifi_id = ", "")))
		#print wifi_driver.Cell.all('wlan0')[wifi_id]
		_ssid = wifi_driver.cell[wifi_id].ssid
		wifi_driver.current_ssid = _ssid
		wifi_setup_started = True
		bot.answerCallbackQuery(query_id, text=("What's the password for " + str(_ssid) + "?"))
	
	elif "set heartbeat = " in query_data:
		print "Set heartbeat"
                #print(query_data.replace("set heartbeat = ", ""))
                strip.set_heartbeat(bool(int(query_data.replace("set heartbeat = ", ""))))
                print "  Heartbeat is now " + str(strip.heartbeat_enabled)
                bot.answerCallbackQuery(query_id, text=("Heartbeat is now " + str(strip.heartbeat_enabled)))

def process_color_name(strip, color_name):
	print "Turning " + str(strip.color_list[color_name])
	red_channel = int(strip.color_list[color_name][0])
	green_channel = int(strip.color_list[color_name][1])
	blue_channel = int(strip.color_list[color_name][2])

	strip.set_all_leds(red_channel, green_channel, blue_channel)

def google_color(chat_id, message):
	for known_term in commands['google']:
		search_term = str(message.replace(known_term, ""))
		
	print search_term
	start_index = '1'

	telegram_send(chat_id, 'Let me see what I can find for ' + search_term)

	search_url = "https://www.googleapis.com/customsearch/v1?q=" + search_term + "&start=" + start_index + "&key=" + google_key + "&cx=" + google_cx + "&searchType=image" + "&fileType=png"
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
				if get_image_colors('img.png', 'img2.png', strip.simplified_color_blocks):
					img = open('img.png', 'rb')
					img2 = open('img2.png', 'rb')
					bot.sendPhoto(chat_id, img, caption="Here is what I found for" + search_term)
					bot.sendPhoto(chat_id, img2, caption="And this is all I can do with it")

					img.close()
					img2.close()
					break
				
				else:
					telegram_send(chat_id, "I found an image, but it didn't work very well, let me try again (" + str(i+1) + " out of 5 tries)")

			except Exception as err:
				print "Image not downloaded %s" % err

	else:
		print "Something went wrong"
		print r.status_code
		#pprint(response)

def get_image_colors(infile, outfile, numcolors=strip.simplified_color_blocks, swatchsize=20, resize=150):
	try:
		image = Image.open(infile)
		image = image.resize((resize, resize))
		#result = image.convert('P', palette=Image.ADAPTIVE, colors=numcolors)
		
		result = image.quantize(colors=strip.simplified_color_blocks)
		result.putalpha(0)
		colors = result.getcolors(resize*resize)
		#colors = result.getcolors(16)
		print(colors)
		print "Reducing the image to " + str(numcolors) + " colors"
		print "Obtained colors in image: " + str(len(colors))
		if len(colors)<numcolors:
			numcolors = len(colors)

		#print "Resulting colors: "
		LED_per_color = strip.numPixels()/numcolors

		print "Simplified " + str(numcolors) + " color blocks:"
		for i in range(0,numcolors):
			r = int(colors[i][1][0])
			g = int(colors[i][1][1])
			b = int(colors[i][1][2])

			print "Block " + str(i) + ": " + str(r) + " ," + str(g) + " ," + str(b)

			for j in range((i*LED_per_color), (i*LED_per_color)+LED_per_color):
				strip.set_single_led(j, r, g, b)
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
		return SUCCESS

	except Exception as err:
		print "ERROR: Can't open " + str(infile)
		print err
		return FAIL

def telegram_send(chat_id, text, markup = ""):
	print "Sending message to " + str(chat_id)
	print text
	#pprint(markup)
	print "---------------------"
	try:
		bot.sendMessage(chat_id, text, reply_markup=markup)
		return SUCCESS

	except Exception as err:
		print "ERROR sending telegram message: "
		print err
		return FAIL

		
alarm_time = None

if __name__ == '__main__':
	print "-------------------------------"
	print "|     Connected Gato 0.2      |"
	print "-------------------------------"
	print "  Reading configuration file: " + config_file_path
	try:
		config = ConfigParser.RawConfigParser()   
		config.read(config_file_path)
		name = config.get('general', 'name')
		owner = config.get('general', 'owner')
		#Google API
		google_key = config.get('google', 'key')
		google_cx = config.get('google', 'cx')
		
		print "    Name: " + name
		print "    Owner: " + owner

	except Exception as err:
		print "ERROR reading " + config_file_path
		print err

	print str(datetime.datetime.now()) + "  Setting up the Timezone"
	
	print str(datetime.datetime.now()) + "  Starting LED strip..."
	print str(datetime.datetime.now()) + "    ... Done"

	print str(datetime.datetime.now()) + "  Starting Telegram Bot"
	bot = telepot.Bot(TOKEN)
	bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})	
	print str(datetime.datetime.now()) + "    ... Done"
	
	print str(datetime.datetime.now()) + "  Starting P2P driver to connect to the paired cat"
	#Paired cat
	p2p = p2p_driver.p2p_driver()
	p2p.send_message("Hello from " + owner)

	print str(datetime.datetime.now()) + "  Temperature: " + str(pressure_sensor.get_temperature())
	print str(datetime.datetime.now()) + "  Your Connected Gato is now listening"
	#Text Angel when Connected gato is ready
	telegram_send(OWNER_CHAT_ID, "I'm up! It's like " + str(pressure_sensor.get_temperature()) + " degrees in here!")
	strip.colorWipe(0, 0, 255)  # Blue wipe GRB
	strip.colorWipe(0, 0, 0)  # Off wipe

	# Keep the program running.
	user_interactions = 0
	squishing_interactions = 0


	_previous_compression_state = "stable"

	while 1:
		try:
			if p2p.received_compression:
				p2p.received_compression = False
				print "Paired cat has been squished"
				strip.colorWipe(0, 0, 255)  # blue wipe GRB
				strip.colorWipe(0, 0, 0)  # Off wipe
				telegram_send(OWNER_CHAT_ID, "Your paired cat has been squished")
				strip.colorWipe(strip.current_g, strip.current_r, strip.current_b)  # Blue wipe GRB

			if thingspeak_last_update < (time.time() - thingspeak_delay):
				print "Updating Thingspeak"
				thingspeak.thingspeakUpdate({"field1": squishing_interactions, "field2": pressure_sensor.current_pressure, "field3": pressure_sensor.get_temperature(), 'field4': user_interactions})
				user_interactions = 0
				squishing_interactions = 0
				thingspeak_last_update = time.time()

			_current_compression_state = pressure_sensor.current_compressiong_state

			if alarm_time != None:
				if time.strftime("%H:%M", alarm_time) == time.strftime("%H:%M", time.localtime()):
					print "ALARM!"
					strip.colorWipe(245, 208, 76)  #Yellow wipe GRB
					telegram_send(OWNER_CHAT_ID, 'WAKE UP!!!!!')
					alarm_time = None
				
			if _current_compression_state != _previous_compression_state:
				print "Pressure changed to " + _current_compression_state

				if pressure_sensor.current_compressiong_state == "compressing":
					#print "compressing"
					squishing_interactions += 1
					strip.set_all_leds(255, 0, 0, strip.current_brightness, False)	
					_previous_compression_state = _current_compression_state

				
				elif pressure_sensor.current_compressiong_state == "decompressing":
					#print "decompressing"
					strip.colorWipe(255, 255, 0)  # Yellow wipe GRB
					_previous_compression_state = _current_compression_state

					
				elif pressure_sensor.current_compressiong_state == "stable":
					#print "decompressed"
					strip.colorWipe(0, 255, 0)  # Green wipe GRB
					strip.colorWipe(0, 0, 0)  # Off wipe
					telegram_send(OWNER_CHAT_ID, "I've just been squished")
					p2p.send_message(owner + "'s cat has been compressed")
					strip.colorWipe(strip.current_g, strip.current_r, strip.current_b)  # Blue wipe GRB
					_previous_compression_state = _current_compression_state

				elif pressure_sensor.current_compressiong_state == "calibrated":
					print "Calibrated to " + str(pressure_sensor.ambient_pressure) + "Pa"
					pressure_sensor.ambient_pressure
					#telegram_send(OWNER_CHAT_ID, ("Calibrated to " + str(pressure_sensor.ambient_pressure) + "Pa"))
					_previous_compression_state = "stable" #This avoids triggering the "stable" state
					
				else:
					print "Unknown compression state"
			
			time.sleep(0.01)
			
		except KeyboardInterrupt:
			print "Connected Gato is sad and letting you go... :("
			sys.exit()
