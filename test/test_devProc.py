import pickle
import unittest

from confproc.fileProc import yaml_load
from devproc.devProc import dev_task_threader


class TestDevProc(unittest.TestCase):

    def setUp(self):
        self.credentials = ["cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
        self.td = yaml_load("..\\decisionTreeCLI.yaml")
        self.qd = yaml_load("..\\queriesCLI.yaml")
        self.q = yaml_load("..\\_DeviceQueryScripts\\CiscoCatSwitch.yaml")

        with open('./testing_database/openportslist.pickle', 'rb') as f:
            self.portslist = pickle.load(f)

    # def test_check_credentials(self):
    #     print(self.q)
    #     dev = self.portslist[0]
    #     print(dev)
    #     dev, conn = check_credentials(dev, self.credentials)
    #     lock = Lock()
    #     _device_query(conn.func_data, self.q, '.', lock)
    #     self.assertEqual(dev, ('10.171.18.7', 22, "nburnykov/!QAZ2wsx"))

    def test_dev_task_threader(self):
        dev_task_threader(self.portslist[0], self.credentials, self.td, self.qd, 1)


    # TODO test single wrong credentials pair
