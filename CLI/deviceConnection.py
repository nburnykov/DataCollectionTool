import paramiko
import telnetlib
import time

class DeviceConnection:
    def __init__(self, device, ctype='SSH', commandtimeout=2):
        self.device = device
        self.connectiontype = ctype.lower()
        self.__commandtimeout__ = commandtimeout
        self.__connectionerror__ = False

        if self.connectiontype == 'ssh':

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                client.connect(hostname=device['ip'], username=device['username'], password=device['password'],
                               look_for_keys=False, allow_agent=False)
            except paramiko.ssh_exception.NoValidConnectionsError:
                self.__connectionerror__ = True
                return
            self.__sshc__ = client.invoke_shell()

            # TODO handle possible connection exceptions

        if self.connectiontype == 'telnet':

            self.__tc__ = telnetlib.Telnet(device['ip'])

            self.__tc__.read_until(b"sername:")
            self.__tc__.write((device['username'] + '\n').encode('ascii'))

            self.__tc__.read_until(b"assword:")
            self.__tc__.write((device['password'] + '\n').encode('ascii'))

            time.sleep(self.__commandtimeout__)
            output = str(self.__tc__.read_very_eager(), 'ascii')

            # TODO handle possible connection exceptions, not only Cisco (... error string "error" maybe)

            if output.lower().find("failed") > -1:
                self.__connectionerror__ = True
                return

            #self.__tc__.write(b"terminal length 0\n")

    def runcommand(self, command):
        if self.__connectionerror__:
            return

        output = ''
        if self.connectiontype == 'telnet':

            self.__tc__.write("\n".encode('ascii'))
            self.__tc__.write((command + "\n").encode('ascii'))
            time.sleep(self.__commandtimeout__)
            output = str(self.__tc__.read_very_eager(), 'ascii')

        if self.connectiontype == 'ssh':

            self.__sshc__.send("\n")
            self.__sshc__.send(command + "\n")
            time.sleep(self.__commandtimeout__)
            output = self.__sshc__.recv(5000)

        time.sleep(self.__commandtimeout__)

        return output

    def disconnect(self):
        if self.__connectionerror__:
            return
        if hasattr(self, '__sshc__'):
            self.__sshc__.close()

    def isconnected(self):
        return not self.__connectionerror__

dev = {'ip': '10.171.18.201',
       'username': 'cisco',
       'password': 'cisco'}

dc = DeviceConnection(dev, ctype='Telnet')

out = ''
out += (dc.runcommand('sh ver'))
out += (dc.runcommand('sh system-information'))

print(out)




