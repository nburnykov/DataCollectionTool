import socket


class PortScan:
    def __init__(self, device):

        self.device = device
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        result = sock.connect_ex((device['ip'], 23))
        self.__telnetisopen__ = (result == 0)

        result = sock.connect_ex((device['ip'], 22))
        self.__sshisopen__ = (result == 0)

    def istelnetopen(self):
        return self.__telnetisopen__

    def issshopen(self):
        return self.__sshisopen__
