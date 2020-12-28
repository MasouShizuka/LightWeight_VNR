import os
from ctypes import *

DLL = 'JBJCT.dll'
BUFFER_SIZE = 3000
CODEPAGE_JA = 932
CODEPAGE_GB = 936
CODEPAGE_BIG5 = 950

jbeijing_to = {
      '简体中文': CODEPAGE_GB,
      '繁体中文': CODEPAGE_BIG5,
}
jbeijing_translate = [i for i in jbeijing_to]

class JBeijing(object):
    def __init__(self, **kw):
        self.path = kw['path']
        self.path_dll = os.path.join(self.path, DLL)
        self.to = jbeijing_to[kw['jbeijing_to']]
        self.working = kw['working']

        self.label = 'text_jbeijing_translate'
        self.name = '北京'
        self.key = 'text_jbeijing_translated'

    def set_path(self, path):
        self.path = path
        self.path_dll = os.path.join(self.path, DLL)

    def set_to(self, to):
        self.to = to

    # 借鉴了VNR中调用Jbeijing的方法
    def translate(self, text):
        if not os.path.exists(self.path) or \
           not os.path.exists(self.path_dll):
            return ''
        try:
            self.path_dll = CDLL(self.path_dll)
            out = create_unicode_buffer(BUFFER_SIZE)
            buf = create_unicode_buffer(BUFFER_SIZE)
            self.path_dll.JC_Transfer_Unicode(
                0,
                CODEPAGE_JA,
                self.to,
                1,
                1,
                text,
                out,
                byref(c_int(BUFFER_SIZE)),
                buf,
                byref(c_int(BUFFER_SIZE)),
            )
            return out.value
        except:
            pass
        return ''

    def update_config(self, config):
        self.to = jbeijing_to[config['jbeijing_to']]
        self.working = config['jbeijing']
    
    def thread(self, text, text_translate, *args):
        text_translate[self.label] = self.translate(text)
