import RPi.GPIO as GPIO
import time
import sys
import led_driver

LIGHT_SENSOR_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)

buffer_length = 32
result = ['0']*(buffer_length+2)
end_header_high = 0
end_header_low = 0

strip = led_driver.led_driver()
IR_LED_ID = 1
strip.set_heartbeat(False)
strip.colorWipe(50, 50, 0)
strip.colorWipe(0, 0, 0)
if __name__ == '__main__':
	#try:
	strip.set_single_led(IR_LED_ID, 50, 50, 0, show=True)
	
	while True:
		time_high = [0]*buffer_length
		time_low = [0]*buffer_length
		new_pulse = not(GPIO.input(LIGHT_SENSOR_PIN))
		valid_input = False
		valid_timing = True
		valid_data = False
		
		if (new_pulse == True): 
			start_header_high = time.clock()
			while (not(GPIO.input(LIGHT_SENSOR_PIN))):
				time.sleep(0)
			
			end_header_high = time.clock() - start_header_high
			
			start_header_low = time.clock()
			while (GPIO.input(LIGHT_SENSOR_PIN)):
				time.sleep(0)
			end_header_low = time.clock() - start_header_low
			
			for i in range(0, buffer_length):
				start_high = time.clock()
				while (not(GPIO.input(LIGHT_SENSOR_PIN))):
					time.sleep(0)
				time_high[i] = time.clock() - start_high

				start_low = time.clock()
				while (GPIO.input(LIGHT_SENSOR_PIN)):
					time.sleep(0)
					if (time.clock() - start_low) > 0.002:
						valid_input = False
						break
				time_low[i] = time.clock() - start_low
			valid_input = True

		time.sleep(0.000005)
		
		
						
		if valid_input == True:
			
			print "\n New Data"
			
			if (0.0085 < end_header_high < 0.0095):
				print str("%.6f" % end_header_high) + " --> Valid start"
				result[0] = "S"
				
				if (0.0018 < end_header_low < 0.0025):
					result[1] = "R"
					print str("%.6f" % end_header_low) + " --> Valid remainder"
					
				elif (0.004 < end_header_low < 0.0045):
					print str("%.6f" % end_header_low) + " --> Valid header"
					result[1] = "_"
					
					for i in range(0,buffer_length):
						if (0.000500 < time_high[i] < 0.0009):
							if(0.0002 < time_low[i] < 0.0005):
								result[i+2] = "0"
								print str(i) + "	" + str("%.6f" % time_high[i]) + "	" +str("%.6f" % time_low[i]) + "	--> 0"
							elif(0.0011 < time_low[i] < 0.0016):
								result[i+2] = "1"
								print str(i) + "	" + str("%.6f" % time_high[i]) + "	" +str("%.6f" % time_low[i]) + "	--> 1"
							else:
								if (i == buffer_length-1):
									result[i+2] = "1"
									print str(i) + "	" + str("%.6f" % time_high[i]) + "	" +str("%.6f" % time_low[i]) + "	--> 1 - Long"
								else:
									print str(i) + "	" + str("%.6f" % time_high[i]) + "	" +str("%.6f" % time_low[i]) + " --> Invalid Low"
									valid_timing = False
						else:
							print str(i) + "	" + str("%.6f" % time_high[i]) + "	" +str("%.6f" % time_low[i]) + " --> Invalid High"
							valid_timing = False
						
				else:
					print str("%.6f" % end_header_low) + " --> Invalid header"
					strip.set_single_led(IR_LED_ID, 50, 0, 0, show=True)
					valid_timing = False
				
			else:
				print str("%.6f" % end_header_high) + " --> Invalid start"
				strip.set_single_led(IR_LED_ID, 50, 0, 0, show=True)
				valid_timing = False
				
			
			strip.set_single_led(IR_LED_ID, 0, 0, 0, show=True)
			if (valid_timing):
				print "Data input has valid times:"
				
				print "Header:  ", result[0:2]
								
				print "Address: ", bin(int(''.join(result[2:10]), 2)), " ~ ", bin(int(''.join(result[10:18]), 2))
				address = int(''.join(result[2:10]), 2)
				address_ = int(''.join(result[10:18]), 2)
				
				print "Command: ", bin(int(''.join(result[18:26]), 2)), " ~ ", bin(int(''.join(result[26:34]), 2))
				command = int(''.join(result[18:26]), 2)
				command_ = int(''.join(result[26:34]), 2)
				
				
				print "\nData Check: "
				if (255-address) == address_:
					print "Valid Address --> " + str(address)
					strip.set_single_led(IR_LED_ID, 0, 50, 0, show=True)
					valid_data = True
				else: 
					print "Address Error --> " + str(address) + " != " + str(address_)
					strip.set_single_led(IR_LED_ID, 50, 0, 0, show=True)
					valid_data = False
				
				if (255-command) == command_:
					print "Valid Command --> " + str(command)
					valid_data = True
					strip.set_single_led(IR_LED_ID, 0, 50, 0, show=True)

				else: 
					print "Command Error --> " + str(command) + " != " + str(command_)
					valid_data = False
					strip.set_single_led(IR_LED_ID, 50, 0, 0, show=True)
				
				if valid_data == True:
					if (command == 136):
						strip.colorWipe(200, 0, 0)
					elif (command == 72):
						strip.colorWipe(0, 200, 0)
					elif (command == 200):
						strip.colorWipe(0, 0, 200)
					elif (command == 8):
						strip.colorWipe(0, 0, 0)
					
					strip.set_single_led(IR_LED_ID, 0, 50, 0, show=True)
				else:
					strip.set_single_led(IR_LED_ID, 50, 0, 0, show=True)
				

		#else:
			#strip.set_single_led(1, 50, 0, 0)
		#	pass

		
	#time.sleep(0.1)

	#finally:
	#	print "\nCleanning up before exiting"
	#	GPIO.cleanup()
	#	print "Bye!"
	#	sys.exit()	
