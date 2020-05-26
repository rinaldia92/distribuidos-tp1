from multiprocessing import Process
from common.controller import Controller
from common.client import Client
import logging

class DownloadController(Controller):
    def __init__(self, server_downloads, host, port):
        self._process = Process(target=self._method, args=(server_downloads, host, port))
        self._run = True

    def _method(self, server_downloads, host, port):
        while self._run:
            try:
                middle = server_downloads.accept_new_connection()
                message = middle.receive_message()
                message_to_client = "Download request received"
                logging.info(message_to_client)
                try:
                    client_downloads = Client(host, port)
                    client_downloads.send_message(message)
                    client_downloads.close()
                except ConnectionRefusedError:
                    message_to_client = "Download request fail"
                middle.respond_message(message_to_client)
            except:
                self._run = False
    