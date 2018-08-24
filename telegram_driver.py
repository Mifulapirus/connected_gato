"""
 Title: Telegram Driver
 Description: Telegram stuff
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import ConfigParser
#import telepot
#from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

config_file_path = "/home/pi/connected_gato/connected_gato.conf"

class telegram_driver:
	def __init__(self):
		print ""
		print "Starting Telegram Bot"
		#self.user_interactions = 0
		#print "  User interactions: " + str(self.user_interactions)
		#self.new_message = False
		#print "  New message flag: " + str(self.new_message)
		#self.message_received = ""
		#print "  Message Received: " + self.message_received

		print "  Reading config. file: " + config_file_path
		try:
			config = ConfigParser.RawConfigParser()   
			config.read(config_file_path)
			self.token = config.get('telegram', 'token')
			self.owner_id = config.getint('telegram', 'owner_id')
			
			print "    Token: " + self.token
			print "    Owner ID: " + str(self.owner_id)

			#self.bot = telepot.Bot(self.token)
			#self.bot.message_loop({'chat': self.on_chat_message, 'callback_query': self.on_callback_query})	

		except Exception as err:
			print "ERROR reading " + config_file_path
			print err

'''
	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)
		self.user_interactions += 1

		if content_type == 'text':
			#convert to lowercase text
			message = msg['text'].lower()
			print "New message from:        " + msg['from']['first_name']
			print "Message content:         " + msg['text']

			#set new message flag
			self.message_received = msg
			self.new_message = True

	def on_callback_query(self, msg):
		global wifi_setup_started
		self.user_interactions += 1
		query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
		print('Callback Query:', query_id, from_id, query_data)
		
		if query_data in strip.color_list:
			print query_data + " it's a color"
			process_color_name(strip, query_data)
			self.bot.answerCallbackQuery(query_id, text="Connected Gato is now " + query_data)

		if "set simplified_color_blocks = " in query_data:
			print "Change number of simplified blocks. TESTING VERSION"
			strip.simplified_color_blocks = int(str(query_data.replace("set simplified_color_blocks = ", "")))
			print "  New number of blocks: " + str(strip.simplified_color_blocks)
			#self.bot.answerCallbackQuery(query_id, text="I will use " + str(strip.simplified_color_blocks) + " LED blocks")
			self.bot.answerCallbackQuery(query_id, text="Ok")
		
		elif "set brightness = " in query_data:
			print "Set a new brightness value"
			strip.current_brightness = float(str(query_data.replace("set brightness = ", "")))
			print "  New brightness level: " + str(strip.current_brightness)
			self.bot.answerCallbackQuery(query_id, text=("My brightness level is now " + str(strip.current_brightness*100) + "%"))

		elif "wifi_id = " in query_data:
			wifi_id = int(str(query_data.replace("wifi_id = ", "")))
			#print wifi_driver.Cell.all('wlan0')[wifi_id]
			_ssid = wifi_driver.cell[wifi_id].ssid
			wifi_driver.current_ssid = _ssid
			wifi_setup_started = True
			telegram_send(from_id, "What's the password for " + str(_ssid) + "?")
		
		elif "set heartbeat = " in query_data:
			print "Set heartbeat"
                        strip.heartbeat_enabled = bool(str(query_data.replace("set heartbeat = ", "")))
                        print "  Heartbeat is now " + str(strip.heartbeat_enabled)
                        self.bot.answerCallbackQuery(query_id, text=("Heartbeat is now " + str(strip.heartbeat_enabled)))

'''
