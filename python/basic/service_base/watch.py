#!/usr/bin/env python3

'''
Using a volume, it watches for changes in the filesystem and restarts the server.

'''

import subprocess
import os
import signal
from inotify_simple import INotify, flags

#In docker-compose, we have set this as a volume for our source files
start_dirs = ["/service_source", "/service_base_source"]

inotify = INotify()
watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF

#Let's find all our watch folders!
for start_dir in start_dirs:

	#The root is hard coded
	#print("Watching: ", start_dir)
	inotify.add_watch(start_dir, watch_flags)

	#recursively setup the watches
	for root, dirs, files in os.walk(start_dir):
		for dir in dirs:
			full_path = root + os.sep + dir
			
			#Should probably have a proper ignore list
			if '.git' in full_path or dir == "cache" or dir == "__pycache__":
				continue

			#print("Watching: ", full_path)
			inotify.add_watch(full_path, watch_flags)

def watch_loop():

	print("\nBringing server.py up...");		
	process = subprocess.Popen(['python3.7', '-u', 'server.py'])

	#wait for an event based on our watch flags
	#the loop will end when something happens
	for event in inotify.read():
	    for flag in flags.from_mask(event.mask):
	        action = str(flag).split('.')[1]
	        print(f'{action}: {event.name}')

	        #for some reason this triggers more than once, so we'll break out manually
	        break

	#shut down gracefully
	print("Sending CTRL^C to server.py...");		
	process.send_signal(signal.SIGINT)
	process.wait()

	print("Wiping /app ...")
	delete_process = subprocess.Popen('rm /app/* -R', shell=True)
	delete_process.wait()
	
	print("Copying service_base files over...")
	copy_process = subprocess.Popen('cp /service_base_source/* /app/. --recursive', shell=True)
	copy_process.wait()

	print("Copying service files over...")
	copy_process = subprocess.Popen('cp /service_source/* /app/. --recursive', shell=True)
	copy_process.wait()

	print("Restarting watch loop...")
	
	#start again
	watch_loop()

#start things off
watch_loop()