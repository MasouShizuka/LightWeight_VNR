import os
from time import sleep
from pywinauto.application import Application

class Youdao(object):
    def __init__(self, path, interval):
        self.path = os.path.join(path, r'YoudaoDict.exe')
        self.interval = interval
        self.app = None
        self.win = None
        self.working = False

    def set_path(self, path):
        self.path = os.path.join(path, r'YoudaoDict.exe')

    def start(self):
        if os.path.exists(self.path):
            self.app = Application(backend="uia").start(self.path + r' --force-renderer-accessibility')
            self.win = self.app['网易有道词典']
            self.working = True

    def connect(self):
        if os.path.exists(self.path):
            self.app = Application(backend="uia").connect(class_name="YodaoMainWndClass")
            self.win = self.app['网易有道词典']
            self.working = True

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def translate(self, text):
        try:
            self.win['Edit2'].type_keys("^a{BS}" + text)
            sleep(self.interval)
            return self.win['Edit7'].texts()[0]
        except:
            return ''