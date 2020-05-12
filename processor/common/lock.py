from multiprocessing import Condition

class Lock:
    def __init__(self):
        self.cond = Condition()
        self.readers = 0

    def read_acquire(self):
        self.cond.acquire()
        self.readers += 1
        self.cond.release()

    def read_release(self):
        with self.cond:
            self.readers -= 1
            if (self.readers == 0):
                self.cond.notify_all()

    def write_acquire(self):
        self.cond.acquire()
        if (self.readers > 0):
            self.cond.wait()

    def write_release(self):
        self.cond.release()
