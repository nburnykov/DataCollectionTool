import unittest
from parse.confnetparse import parseline, dectoIP, checkline


class TestConfnetparse(unittest.TestCase):
    def setUp(self):
        self.testlist1 = [("192.168.1.1", 1),
                          ("10.10.0.0-10.10.0.255", 256),
                          ("192.168.0.2//48", 0),
                          ("172.168.0.0/16", 65536),
                          ("a.b.c.d", 0),
                          ("10.0.0/24", 0)]

        self.testlist2 = [('192.168.0.1', True),
                          ('256.256.256.256', False),
                          ('10.10.10.10/31', True),
                          ('10.10.10.10/33', False),
                          ('10.554.0.1', False),
                          ('10.12.0.15-10.9.12.12', False),
                          ('10.12.0.15-10.12.12.12', True)]

    def test_parsedcount(self):
        for net, result in self.testlist1:
            pline = parseline(net)
            with self.subTest(line=result):
                self.assertEqual(len(pline), result)

    def test_parsednet30(self):
        net = "10.12.13."
        firstip = 252
        pline = list(parseline(net + str(firstip)+"/30"))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(dectoIP(p), net + str(firstip + i))

    def test_parsednet28(self):
        net = "10.12.13."
        firstip = 224
        pline = list(parseline(net + str(firstip)+"/28"))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(dectoIP(p), net + str(firstip + i))

    def test_parsenetupto24(self):

        net = "10.12.12."
        firstip = 0
        mask = 24

        pline = list(parseline(net + str(firstip) + "/" + str(mask)))
        pline.sort()
        for i, p in enumerate(pline):
            with self.subTest(line=str(p)):
                self.assertEqual(dectoIP(p), net + str(firstip + i))

    def test_parsedhost(self):
        host = "192.168.1.1"
        pline = parseline(host)
        self.assertEqual(dectoIP(list(pline)[0]), host)

    def test_parsedrange(self):
        net = "10.15.20."
        hostmin = 12
        hostmax = 241

        rangestr = "{0}{1}-{0}{2}".format(net, hostmin, hostmax)

        pline = list(parseline(rangestr))
        pline.sort()

        for i, ip in enumerate(range(hostmin, hostmax + 1)):
            with self.subTest(line=str(ip)):
                self.assertEqual(dectoIP(pline[i]), net + str(ip))

    def test_checkline(self):
        for net, result in self.testlist2:
            with self.subTest(line=str(net)):
                self.assertEqual(checkline(net), result)
