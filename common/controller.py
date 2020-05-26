from multiprocessing import Process, Event
import logging

class Controller:
    def __init__(self):
        self._process = Process(target=self._method)
        self._run = Event()

    def _method(self):
        pass

    def start(self):
        self._run.set()
        self._process.start()

    def stop(self):
        self._run.clear()

    def alive(self):
        return self._process.is_alive()

    def get_pid(self):
        return self._process.pid