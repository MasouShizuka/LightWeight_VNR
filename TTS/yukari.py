import sys
sys.path.append("..")
import os
import win32gui
import win32con
from pywinauto.application import Application
from pyperclip import copy
# from set_focus import set_focus


# 因Voiceroid的结月缘便于下载，且不存在激活问题，所以使用
# 调用Yukari的方法借鉴了VNR中的源码

def post_window_message(hwnd, msg, wparam=0, lparam=0):
    try:
        win32gui.PostMessage(hwnd, msg, wparam, lparam)  # return None
        return True
    except:
        return False


def send_window_command(hwnd, cmd):
    try:
        return 0 == win32gui.SendMessage(hwnd, win32con.WM_COMMAND, cmd, 0)
    except:
        return False


class Yukari(object):
    MSG_CLICK = 0
    CMD_CUT = 52
    CMD_PASTE = 56
    CMD_SELECTALL = 60

    def __init__(self, **kw):
        self.path = kw['path']
        self.path_exe = os.path.join(kw['path'], 'VOICEROID.exe')
        self.constantly = kw['constantly']
        self.aside = kw['aside']
        self.character = kw['character']
        self.working = False

        self.app = None
        self.win = None
        self.edit = None
        self.play_button = None
        self.stop_button = None

    def set_path(self, path):
        self.path = path
        self.path_exe = os.path.join(path, 'VOICEROID.exe')

    def set_transparency(self, alpha):
        try:
            self.app.top_window().set_transparency(alpha=alpha)
        except:
            pass

    def set_aside(self, aside):
        self.aside = aside

    def set_character(self, character):
        self.character = character

    def start(self):
        self.stop()

        if os.path.exists(self.path):
            try:
                self.app = Application().start(self.path_exe, work_dir=self.path, timeout=10)
                self.working = True
            except:
                pass

    def connect(self):
        if os.path.exists(self.path):
            self.app = Application().connect(title_re='VOICEROID')
            self.working = True

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def set_text(self, hwnd, text):
        if hwnd:
            if send_window_command(hwnd, self.CMD_SELECTALL):
                if send_window_command(hwnd, self.CMD_CUT):
                    copy(text)
                    if send_window_command(hwnd, self.CMD_PASTE):
                        return True
        return False

    def read(self, text):
        try:
            if not self.win:
                self.win = self.app.top_window()
            if not self.edit:
                self.edit = self.win.handle
            if not self.play_button:
                self.play_button = self.win.Button5.handle
            if not self.stop_button:
                self.stop_button = self.win.Button4.handle

            post_window_message(self.stop_button, self.MSG_CLICK)
            self.set_text(self.edit, text)
            post_window_message(self.play_button, self.MSG_CLICK)
        except:
            pass

    def read_text(self, text):
        if '「' in text or \
           '『' in text or \
           '（' in text or \
           '(' in text:
            if self.character:
                self.read(text)
        else:
            if self.aside:
                self.read(text)
    
    def update_config(self, config):
        self.constantly = config['yukari_constantly']
        self.set_aside(config['yukari_aside'])
        self.set_character(config['yukari_character'])


# 因Voiceroid2存在声源过期问题，所以弃用

# class Yukari2(object):
#     def __init__(self, **kw):
#         self.path = kw['path']
#         self.path_exe = os.path.join(kw['path'], 'VOICEROID.exe')
#         self.working = kw['constantly']
#         self.aside = kw['aside']
#         self.character = kw['character']
#         self.app = None
#         self.win = None
#         self.edit = None
#         self.play_button = None
#         self.stop_button = None
#
#     def set_path(self, path):
#         self.path = path
#         self.path_exe = os.path.join(path, 'VOICEROID.exe')
#
#     def set_aside(self, aside):
#         self.aside = aside
#
#     def set_character(self, character):
#         self.character = character
#
#     def start(self):
#         if os.path.exists(self.path):
#             try:
#                 self.app = Application(backend='uia').start(self.path_exe, work_dir=self.path, timeout=10)
#             except:
#                 pass
#
#     def connect(self):
#         if os.path.exists(self.path):
#             self.app = Application(backend='uia').connect(title_re='VOICEROID2 FE')
#
#     def stop(self):
#         try:
#             self.app.kill()
#         except:
#             pass
#         self.working = False
#
#     def read(self, text):
#         try:
#             if not self.win:
#                 self.win = self.app.top_window()
#             if not self.edit:
#                 self.edit = self.win.custom.children()[0]
#             if not self.play_button:
#                 self.play_button = self.win.custom.children()[1]
#             if not self.stop_button:
#                 self.stop_button = self.win.custom.children()[2]
#
#             self.stop_button.click()
#             self.edit.set_text(text)
#             self.play_button.click()
#         except:
#             pass
#
#     def read_text(self, text, pid=None):
#         if '「' in text or \
#            '『' in text or \
#            '（' in text or \
#            '(' in text:
#             if self.character:
#                 self.read(text)
#                 if pid:
#                     set_focus(pid)
#         else:
#             if self.aside:
#                 self.read(text)
#                 if pid:
#                     set_focus(pid)
