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

    def test_parsedcount(self):
        for net, result in self.testlist1:
            pline = confnet.parseline(net)
            with self.subTest(line=result):
                self.assertEqual(len(pline), result)

    def test_parsednet30(self):
        net = "10.12.13."
        firstIP = 252
        pline = list(confnet.parseline(net + str(firstIP)+"/30"))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(confnet.dectoIP(p), net + str(firstIP + i))

    def test_parsednet28(self):
        net = "10.12.13."
        firstIP = 224
        pline = list(confnet.parseline(net + str(firstIP)+"/28"))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(confnet.dectoIP(p), net + str(firstIP + i))

    def test_parsenetupto24(self):

        net = "10.12.12."
        firstIP = 0
        mask = 24

        pline = list(confnet.parseline(net + str(firstIP) + "/" + str(mask)))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(confnet.dectoIP(p), net + str(firstIP + i))

    def test_parsedhost(self):
        host = "192.168.1.1"
        pline = confnet.parseline(host)
        self.assertEqual(confnet.dectoIP(list(pline)[0]), host)

    def test_parsedrange(self):
        net = "10.15.20."
        hostmin = 12
        hostmax = 241

        rangestr = "{0}{1}-{0}{2}".format(net, hostmin, hostmax)

        pline = list(confnet.parseline(rangestr))
        pline.sort()

        for i, ip in enumerate(range(hostmin, hostmax + 1)):
            with self.subTest(line=str(ip)):
                self.assertEqual(confnet.dectoIP(pline[i]), net + str(ip))




