"""
 Title: BMP180
 Description: Pressure sensor driver
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import time
import datetime
import Adafruit_BMP.BMP085 as BMP085
import threading
import ConfigParser


config_file_path = "/home/pi/connected_gato/connected_gato.conf"

class BMP180:

	def __init__(self):
		print ""
		print "Starting Pressure driver"

		print "  Reading config. file: " + config_file_path
		try:
			config = ConfigParser.RawConfigParser()   
			config.read(config_file_path)
			self.pressure_threshold = config.getint('pressure', 'pressure_threshold')
			self.ambient_pressure_threshold = config.getint('pressure', 'ambient_pressure_threshold')
			self.ambient_pressure_threshold_max = config.getint('pressure', 'ambient_pressure_threshold_max')
			
			self.pressure_timer = config.getint('pressure', 'pressure_timer')
			
			print "    Threshold: " + str(self.pressure_threshold)
			print "    Calibration timer: " + str(self.pressure_timer)
			
		except Exception as err:
			print "ERROR reading " + config_file_path
			print err
		
		self.pressure_sensor = BMP085.BMP085()
		self.current_compressiong_state = "none"
		self.ambient_pressure = 0
		self.min_squish_pressure_threshold = 0
		self.max_squish_pressure_threshold = 0
		self.current_pressure = 0
		self.pressure_last_update = 0
		self.last_pressure_delta = 0
		
		check_compression_thread = threading.Thread(target=self.check_compression)
		check_compression_thread.daemon = True
		check_compression_thread.start()

	def check_compression(self):
		print "Checking compression thread started"
		#_decompressing = False
		#_compressing = False

		while 1:
			try:
				_current_pressure = self.get_pressure(5)
				_pressure_delta = self.ambient_pressure - _current_pressure
				
				#Self calibrate every 5 pressure_timer minutes
				if self.pressure_last_update < (time.time() - self.pressure_timer):
					print "Time to update the pressure"
					self.calibrate_ambient_pressure()
					self.pressure_last_update = time.time()
					print "  Next pressure update in " + str((self.pressure_timer)/60) + " minutes" + "\n"
					self.current_compressiong_state = "stable"

				#It just finished decompressing
				if (self.min_squish_pressure_threshold < _current_pressure < self.max_squish_pressure_threshold):	
					#_decompressing = False
					#self.last_pressure_delta = _pressure_delta	#Reset pressure delta
					#self.pressure_last_update = time.time()
					#	self.current_compressiong_state = "decompressed"
					#else:
					
					#Adjust ambient pressure when needed
					self.current_compressiong_state = "stable"
					
					if abs(_current_pressure) > abs(self.ambient_pressure) + abs(self.ambient_pressure_threshold) and abs(_current_pressure) < abs(self.ambient_pressure) + abs(self.ambient_pressure_threshold_max):
						print ("Ambient Pressure is been updated due to minimal change in environment")
						self.calibrate_ambient_pressure(_current_pressure)
						self.current_compressiong_state = "calibrated"
					
					

				#It started decompressing
				elif _current_pressure < self.max_squish_pressure_threshold:
					print "Decompressing: " + str(_current_pressure) + " < " + str(self.max_squish_pressure_threshold) + "  Delta: " + str(_pressure_delta)
					#self.pressure_last_update = time.time()
					self.current_compressiong_state = "decompressing"

				#It is compressing
				else:
					print "Compressing: " + str(_current_pressure) + " < " + str(self.max_squish_pressure_threshold) + "  Delta: " + str(_pressure_delta)
					#self.pressure_last_update = time.time()
					if abs(_pressure_delta) > abs(self.last_pressure_delta):
						self.last_pressure_delta = _pressure_delta
						print ("New Max Pressure Delta: " + str(self.last_pressure_delta))
					self.current_compressiong_state = "compressing"

				self.current_pressure = _current_pressure
				time.sleep(0.01)
			
			except KeyboardInterrupt:
				print "Exiting pressure reading loop."
				sys.exit()

	def get_pressure(self, samples = 10):
		cumulative_pressure = 0.0
		for i in range(0, samples):
			cumulative_pressure += self.pressure_sensor.read_pressure()
		
		current_pressure = cumulative_pressure/samples
		return current_pressure

	def get_temperature(self, samples = 1):
		cumulative_temp = 0.0
		for i in range(0, samples):
			_current_temp = self.pressure_sensor.read_temperature()
			cumulative_temp += _current_temp
			print " Temp " + str(i) + ": " + str(_current_temp) + " --> " + str(cumulative_temp)
			time.sleep(0.01)
		
		print " Cumulative = " + str(cumulative_temp)
		print " Samples =    " + str(samples)
		current_temp = cumulative_temp/samples
		return current_temp

	def calibrate_ambient_pressure(self, _calibrated_pressure = 0):
		_previous_ambient_pressure = self.ambient_pressure
		
		if _calibrated_pressure == 0:
			self.ambient_pressure = self.get_pressure(10)
		else:
			self.ambient_pressure = _calibrated_pressure
		self.min_squish_pressure_threshold = int(self.ambient_pressure - self.pressure_threshold)
		self.max_squish_pressure_threshold = int(self.ambient_pressure + self.pressure_threshold)
		
		print str(datetime.datetime.now()) + "  Reading initial pressure..."
		print str(datetime.datetime.now()) + "    Previous Ambient: " + str(_previous_ambient_pressure)
		print str(datetime.datetime.now()) + "    Current Ambient: " + str(self.ambient_pressure)
		print str(datetime.datetime.now()) + "    Squish Threshold:	" + str(self.pressure_threshold)
		print str(datetime.datetime.now()) + "    Ambient Threshold: " + str(self.ambient_pressure_threshold)
		print str(datetime.datetime.now()) + "    Ambient Threshold Max: " + str(self.ambient_pressure_threshold_max)
		print str(datetime.datetime.now()) + "    Min Threshold:    " + str(self.min_squish_pressure_threshold)
		print str(datetime.datetime.now()) + "    Max Threshold:    " + str(self.max_squish_pressure_threshold) + "\n"