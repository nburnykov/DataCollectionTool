import time
import unittest

from devproc.devProc import check_credentials
from devproc.threader import task_threader, ThreadResult


class TestThreader(unittest.TestCase):
    def setUp(self):
        pass

    def test_simplefunction(self):

        def a3(a: int, resobj: ThreadResult) -> None:
            time.sleep(.01)
            resobj.func_data = a+3

        inputlist = [(8,), (10,), (12,)]
        result = task_threader(inputlist, a3, thread_num=2)
        result = [res.func_data for arg, res, st in result]
        with self.subTest(line=11):
            self.assertIn(11, result)
        with self.subTest(line=13):
            self.assertIn(13, result)
        with self.subTest(line=15):
            self.assertIn(15, result)

    # def test_verify_credentials(self):
    #     dev = ('10.171.18.202', 22, True, 23, True)
    #     credentials = ["1/1", "2/2", "3/3", "4/4", "cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
    #     print(check_credentials(dev, credentials))

    def test_verify_credentials2(self):
        dev = ('10.171.18.201', 22, False, 23, True)
        credentials = ["1/1", "2/2", "3/3", "4/4", "cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
        print(check_credentials(dev, credentials))

    def test_verify_credentials3(self):
        dev = ('10.171.18.203', 22, False, 23, True)
        credentials = ["1/1", "2/2", "3/3", "4/4", "cisco/cisco", "ps/ps1234", "nburnykov/!QAZ2wsx"]
        print(check_credentials(dev, credentials))
