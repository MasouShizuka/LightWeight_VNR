import os
from ctypes import *

from Translator.translator import Translator

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


class JBeijing(Translator):
    label = 'jbeijing'
    name = '北京'
    key = 'text_jbeijing_translate'

    def __init__(self, config):
        self.update_config(config)

    def update_config(self, config):
        self.working = config['jbeijing']

        self.path = config['jbeijing_path']
        self.path_dll = os.path.join(self.path, DLL)
        self.to = jbeijing_to[config['jbeijing_to']]

    # 借鉴了VNR中调用JBeijing的方法
    def translate(self, text, **kw):
        if not os.path.exists(self.path) or \
           not os.path.exists(self.path_dll):
            return ''
        try:
            dll = CDLL(self.path_dll)
            out = create_unicode_buffer(BUFFER_SIZE)
            buf = create_unicode_buffer(BUFFER_SIZE)
            dll.JC_Transfer_Unicode(
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

    def stop(self):
        if os.path.exists('GPS.txt'):
            os.remove('GPS.txt')
