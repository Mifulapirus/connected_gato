Connect your gato
=================
This project helps you connecting your gato to other gatos or just to the internet so you can control it yourself.
Miau. (Yeah, gatos do Miau!)

Libraries used:
---------------
- Telepot: http://telepot.readthedocs.io/en/latest/
- LED strip: https://github.com/jgarff/rpi_ws281x
- Flickr API: http://joequery.me/code/flickr-api-image-search-python/

Installation:
-------------
1. Make the work directory
mkdir connected_gato

2. clone this repo
git clone https://github.com/Mifulapirus/connected_gato.git

3. Install the LED strip library:
cd ~/connected_gato
sudo apt-get update
sudo apt-get install build-essential python-dev git scons swig
git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons
cd python
sudo python setup.py install

4. Disable the sound card
4.1 Create the blacklist file: 
sudo nano /etc/modprobe.d/snd-blacklist.conf

4.2 Blacklist the sound card by typing the following and saving the file
blacklist snd_bcm2835

5. Install PIL library

6. Install Telepot (Telegram Bot) library
pip install telepot


7. Install ZeroTier
curl -s https://install.zerotier.com/ | sudo bash

8. Create the upstart job on Jessie
sudo nano /lib/systemd/system/gato-core.service

	[Unit]
	Description=Start and stop your connected gato
	After=multi-user.target

	[Service]
	Type=idle
	ExecStart=/usr/bin/python /home/pi/connected_gato/gato_core.py

	[Install]
	WantedBy=multi-user.target

sudo chmod 644 /lib/systemd/system/gato_core.service
sudo systemctl daemon-reload
sudo systemctl enable gato-core.service