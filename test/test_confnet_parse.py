import unittest
from parse import confnet


class test_confnet_parse(unittest.TestCase):
    def setUp(self):
        self.testlist1 = [("192.168.1.1", 1),
                          ("10.10.0.0-10.10.0.255", 256),
                          ("192.168.0.2//48", 0),
                          ("172.168.0.0/16", 65536),
                          ("a.b.c.d", 0),
                          ("10.0.0/24", 0)]

    def test_list1(self):
        for net, result in self.testlist1:
            pline = confnet.parseline(net)
            with self.subTest(line=result):
                self.assertEqual(len(pline), result)

