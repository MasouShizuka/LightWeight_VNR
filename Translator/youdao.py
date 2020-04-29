import sys
sys.path.append("..")
import os
from time import sleep
from pywinauto.application import Application
from set_game_focus import set_focus
from pyperclip import copy

class Youdao(object):
    def __init__(self, **kw):
        self.path = os.path.join(kw['path'], r'YoudaoDict.exe')
        self.interval = kw['interval']
        self.get_translate = kw['get_translate']
        self.working = False
        self.app = None
        self.win = None

    def set_path(self, path):
        self.path = os.path.join(path, r'YoudaoDict.exe')

    def set_interval(self, interval):
        self.interval = float(interval)

    def set_get_translate(self, get_translate):
        self.get_translate = get_translate

    def start(self):
        if os.path.exists(self.path):
            try:
                self.app = Application(backend="uia").start(self.path + r' --force-renderer-accessibility')
                self.win = self.app.top_window()
                self.working = True
            except:
                pass

    def connect(self):
        if os.path.exists(self.path):
            self.app = Application(backend="uia").connect(class_name="YodaoMainWndClass")
            self.win = self.app.top_window()
            self.working = True

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def translate(self, text, pid=None):
        try:
            copy(text)
            self.win.Edit2.type_keys("^a^v")
            if self.get_translate:
                text_translate = ''
                while True:
                    sleep(self.interval)
                    temp = self.win.Edit7.texts()[0]
                    if text_translate != temp:
                        text_translate = temp
                    else:
                        break
            else:
                text_translate = ''
            return text_translate
        except:
            return ''
        finally:
            if pid:
                set_focus(pid)