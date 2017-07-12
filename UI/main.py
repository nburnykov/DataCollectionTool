from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from parse.confnet import checkline


class MainForm(BoxLayout):

    def addcredentials(self, login: str, password: str):
        if login != '':
            self.scr_mng.mainsm.scr2.scr2bl.brv.cred_view.data.insert(0, {'value': login})

    def startscan(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>")

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


if __name__ == '__main__':
    DataCollectionToolApp().run()