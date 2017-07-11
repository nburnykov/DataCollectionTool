from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from parse.confnet import checkline


class MainForm(BoxLayout):

    def addcredentials(self, login: str, password: str):
        if login != '':
            self.scr_mng.msm.sc2.scr2bl.brv.cred_view.data.insert(0, {'value': login})

    def startscan(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>")

    def setscanrange(self, text: str):

        t = text.split("\n")
        for line in t:
            if not checkline(line):
                pass




class DataCollectionToolApp(App):
    pass

if __name__ == '__main__':
    DataCollectionToolApp().run()