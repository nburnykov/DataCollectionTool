from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image


class MainForm(BoxLayout):
    def addcredentials(self, login: str, password: str):
        if login != '':
            self.scr_mng.msm.sc2.scr2bl.brv.cred_view.data.insert(0, {'value': login})



class DataCollectionToolApp(App):
    pass

if __name__ == '__main__':
    DataCollectionToolApp().run()