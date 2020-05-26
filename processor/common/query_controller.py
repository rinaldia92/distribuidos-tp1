import json
from multiprocessing import Process, Event
from common.utils import grep_file
from common.controller import Controller

class QueryController(Controller):
    def __init__(self, server_request, repos_search_queue, repo_file, lock):
        self._process = Process(target=self._method, args=(server_request, repos_search_queue, repo_file, lock))
        self._run = Event()

    def _method(self, server_request, repos_search_queue, repo_file, lock):
        while self._run:
            try:
                middle = server_request.accept_new_connection()
                message = middle.receive_message()
                params = json.loads(message)
                repos = grep_file(repo_file, params["regex_repos"], lock)
                data = {
                    "process_id": params["process_id"],
                    "regex": params["regex"],
                    "paths": repos
                }
                repos_search_queue.put(data)
            except:
                self._run.clear()
