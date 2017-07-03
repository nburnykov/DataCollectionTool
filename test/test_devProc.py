import unittest
import pickle
from mainproc.devProc import check_credentials, _device_query, dev_task_threader
from confproc.yamlDecoder import yamlload
from threading import Lock


class TestDevProc(unittest.TestCase):

    def setUp(self):
        self.credentials = ["cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
        self.td = yamlload("..\\decisionTreeCLI.yaml")
        self.qd = yamlload("..\\queriesCLI.yaml")
        self.q = yamlload("..\\_DeviceQueryScripts\\CiscoCatSwitch.yaml")

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
