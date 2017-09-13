from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from parse.confnetparse import checkline
from parse.collecteddataparse import collected_data_parse
from typing import List
from mainproc.rangeProc import rangeproc, ScanData
from kivy.uix.button import Button
from constants import PROJECTPATH
from functools import partial
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from confproc.yamlDecoder import yamlload, yamldump
from threading import Thread
import time
from io import StringIO

import logging

logger = logging.getLogger('main')

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

    log_stream: StringIO = ObjectProperty()
    log_handler: logging.StreamHandler = ObjectProperty()
    log_thread = ObjectProperty()

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

        yamldump('scans.yaml', list(self.slist))

        if not self.is_data_load:
            self.add_saved_scan_button(scan_name)

    def setscanrange(self, text: str):
        t = text.split("\n")
        is_valid_input = True
        for line in t:
            is_valid_input &= checkline(line)

        if not is_valid_input:
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
        btn.background_normal = f"{PROJECTPATH}/UI/Images/button_bg.png"
        btn.bind(on_release=partial(self.load_project_data, scan_name))

        self.project_list.add_widget(btn)
        self.project_list.height += 50

    def load_project_data(self, scan_name: str, *args):

        collected_config = yamlload(f"{PROJECTPATH}/_DATA/{scan_name}/{scan_name}.yaml")
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

    def start_log_listener(self):

        def _listen_log_queue():

            while True:

                #logger.debug("The time is %s" % time.ctime())
                self.applog.text += f'{self.log_stream.getvalue()}'

                time.sleep(1)

                self.log_handler.flush()
                self.log_stream.truncate(0)
                self.log_stream.seek(0)

        self.log_thread = Thread(target=_listen_log_queue)
        self.log_thread.daemon = True
        self.log_thread.start()


class DataCollectionToolApp(App):
    title = 'Data Collection Tool'

    def on_start(self):

        self.root.log_stream = StringIO()
        self.root.log_handler = logging.StreamHandler(self.root.log_stream)
        self.root.log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.root.log_handler)
        self.root.start_log_listener()

        scan_list = yamlload('scans.yaml')
        self.root.set_scan_list(scan_list)
        for scan in scan_list:
            self.root.add_saved_scan_button(scan['Scan name'])


def showmainform():
    logger.debug('Show application main form')
    DataCollectionToolApp().run()
