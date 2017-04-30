Connect your gato
=================
This project helps you connecting your gato to other gatos or just to the internet so you can control it yourself.
Miau. (Yeah, gatos do Miau!)

Libraries used:
---------------
- Python-telegram-bot: https://github.com/python-telegram-bot/python-telegram-bot
- LED strip: https://github.com/jgarff/rpi_ws281x

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
