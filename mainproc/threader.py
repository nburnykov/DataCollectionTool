from threading import Thread, Lock
from queue import Queue


class ThreadResult:

    is_stop_queue = False

    def __init__(self) -> None:
        self.func_result = False
        self.func_data = None
        self.is_exception_in_thread = False
        self.exception_description = ''
        self.is_stop_queue = False


class ThreadWorker(Thread):
    def __init__(self, thread_queue: Queue(), threadfunc, result_list: list, lock: Lock, threadnum: int = 0) -> None:
        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.func = threadfunc
        self.threadnum = threadnum
        self.result = ThreadResult()
        self.lock = lock

    def run(self):
        while True:
            data, pos_num = self.thread_queue.get()

            self.lock.acquire()
            qstop = ThreadResult.is_stop_queue
            self.lock.release()

            try:
                if not qstop:
                    self.func(*data, self.result)
                    if self.result.is_stop_queue:

                        self.lock.acquire()
                        ThreadResult.is_stop_queue = True
                        self.lock.release()
                else:
                    self.result.is_stop_queue = True

            except Exception as err:
                self.result.is_exception_in_thread = True
                self.result.exception_description = str(err)
            finally:
                self.result_list[pos_num] = (data, self.result, self.name)
                self.thread_queue.task_done()


def task_threader(input_arg_list: list, f, thread_num=100):
    thread_queue = Queue()
    lock = Lock()
    result_list = [None] * len(input_arg_list)
    for num in range(thread_num):
        worker = ThreadWorker(thread_queue, f, result_list, lock, num)
        worker.daemon = True
        worker.start()

    for pos_num, arg in enumerate(input_arg_list):
        thread_queue.put((arg, pos_num))

    thread_queue.join()
    return result_list
