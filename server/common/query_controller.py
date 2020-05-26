from multiprocessing import Process
from common.client import Client
from common.controller import Controller
import json

class QueryController(Controller):
    def __init__(self, server_query, host, port, response_queue, thread_id):
        self._process = Process(target=self._method, args=(server_query, host, port, response_queue, thread_id))
        self._run = True

    def _method(self, server_query, host, port, response_queue, thread_id):
        while self._run:
            try:
                middle = server_query.accept_new_connection()
                msg = middle.receive_message()
                data = json.loads(msg)
                data["thread_id"] = thread_id
                results = []
                message_to_client = ''
                try:
                    client_query = Client(host, port)
                    client_query.send_message(json.dumps(data))
                    client_query.close()
                    amount = response_queue.get(True, 5)
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
                self._run = False
