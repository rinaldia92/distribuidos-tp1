import os
import time
import logging
import json
from client import Client
import threading

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
        config_params["host"] = config_data.get("SERVER_IP", None) or int(os.environ["SERVER_IP"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
    return config_params



def download(number, url, config):
    request = {}
    clientDownloader = Client(config["host"], config["download_port"])
    request["url"] = url
    request["branch"] = "master"
    message = json.dumps(request)
    clientDownloader.send_message(message)
    res = clientDownloader.receive_message()
    logging.info("Download Thread {}. Response: {}".format(number, res))
    clientDownloader.close()

def query(number, regex, regex_path, config):
    request = {}
    clientRequest = Client(config["host"], config["query_port"])
    request["regex"] = regex
    request["regex_repos"] = regex_path
    message = json.dumps(request)
    clientRequest.send_message(message)
    res = clientRequest.receive_message()
    logging.info("Query Thread {}. Response: {}".format(number, res))
    clientRequest.close()

def main():
    initialize_log()
    config = parse_config_params('config.json')
    threads = []

    for i in range(2):
        r = threading.Thread(target=download, args=(i, "https://github.com/rinaldia92/TDA2.git",config))
        threads.append(r)
        r.start() 
    for i in range(5):
        r = threading.Thread(target=query, args=(i, "hello", "hello", config))
        threads.append(r)
        r.start()
    for i in range(2):
        r = threading.Thread(target=download, args=(i, "https://github.com/githubtraining/hellogitworld.git",config))
        threads.append(r)
        r.start() 
    for i in range(5, 15):
        r = threading.Thread(target=query, args=(i, "hello", "hello",config))
        threads.append(r)
        r.start()

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

main()