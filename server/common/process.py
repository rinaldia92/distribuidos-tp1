from multiprocessing import Process
import logging

class Process:
    def __init__(self, method , arguments):
        self._process = Process(target=self._method, args=(method, arguments))
        self._run = True

    def _method(self, method, args):
        while self._run:
            try:
                method(*args)
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
