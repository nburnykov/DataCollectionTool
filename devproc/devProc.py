import os
from queue import Queue
from threading import Thread, Lock
from typing import Tuple, Sequence, Optional, Callable, List

from cli.decisionTreeWalkCLI import DecisionTreeWalkCLI
from confproc.fileProc import yaml_load
from constants import PROJECTPATH
from devproc.deviceConnection import DeviceConnection
import logging

logger = logging.getLogger('main')


class ThreadResult:
    def __init__(self) -> None:
        self.func_result = False
        self.func_data: Optional[Callable] = None
        self.is_exception_in_thread = False
        self.exception_description = ''
        self.is_stop_queue = False


class CCThreadWorker(Thread):
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


class DevThreadWorker(Thread):
    def __init__(self, thread_queue: Queue(), creds: List[Tuple[str, str]], scanname: str, treedict: dict,
                 result_list: list, lock: Lock) -> None:

        Thread.__init__(self)
        self.creds = creds
        self.scanname = scanname
        self.treedict = treedict
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.lock = lock

    def run(self):
        while True:

            res_dict = {'IP': '',
                        'port': '',
                        'credentials': [],  # type: List[str]
                        'is login successful': False,
                        'is device recognized': False,
                        'is data collected': False,
                        'filepath': [],  # type: List[str]
                        'queryscript': ''
                        }

            dev, pos_num, resultobj = self.thread_queue.get()

            res_dict['IP'] = dev[0]
            ccresult = check_credentials(dev, self.creds)

            if ccresult is None:
                logger.debug('IP {}, login failed'.format(res_dict['IP']))
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue
            logger.debug('IP {}, login successful'.format(res_dict['IP']))
            res_dict['is login successful'] = True

            devdata, tr = ccresult
            res_dict['credentials'] = [tr.func_data.login, tr.func_data.password]
            res_dict['port'] = tr.func_data.connectiontype

            dcw = DecisionTreeWalkCLI(tr.func_data, self.treedict)
            dcw.getlog()

            if dcw.istreeconfigerror():
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue

            logger.debug('IP {}, device recognized'.format(res_dict['IP']))
            res_dict['is device recognized'] = True

            plist: List[str] = dcw.getpathlist()

            dpath = '\\'.join([directory for directory, script in plist])

            dp = self.scanname + '\\' + dpath

            plist.reverse()
            qname = plist[0][1]

            self.lock.acquire()

            query_scheme = yaml_load(PROJECTPATH + "/_DeviceQueryScripts/"
                                     + qname)
            self.lock.release()

            if not query_scheme:
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue

            logger.debug('IP {}, data collected'.format(res_dict['IP']))
            res_dict['is data collected'] = True

            res_dict['filepath'] = _device_query(tr.func_data, query_scheme, dp, self.lock)
            res_dict['queryscript'] = qname

            self.result_list[pos_num] = res_dict
            self.thread_queue.task_done()


def _cc_task_threader(input_arg_list: list, f: Callable, thread_num=100) \
        -> Sequence[Optional[Tuple[Tuple, ThreadResult, str]]]:
    thread_queue = Queue()
    llock = Lock()
    result_list = [None] * len(input_arg_list)
    thread_queue.stop_threads = False

    for num in range(thread_num):
        worker = CCThreadWorker(thread_queue, f, result_list, llock)
        worker.daemon = True
        worker.start()

    for pos_num, arg in enumerate(input_arg_list):
        res = ThreadResult()
        thread_queue.put((arg, pos_num, res))

    thread_queue.join()
    return result_list


def dev_task_threader(input_arg_list: Sequence[Tuple[str, int, bool, int, bool]], creds: List[Tuple[str, str]],
                      scanname: str, treedict: dict, thread_num=100) \
        -> Sequence[Optional[Tuple[Tuple, ThreadResult, str]]]:
    thread_queue = Queue()
    lock = Lock()
    result_list = [None] * len(input_arg_list)

    for num in range(thread_num):
        worker = DevThreadWorker(thread_queue, creds, scanname, treedict, result_list, lock)
        worker.daemon = True
        worker.start()

    for pos_num, dev in enumerate(input_arg_list):
        res = ThreadResult()
        thread_queue.put((dev, pos_num, res))

    thread_queue.join()
    return result_list


def _device_query(connection: DeviceConnection, query_scheme: dict, folder: str, lock: Lock()) -> List[str]:
    flist = []
    pfolder = PROJECTPATH + '\\_DATA\\'
    for item in query_scheme:
        ffolder = folder + '\\' + connection.ip
        result = ''
        if 'command' in item:
            result = connection.runcommand(item['command'])

        if 'file' in item:
            fp = ffolder + '\\' + item['file']
            lock.acquire()
            try:
                if not os.path.isdir(pfolder + ffolder):
                    os.makedirs(pfolder + ffolder)
                with open(pfolder + fp, 'w') as data_file:
                    data_file.write(result)
            except IOError:
                logger.error(f'Can\'t create file {(pfolder + fp)} to write data')
            finally:
                lock.release()
                flist.append(fp)
    return flist


def _devconnection_wrapper(ip: str, port: int, creds: Tuple[str, str], result: ThreadResult()) -> None:
    if port == 22:
        ctype = 'SSH'
    else:
        ctype = 'telnet'

    dc = DeviceConnection(ip, ctype=ctype)
    login, password = creds
    result.func_result = dc.connect(login=login, password=password)

    # TODO if not connected try to reconnect in 1, 3, 7 secs
    if result.func_result:
        result.func_data = dc
        result.is_stop_queue = True
        # else:
        #     dc.disconnect()


def _get_valid_connection(rlist: Sequence[Tuple[Tuple, ThreadResult, str]]) \
        -> Optional[Tuple[Tuple, ThreadResult]]:
    for r in rlist:
        args, tr, tname = r
        if tr.func_result:
            return args, tr
    return


def check_credentials(dev: Tuple[str, int, bool, int, bool], creds: List[Tuple[str, str]]) \
        -> Optional[Tuple[Tuple, ThreadResult]]:
    ip, port, is_ssh_port_open, port2, is_telnet_port_open = dev

    ssh_authenticated = False
    valid_connection = None

    logger.debug(f'IP {ip}, SSH is open: {is_ssh_port_open}, Telnet is open: {is_telnet_port_open}')
    if is_ssh_port_open:
        arglist = [(ip, port, cred) for cred in creds]
        resultlist = _cc_task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

        if valid_connection is not None:
            ssh_authenticated = True

    if not ssh_authenticated and is_telnet_port_open:
        arglist = [(ip, port2, cred) for cred in creds]
        resultlist = _cc_task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

    return valid_connection


def ident_device(ccresult: Optional[Tuple[Tuple, ThreadResult]], treedict: dict) \
        -> Optional[Sequence[Tuple[str, str]]]:
    if ccresult is None:
        return None

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict)

    return dcw.getpathlist()


def process_device_wrap(dev: Tuple[str, int, bool, int, bool], creds: List[Tuple[str, str]], treedict: dict,
                        result: ThreadResult()) -> None:
    ccresult = check_credentials(dev, creds)

    if ccresult is None:
        result.func_result = False
        return

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict)

    plist = dcw.getpathlist()
    dpath = '/'.join([directory for directory, script in plist])

    if not os.path.isdir(dpath):
        os.makedirs(dpath)

    result.func_result = True
    result.func_data = dcw
