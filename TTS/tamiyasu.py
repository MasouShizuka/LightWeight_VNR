import os

from pyperclip import copy
from pywinauto import win32defines
from pywinauto.application import Application

from TTS.TTS import TTS


# VOICEROID+ 民安ともえ
# 调用Tamiyasu的方法借鉴了VNR中的源码
class Tamiyasu(TTS):
    label = 'tamiyasu'
    name = '弦卷マキ'

    MSG_CLICK = 0
    CMD_DELETE = 46
    CMD_PASTE = 56

    def __init__(self, config, **kw):
        self.app = None
        self.win = None
        self.edit = None
        self.play_button = None
        self.stop_button = None

        self.update_config(config)

    def update_config(self, config, **kw):
        self.path = config['tamiyasu_path']
        self.path_exe = os.path.join(self.path, 'VOICEROID.exe')

    def start(self):
        self.stop()

        if os.path.exists(self.path_exe):
            try:
                self.app = Application().start(
                    self.path_exe,
                    work_dir=self.path,
                    timeout=10,
                )
                self.working = True
            except:
                pass

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

        self.app = None
        self.win = None
        self.edit = None
        self.play_button = None
        self.stop_button = None

    def set_text(self, widget, text):
        widget.send_message(win32defines.WM_COMMAND, self.CMD_DELETE, 0)
        copy(text)
        widget.send_message(win32defines.WM_COMMAND, self.CMD_PASTE, 0)

    def read(self, text):
        try:
            if not self.win:
                self.win = self.app.top_window()
                self.edit = self.win
                self.play_button = self.win.Button5
                self.stop_button = self.win.Button4

            self.stop_button.post_message(self.MSG_CLICK, 0, 0)
            self.set_text(self.edit, text)
            self.play_button.post_message(self.MSG_CLICK, 0, 0)
        except:
            pass
