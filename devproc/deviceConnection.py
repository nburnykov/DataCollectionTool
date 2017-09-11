from netmiko import ConnectHandler
from netmiko.base_connection import BaseConnection
import telnetlib
import time
import logging

logger = logging.getLogger('main')


class DeviceConnection:
    def __init__(self, ip: str, ctype: str ='SSH', commandtimeout: int =2) -> None:
        self.ip = ip
        self.connectiontype = ctype.lower()
        self._commandtimeout = commandtimeout
        self._isconnected = False
        self._tc = None
        self._ssh = None
        self.login: str = ''
        self.password: str = ''

    def connect(self, login: str, password: str) -> bool:

        logger.debug(f'Connecting to {self.ip}, login {login} via {self.connectiontype}')

        self.login = login
        self.password = password

        self._isconnected = False

        if self.connectiontype == 'ssh':

            device = {'device_type': 'cisco_ios',
                      'ip':   self.ip,
                      'username': login,
                      'password': password}

            try:
                client = ConnectHandler(**device)
            except Exception:
                return self._isconnected
            self._ssh = client

            # TODO handle possible connection exceptions

        if self.connectiontype == 'telnet':

            # TODO Verify possible problems with telnet and SSH connections like session-limit

            self._tc = telnetlib.Telnet(self.ip)

            self._tc.read_until(b":")
            self._tc.write((login + '\n').encode('ascii'))

            self._tc.read_until(b":")
            self._tc.write((password + '\n').encode('ascii'))

            time.sleep(self._commandtimeout)
            output = str(self._tc.read_very_eager(), 'ascii')

            # TODO handle possible connection exceptions

            if output[-2].find(":") > -1:
                self.disconnect()
                return self._isconnected

        self._isconnected = True
        logger.debug(f'Connection to {self.ip} successful')

        return self._isconnected

    def runcommand(self, command: str, timeout=0) -> str:

        logger.debug(f'Executing command on {self.ip}: \'{command}\'')

        timeout_ = self._commandtimeout

        if timeout > 0:
            timeout_ = timeout

        output = ''
        if not self._isconnected:
            return output

        if self._tc is not None:

            self._tc.write("\n".encode('ascii'))
            self._tc.write((command + "\n").encode('ascii'))
            time.sleep(timeout_)
            output = str(self._tc.read_very_eager(), 'ascii')
            time.sleep(timeout_)

        if self._ssh is not None:
            host = self._ssh.find_prompt()
            output += host + '\n'
            logger.debug(f'Hostname is {host}')
            output += self._ssh.send_command(command, expect_string=host)

        return output

    def disconnect(self) -> None:

        if not self._isconnected:
            return
        if self._ssh is not None:
            self._ssh.disconnect()
        if self._tc is not None:
            self._tc.close()

    def isconnected(self) -> bool:

        self._isconnected = False

        if self._tc is not None:
            try:
                if self._tc.sock:
                    self._tc.sock.send(telnetlib.IAC + telnetlib.NOP)
                    self._isconnected = True
            except Exception:
                self._isconnected = False

        if self._ssh is not None:
            self._isconnected = self._ssh.remote_conn.get_transport().is_alive()

        return self._isconnected

    def reconnect(self):

        if not self.isconnected():
            self.connect(self.login, self.password)






