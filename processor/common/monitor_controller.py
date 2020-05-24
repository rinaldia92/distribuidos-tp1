from multiprocessing import Process
import logging
import time

class MonitorController:
    def __init__(self, new_repos_queue, repos_search_queue, cron_time):
        self._process = Process(target=self._method, args=(new_repos_queue, repos_search_queue, cron_time))
        self._run = True

    def _method(self, new_repos_queue, repos_search_queue, cron_time):
        while self._run:
            try:
                time.sleep(cron_time)
                logging.info("New repositories to be available: {}".format(new_repos_queue.qsize()))
                logging.info("Pending queries: {}".format(repos_search_queue.qsize()))
            except:
                self._run = False

    def start(self):
        self._process.start()

    def stop(self):
        self._run = False

    def alive(self):
        return self._run
