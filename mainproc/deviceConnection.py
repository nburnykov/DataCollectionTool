import paramiko
import telnetlib
import time


class DeviceConnection:
    def __init__(self, ip: str, ctype='SSH', commandtimeout=2) -> None:
        self.ip = ip
        self.connectiontype = ctype.lower()
        self._commandtimeout = commandtimeout
        self._isconnected = False
        self._connectionlog = []        # TODO implement logger
        self._tc = None
        self._sshc = None
        self._ssh = None

    def connect(self, login: str, password: str) -> bool:

        self._isconnected = False

        if self.connectiontype == 'ssh':

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                client.connect(hostname=self.ip, username=login, password=password,
                               look_for_keys=False, allow_agent=False)
            except paramiko.ssh_exception.NoValidConnectionsError:
                return self._isconnected
            self._ssh = client
            self._sshc = self._ssh.invoke_shell()
            
            # TODO handle possible connection exceptions

        if self.connectiontype == 'telnet':

            # TODO Verify possible problems with telnet ad SSH connections like session-limit

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

        return self._isconnected

    def runcommand(self, command: str, timeout=0) -> str:

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

        if self._sshc is not None:

            self._sshc.send("\n")
            self._sshc.send(command + "\n")
            time.sleep(timeout_)
            output = self._sshc.recv(5000)

        time.sleep(timeout_)

        return output

    def disconnect(self) -> None:

        if not self._isconnected:
            return
        if self._ssh is not None:
            self._ssh.close()
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
            self._isconnected = self._ssh.get_transport() and self._ssh.get_transport().is_active()

        return self._isconnected








