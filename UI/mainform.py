from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from parse.confnetparse import checkline
from typing import List, Tuple, Optional
from mainproc.rangeProc import rangeproc, ScanData


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

        rangeproc(sd)
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
    DataCollectionToolApp().run()