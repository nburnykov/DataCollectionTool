import unittest
from mainproc.rangeProc import ScanData, rangeproc


class TestRangeProc(unittest.TestCase):

    def setUp(self):
        self.sd = ScanData()
        self.sd.scan_name = "Test_scan"
        self.sd.scan_list = ['10.171.18.0/24', "10.171.2.5"]
        self.sd.do_not_scan_list = ["10.171.18.0", "10.171.18.255", "10.171.18.1"]
        self.sd.credential_list = [("1", "1"), ("cisco", "cisco"), ("ps", "ps1234"), ("nburnykov", "!QAZ2wsx")]
        self.sd.is_scan = True
        self.sd.is_parse = True


    def test_rangeproc(self):
        rangeproc(self.sd)
