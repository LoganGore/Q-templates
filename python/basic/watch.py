#!/usr/bin/env python3

'''
Implements a watch mode for docker-compose

'''

import subprocess
import os
import signal
import argparse
from inotify_simple import INotify, flags

start_dir = "."

parser = argparse.ArgumentParser(description='Watch mode for docker-compose.')
parser.add_argument('--kill', dest='should_kill', action='store_true')
args = parser.parse_args()

inotify = INotify()
watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF

inotify.add_watch(start_dir, watch_flags)

#recursively setup the watches
for root, dirs, files in os.walk(start_dir):
	for dir in dirs:
		print("Watching: ", root + os.sep + dir)
		inotify.add_watch(root + os.sep + dir, watch_flags)

def watch_loop():

	print("Rebuilding and bringing docker-compose up...\n");		
	process = subprocess.Popen(['docker-compose', 'up', '--build'])

	#wait for an event based on our watch flags
	#the loop will end when something happens
	for event in inotify.read():
	    for flag in flags.from_mask(event.mask):
	        action = str(flag).split('.')[1]
	        print(f'\n{action}: {event.name}\n')

	if (args.should_kill):
		#this will ungracefully terminate - which may well be fine, and is faster!
		print("Terminating docker-compose process...\n");		
		process.kill()
	else:
		#shut down gracefully
		print("Sending CTRL^C to docker-compose process...\n");		
		process.send_signal(signal.SIGINT)
		process.wait()
	
	#start again
	watch_loop()

#start things off
watch_loop()