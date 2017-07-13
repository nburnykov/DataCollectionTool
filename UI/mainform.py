from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from parse.confnet import checkline
from typing import List, Tuple, Optional
from mainproc.rangeProc import rangeproc


class ScanData:
    def __init__(self):
        self.scan_name = ''
        self.scan_list = []         # type: List[str]
        self.do_not_scan_list = []  # type: List[str]
        self.credential_list = []   # type: List[Tuple[str, str]]
        self.is_scan = False
        self.is_parse = False

    def __str__(self):
        result = "Scan name: {}\n".format(self.scan_name)
        result += "Scan list: \n"

        for line in self.scan_list:
            result += "{}\n".format(line)

        result += "Do not scan list:\n"

        for line in self.do_not_scan_list:
            result += "{}\n".format(line)

        result += "Credentials list:\n"

        for line in self.credential_list:
            result += "{}\n".format(line)

        result += "Scan: {}\n".format(self.is_scan)
        result += "Parse: {}\n".format(self.is_parse)

        return result

class MainForm(BoxLayout):

    sd = ScanData()

    def addcredentials(self, login: str, password: str, sd=sd):
        if login != '':
            sd.credential_list.append((login, password))
            self.scr_mng.mainsm.scr2.scr2bl.brv.cred_view.data.insert(0, {'value': login})

    def startscan(self, scan_name: str, scan_range: str, do_not_scan_range: str, is_scan: bool, is_parse: bool, sd=sd):
        sd.scan_name = scan_name
        sd.scan_list = scan_range.split('\n')
        sd.do_not_scan_list = do_not_scan_range.split('\n')
        sd.is_scan = is_scan
        sd.is_parse = is_parse

        # TODO Start main procedure

        # TODO add scan to saved scans and csv

        print(sd)

    def setscanrange(self, text: str):
        t = text.split("\n")
        isvalidinput = True
        for line in t:
            isvalidinput &= checkline(line)

        if not isvalidinput:
            self.scr_mng.mainsm.scr1.scr1bl2.scan_range.background_color = [1, 0.5, 0, 1]
        else:
            self.scr_mng.mainsm.scr1.scr1bl2.scan_range.background_color = [1, 1, 1, 1]

    def setdonotscanrange(self, text: str):
        t = text.split("\n")
        isvalidinput = True
        for line in t:
            isvalidinput &= checkline(line)

        if not isvalidinput:
            self.scr_mng.mainsm.scr1.scr1bl3.do_not_scan_range.background_color = [1, 0.5, 0, 1]
        else:
            self.scr_mng.mainsm.scr1.scr1bl3.do_not_scan_range.background_color = [1, 1, 1, 1]






class DataCollectionToolApp(App):
    pass


def showmainform():
    #MainForm.sd = ScanData()
    DataCollectionToolApp().run()