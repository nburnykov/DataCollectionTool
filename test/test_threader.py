import unittest
from devproc.threader import task_threader
import time


class TestThreader(unittest.TestCase):
    def setUp(self):
        pass

    def test_simplefunction(self):

        def a3(a):
            time.sleep(.01)
            return a+3

        inputlist = [8, 10, 12]
        result = task_threader(inputlist, a3, thread_num=30)
        print(result)
        result = [r[1] for r in result]
        with self.subTest(line=11):
            self.assertIn(11, result)
        with self.subTest(line=13):
            self.assertIn(13, result)
        with self.subTest(line=15):
            self.assertIn(15, result)

    def test_error(self):

        pass
