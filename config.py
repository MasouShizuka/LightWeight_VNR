import os

config = {
    # 界面相关
    'alpha': 1.0,
    'copy': False,

    # Textractor相关
    'textractor_path': os.path.abspath('.') + r'/Textractor',
    'textractor_interval': 0,

    # OCR相关
    'OCR_language': '日文',
    'OCR_continuously': False,
    'OCR_interval': 1,
    'threshold_way': 'BINARY',
    'threshold': 127,

    # 翻译相关
    'jbeijing': False,
    'jbeijing_path': os.path.abspath('.') + r'/jbeijing',
    'jbeijing_to': '简体中文',
    'youdao_path': os.path.abspath('.') + r'/有道词典',
    'youdao_get_translate': True,
    'youdao_interval': 1.0,
    'baidu': False,
    'baidu_appid': '',
    'baidu_key': '',

    # TTS相关
    'yukari2_path': os.path.abspath('.') + r'/Yukari2',
    'yukari2_constantly': False,
    'yukari2_aside': True,
    'yukari2_character': True,

    # 文本相关
    'deduplication': 1,
    'garbage_chars': '',
    're': r'.*',

    # 浮动窗口相关
    'float_interval': 0.1,
}