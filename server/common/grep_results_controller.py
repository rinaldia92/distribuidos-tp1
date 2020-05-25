from multiprocessing import Process
import json

class GrepResultsController:
    def __init__(self, server_responses, response_queues):
        self._process = Process(target=self._method, args=(server_responses, response_queues))
        self._run = True

    def _method(self, server_responses, response_queues):
        while self._run:
            try:
                conn_resp, addr_resp = server_responses.accept_new_connection()
                response = server_responses.receive_message(conn_resp)
                response = json.loads(response)
                queue_index = int(response["thread_id"])
                msg = response["message"]
                response_queues[queue_index].put(msg)
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