import logging
from threading import Thread
from queue import Queue


log_level = 'INFO'
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ThreadWorker(Thread):
    def __init__(self, thread_queue, result_list):
        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list

    def run(self):
        while True:
            data, pos_num = self.thread_queue.get()
            # Sample shit-code block for demo start{
            try:
                result = data + 10
                logger.info('Successfully got result: {}'.format(result))
            except Exception as err:
                logger.error('Error: {}'.format(err))
                result = False
            # Sample shit-code block for demo end }
            finally:
                self.result_list[pos_num] = result
                self.thread_queue.task_done()


def task_threader(input_arg_list, thread_num=100):
    thread_queue = Queue()
    result_list = list(None for elt in input_arg_list)
    for num in range(thread_num):
        worker = ThreadWorker(thread_queue, result_list)
        worker.daemon = True
        worker.start()
    pos_num = 0
    for arg in input_arg_list:
        logger.info('Queueing task {} in thrad_queue'.format(arg))
        thread_queue.put((arg, pos_num))
        pos_num += 1
    thread_queue.join()
    return result_list


if __name__ == '__main__':
    sample_input_1 = [1, 2, 3, 4, 'jabra']
    print(task_threader(sample_input_1))
