import pickle

from devproc.portScan import istcpportopen
from devproc.threader import task_threader
# from .deviceConnection import DeviceConnection
from parse import confnet


scanlist = ["10.171.18.0/24", "10.171.2.5"]
notscanlist = ["10.171.18.0", "10.171.18.255", "10.171.18.1"]

credentials = ["cisco/cisco", "ps/ps1234"]

scanset = confnet.composeset(scanlist)
notscanset = confnet.composeset(notscanlist)

scanset ^= notscanset

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

with open('portslist.pickle', 'rb') as f:
    portslist = pickle.load(f)

openportslist = []

for i in range(0, len(portslist), 2):
    if portslist[i][1] or portslist[i+1][1]:

        connection_args1, connection_result1, connection_thread1 = portslist[i]
        host1, port1, timeout1 = connection_args1

        connection_args2, connection_result2, connection_thread2 = portslist[i+1]
        host2, port2, timeout2 = connection_args2

        openportslist.append(((host1, port1, connection_result1), (host2, port2, connection_result2)))

[print(ops) for ops in openportslist]


# TODO - connect to devices with opened ports and check credential list



# TODO - connect to device console and run decision tree

