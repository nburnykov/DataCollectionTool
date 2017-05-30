import socket


class PortScan:
    def __init__(self, device, timeout=5):

        self.connectiontype = ''
        self.__telnetisopen__ = False
        self.__sshisopen__ = False

        self.device = device
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        if 'ip' not in device:
            return

        result = sock.connect_ex((device['ip'], 23))
        self.__telnetisopen__ = (result == 0)
        if self.__telnetisopen__:
            self.connectiontype = 'telnet'

        result = sock.connect_ex((device['ip'], 22))
        self.__sshisopen__ = (result == 0)
        if self.__sshisopen__:
            self.connectiontype = 'ssh'


    def istelnetopen(self):

        return self.__telnetisopen__

    def issshopen(self):

        return self.__sshisopen__
