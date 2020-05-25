import logging
import json
from common.client import Client

def monitor_threads_controller(threads):
	kill_threads = False
	for thread in threads:
		if not thread.alive():
			kill_threads = True
			break
	if kill_threads:
		for thread in threads:
			thread.stop()
	return kill_threads