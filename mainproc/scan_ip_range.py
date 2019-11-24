from typing import List, Tuple
import logging
from os.path import join

from utils.yaml_file_io import yaml_load, yaml_dump
from constants import PROJECT_PATH
from devproc.query_device import dev_task_threader
from devproc.check_port import is_tcp_port_opened
from utils.threader import task_threader
from parse import parse_net

logger = logging.getLogger('main')


class ScanData:
    def __init__(self):
        self.scan_name = ''
        self.scan_list: List[str] = []
        self.do_not_scan_list: List[str] = []
        self.credential_list: List[Tuple[str, str]] = []
        self.is_scan = False
        self.is_parse = False


def range_proc(scan_data: ScanData):
    logger.info(scan_data)

    scan_set = parse_net.compose_set(scan_data.scan_list)
    do_not_scan_set = parse_net.compose_set(scan_data.do_not_scan_list)

    scan_set ^= do_not_scan_set

    scan_list = []

    timeout = 1

    for ip in scan_set:
        for port in [22, 23]:
            scan_list.append((parse_net.dec_to_ip(ip), port, timeout))

    ports_list = task_threader(scan_list, is_tcp_port_opened)

    open_ports_list = []

    for i in range(0, len(ports_list), 2):
        if ports_list[i][1] or ports_list[i + 1][1]:

            connection_args1, connection_result1, connection_thread1 = ports_list[i]
            host1, port1, timeout1 = connection_args1

            connection_args2, connection_result2, connection_thread2 = ports_list[i + 1]
            host2, port2, timeout2 = connection_args2
            if connection_result1.func_result or connection_result2.func_result:
                open_ports_list.append((host1, port1,
                                        connection_result1.func_result, port2, connection_result2.func_result))

    logger.info(f'Found {(len(open_ports_list))} open ports')

    if len(open_ports_list):
        logger.info(f'Open ports:')
    for port in open_ports_list:
        logger.info(port)

    decision_tree = yaml_load(join(PROJECT_PATH, "decision_tree_cli.yaml"))

    dcw_list = dev_task_threader(open_ports_list, scan_data.credential_list, scan_data.scan_name, decision_tree, 50)

    conf_file = {'Scan Name': scan_data.scan_name,
                 'Scan List': scan_data.scan_list,
                 'Do Not Scan List': scan_data.do_not_scan_list,
                 'Credentials List': [list(cred) for cred in scan_data.credential_list],
                 'Discovered Data': dcw_list}

    # TODO crypt passwords and logins

    yaml_dump(join(PROJECT_PATH, '_DATA', {scan_data.scan_name}, f'{scan_data.scan_name}.yaml'), conf_file)
