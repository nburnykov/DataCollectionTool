from mainproc.deviceConnection import DeviceConnection
from cli.decisionTreeWalkCLI import DecisionTreeWalkCLI
from threading import Thread, Lock
from queue import Queue
from typing import Tuple, Sequence, Optional, Callable


class DevThreadResult:

    def __init__(self) -> None:
        self.func_result = False
        self.func_data = None  # type: Optional[Callable]
        self.is_exception_in_thread = False
        self.exception_description = ''
        self.is_stop_queue = False


class DevThreadWorker(Thread):
    def __init__(self, thread_queue: Queue(), thread_func: Callable, result_list: list, lock: Lock) -> None:
        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.func = thread_func
        self.lock = lock

    def run(self):
        while True:
            data, pos_num, resultobj = self.thread_queue.get()

            self.lock.acquire()
            qstop = self.thread_queue.stop_threads
            self.lock.release()

            try:
                if not qstop:
                    self.func(*data, resultobj)
                    if resultobj.is_stop_queue:

                        self.lock.acquire()
                        self.thread_queue.stop_threads = True
                        self.lock.release()
                else:
                    resultobj.is_stop_queue = True

            except Exception as err:
                resultobj.is_exception_in_thread = True
                resultobj.exception_description = str(err)
            finally:
                self.result_list[pos_num] = (data, resultobj, self.name)
                self.thread_queue.task_done()


def dev_task_threader(input_arg_list: list, f: Callable, thread_num=100) \
        -> Sequence[Optional[Tuple[Tuple, DevThreadResult, str]]]:
    thread_queue = Queue()
    lock = Lock()
    result_list = [None] * len(input_arg_list)
    thread_queue.stop_threads = False

    for num in range(thread_num):
        worker = DevThreadWorker(thread_queue, f, result_list, lock)
        worker.daemon = True
        worker.start()

    for pos_num, arg in enumerate(input_arg_list):
        res = DevThreadResult()
        thread_queue.put((arg, pos_num, res))

    thread_queue.join()
    return result_list


def _devconnection_wrapper(ip: str, port: int, creds: str, result: DevThreadResult()) -> None:

    if port == 22:
        ctype = 'SSH'
    else:
        ctype = 'telnet'

    dc = DeviceConnection(ip, ctype=ctype)
    login, password = creds.split('/')
    result.func_result = dc.connect(login=login, password=password)

    # TODO if not connected try to reconnect in 1, 3, 7 secs
    if result.func_result:
        result.func_data = dc
        result.is_stop_queue = True


def _get_valid_connection(rlist: Sequence[Tuple[Tuple, DevThreadResult, str]]) \
        -> Optional[Tuple[Tuple, DevThreadResult]]:

    for r in rlist:
        args, tr, tname = r
        if tr.func_result:
            return args, tr

    return


def check_credentials(dev: Tuple[str, int, bool, int, bool], creds: Sequence[str]) \
        -> Optional[Tuple[Tuple, DevThreadResult]]:

    ip, port, is_ssh_port_open, port2, is_telnet_port_open = dev

    ssh_authenticated = False

    valid_connection = None

    if is_ssh_port_open:
        arglist = [(ip, port, cred) for cred in creds]
        resultlist = dev_task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

        if valid_connection is not None:
            ssh_authenticated = True

    if not ssh_authenticated and is_telnet_port_open:
        arglist = [(ip, port2, cred) for cred in creds]
        resultlist = dev_task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

    return valid_connection


def ident_device(ccresult: Optional[Tuple[Tuple, DevThreadResult]], treedict: dict, querydict: dict) \
        -> Optional[Sequence[Tuple[str, str]]]:

    if ccresult is None:
        return None

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict, querydict)

    return dcw.getpathlist()


def process_device_wrap(dev: Tuple[str, int, bool, int, bool], creds: Sequence[str], treedict: dict, querydict: dict,
                        result: DevThreadResult()) -> None:

    ccresult = check_credentials(dev, creds)
    print(dev, ccresult)
    if ccresult is None:
        result.func_result = False
        return

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict, querydict)

    # plist = dcw.getpathlist()
    # dpath = '/'.join([directory for directory, script in plist])
    # print(dpath)

    result.func_result = True
    result.func_data = dcw


