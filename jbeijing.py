from ctypes import *

DLL = 'JBJCT.dll'
BUFFER_SIZE = 3000
CODEPAGE_JA = 932
CODEPAGE_GB = 936
CODEPAGE_BIG5 = 950

# 借鉴了VNR中调用Jbeijing的方法
def jbeijing(text, dll_path):
      dll = CDLL(dll_path)
      out = create_unicode_buffer(BUFFER_SIZE)
      buf = create_unicode_buffer(BUFFER_SIZE)
      dll.JC_Transfer_Unicode(
            0,
            CODEPAGE_JA,
            CODEPAGE_GB,
            1,
            1,
            text,
            out,
            byref(c_int(BUFFER_SIZE)),
            buf,
            byref(c_int(BUFFER_SIZE)),
      )
      return out.value