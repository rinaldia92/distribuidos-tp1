import time
import logging
from multiprocessing import Process, Event
from common.utils import repos_garbage_collector
from common.controller import Controller

class GarbageCollectorController(Controller):
    def __init__(self, folder, file, cron_time, lock):
        self._process = Process(target=self._method, args=(folder, file, cron_time, lock))
        self._run = Event()

    def _method(self, folder, file, cron_time, lock):
        while self._run:
            try:
                time.sleep(cron_time)
                repos_garbage_collector(folder, file, lock)
            except:
                self._run.clear()
