from multiprocessing import Process
from common.utils import save_to_file

class UpdateRepositoriesController:
    def __init__(self, file, new_repos_queue, lock):
        self._process = Process(target=self._method, args=(file, new_repos_queue, lock))
        self._run = True

    def _method(self, file, new_repos_queue, lock):
        while self._run:
            try:
                register = new_repos_queue.get()
                save_to_file(file, register, lock)
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
