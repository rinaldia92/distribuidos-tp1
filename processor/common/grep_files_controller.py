from multiprocessing import Process
from common.utils import grep_folders
from common.client import Client
import json

class GrepFilesController:
    def __init__(self, host, port, repos_search_queue, folder):
        self._process = Process(target=self._method, args=(host, port, repos_search_queue, folder))
        self._run = True

    def _method(self, host, port, repos_search_queue, folder):
        while self._run:
            try:
                params = repos_search_queue.get()
                results = grep_folders(params["regex"], params["paths"], folder)
                message = {
                    "thread_id": params["thread_id"],
                    "message": len(results)
                }
                try:
                    client_response = Client(host, port)
                    client_response.send_message(json.dumps(message))
                    client_response.close()
                    for res in results:
                        message["message"] = res
                        client_response = Client(host, port)
                        client_response.send_message(json.dumps(message))
                        client_response.close()	
                except ConnectionRefusedError:
                    logging.error("Connection refused. Can't return grep results")
                    raise
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
