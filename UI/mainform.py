from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from parse.confnetparse import checkline
from parse.collecteddataparse import collected_data_parse
from typing import List, Tuple, Optional
from mainproc.rangeProc import rangeproc, ScanData
from kivy.uix.button import Button
from constants import PROJECTPATH
from functools import partial
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from confproc.yamlDecoder import yamlload, yamldump


class MainForm(BoxLayout):
    sd = ScanData()
    slist = ListProperty()
    is_data_load = BooleanProperty(False)

    scan_name = ObjectProperty()
    project_list = ObjectProperty()
    credential_data = ObjectProperty()
    scan_list = ObjectProperty()
    do_not_scan_list = ObjectProperty()
    screen1 = ObjectProperty()
    screen_manager = ObjectProperty()

    def set_scan_list(self, scan_list: List):
        self.slist = scan_list

    def addcredentials(self, login: str, password: str, sd=sd):
        if login != '':
            sd.credential_list.append((login, password))
            self.credential_data.data.insert(0, {'value': login})

    def clearcredentials(self):
        self.credential_data.data = []

    def startscan(self, scan_name: str, scan_range: str, do_not_scan_range: str, is_scan: bool, is_parse: bool,
                  sd=sd):
        sd.scan_name = scan_name
        sd.scan_list = scan_range.split('\n')
        sd.do_not_scan_list = do_not_scan_range.split('\n')
        sd.is_scan = is_scan
        sd.is_parse = is_parse

        if sd.is_scan:
            rangeproc(sd)

        if sd.is_parse:
            collected_data_parse(sd.scan_name)

        self.slist.append({'Scan name': sd.scan_name,
                           'Folder': '_DATA\\' + sd.scan_name})
        print(self.slist)
        yamldump('scans.yaml', list(self.slist))

        if not self.is_data_load:
            self.add_saved_scan_button(scan_name)

    def setscanrange(self, text: str):
        t = text.split("\n")
        isvalidinput = True
        for line in t:
            isvalidinput &= checkline(line)

        if not isvalidinput:
            self.scan_list.background_color = [1, 0.5, 0, 1]
        else:
            self.scan_list.background_color = [1, 1, 1, 1]

    def setdonotscanrange(self, text: str):
        t = text.split("\n")
        isvalidinput = True
        for line in t:
            isvalidinput &= checkline(line)

        if not isvalidinput:
            self.do_not_scan_list.background_color = [1, 0.5, 0, 1]
        else:
            self.do_not_scan_list.background_color = [1, 1, 1, 1]

    def add_saved_scan_button(self, scan_name: str):

        btn = Button()
        btn.size_hint_y = None
        btn.text = scan_name
        btn.height = "50dp"
        btn.background_normal = "{}/UI/Images/button_bg.png".format(PROJECTPATH)
        btn.bind(on_release=partial(self.load_project_data, scan_name))

        self.project_list.add_widget(btn)
        self.project_list.height += 50

    def load_project_data(self, scan_name: str, *args):

        collected_config = yamlload("{0}/_DATA/{1}/{1}.yaml".format(PROJECTPATH, scan_name))
        if collected_config.get('Credentials List', None) is not None:
            self.clearcredentials()
            for cred in collected_config['Credentials List']:
                self.addcredentials(cred[0], cred[1])

        if collected_config.get('Scan Name', None) is not None:
            self.scan_name.text = collected_config['Scan Name']

        if collected_config.get('Scan List', None) is not None:
            self.scan_list.text = "\n".join(collected_config['Scan List'])

        if collected_config.get('Do Not Scan List', None) is not None:
            self.do_not_scan_list.text = "\n".join(collected_config['Do Not Scan List'])

        self.screen1.manager.transition.direction = 'left'
        self.screen_manager.current = 'Config_net'
        self.is_data_load = True

    def new_scan(self):
        self.scan_name.text = ''
        self.credential_data.data = []
        self.scan_list.text = ''
        self.do_not_scan_list.text = ''
        self.is_data_load = False


class DataCollectionToolApp(App):
    title = 'Data Collection Tool'

    def on_start(self):
        scan_list = yamlload('scans.yaml')
        self.root.set_scan_list(scan_list)
        for scan in scan_list:
            self.root.add_saved_scan_button(scan['Scan name'])


def showmainform():
    DataCollectionToolApp().run()
