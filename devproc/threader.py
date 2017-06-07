from threading import Thread
from queue import Queue


class ThreadWorker(Thread):
    def __init__(self, thread_queue: Queue(), threadfunc, result_list: list, threadnum: int = 0) -> None:
        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.func = threadfunc
        self.threadnum = threadnum

    def run(self):
        while True:
            data, pos_num = self.thread_queue.get()
            try:
                result = self.func(*data)
            except Exception as err:
                result = False, str(err)
            finally:
                self.result_list[pos_num] = (data, result, self.threadnum)
                self.thread_queue.task_done()


def task_threader(input_arg_list, f, thread_num=100):
    thread_queue = Queue()
    result_list = [None] * len(input_arg_list)
    for num in range(thread_num):
        worker = ThreadWorker(thread_queue, f, result_list, num)
        worker.daemon = True
        worker.start()

    for pos_num, arg in enumerate(input_arg_list):
        thread_queue.put((arg, pos_num))

    thread_queue.join()
    return result_list
