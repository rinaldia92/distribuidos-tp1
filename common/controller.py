from multiprocessing import Process
import logging

class Controller:
    def __init__(self):
        self._process = Process(target=self._method)
        self._run = True

    def _method(self):
        pass

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run

    def get_pid(self):
        return self._process.pid