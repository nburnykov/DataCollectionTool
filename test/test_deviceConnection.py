import unittest
from mainproc.deviceConnection import DeviceConnection


class TestDeviceConnection(unittest.TestCase):

    def test_SSH_connection(self):
        connection = DeviceConnection('10.171.18.7')
        connection.connect('nburnykov', '!QAZ2wsx')
        self.assertTrue(connection.isconnected())

    def test_SSH_disconnect(self):
        connection = DeviceConnection('10.171.18.7')
        connection.connect('nburnykov', '!QAZ2wsx')
        connection.disconnect()
        self.assertFalse(connection.isconnected())

    def test_SSH_send_command(self):
        connection = DeviceConnection('10.171.18.7')
        connection.connect('nburnykov', '!QAZ2wsx')
        self.assertEqual(connection.runcommand('uname -a')[:10], b'Welcome to')
        connection.disconnect()