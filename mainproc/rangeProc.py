import pickle
import os
from mainproc.portScan import istcpportopen
from mainproc.devProc import process_device_wrap, dev_task_threader
from parse import confnet
from confproc.yamlDecoder import yamlload


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


def rangeproc():

    scanlist = ["10.171.18.0/24", "10.171.2.5"]
    dontscanlist = ["10.171.18.0", "10.171.18.255", "10.171.18.1"]

    scanset = confnet.composeset(scanlist)
    dontscanset = confnet.composeset(dontscanlist)

    scanset ^= dontscanset

    scanlist = []

    timeout = 1

    # for ip in scanset:
    #     for port in [22, 23]:
    #         scanlist.append((confnet.dectoIP(ip), port, timeout))
    #
    # portslist = task_threader(scanlist, istcpportopen)
    #
    # with open('portslist.pickle', 'wb') as f:
    #     pickle.dump(portslist, f)

    print(os.path.dirname(os.path.abspath(__package__)))
    with open(os.path.dirname(os.path.abspath(__package__))+'\\test\\testing_database\\portslist.pickle', 'rb') as f:
        portslist = pickle.load(f)

    openportslist = []

    for i in range(0, len(portslist), 2):
        if portslist[i][1] or portslist[i+1][1]:

            connection_args1, connection_result1, connection_thread1 = portslist[i]
            host1, port1, timeout1 = connection_args1

            connection_args2, connection_result2, connection_thread2 = portslist[i+1]
            host2, port2, timeout2 = connection_args2

            openportslist.append((host1, port1, connection_result1, port2, connection_result2))

    #credentials = ["1/1", "cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
    credentials = ["1/1", "cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]

    td = yamlload(os.path.dirname(os.path.abspath(__package__))+"\\decisionTreeCLI.yaml")
    qd = yamlload(os.path.dirname(os.path.abspath(__package__))+"\\queriesCLI.yaml")

    dcwlist = dev_task_threader(openportslist, credentials, td, qd, 50)

    print(dcwlist)


