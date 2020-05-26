from multiprocessing import Process, Event
from common.controller import Controller
import json

class GrepResultsController(Controller):
    def __init__(self, server_responses, response_queues, queues_dict):
        self._process = Process(target=self._method, args=(server_responses, response_queues, queues_dict))
        self._run = Event()

    def _method(self, server_responses, response_queues, queues_dict):
        while self._run:
            try:
                middle = server_responses.accept_new_connection()
                response = middle.receive_message()
                response = json.loads(response)
                queue_index = queues_dict.get(int(response["process_id"]))
                msg = response["message"]
                response_queues[queue_index].put(msg)
            except:
                self._run.clear()
