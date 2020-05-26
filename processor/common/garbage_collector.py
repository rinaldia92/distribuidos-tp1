from multiprocessing import Process
from common.utils import repos_garbage_collector
from common.controller import Controller
import logging
import time

class GarbageCollectorController(Controller):
    def __init__(self, folder, file, cron_time, lock):
        self._process = Process(target=self._method, args=(folder, file, cron_time, lock))
        self._run = True

    def _method(self, folder, file, cron_time, lock):
        while self._run:
            try:
                time.sleep(cron_time)
                repos_garbage_collector(folder, file, lock)
            except:
                self._run = False
