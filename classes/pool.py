from queue import Queue, Empty
import threading
from threading import Thread
import json
import time

class Worker(Thread):
    _TIMEOUT = 2
    def __init__(self, tasks, th_num):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon, self.th_num = True, th_num
        self.done = threading.Event()
        self.start()

    def run(self):       
        while not self.done.is_set():
            try:
                func, args, kwargs = self.tasks.get(block=True, timeout=self._TIMEOUT)
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(e)
                finally:
                    self.tasks.task_done()
            except Empty as e:
                pass
        return

    def signal_exit(self):
        self.done.set()


class ThreadPool:
    stopping = False
    def __init__(self, num_threads, tasks=[]):
        self.tasks = Queue(num_threads)
        self.workers = []
        self.done = False
        self._init_workers(num_threads)
        for task in tasks:
            self.tasks.put(task)

    def _init_workers(self, num_threads):
        for i in range(num_threads):
            self.workers.append(Worker(self.tasks, i))

    def add_task(self, func, *args, **kwargs):
        if not self.stopping:
            self.tasks.put((func, args, kwargs))

    def _close_all_threads(self):
        for workr in self.workers:
            workr.signal_exit()
        self.workers = []

    def wait_completion(self):
        self.stopping = True
        self.tasks.join()

    def __del__(self):
        self._close_all_threads()