import pickle
from .threader import task_threader, ThreadResult
from mainproc.deviceConnection import DeviceConnection


def devconnectionWrapper(ip: str, creds: str, port: int,  result: ThreadResult()) -> None:

    if port==22:
        ctype = 'SSH'
    else:
        ctype = 'telnet'

    dc = DeviceConnection(ip, ctype=ctype)
    login, password = creds.split('/')
    result.func_result = dc.connect(login=login, password=password)

    if result.func_result:
        result.func_data = dc
        result.is_stop_queue = True

credentials = ["1/1", "2/2", "cisco/cisco", "ps/ps1234"]

with open('openportslist.pickle', 'rb') as f:
    portslist = pickle.load(f)

device = portslist[1]

ip, port, is_ssh_port_open, port2, is_telnet_port_open = device[0]


ssh_authenticated = False

if is_ssh_port_open:
    ssh_authenticated = True

if not ssh_authenticated and is_telnet_port_open:
    pass