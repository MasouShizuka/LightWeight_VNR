import sys
sys.path.append("..")
import os
from pywinauto.application import Application
from threading import Lock
from set_game_focus import set_focus
# from pyperclip import copy

lock = Lock()

# class Yukari(object):
#     def __init__(self, **kw):
#         self.path = kw['path']
#         self.path_exe = os.path.join(kw['path'], r'VOICEROID.exe')
#         self.alpha = kw['alpha']
#         self.working = kw['constantly']
#         self.aside = kw['aside']
#         self.character = kw['character']
#         self.app = None
#         self.win = None
#
#     def set_path(self, path):
#         self.path = path
#         self.path_exe = os.path.join(path, r'VOICEROID.exe')
#
#     def set_transparency(self, alpha):
#         try:
#             self.app.top_window().set_transparency(alpha=alpha)
#         except:
#             pass
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
#                 self.app = Application().start(self.path_exe, work_dir=self.path, timeout=10)
#             except:
#                 pass
#
#     def connect(self):
#         if os.path.exists(self.path):
#             self.app = Application().connect(title_re='VOICEROID＋ 結月ゆかり')
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
#             self.set_transparency(self.alpha)
#             self.win = self.app.top_window()
#             self.win.set_focus()
#             copy(text)
#             self.win.TkChild.TkChild4.Button4.click_input()
#             self.win.TkChild.TkChild5.TkChild7.type_keys("^a^v")
#             self.win.TkChild.TkChild4.Button5.click_input()
#             self.win.minimize()
#         except:
#             pass
#
#     def read_text(self, text, pid=None):
#         if (self.aside and not '「' in text) or \
#            (self.character and '「' in text):
#             lock.acquire()
#             self.read(text)
#             lock.release()
#
#             if pid:
#                 set_focus(pid)

class Yukari2(object):
    def __init__(self, **kw):
        self.path = kw['path']
        self.path_exe = os.path.join(kw['path'], r'VOICEROID.exe')
        self.working = kw['constantly']
        self.aside = kw['aside']
        self.character = kw['character']
        self.app = None
        self.win = None

    def set_path(self, path):
        self.path = path
        self.path_exe = os.path.join(path, r'VOICEROID.exe')

    def set_aside(self, aside):
        self.aside = aside

    def set_character(self, character):
        self.character = character

    def start(self):
        if os.path.exists(self.path):
            try:
                self.app = Application(backend='uia').start(self.path_exe, work_dir=self.path, timeout=10)
            except:
                pass

    def connect(self):
        if os.path.exists(self.path):
            self.app = Application(backend='uia').connect(title_re='VOICEROID2 FE')

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

    def read(self, text):
        try:
            self.win = self.app.top_window()
            self.win.Button7.click()
            self.win.Edit.set_text(text)
            self.win.Button6.click()
        except:
            pass

    def read_text(self, text, pid=None):
        if (self.aside and '「' not in text) or \
           (self.character and '「' in text):
            lock.acquire()
            self.read(text)
            lock.release()

            if pid:
                set_focus(pid)