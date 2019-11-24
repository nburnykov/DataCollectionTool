import time
import unittest

from devproc.deviceConnection import DeviceConnection


class TestDeviceConnection(unittest.TestCase):

    # def test_SSH_connection(self):
    #     connection = DeviceConnection('10.171.2.5')
    #     connection.connect('cisco', 'cisco')
    #     self.assertTrue(connection.isconnected())
    #
    def test_SSH_disconnect(self):
        connection = DeviceConnection('10.171.2.5')
        connection.connect('cisco', 'cisco')
        connection.disconnect()
        self.assertFalse(connection.connected())

    def test_SSH_send_command(self):
        connection = DeviceConnection('10.171.2.5')
        connection.connect('cisco', 'cisco')
        time.sleep(1)
        print(connection.connected())
        print(connection.run_command('sh ip int br'))
        time.sleep(1)
        print(connection.connected())
        print(connection.run_command('sh ver'))
        print(connection.run_command('display system-information'))
        print(connection.run_command('sh ver'))
        #self.assertEqual(connection.runcommand('sh run')[:10], 'Linux ubun')
        connection.disconnect()