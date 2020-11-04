import unittest
from parse.parse_collected_data import collected_data_parse


class TestCollectedDataParse(unittest.TestCase):
    def setUp(self):
        self.test_scan = 'Test_scan'

    def test_one(self):
        collected_data_parse(self.test_scan)
