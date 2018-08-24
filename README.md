Connect your gato
=================
This project helps you connecting your gato to other gatos or just to the internet so you can control it yourself.
Miau. (Yeah, gatos do Miau!)

Libraries used:
---------------
- Telepot: http://telepot.readthedocs.io/en/latest/
- LED strip: https://github.com/jgarff/rpi_ws281x
- BMP Library (Pressure sensor)

Installation:
-------------
0. Update your raspberry
sudo apt-get update

1. Install various packages 
sudo apt-get install build-essential python-dev git scons swig python-smbus

2. Install ZeroTier
2.1 clone the git repo
git clone https://github.com/zerotier/ZeroTierOne.git
2.2 Build ZeroTier
cd ZeroTierOne
sudo make
2.3 Wait until the build is completed. It will take few minutes.
2.4 Copy the service file: $ sudo cp /YOUR_ZERO_TIER_FOLDER/debian/zerotier-one.service /lib/systemd/system/
2.5 Change permissions: $ sudo chmod 644 /lib/systemd/system/zerotier-one.service
2.6 Reload services: $ sudo systemctl daemon-reload
2.7 Start the service: $ sudo systemctl start zerotier-one.service

3. clone this repo on your home
git clone https://github.com/Mifulapirus/connected_gato.git

4. Install the LED strip library:
cd ~/connected_gato
git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons
cd python
sudo python setup.py install

5. Disable the sound card
5.1 Create the blacklist file: 
sudo nano /etc/modprobe.d/snd-blacklist.conf

5.2 Blacklist the sound card by typing the following and saving the file
blacklist snd_bcm2835

6. Install PIL library
sudo pip install pillow==2.9.0

7. Install Telepot (Telegram Bot) library
sudo pip install telepot

8. Install Requests
sudo pip install requests

9. Install the BMP180 library
git clone https://github.com/adafruit/Adafruit_Python_BMP.git
sudo python ~/connected_gato/Adafruit_Python_BMP/setup.py install

10. Install the WiFi library
sudo pip install wifi

11. Install Git Python
sudo pip install GitPython

12. Create the upstart job on Jessie: http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/
sudo nano /lib/systemd/system/gato-core.service

	[Unit]
	Description=Start and stop your connected gato
	After=multi-user.target

	[Service]
	Type=idle
	ExecStart=/usr/bin/python /home/pi/connected_gato/gato_core.py

	[Install]
	WantedBy=multi-user.target

sudo chmod 644 /lib/systemd/system/gato-core.service
sudo systemctl daemon-reload
sudo systemctl enable gato-core.service
sudo systemctl start gato-core.service