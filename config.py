import os

default_config = {
    # 界面相关
    'alpha': 1.0,
    'top': False,
    'copy': False,

    # 游戏相关
    'locale_emulator_path': os.path.abspath('.') + r'\Locale Emulator',

    # Textractor相关
    'textractor_path': os.path.abspath('.') + r'\Textractor',
    'textractor_interval': 0,

    # OCR相关
    'tesseract_OCR_path': os.path.abspath('.') + r'Tesseract-OCR',
    'OCR_language': '日文',
    'OCR_interval': 1,
    'threshold_way': 'BINARY',
    'threshold': 127,

    # 翻译相关
    'jbeijing': False,
    'jbeijing_path': os.path.abspath('.') + r'\jbeijing',
    'jbeijing_to': '简体中文',
    'youdao_path': os.path.abspath('.') + r'\有道词典',
    'youdao_get_translate': True,
    'youdao_interval': 1.0,
    'baidu': False,
    'baidu_appid': '',
    'baidu_key': '',

    # TTS相关
    'yukari_path': os.path.abspath('.') + r'\Yukari',
    'yukari_constantly': False,
    'yukari_aside': True,
    'yukari_character': True,
    'tamiyasu_path': os.path.abspath('.') + r'\Tamiyasu',
    'tamiyasu_constantly': False,
    'tamiyasu_aside': True,
    'tamiyasu_character': True,

    # 文本相关
    'deduplication': 1,
    'deduplication_auto': False,
    'garbage_chars': '',
    're': '',

    # 浮动窗口相关
    'floating_text_original': True,
}
