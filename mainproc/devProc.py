from mainproc.threader import task_threader, ThreadResult
from mainproc.deviceConnection import DeviceConnection
from CLI.decisionTreeWalkCLI import DecisionTreeWalkCLI
from typing import Tuple, Sequence, Optional


def _devconnection_wrapper(ip: str, port: int, creds: str, result: ThreadResult()) -> None:

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


def _get_valid_connection(rlist: Sequence[Tuple[Tuple, ThreadResult, str]]) \
        -> Optional[Tuple[Tuple, ThreadResult]]:

    for r in rlist:
        args, tr, tname = r
        if tr.func_result:
            return args, tr

    return


def check_credentials(dev: Tuple[str, int, bool, int, bool], creds: Sequence[str]) \
        -> Optional[Tuple[Tuple, ThreadResult]]:

    ip, port, is_ssh_port_open, port2, is_telnet_port_open = dev
    ssh_authenticated = False

    valid_connection = None

    if is_ssh_port_open:
        arglist = [(ip, port, cred) for cred in creds]
        resultlist = task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

        if valid_connection is not None:
            ssh_authenticated = True

    if not ssh_authenticated and is_telnet_port_open:
        arglist = [(ip, port2, cred) for cred in creds]
        resultlist = task_threader(arglist, _devconnection_wrapper, 3)
        valid_connection = _get_valid_connection(resultlist)

    return valid_connection


def ident_device(ccresult: Optional[Tuple[Tuple, ThreadResult]], treedict: dict, querydict: dict) \
        -> Optional[Sequence[Tuple[str, str]]]:

    if ccresult is None:
        return None

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict, querydict)

    return dcw.getpathlist()


def ident_device_wrap(dev: Tuple[str, int, bool, int, bool], creds: Sequence[str], treedict: dict, querydict: dict,
                      result: ThreadResult()) -> None:

    ccresult = check_credentials(dev, creds)
    print(dev, ccresult)
    if ccresult is None:
        result.func_result = False
        return

    devdata, tr = ccresult
    dcw = DecisionTreeWalkCLI(tr.func_data, treedict, querydict)

    result.func_result = True
    result.func_data = dcw


