import os
from os.path import join, isdir
from queue import Queue
from threading import Thread, Lock
from typing import Tuple, Sequence, Optional, Callable, List

from cli.decision_tree_cli import DecisionTreeCLI
from utils.yaml_file_io import yaml_load
from devproc.device_connect import DeviceConnection
import logging

from constants import DIR_PROJECT, DIR_DATA, DIR_QUERY_SCRIPTS

logger = logging.getLogger('main')


class ThreadResult:
    def __init__(self) -> None:
        self.func_result = False
        self.func_data: Optional[Callable] = None
        self.is_exception_in_thread = False
        self.exception_description = ''
        self.is_stop_queue = False


class CCThreadWorker(Thread):
    def __init__(self, thread_queue: Queue, thread_func: Callable, result_list: list, lock: Lock) -> None:

        Thread.__init__(self)
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.func = thread_func
        self.lock = lock

    def run(self):
        while True:
            data, pos_num, result_obj = self.thread_queue.get()

            self.lock.acquire()
            qstop = self.thread_queue.stop_threads
            self.lock.release()

            try:
                if not qstop:
                    self.func(*data, result_obj)
                    if result_obj.is_stop_queue:
                        self.lock.acquire()
                        self.thread_queue.stop_threads = True
                        self.lock.release()
                else:
                    result_obj.is_stop_queue = True

            except Exception as err:
                result_obj.is_exception_in_thread = True
                result_obj.exception_description = str(err)
            finally:
                self.result_list[pos_num] = (data, result_obj, self.name)
                self.thread_queue.task_done()


class DevThreadWorker(Thread):
    def __init__(self, thread_queue: Queue, credentials: List[Tuple[str, str]], scan_name: str, tree: dict,
                 result_list: list, lock: Lock) -> None:

        Thread.__init__(self)
        self.credentials = credentials
        self.scan_name = scan_name
        self.tree = tree
        self.thread_queue = thread_queue
        self.result_list = result_list
        self.lock = lock

    def run(self):
        while True:

            res_dict = {'IP': '',
                        'port': '',
                        'credentials': [],  # type: List[str]
                        'is_login_successful': False,
                        'is_device_recognized': False,
                        'is_data_collected': False,
                        'filepath': [],  # type: List[str]
                        'queryscript': ''
                        }

            dev, pos_num, result_obj = self.thread_queue.get()

            res_dict['IP'] = dev[0]
            cc_result = check_credentials(dev, self.credentials)

            if cc_result is None:
                logger.debug('IP {}, login failed'.format(res_dict['IP']))
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue
                
            logger.debug('IP {}, login successful'.format(res_dict['IP']))
            res_dict['is_login_successful'] = True

            dev_data, tr = cc_result
            res_dict['credentials'] = [tr.func_data.login, tr.func_data.password]
            res_dict['port'] = tr.func_data.connectiontype

            dcw = DecisionTreeCLI(tr.func_data, self.tree)
            dcw.dump_log()

            if dcw.is_tree_config_error():
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue

            logger.debug('IP {}, device recognized'.format(res_dict['IP']))
            res_dict['is_device_recognized'] = True

            plist = dcw.get_path_list()

            dpath = join(*[directory for directory, script in plist])

            dp = join(self.scan_name, dpath)

            plist.reverse()
            qname = plist[0][1]

            self.lock.acquire()

            query_scheme = yaml_load(join(DIR_PROJECT, DIR_QUERY_SCRIPTS, qname))
            self.lock.release()

            if not query_scheme:
                self.result_list[pos_num] = res_dict
                self.thread_queue.task_done()
                continue

            logger.debug(f"IP {res_dict['IP']}, data collected")
            res_dict['is_data_collected'] = True

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
    f_list = []
    for item in query_scheme:
        ffolder = join(folder, connection.ip)
        result = ''
        if 'command' in item:
            result = connection.runcommand(item['command'])

        if 'file' in item:
            fp = join(ffolder, item['file'])
            lock.acquire()
            try:
                if not isdir(join(DIR_DATA, ffolder)):
                    os.makedirs(join(DIR_DATA, ffolder))
                with open(join(DIR_DATA, fp), 'w') as data_file:
                    data_file.write(result)
            except IOError:
                logger.error(f'Can\'t create file {join(DIR_DATA, fp)} to write data')
            finally:
                lock.release()
                f_list.append(fp)
    return f_list


def _device_conn_wrapper(ip: str, port: int, credentials: Tuple[str, str], result: ThreadResult()) -> None:
    conn_type = 'unknown'
    if port == 22:
        conn_type = 'SSH'
    if port == 23:
        conn_type = 'telnet'

    dc = DeviceConnection(ip, ctype=conn_type)
    login, password = credentials
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
    ip, port_telnet, is_ssh_port_open, port_ssh, is_telnet_port_open = dev

    ssh_authenticated = False
    valid_connection = None

    logger.debug(f'IP {ip}, SSH is open: {is_ssh_port_open}, Telnet is open: {is_telnet_port_open}')
    if is_ssh_port_open:
        arglist = [(ip, port_telnet, cred) for cred in creds]
        resultlist = _cc_task_threader(arglist, _device_conn_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

        if valid_connection is not None:
            ssh_authenticated = True

    if not ssh_authenticated and is_telnet_port_open:
        arglist = [(ip, port_ssh, cred) for cred in creds]
        resultlist = _cc_task_threader(arglist, _device_conn_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

    return valid_connection


def identify_device(cc_result: Optional[Tuple[Tuple, ThreadResult]], tree: dict) \
        -> Optional[Sequence[Tuple[str, str]]]:
    if cc_result is None:
        return None

    dev_data, tr = cc_result
    dcw = DecisionTreeCLI(tr.func_data, tree)

    return dcw.get_path_list()


def query_device(dev: Tuple[str, int, bool, int, bool], credentials: List[Tuple[str, str]], tree: dict,
                 result: ThreadResult()) -> None:
    cc_result = check_credentials(dev, credentials)

    if cc_result is None:
        result.func_result = False
        return

    dev_data, tr = cc_result
    dcw = DecisionTreeCLI(tr.func_data, tree)

    plist = dcw.get_path_list()
    dpath = join(*[directory for directory, script in plist])

    if not isdir(dpath):
        os.makedirs(dpath)

    result.func_result = True
    result.func_data = dcw
