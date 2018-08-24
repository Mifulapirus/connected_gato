"""
 Title: socket driver
 Description: socket stuff
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import socket
import sys
import threading
import ConfigParser
import time


config_file_path = "/home/pi/connected_gato/connected_gato.conf"

class p2p_driver:
	def __init__(self):
		print ""
		print "Starting p2p driver"

		print "  Reading config. file: " + config_file_path
		try:
			config = ConfigParser.RawConfigParser()   
			config.read(config_file_path)
			self.own_port = config.getint('socket', 'own_port')
			self.own_ip = config.get('socket', 'own_ip')
			self.paired_port = config.getint('socket', 'paired_port')
			self.paired_ip = config.get('socket', 'paired_ip')
			self.received_compression = False
			
			print "    Own IP: " + self.own_ip
			print "    Own Port: " + str(self.own_port)
			print "    Paired IP: " + self.paired_ip
			print "    Paired Port: " + str(self.paired_port)
			
		except Exception as err:
			print "ERROR reading " + config_file_path
			print err

		self.create_server()


	def create_server(self):
		# Create a TCP/IP socket
		self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				
		print "Starting Cat to Cat connection on " + str(self.own_ip) + " port " + str(self.own_port)
		self.server_sock.bind((self.own_ip, self.own_port))

		# Listen for incoming connections
		self.server_sock.listen(1)


		sock_listener_thread = threading.Thread(target=self.sock_listener)
		sock_listener_thread.daemon = True
		sock_listener_thread.start()

	def send_message(self, msg=""):
		sender_thread = threading.Thread(target=self.sender, args=(msg,))
		sender_thread.daemon = True
		sender_thread.start()

	def sender(self, msg=""):
		client_connected = False
		print "Sending: " + msg
		while (client_connected == False):
			try:
				# Create a TCP/IP socket
				self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

				# Connect the socket to the port where the server is listening
				print "Connecting to Paired cat on " + str(self.paired_ip) + " port " + str(self.paired_port)

				self.client_sock.connect((self.paired_ip, self.paired_port))

				self.client_sock.sendall(msg)
				client_connected = True

			except Exception as err:
				time.sleep(5)
				print "ERROR client not ready "
				print err
			
			finally:
				self.client_sock.close()


	def sock_listener(self):
		while True:
			try:
				# Wait for a connection
				print "Waiting for new connection"
				connection, client_address = self.server_sock.accept()
				data = connection.recv(1000)
				print 'received "%s"' % data
				#self.send_message(data)
				self.received_compression = True

			except KeyboardInterrupt:
				print "Exiting socket listener reading loop."
				sys.exit()
			
if __name__ == '__main__':
	print "Socket connection test"
	p2p = p2p_driver()
	
	while True:
		p2p.send_message("Hola from " + str(p2p.own_ip))
		time.sleep(1)