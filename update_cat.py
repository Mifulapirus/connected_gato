"""
 Title: Connected Gato Updater
 Description: This will help you updating your cat
""" 
__author__ = "Angel Hernandez"
__contributors__ = "Angel Hernandez"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Angel Hernandez"
__email__ = "angel@tupperbot.com"
__status__ = "beta"

import git 

git_obj = git.cmd.Git("/home/pi/connected_gato/")
print git_obj.pull()