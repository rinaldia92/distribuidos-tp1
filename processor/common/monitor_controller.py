from multiprocessing import Process, Event
from common.controller import Controller
import logging
import time

class MonitorController(Controller):
    def __init__(self, new_repos_queue, repos_search_queue, cron_time):
        self._process = Process(target=self._method, args=(new_repos_queue, repos_search_queue, cron_time))
        self._run = Event()

    def _method(self, new_repos_queue, repos_search_queue, cron_time):
        while self._run:
            try:
                time.sleep(cron_time)
                logging.info("New repositories to be available: {}".format(new_repos_queue.qsize()))
                logging.info("Pending queries: {}".format(repos_search_queue.qsize()))
            except:
                self._run.clear()
