from multiprocessing import Process, Event
from common.utils import download
from common.controller import Controller
import json
import uuid

class DownloadController(Controller):
    def __init__(self, server_download, new_repos_queue):
        self._process = Process(target=self._method, args=(server_download, new_repos_queue))
        self._run = Event()

    def _method(self, server_download, new_repos_queue):
        while self._run:
            try:
                middle = server_download.accept_new_connection()
                message = middle.receive_message()
                params = json.loads(message)
                branch = params["branch"]
                name = params["url"].split('/')[-1][:-4]
                uid = str(uuid.uuid4())
                complete_name = "{}-{}-{}".format(uid, name, branch)
                try:
                    download(params["url"], params["branch"], "./repositories/{}".format(complete_name))
                except Exception:
                    logging.error("Unable to download repository {}".format(params["url"]))
                    return
                register = { "name": name, "branch": branch, "complete_name": complete_name }
                new_repos_queue.put(register)
            except:
                self._run.clear()
