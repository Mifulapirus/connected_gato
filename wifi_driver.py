"""
 Title: Wifi_Driver
 Description: Wifi related stuff
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
from wifi import Cell, Scheme
import urllib


class wifi_driver:
	def __init__(self, interface='wlan0'):
		self.cell = Cell.all(interface)

	def checkInternetConnection(self):
		try:
			urllib2.urlopen('http://8.8.8.8', timeout=1)
			return True
		except urllib2.URLError as err: 
			return False

	def connect_wifi(self, wifi_id, passkey):
		print "Adding new Wifi"
		current_cell = self.cell[wifi_id]
		current_ssid = self.cell[wifi_id].ssid
		print "Cell info: "
		print current_cell

		scheme = Scheme.for_cell('wlan0', self.current_ssid, self.cell, passkey)
		scheme.save()
		print "Scheme info"
		print scheme
		return scheme.activate()

	def scann_wifi(self, interface='wlan0'):
		return self.cell

	def checkInternetConnection():
		try:
			urllib2.urlopen('http://8.8.8.8', timeout=1)
			return True
		except urllib2.URLError as err: 
			return False