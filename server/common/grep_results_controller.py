from multiprocessing import Process
from common.controller import Controller
import json

class GrepResultsController(Controller):
    def __init__(self, server_responses, response_queues):
        self._process = Process(target=self._method, args=(server_responses, response_queues))
        self._run = True

    def _method(self, server_responses, response_queues):
        while self._run:
            try:
                middle = server_responses.accept_new_connection()
                response = middle.receive_message()
                response = json.loads(response)
                queue_index = int(response["thread_id"])
                msg = response["message"]
                response_queues[queue_index].put(msg)
            except:
                self._run = False
