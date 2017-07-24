from threading import Thread, Lock
from queue import Queue
from typing import Tuple, Optional, Sequence, Callable


class ThreadResult:

    def __init__(self) -> None:
        self.func_result = False
        self.func_data = None  # type: Optional[Callable]
        self.is_exception_in_thread = False
        self.exception_description = ''
        self.is_stop_queue = False


class ThreadWorker(Thread):
    def __init__(self, thread_queue: Queue(), thread_func: Callable, result_list: list, lock: Lock) -> None:
        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.func = thread_func
        self.lock = lock

    def run(self):
        while True:
            data, pos_num, resultobj = self.thread_queue.get()

            try:

                resultobj.func_result = self.func(*data)

            except Exception as err:
                resultobj.is_exception_in_thread = True
                resultobj.exception_description = str(err)
            finally:
                self.result_list[pos_num] = (data, resultobj, self.name)
                self.thread_queue.task_done()


def task_threader(input_arg_list: list, f: Callable, thread_num=100) \
        -> Sequence[Optional[Tuple[Tuple, ThreadResult, str]]]:
    thread_queue = Queue()
    lock = Lock()
    result_list = [None] * len(input_arg_list)
    for num in range(thread_num):
        worker = ThreadWorker(thread_queue, f, result_list, lock)
        worker.daemon = True
        worker.start()

    for pos_num, arg in enumerate(input_arg_list):
        res = ThreadResult()
        thread_queue.put((arg, pos_num, res))

    thread_queue.join()
    return result_list
