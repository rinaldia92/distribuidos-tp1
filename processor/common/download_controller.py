from multiprocessing import Process
from common.utils import download
import json
import uuid

class DownloadController:
    def __init__(self, server_download, new_repos_queue):
        self._process = Process(target=self._method, args=(server_download, new_repos_queue))
        self._run = True

    def _method(self, server_download, new_repos_queue):
        while self._run:
            try:
                conn, addr = server_download.accept_new_connection()
                message = server_download.receive_message(conn)
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
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
