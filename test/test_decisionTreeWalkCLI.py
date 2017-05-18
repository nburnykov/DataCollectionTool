import unittest
from CLI.decisionTreeWalkCLI import DecisionTreeWalkCLI
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



