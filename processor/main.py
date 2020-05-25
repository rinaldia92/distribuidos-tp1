#!/usr/bin/env python3

import os
import logging
import json
import threading
import time
from multiprocessing import Queue
from common.server import Server
from common.lock import Lock
from common.download_controller import DownloadController
from common.grep_files_controller import GrepFilesController
from common.query_controller import QueryController
from common.update_repositories_controller import UpdateRepositoriesController
from common.monitor_controller import MonitorController
from common.garbage_collector import GarbageCollectorController

REPOSITORIES_FOLDER = "./repositories/"
REPOSITORIES_FILE = "./repositories/repositories_list"

def monitor_processes_controller(processes):
	kill_processes = False
	for process in processes:
		if not process.alive():
			kill_processes = True
			break
	if kill_processes:
		for process in processes:
			process.stop()
	return kill_processes

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

	processes = []

	processes.append(QueryController(server_request, repos_search_queue, REPOSITORIES_FILE ,lock))
	processes.append(GrepFilesController(config_params["host"], config_params["grep_results_port"], repos_search_queue, REPOSITORIES_FOLDER))
	processes.append(DownloadController(server_download, new_repos_queue))
	processes.append(UpdateRepositoriesController(REPOSITORIES_FILE, new_repos_queue, lock))
	processes.append(MonitorController(new_repos_queue, repos_search_queue, config_params["monitor_time"]))
	processes.append(GarbageCollectorController(REPOSITORIES_FOLDER, REPOSITORIES_FILE, config_params["g_c_time"], lock))

	for process in processes:
		process.start()
	
	while True:
		time.sleep(1)
		killed = monitor_processes_controller(processes)
		if killed:
			break

	return


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