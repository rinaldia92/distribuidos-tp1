#!/usr/bin/env python3

import os
import logging
import json
import threading
import time
from queue import Queue
from common.server import Server
from common.lock import Lock
from common.thread import Thread
from common.controllers import query_controller, grep_files_controller, download_controller, update_repositories_controller, monitor, garbage_collector, monitor_threads_controller

REPOSITORIES_FOLDER = "./repositories/"
REPOSITORIES_FILE = "./repositories/repositories_list"

def parse_config_params(config_file_path):
	""" Parse env variables to find program config params

	Function that search and parse program configuration parameters in the
	program environment variables. If at least one of the config parameters
	is not found a KeyError exception is thrown. If a parameter could not
	be parsed, a ValueError is thrown. If parsing succeeded, the function
	returns a map with the env variables
	"""

	with open(config_file_path) as config_file:
		config_data = json.load(config_file)

	config_params = {}
	try:
		config_params["download_port"] = config_data.get("SERVER_DOWNLOAD_PORT", None) or int(os.environ["SERVER_DOWNLOAD_PORT"])
		config_params["query_port"] = config_data.get("SERVER_QUERY_PORT", None) or int(os.environ["SERVER_QUERY_PORT"])
		config_params["grep_results_port"] = config_data.get("CLIENT_GREP_RESULTS_PORT", None) or int(os.environ["CLIENT_GREP_RESULTS_PORT"])
		config_params["listen_backlog"] = config_data.get("SERVER_LISTEN_BACKLOG", None) or int(os.environ["SERVER_LISTEN_BACKLOG"])
		config_params["host"] = config_data.get("SERVER_IP", None) or int(os.environ["SERVER_IP"])
		config_params["monitor_time"] = config_data.get("MONITOR_TIME", None) or int(os.environ["MONITOR_TIME"])
		config_params["g_c_time"] = config_data.get("GARBAGE_COLLECTOR_TIME", None) or int(os.environ["GARBAGE_COLLECTOR_TIME"])
	except KeyError as e:
		raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
	except ValueError as e:
		raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
	return config_params

def main():
	initialize_log()
	config_params = parse_config_params("config.json")
	new_repos_queue = Queue()
	repos_search_queue = Queue()

	lock = Lock()

	# Initialize server and start server loop
	server_download = Server(config_params["download_port"], config_params["listen_backlog"])
	server_request = Server(config_params["query_port"], config_params["listen_backlog"])

	threads = []

	threads.append(Thread(query_controller, (server_request, repos_search_queue, REPOSITORIES_FILE ,lock)))
	threads.append(Thread(grep_files_controller, (config_params["host"], config_params["grep_results_port"], repos_search_queue, REPOSITORIES_FOLDER)))
	threads.append(Thread(download_controller, (server_download, new_repos_queue)))
	threads.append(Thread(update_repositories_controller, (REPOSITORIES_FILE, new_repos_queue, lock)))
	threads.append(Thread(monitor, (new_repos_queue, repos_search_queue, config_params["monitor_time"])))
	threads.append(Thread(garbage_collector, (REPOSITORIES_FOLDER, REPOSITORIES_FILE, config_params["g_c_time"], lock)))

	for thread in threads:
		thread.start()
	
	while True:
		time.sleep(1)
		killed = monitor_threads_controller(threads)
		if killed:
			break

	os._exit(0)


def initialize_log():
	"""
	Python custom logging initialization

	Current timestamp is added to be able to identify in docker
	compose logs the date when the log has arrived
	"""
	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO,
		datefmt='%Y-%m-%d %H:%M:%S',
	)


# if __name__== "__main__":
# 	main()
main()