import unittest
from cli.decisionTreeWalkCLI import DecisionTreeWalkCLI
from confproc.yamlDecoder import yamlload
import csv


TESTDATABASEPATH = ".\\testing_database\\decisiontreeprocessing\\"


def loadcsv(path=TESTDATABASEPATH + "_verify.csv"):
    with open(path) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        outlist = [row for row in csvreader]
    return outlist


class TestDecisionTreeWalkCLI(unittest.TestCase):

    def setUp(self):
        self.td = yamlload("..\\decisionTreeCLI.yaml")
        self.qd = yamlload("..\\queriesCLI.yaml")
        self.fol = []

        ol = loadcsv()

        for row in ol:
            with open(TESTDATABASEPATH+row[0]) as textfile:
                txt = textfile.read()

            self.fol.append([txt, 'CLI_Data ' + row[1] + ' ' + row[2], row[0]])

    def test_one_template(self):
        hdata = dict(ip='10.171.2.6', username='cisco', password='cisco')
        for ind, row in enumerate(self.fol):
            testdict = dict(vShowVersion=row[0], vCiscoShowVersionExt=row[0])
            with self.subTest(line=row[2]):
                result = DecisionTreeWalkCLI(hdata, self.td, self.qd, testdict).getteststring()
                print("{0:50s} {1:40s}".format(row[2], result))
                self.assertEqual(result, row[1])

    def test_two(self):
        dcw2 = DecisionTreeWalkCLI({}, {}, {})
        print('Two')
        print(dcw2.getlog())
        self.assertEqual(dcw2.isportsopen(), False)

    def test_three(self):
        print('Three')
        hdata = dict(ip='10.171.2.6', username='cisco', password='cisco')
        dcw3 = DecisionTreeWalkCLI(hdata, self.td, self.qd)
        print(dcw3.getlog())
        self.assertEqual(dcw3.isportsopen(), False)

    def test_four(self):
        print('Four')
        hdata = dict(ip='10.171.2.5', username='cisco', password='cisco')
        dcw4 = DecisionTreeWalkCLI(hdata, self.td, self.qd)
        print(dcw4.getlog())
        self.assertEqual(dcw4.isportsopen(), True)
