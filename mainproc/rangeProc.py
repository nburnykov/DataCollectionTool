from typing import List, Tuple
import logging

from confproc.fileProc import yaml_load, yaml_dump
from constants import PROJECTPATH
from devproc.devProc import dev_task_threader
from devproc.portScan import istcpportopen
from devproc.threader import task_threader
from parse import confnetparse

logger = logging.getLogger('main')


class ScanData:
    def __init__(self):
        self.scan_name = ''
        self.scan_list: List[str] = []
        self.do_not_scan_list: List[str] = []
        self.credential_list: List[Tuple[str, str]] = []
        self.is_scan = False
        self.is_parse = False

    def __str__(self):
        result = "Scan name: {}\n".format(self.scan_name)
        result += "Scan list: \n"

        for line in self.scan_list:
            result += "{}\n".format(line)

        result += "Do not scan list:\n"

        for line in self.do_not_scan_list:
            result += "{}\n".format(line)

        result += "Credentials list:\n"

        for line in self.credential_list:
            result += "{}\n".format(line)

        result += "Scan: {}\n".format(self.is_scan)
        result += "Parse: {}\n".format(self.is_parse)

        return result


def rangeproc(scandata: ScanData):

    logger.info(scandata)

    scanset = confnetparse.composeset(scandata.scan_list)
    dontscanset = confnetparse.composeset(scandata.do_not_scan_list)

    scanset ^= dontscanset

    scanlist = []

    timeout = 1

    for ip in scanset:
        for port in [22, 23]:
            scanlist.append((confnetparse.dectoIP(ip), port, timeout))

    portslist = task_threader(scanlist, istcpportopen)

    openportslist = []

    for i in range(0, len(portslist), 2):
        if portslist[i][1] or portslist[i+1][1]:

            connection_args1, connection_result1, connection_thread1 = portslist[i]
            host1, port1, timeout1 = connection_args1

            connection_args2, connection_result2, connection_thread2 = portslist[i+1]
            host2, port2, timeout2 = connection_args2
            if connection_result1.func_result or connection_result2.func_result:
                openportslist.append((host1, port1,
                                      connection_result1.func_result, port2, connection_result2.func_result))

    logger.info(f'Found {(len(openportslist))} open ports')

    if len(openportslist):
        logger.info(f'Open ports:')
    for port in openportslist:
        logger.info(port)

    td = yaml_load(PROJECTPATH + "/decisionTreeCLI.yaml")

    dcwlist = dev_task_threader(openportslist, scandata.credential_list, scandata.scan_name, td, 50)

    conffile = {'Scan Name': scandata.scan_name,
                'Scan List': scandata.scan_list,
                'Do Not Scan List': scandata.do_not_scan_list,
                'Credentials List': [list(cred) for cred in scandata.credential_list],
                'Discovered Data': dcwlist}

    # TODO crypt passwords and logins

    yaml_dump(f'{PROJECTPATH}_DATA/{scandata.scan_name}/{scandata.scan_name}.yaml', conffile)


