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

# 借鉴了VNR中调用Jbeijing的方法
def jbeijing(text, dll_path, to):
    dll = os.path.join(dll_path, DLL)
    if not os.path.exists(dll_path) or \
       not os.path.exists(dll):
        return ''
    try:
        dll = CDLL(dll)
        out = create_unicode_buffer(BUFFER_SIZE)
        buf = create_unicode_buffer(BUFFER_SIZE)
        dll.JC_Transfer_Unicode(
            0,
            CODEPAGE_JA,
            to,
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