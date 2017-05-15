import paramiko
import telnetlib
import time

class DeviceConnection:
    def __init__(self, device, ctype='SSH'):
        self.device = device
        self.connectiontype = ctype
        self.__connectionerror__ = False

        if ctype == 'SSH':

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=device['ip'], username=device['username'], password=device['password'],
                           look_for_keys=False, allow_agent=False)
            self.__sshc__ = client.invoke_shell()

            # TODO handle possible connection exceptions

        if ctype == 'Telnet':

            self.__tc__ = telnetlib.Telnet(device['ip'])

            self.__tc__.read_until(b"sername:")
            self.__tc__.write((device['username'] + '\n').encode('ascii'))

            self.__tc__.read_until(b"assword:")
            self.__tc__.write((device['password'] + '\n').encode('ascii'))

            time.sleep(2)
            output = str(self.__tc__.read_very_eager(), 'ascii')

            # TODO handle possible connection exceptions

            if output[:-8] == "assword:":
                self.__connectionerror__ = True
                return

            #self.__tc__.write(b"terminal length 0\n")

    def runcommand(self, command, file):
        if self.__connectionerror__:
            return

        output = ''
        if self.connectiontype == 'Telnet':

            self.__tc__.write((command + "\n").encode('ascii'))
            time.sleep(2)
            output = str(self.__tc__.read_very_eager(), 'ascii')

        if self.connectiontype == 'SSH':

            self.__sshc__.send(command + "\n")
            time.sleep(2)
            output = self.__sshc__.recv(5000)

        with open(file, 'w') as data_file:
            data_file.write(output)

    def disconnect(self):
        if self.__connectionerror__:
            return
        self.__ssh_connection__.disconnect()

    def isconnected(self):
        return not self.__connectionerror__

dev = {'device_type': 'cisco_ios_telnet',
       'ip': '10.171.2.5',
       'username': 'cisco',
       'password': 'cisco'}

dc = DeviceConnection(dev, ctype='Telnet')


dc.runcommand('sh ver', 'sh_ver.txt')






