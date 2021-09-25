import os

default_config = {
    # 界面相关
    'alpha': 1.0,
    'top': False,
    'copy': False,

    # 游戏相关
    'locale_emulator_path': os.path.join(os.path.abspath('.'), 'Locale Emulator'),

    # Textractor相关
    'textractor_path': os.path.join(os.path.abspath('.'), 'Textractor'),
    'textractor_interval': 0,

    # OCR相关
    'tesseract_OCR_path': os.path.join(os.path.abspath('.'), 'Tesseract-OCR'),
    'OCR_language': '日文',
    'OCR_interval': 1,
    'threshold_way': 'BINARY',
    'threshold': 127,

    # 翻译相关
    'jbeijing': False,
    'jbeijing_path': os.path.join(os.path.abspath('.'), 'Jbeijing'),
    'jbeijing_to': '简体中文',
    'youdao_path': os.path.join(os.path.abspath('.'), '有道词典'),
    'youdao_get_translate': True,
    'youdao_interval': 1.0,
    'baidu': False,
    'baidu_appid': '',
    'baidu_key': '',

    # TTS相关
    'yukari_path': os.path.join(os.path.abspath('.'), 'Yukari'),
    'yukari_constantly': False,
    'yukari_aside': True,
    'yukari_character': True,
    'tamiyasu_path': os.path.join(os.path.abspath('.'), 'Tamiyasu'),
    'tamiyasu_constantly': False,
    'tamiyasu_aside': True,
    'tamiyasu_character': True,

    # 文本相关
    'deduplication': 1,
    'deduplication_auto': True,
    'garbage_chars': '',
    're': '',

    # 浮动窗口相关
    'floating_text_original': False,
}
