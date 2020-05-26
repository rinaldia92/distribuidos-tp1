import json
import logging
from multiprocessing import Process, Event
from common.controller import Controller
from common.dispatcher import Dispatcher


TIMEOUT = 5
class QueryController(Controller):
    def __init__(self, server_query, host, port, response_queue):
        self._process = Process(target=self._method, args=(server_query, host, port, response_queue))
        self._run = Event()

    def _method(self, server_query, host, port, response_queue):
        dispatcher = Dispatcher(host, port)
        while self._run:
            try:
                middle = server_query.accept_new_connection()
                msg = middle.receive_message()
                logging.info("Query request received: " + msg)
                data = json.loads(msg)
                data["process_id"] = self._process.pid
                results = []
                message_to_client = ''
                try:
                    dispatcher.send_message(json.dumps(data))
                    amount = response_queue.get(True, TIMEOUT)
                    for _ in range(int(amount)):
                        file = response_queue.get() 
                        results.append(file)
                    message_to_client = str(results)
                except ConnectionRefusedError:
                    message_to_client = 'Query request fail'
                except:
                    message_to_client = 'Query request fail'
                middle.respond_message(message_to_client)
            except:
                self._run.clear()
