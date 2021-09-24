import sys
sys.coinit_flags = 2
import os
import win32gui
from time import sleep

from pyperclip import copy
from pywinauto.application import Application

from Translator.translator import Translator


class Youdao(Translator):
    label = 'youdao'
    name = '有道'
    key = 'text_youdao_translate'

    def __init__(self, config):
        self.working = False
        self.get_translate = config['youdao_get_translate']
        self.path = config['youdao_path']
        self.path_exe = os.path.join(self.path, 'YoudaoDict.exe')
        self.interval = config['youdao_interval']

        self.app = None
        self.win = None
        self.edit_original = None
        self.edit_translate = None

    def start(self):
        self.stop()

        if os.path.exists(self.path):
            try:
                self.app = Application(backend="uia").start(self.path_exe, work_dir=self.path, timeout=10)
                self.working = True
            except:
                pass

    def stop(self):
        self.win = None
        self.edit_original = None
        self.edit_translate = None
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def translate(self, text, hwnds=None):
        try:
            if not self.win:
                self.win = self.app.top_window().Pane3.Pane2.Document
                self.edit_original = self.win.Edit

            # 向原文栏发送ctrl+a+v
            copy(text)
            self.edit_original.type_keys("^a^v")

            # 取回游戏窗口的焦点
            if hwnds:
                for hwnd in hwnds:
                    win32gui.SetForegroundWindow(hwnd)

            # 取得有道翻译栏的翻译结果
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
            pass
        return ''

    def thread(self, text, text_translate, is_floating, textarea, hwnds, *args):
        text_translate[self.label] = self.translate(text, hwnds=hwnds)

        if self.get_translate:
            # 更新界面中对应翻译的文本
            if not is_floating:
                textarea.update(
                    self.name + ':\n' +
                    text_translate[self.label] + '\n\n',
                    append=True,
                )
            else:
            # 更新浮动窗口中对应翻译的文本
                try:
                    textarea.update(text_translate[self.label])
                except:
                    pass

    def update_config(self, config):
        self.path = config['youdao_path']
        self.path_exe = os.path.join(self.path, 'YoudaoDict.exe')
        self.interval = config['youdao_interval']
        self.get_translate = config['youdao_get_translate']
