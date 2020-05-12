import os
import time
import logging
import json
from common.client import Client
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



    DOWNLOAD = '1'
REQUEST = '2'

def main():
    config = parse_config_params('config.json')
    print(config)
    time.sleep(0.5)
    while True:
        request = {}
        print('Ingrese opcion 1 para descargar un repositorio')
        print('Ingrese opcion 2 para buscar archivos')
        option = input("Seleccione opcion: ")
        if option == DOWNLOAD:
            clientDownloader = Client(config["host"], config["download_port"])
            print('Opcion 1 seleccionada')
            request["url"] = input('Ingrese url de repositorio: ')
            request["branch"] = input('Ingrese branch: ')
            message = json.dumps(request)
            clientDownloader.send_message(message)
            res = clientDownloader.receive_message()
            print(res)
            clientDownloader.close()
            continue
        if option == REQUEST:
            print('Opcion 2 seleccionada')
            clientRequest = Client(config["host"], config["query_port"])
            request["regex"] = input('Ingrese regex a buscar: ')
            request["regex_repos"] = input('Ingrese regex de repositorios a buscar: ')
            message = json.dumps(request)
            clientRequest.send_message(message)
            res = clientRequest.receive_message()
            print(res)
            clientRequest.close()
            continue
        print('Otra opcion seleccionada')
        break


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