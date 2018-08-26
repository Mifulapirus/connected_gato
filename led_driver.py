"""
 Title: Wifi_Driver
 Description: Wifi related stuff
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import time
import neopixel
import threading
import ConfigParser



# LED strip configuration:
REVERSE_TOP_BOT = False		#if connection order is Top - Bottom, then False (Maresi and Angel = False, Bob and Cory = True)
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_RED_CORRECTION 		= 0.95
LED_GREEN_CORRECTION 	= 1
LED_BLUE_CORRECTION 	= 0.85

config_file_path = "/home/pi/connected_gato/connected_gato.conf"


class led_driver:
	
	def __init__(self):
		print ""
		print "Starting LED Driver" + " v." + str(__version__)
		print "  Reading config. file: " + config_file_path
		try:
			config = ConfigParser.RawConfigParser()   
			config.read(config_file_path)
			_str_reverse_top_bot = config.get('led', 'reverse_top_bot') #Falsen if connection order is Top - Bottom, 
																		#Maresi and Angel = False, 
																		#Bob and Cory = True
			if _str_reverse_top_bot == "False": 
				self.reverse_top_bot = False
			else:
				self.reverse_top_bot = True
				
			self.top_led_count = int(config.get('led', 'top_led_count'))
			self.bot_led_count = int(config.get('led', 'bot_led_count'))
			self.led_count = self.top_led_count + self.bot_led_count

			self.heart_led = int(config.get('led', 'heart_led'))
			self.heartbeat_intensity = int(config.get('led', 'heartbeat_intensity'))
			
			print "    Top count: " + str(self.top_led_count)
			print "    Bot count: " + str(self.bot_led_count)
			print "    Total LED: " + str(self.led_count)
			print "    Heart LED: " + str(self.heart_led)
			print "    Heart Intensity: " + str(self.heartbeat_intensity)
			print "    Reversed:  " + str(self.reverse_top_bot)
			
			if self.reverse_top_bot:
				_temp_top_count = self.top_led_count
				self.top_led_count = self.bot_led_count
				self.bot_led_count = _temp_top_count
			
		except Exception as err:
			print "ERROR reading " + config_file_path
			print err
		
		
		# Create NeoPixel object with appropriate configuration.
		self.neopixel_led = neopixel.Adafruit_NeoPixel(self.led_count, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
		self.simplified_color_blocks = 2
		self.current_brightness = 1
		self.current_r = 0
		self.current_g = 0
		self.current_b = 0
		self.color_list = {'white': 	[255, 255, 255] , 
							'red': 		[255, 0, 0], 
							'green': 	[0, 255, 0], 
							'blue': 	[0, 0, 255], 
							'yellow': 	[255, 255, 0], 
							'fucsia': 	[219 ,29 ,136], 
							'purple': 	[ 148 ,39 ,201], 
							'off': 		[0, 0, 0,]}
		self.numPixels = self.neopixel_led.numPixels
		self.neopixel_led.begin()
		self.heartbeat_enabled = True
		heartbeat_thread = threading.Thread(target=self.heartbeat)
		heartbeat_thread.daemon = True
		heartbeat_thread.start()

	def heartbeat(self):
		while True:
			try:
				if self.heartbeat_enabled == True:
					self.set_single_led(self.heart_led, self.heartbeat_intensity, 0, 0, brightness=None, override=False, show=True)
					time.sleep(1)

					self.set_single_led(self.heart_led, 0, 0, 0, brightness=None, override=False, show=True)
					time.sleep(1)

				else:
					time.sleep(1)
			
			except KeyboardInterrupt:
				print "Exiting heart beat loop."
				sys.exit()

	def set_heartbeat(self, enabled=True):
		self.heartbeat_enabled = enabled
		#print('turning heartbeat to', self.heartbeat_enabled)
	
	def colorWipe(self, r, g, b, first_led = 0, last_led = None, wait_ms=20):
		if last_led == None:
			last_led = self.led_count
		#Wipe color across display a pixel at a time
		for i in range(first_led, last_led):
			self.set_single_led(i, r, g, b)
			self.neopixel_led.show()
			time.sleep(wait_ms/1000.0)

	def wipe_top(self, r, g, b, wait_ms = 20):
		if self.reverse_top_bot: 
			self.colorWipe(r, g, b, self.top_led_count, self.led_count, wait_ms)
		else:
			self.colorWipe(r, g, b, 0, self.top_led_count, wait_ms)

	def wipe_bottom(self, r, g, b, wait_ms = 20):
		if self.reverse_top_bot: 
			self.colorWipe(r, g, b, 0, self.top_led_count, wait_ms)
		else:
			self.colorWipe(r, g, b, self.top_led_count-1, self.led_count, wait_ms)

	def set_top(self, r, g, b, brightness = None, override=True):
		if brightness == None:
			brightness = self.current_brightness

		for i in range(0, self.top_led_count):
			self.set_single_led(i, r, g, b, brightness, override)
		self.neopixel_led.show()

	def set_bottom(self, r, g, b, brightness = None, override=True):
		if brightness == None:
			brightness = self.current_brightness
			
		for i in range(self.top_led_count-1, self.led_count):
			self.set_single_led(i, r, g, b, brightness, override)
		self.neopixel_led.show()

	def set_single_led(self, led_number, r, g, b, brightness = None, override=True, show=False):
		if brightness == None:
			brightness = self.current_brightness
				
		red_channel = int(r * LED_RED_CORRECTION * brightness)
		green_channel = int(g * LED_GREEN_CORRECTION * brightness)
		blue_channel = int(b * LED_BLUE_CORRECTION * brightness)

		if override == True:
			self.current_r = red_channel
			self.current_g = green_channel
			self.current_b = blue_channel
		
		self.neopixel_led.setPixelColor(led_number, self.Color(green_channel, red_channel, blue_channel))
		if (show == True):
			self.neopixel_led.show()


	def set_all_leds(self, r, g, b, brightness = None, override=True):
		if brightness == None:
			brightness = self.current_brightness
			
		for i in range(self.neopixel_led.numPixels()+1):
			self.set_single_led(i, r, g, b, brightness, override)
		self.neopixel_led.show()


	def Color(self, current_g, current_r, current_b):
		return neopixel.Color(int(current_g), int(current_r), int(current_b))

	def show(self):
		return self.neopixel_led.show()
	
	def __del__(self):
		print "Led_driver: Closing LED driver"
		set_heartbeat(False)
		
		

