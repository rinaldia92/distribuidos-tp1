from multiprocessing import Process
from common.client import Client
import logging

class DownloadController:
    def __init__(self, server_downloads, host, port):
        self._process = Process(target=self._method, args=(server_downloads, host, port))
        self._run = True

    def _method(self, server_downloads, host, port):
        while self._run:
            try:
                conn, addr = server_downloads.accept_new_connection()
                message = server_downloads.receive_message(conn)
                message_to_client = "Download request received\n"
                logging.info(message_to_client)
                try:
                    client_downloads = Client(host, port)
                    client_downloads.send_message(message)
                    client_downloads.close()
                except ConnectionRefusedError:
                    message_to_client = "Download request fail\n"
                server_downloads.send_message(conn, message_to_client)
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run

    def get_pid(self):
        return self._process.pid