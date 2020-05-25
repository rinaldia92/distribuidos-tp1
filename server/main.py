#!/usr/bin/env python3

import os
import logging
import json
import threading
import time
from multiprocessing import Queue
from common.server import Server
from common.process import Process
from common.controllers import monitor_threads_controller
from common.download_controller import DownloadController
from common.grep_results_controller import GrepResultsController
from common.query_controller import QueryController

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
		config_params["grep_results_port"] = config_data.get("SERVER_GREP_RESULTS_PORT", None) or int(os.environ["SERVER_GREP_RESULTS_PORT"])
		config_params["client_download_port"] = config_data.get("CLIENT_DOWNLOAD_PORT", None) or int(os.environ["CLIENT_DOWNLOAD_PORT"])
		config_params["client_query_port"] = config_data.get("CLIENT_QUERY_PORT", None) or int(os.environ["CLIENT_QUERY_PORT"])
		config_params["listen_backlog"] = config_data.get("SERVER_LISTEN_BACKLOG", None) or int(os.environ["SERVER_LISTEN_BACKLOG"])
		config_params["host"] = config_data.get("SERVER_IP", None) or int(os.environ["SERVER_IP"])
	except KeyError as e:
		raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
	except ValueError as e:
		raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
	return config_params

def main():
	initialize_log()
	config_params = parse_config_params("config.json")
	server_downloads = Server(config_params["download_port"], config_params["listen_backlog"])
	
	server_query = Server(config_params["query_port"], config_params["listen_backlog"])
	server_responses = Server(config_params["grep_results_port"], config_params["listen_backlog"])

	queues = [Queue() for _ in range(config_params["listen_backlog"])]

	processes = []
	processes.append(DownloadController(server_downloads, config_params["host"], config_params["client_download_port"]))
	for i in range(config_params["listen_backlog"]):
		processes.append(QueryController(server_query, config_params["host"], config_params["client_query_port"], queues[i], i))
	processes.append(GrepResultsController(server_responses, queues))

	for process in processes:
		process.start()
	
	while True:
		time.sleep(1)
		killed = monitor_threads_controller(processes)
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

if __name__== "__main__":
	main()
