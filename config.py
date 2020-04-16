import os

configs = {
    # 界面相关
    'alpha': 1.0,
    'copy': False,

    # Textractor相关
    'textractor_path': os.path.abspath('.') + r'\Textractor',
    'textractor_interval': 0.1,

    # OCR相关
    'OCR_language': '日文',
    'continuously': False,
    'OCR_interval': 1,
    'threshold_way': 'BINARY',
    'threshold': 127,

    # 翻译相关
    'jbeijing': False,
    'jbeijing_path': os.path.abspath('.') + r'\jbeijing',
    'jbeijing_to': '简体中文',
    'youdao_path': os.path.abspath('.') + r'\有道词典',
    'youdao_interval': 1.0,

    # 文本相关
    'deduplication': 1,
    'garbage_chars': '',
    're': r'.*',
}