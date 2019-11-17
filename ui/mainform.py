from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from parse.confnetparse import checkline
from parse.collecteddataparse import collected_data_parse
from typing import List
from mainproc.rangeProc import rangeproc, ScanData
from kivy.uix.button import Button
from constants import PROJECT_PATH
from functools import partial
from kivy.properties import ObjectProperty
from confproc.fileProc import yaml_load, yaml_dump
from threading import Thread
import time
from io import StringIO

import logging

logger = logging.getLogger('main')
log_stream = StringIO()
log_handler = logging.StreamHandler(log_stream)
log_handler.setLevel(logging.DEBUG)
logger.addHandler(log_handler)


class MainForm(BoxLayout):
    scan_name = ObjectProperty()
    project_list = ObjectProperty()
    credential_data = ObjectProperty()
    form_scan_list = ObjectProperty()
    form_do_not_scan_list = ObjectProperty()
    screen1 = ObjectProperty()
    screen_manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scan_list = []
        self.is_data_load = False
        self.scan_thread: Thread = None
        self.sd = ScanData()

    def disable_buttons(self, disabled: bool) -> None:
        logger.debug(f'Button.disabled set to {disabled}')
        for widget in self.walk():
            if widget.__class__.__name__ == 'Button':
                widget.disabled = disabled

    def set_scan_list(self, scan_list: List) -> None:
        self.scan_list = scan_list

    def add_credentials(self, login: str, password: str) -> None:
        if login != '':
            self.sd.credential_list.append((login, password))
            self.credential_data.data.insert(0, {'value': login})

    def clear_credentials(self):
        self.credential_data.data = []

    def start_scan(self, scan_name: str, scan_range: str, do_not_scan_range: str, is_scan: bool, is_parse: bool):

        self.sd.scan_name = scan_name
        self.sd.scan_list = scan_range.split('\n')
        self.sd.do_not_scan_list = do_not_scan_range.split('\n')
        self.sd.is_scan = is_scan
        self.sd.is_parse = is_parse

        if self.sd.scan_name.strip(' ') == '':
            logger.info('Scan name is empty! Abort.')
            return
        _chars = 0
        for line in self.sd.scan_list:
            _chars += len(line.strip(' '))

        if _chars == 0:
            logger.info('Scan list is empty! Abort.')
            return


        def _scan_thread():

            self.disable_buttons(True)
            if self.sd.is_scan:
                rangeproc(self.sd)

            if self.sd.is_parse:
                collected_data_parse(self.sd.scan_name)

            if not self.is_data_load:
                self.add_saved_scan_button(scan_name)
                self.scan_list.append({'Scan name': self.sd.scan_name, 'Folder': '_DATA/' + self.sd.scan_name})
                self.is_data_load = True

            yaml_dump(f'{PROJECT_PATH}/scans.yaml', list(self.scan_list))

            self.disable_buttons(False)

        self.scan_thread = Thread(target=_scan_thread)
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def set_scan_range(self, text: str):
        t = text.split("\n")
        is_valid_input = True
        for line in t:
            is_valid_input &= checkline(line)

        if not is_valid_input:
            self.form_scan_list.background_color = [1, 0.5, 0, 1]
        else:
            self.form_scan_list.background_color = [1, 1, 1, 1]

    def set_do_not_scan_range(self, text: str):
        t = text.split("\n")
        isvalidinput = True
        for line in t:
            isvalidinput &= checkline(line)

        if not isvalidinput:
            self.form_do_not_scan_list.background_color = [1, 0.5, 0, 1]
        else:
            self.form_do_not_scan_list.background_color = [1, 1, 1, 1]

    def add_saved_scan_button(self, scan_name: str):

        btn = Button()
        btn.id = scan_name
        btn.size_hint_y = None
        btn.text = scan_name
        btn.height = "50dp"
        #print(PROJECTPATH)
        btn.background_normal = f"{PROJECT_PATH}/UI/Images/button_bg.png"
        btn.bind(on_release=partial(self.load_project_data, scan_name))

        self.project_list.add_widget(btn)
        self.project_list.height += 50

    def load_project_data(self, scan_name: str, *args):

        collected_config = yaml_load(f"{PROJECT_PATH}/_DATA/{scan_name}/{scan_name}.yaml")
        if collected_config.get('Credentials List', None) is not None:
            self.clear_credentials()
            for cred in collected_config['Credentials List']:
                self.add_credentials(cred[0], cred[1])

        if collected_config.get('Scan Name', None) is not None:
            self.scan_name.text = collected_config['Scan Name']

        if collected_config.get('Scan List', None) is not None:
            self.form_scan_list.text = "\n".join(collected_config['Scan List'])

        if collected_config.get('Do Not Scan List', None) is not None:
            self.form_do_not_scan_list.text = "\n".join(collected_config['Do Not Scan List'])

        self.screen1.manager.transition.direction = 'left'
        self.screen_manager.current = 'Config_net'
        self.is_data_load = True

    def new_scan(self):
        self.scan_name.text = ''
        self.credential_data.data = []
        self.form_scan_list.text = ''
        self.form_do_not_scan_list.text = ''
        self.is_data_load = False

    def start_log_listener(self):

        def _listen_log_queue():
            while True:
                self.applog.text += f'{log_stream.getvalue()}'
                log_stream.truncate(0)
                log_stream.seek(0)
                log_handler.flush()
                time.sleep(1)

        self.log_thread = Thread(target=_listen_log_queue)
        self.log_thread.daemon = True
        self.log_thread.start()
        pass


class DataCollectionToolApp(App):
    title = 'Data Collection Tool'

    def on_start(self):
        self.root.start_log_listener()

        scan_list = yaml_load('scans.yaml')
        self.root.set_scan_list(scan_list)
        for scan in scan_list:
            self.root.add_saved_scan_button(scan['Scan name'])


def show_main_form():
    logger.debug('Show application main form')
    DataCollectionToolApp().run()
