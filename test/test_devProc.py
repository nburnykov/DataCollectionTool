import unittest
import pickle
from mainproc.devProc import check_credentials, ident_device, process_device_wrap
from confproc.yamlDecoder import yamlload


class TestDevProc(unittest.TestCase):

    def setUp(self):
        self.credentials = ["cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
        self.td = yamlload("..\\decisionTreeCLI.yaml")
        self.qd = yamlload("..\\queriesCLI.yaml")

        with open('./testing_database/openportslist.pickle', 'rb') as f:
            self.portslist = pickle.load(f)

    def test_check_credentials(self):
        dev = self.portslist[2]
        dev, conn = check_credentials(dev, self.credentials)
        self.assertEqual(dev, ('10.171.18.202', 23, 'cisco/cisco'))

    # def test_ident_device(self):
    #     print(self.portslist)
    #     dev = self.portslist[0]
    #     cc = check_credentials(dev, self.credentials)
    #     print(dev, cc)
    #     res = ident_device(cc, self.td, self.qd)
    #     print(res)
