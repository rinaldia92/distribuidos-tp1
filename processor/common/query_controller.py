from multiprocessing import Process
from common.utils import grep_file
import json

class QueryController:
    def __init__(self, server_request, repos_search_queue, repo_file, lock):
        self._process = Process(target=self._method, args=(server_request, repos_search_queue, repo_file, lock))
        self._run = True

    def _method(self, server_request, repos_search_queue, repo_file, lock):
        while self._run:
            try:
                conn, addr = server_request.accept_new_connection()
                message = server_request.receive_message(conn)
                params = json.loads(message)
                repos = grep_file(repo_file, params["regex_repos"], lock)
                data = {
                    "thread_id": params["thread_id"],
                    "regex": params["regex"],
                    "paths": repos
                }
                repos_search_queue.put(data)
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
