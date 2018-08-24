"""
 Title: ThingSpeak_Driver
 Description: Thing speak stuff
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import urllib
from pprint import pprint
import httplib
import requests

import ConfigParser

config_file_path = "/home/pi/connected_gato/connected_gato.conf"

class thingspeak_driver:
	def __init__(self):
		print ""
		print "Starting ThingSpeak driver"

		print "  Reading config. file: " + config_file_path
		try:
			config = ConfigParser.RawConfigParser()   
			config.read(config_file_path)
			self.key = config.get('thingspeak', 'key')
			print "    Key: " + str(self.key)
			
		except Exception as err:
			print "  ERROR reading " + config_file_path
			print err

	def thingspeakUpdate(self, params={}):
		print "Sending data to Thing Speak:"

		params['key'] = self.key

		pprint(params)
		#print "  Field:" + field_name
		#print "  Value:" + str(value)

		params_url = urllib.urlencode(params) 
		headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
		connection = httplib.HTTPConnection("api.thingspeak.com:80")

		try:
			connection.request("POST", "/update", params_url, headers)
			response = connection.getresponse()
			print response.status, response.reason
			data = response.read()
			connection.close()
		except:
			print "  ERROR: connection failed"