import logging
from multiprocessing import Process, Event
from common.controller import Controller
from common.dispatcher import Dispatcher

class DownloadController(Controller):
    def __init__(self, server_downloads, host, port):
        self._process = Process(target=self._method, args=(server_downloads, host, port))
        self._run = Event()

    def _method(self, server_downloads, host, port):
        dispatcher = Dispatcher(host, port)
        while self._run:
            try:
                middle = server_downloads.accept_new_connection()
                message = middle.receive_message()
                message_to_client = "Download request received"
                logging.info(message_to_client)
                try:
                    dispatcher.send_message(message)
                except ConnectionRefusedError:
                    message_to_client = "Download request fail"
                middle.respond_message(message_to_client)
            except:
                self._run.clear()
    