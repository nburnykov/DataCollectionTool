import pickle

from mainproc.portScan import istcpportopen
from mainproc.threader import task_threader
from mainproc.devProc import ident_device_wrap
from parse import confnet
from confproc.yamlDecoder import yamlload


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

with open('portslist.pickle', 'rb') as f:
    portslist = pickle.load(f)

openportslist = []

for i in range(0, len(portslist), 2):
    if portslist[i][1] or portslist[i+1][1]:

        connection_args1, connection_result1, connection_thread1 = portslist[i]
        host1, port1, timeout1 = connection_args1

        connection_args2, connection_result2, connection_thread2 = portslist[i+1]
        host2, port2, timeout2 = connection_args2

        openportslist.append((host1, port1, connection_result1, port2, connection_result2))

with open('openportslist.pickle', 'wb') as f:
    pickle.dump(openportslist, f)

credentials = ["cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]

td = yamlload("..\\decisionTreeCLI.yaml")
qd = yamlload("..\\queriesCLI.yaml")

devargs = []
for ops in openportslist:
    devargs.append((ops, credentials, td, qd))

dcwlist = task_threader(devargs, ident_device_wrap, 5)

for dcw in dcwlist:
    dev, tr, thread = dcw
    if tr.func_data is not None:
        tr.func_data = tr.func_data.getpathlist()
    print(tr.func_data, thread)


