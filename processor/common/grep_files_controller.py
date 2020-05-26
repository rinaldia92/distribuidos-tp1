import json
from multiprocessing import Process, Event
from common.utils import grep_folders
from common.dispatcher import Dispatcher
from common.controller import Controller

class GrepFilesController(Controller):
    def __init__(self, host, port, repos_search_queue, folder):
        self._process = Process(target=self._method, args=(host, port, repos_search_queue, folder))
        self._run = Event()

    def _method(self, host, port, repos_search_queue, folder):
        dispatcher = Dispatcher(host, port)
        while self._run:
            try:
                params = repos_search_queue.get()
                results = grep_folders(params["regex"], params["paths"], folder)
                message = {
                    "process_id": params["process_id"],
                    "message": len(results)
                }
                try:
                    dispatcher.send_message(json.dumps(message))
                    for res in results:
                        message["message"] = res
                        dispatcher.send_message(json.dumps(message))
                except ConnectionRefusedError:
                    logging.error("Connection refused. Can't return grep results")
                    raise
            except:
                self._run.clear()
