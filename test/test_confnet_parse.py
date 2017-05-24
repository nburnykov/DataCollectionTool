import unittest
from parse import confnet


class test_confnet_parse(unittest.TestCase):
    def setUp(self):
        self.testlist1 = ["192.168.1.1",
                          "10.10.0.0-10.10.0.255",
                          "192.168.0.2//48",
                          "172.168.0.0/16",
                          "a.b.c.d",
                          "10.0.0/24"]

        self.testresult1 = ["192.168.1.1",
                            ("10.10.0.0", "10.10.0.255"),
                            ("172.168.0.0", "16")]

    def test_list1(self):
        nets = confnet.parse(self.testlist1)
        for i, n in enumerate(nets):
            with self.subTest(line=n):
                self.assertEqual(n, self.testresult1[i])
        print(nets)
