from multiprocessing import Process
from common.client import Client
import json

class QueryController:
    def __init__(self, server_query, host, port, response_queue, thread_id):
        self._process = Process(target=self._method, args=(server_query, host, port, response_queue, thread_id))
        self._run = True

    def _method(self, server_query, host, port, response_queue, thread_id):
        while self._run:
            try:
                conn, addr = server_query.accept_new_connection()
                msg = server_query.receive_message(conn)
                data = json.loads(msg)
                data["thread_id"] = thread_id
                results = []
                message_to_client = ''
                try:
                    client_query = Client(host, port)
                    client_query.send_message(json.dumps(data)+'\n')
                    client_query.close()
                    amount = response_queue.get(True, 5)
                    for _ in range(int(amount)):
                        file = response_queue.get() 
                        results.append(file)
                    message_to_client = str(results)+'\n'
                except ConnectionRefusedError:
                    message_to_client = 'Query request fail\n'
                except:
                    message_to_client = 'Query request fail\n'
                server_query.send_message(conn, message_to_client)
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