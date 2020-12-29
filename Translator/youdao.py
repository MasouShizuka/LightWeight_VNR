import os
from time import sleep
from pywinauto.application import Application
from set_focus import set_focus
from pyperclip import copy


class Youdao(object):
    def __init__(self, **kw):
        self.path = kw['path']
        self.path_exe = os.path.join(kw['path'], 'YoudaoDict.exe')
        self.interval = kw['interval']
        self.get_translate = kw['get_translate']
        self.working = False

        self.app = None
        self.win = None
        self.edit_origin = None
        self.edit_translate = None

        self.label = 'text_youdao_translate'
        self.name = '有道'
        self.key = 'text_youdao_translated'

    def set_path(self, path):
        self.path = path
        self.path_exe = os.path.join(path, 'YoudaoDict.exe')

    def set_interval(self, interval):
        self.interval = float(interval)

    def set_get_translate(self, get_translate):
        self.get_translate = get_translate

    def start(self):
        self.stop()

        if os.path.exists(self.path):
            try:
                self.app = Application(backend="uia").start(self.path_exe, work_dir=self.path, timeout=10)
                self.working = True
            except:
                pass

    def connect(self):
        self.win = None
        self.edit_origin = None
        self.edit_translate = None

        if os.path.exists(self.path):
            self.app = Application(backend="uia").connect(class_name="YodaoMainWndClass")
            self.working = True

    def stop(self):
        self.win = None
        self.edit_origin = None
        self.edit_translate = None
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def translate(self, text, pid=None):
        try:
            if not self.win:
                self.win = self.app.top_window().Pane3.Pane2.Document
                self.edit_origin = self.win.Edit

            copy(text)
            self.edit_origin.type_keys("^a^v")
            if pid:
                set_focus(pid)

            if self.get_translate:
                if not self.edit_translate:
                    self.edit_translate = self.win.children()[5]

                sleep(self.interval)
                text_translate = ''
                for i in self.edit_translate.children():
                    text_translate += i.get_line(0)
            else:
                text_translate = ''

            return text_translate
        except:
            return ''

    def update_config(self, config):
        self.set_interval(config['youdao_interval'])
        self.set_get_translate(config['youdao_get_translate'])

    def thread(self, text, text_translate, pid, *args):
        text_translate[self.label] = self.translate(text, pid=pid)
