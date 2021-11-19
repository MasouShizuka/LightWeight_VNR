import sys
sys.coinit_flags = 2
import os
import win32con
import win32gui

from pywinauto.application import Application
from pyperclip import copy

from TTS.TTS import TTS


# VOICEROID+ 民安ともえ
# 调用Tamiyasu的方法借鉴了VNR中的源码

class Tamiyasu(TTS):
    label = 'tamiyasu'
    name = '弦卷マキ'

    MSG_CLICK = 0
    CMD_DELETE = 46
    CMD_PASTE = 56

    def __init__(self, config):
        self.working = False
        self.update_config(config)

        self.app = None
        self.win = None
        self.edit = None
        self.play_button = None
        self.stop_button = None

    def update_config(self, config, main_window=None):
        self.constantly = config['tamiyasu_constantly']
        self.aside = config['tamiyasu_aside']
        self.character = config['tamiyasu_character']

        self.path = config['tamiyasu_path']
        self.path_exe = os.path.join(self.path, 'VOICEROID.exe')

    def start(self):
        self.stop()

        if os.path.exists(self.path):
            try:
                self.app = Application().start(self.path_exe, work_dir=self.path, timeout=10)
                self.working = True
            except:
                pass

    def stop(self):
        self.win = None
        self.edit = None
        self.play_button = None
        self.stop_button = None
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def set_text(self, hwnd, text):
        win32gui.SendMessage(hwnd, win32con.WM_COMMAND, self.CMD_DELETE, 0)
        copy(text)
        win32gui.SendMessage(hwnd, win32con.WM_COMMAND, self.CMD_PASTE, 0)

    def read(self, text):
        try:
            if not self.win:
                self.win = self.app.top_window()
                self.edit = self.win.handle
                self.play_button = self.win.Button5.handle
                self.stop_button = self.win.Button4.handle

            win32gui.PostMessage(self.stop_button, self.MSG_CLICK, 0, 0)
            self.set_text(self.edit, text)
            win32gui.PostMessage(self.play_button, self.MSG_CLICK, 0, 0)
        except:
            pass
