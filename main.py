import PySimpleGUI as sg
import os
import re
import json
import psutil
from config import config
from game import game, start_mode, start_directly, start_with_locale_emulator
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE
from PIL import Image
from pyautogui import position, screenshot, size
from pyperclip import copy
from OCR.tesseract_OCR import pytesseract, languages, lang_translate, tesseract_OCR
from OCR.threshold_ways import threshold_ways, threshold_name
from Translator.jbeijing import jbeijing_to, jbeijing_translate, jbeijing
from Translator.baidu import Baidu

sg.theme('DarkGrey5')
sg.set_options(font=('Microsoft YaHei Mono', 15))


class Main_Window(object):
    def __init__(self):
        super().__init__()

        # 默认设置参数
        self.config = config
        # 读取设置
        self.load_config()

        # 默认游戏信息
        self.game = game
        # 读取游戏信息
        self.load_game()
        self.games = [i['name'] for i in self.game['game_list']]

        # Textractor相关变量
        self.textractor_working = False
        self.textractor_pause = False
        self.cli = None
        self.fixed_hook = None
        # OCR相关变量
        pytesseract.pytesseract.tesseract_cmd = os.path.join(self.config['tesseract_OCR_path'], 'tesseract.exe')
        tessdata_dir_config = '--tessdata-dir "' + os.path.join(self.config['tesseract_OCR_path'], 'tessdata') + '"'
        self.screenshot = None
        self.OCR_working = False
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        # 文本相关变量
        self.text = ''
        # Jbeijing相关变量
        self.text_jbeijing_translate = ''
        # 有道相关变量
        self.youdao = None
        self.text_youdao_translate = ''
        # 百度相关变量
        self.baidu = Baidu(
            appid=self.config['baidu_appid'],
            key=self.config['baidu_key'],
            enable=self.config['baidu'],
        )
        self.text_baidu_translate = ''
        # TTS相关变量
        self.yukari2 = None

        # 浮动窗口相关变量
        self.float = False

        self.main_window = sg.Window(
            'VNR_OCR',
            self.interface(),
            resizable=True,
            alpha_channel=self.config['alpha'],
            margins=(0, 0),
        )

        while True:
            event, values = self.main_window.read()
            if event is None:
                break

            # 游戏界面
            elif event == 'game_list':
                self.get_game_info()
            elif event == '添加':
                self.add_game()
            elif event == '删除':
                self.delete_game()
            elif event == '启动游戏':
                self.start_game()
            # 抓取界面
            elif event == '刷新':
                self.refresh_process_list()
            elif event == '固定':
                self.fixed_hook = self.main_window['hook'].get()
            elif event == '启动TR':
                self.textractor_start()
            elif event == 'Attach':
                self.textractor_attach()
            elif event == '暂停TR':
                self.textractor_pause = not self.textractor_pause
            elif event == '特殊码':
                self.textractor_hook_code()
            elif event == '终止TR':
                self.textractor_stop()

            # 光学界面
            elif event == '截取':
                self.get_area()
            elif event == '连续':
                self.OCR_start()
            elif event == '结束':
                self.OCR_stop()

            # 翻译界面
            elif event == '启动有道':
                self.youdao_start()
            elif event == '终止有道':
                if self.youdao:
                    self.youdao.stop()
                    self.youdao = None

            # 语音界面
            elif event == '启动Yukari2':
                self.yukari2_start()
            elif event == '终止Yukari2':
                if self.yukari2:
                    self.yukari2.stop()
                    self.yukari2 = None

            # 设置界面
            elif event.startswith('保存'):
                self.save_config(values)

            # 浮动相关
            elif event.startswith('浮动'):
                self.float_window()

        if self.youdao:
            self.youdao.stop()
        if self.yukari2:
            self.yukari2.stop()

        self.main_window.close()

    # 界面设置
    def interface(self):
        game_list = [
            [
                sg.Listbox(
                    key='game_list',
                    values=self.games,
                    enable_events=True,
                    size=(82, 10),
                )
            ],
        ]

        game_info = [
            [
                sg.Text('游戏名称：'),
                sg.Input(
                    key='game_name',
                    default_text='',
                    size=(72, 1),
                ),
            ],
            [
                sg.Text('程序目录：'),
                sg.Input(
                    key='game_path',
                    default_text='',
                    size=(67, 1),
                ),
                sg.FileBrowse(
                    '目录',
                    key='game_dir',
                    size=(5, 1),
                    font=('微软雅黑', 11)
                ),
            ],
            [
                sg.Text('特殊码：  '),
                sg.Input(
                    key='game_hook_code',
                    default_text='',
                    size=(72, 1),
                ),
            ],
            [
                sg.Text('启动方式：'),
                sg.Combo(
                    start_mode,
                    key='game_start_mode',
                    default_value='',
                    size=(71, 1),
                    readonly=True,
                ),
            ],
            [
                sg.Button('添加', pad=(20, 0)),
                sg.Button('删除', pad=(20, 0)),
                sg.Button('启动游戏', pad=(20, 0)),
            ],
        ]

        game_layout = [
            [
                sg.Frame(
                    '游戏列表',
                    layout=game_list,
                )
            ],
            [
                sg.Frame(
                    '游戏信息',
                    layout=game_info,
                    element_justification='c',
                )
            ],
        ]

        textractor_buttons = [
            [sg.Button('启动TR', pad=(20, 20))],
            [sg.Button('Attach', pad=(20, 20))],
            [sg.Button('暂停TR', pad=(20, 20))],
            [sg.Button('特殊码', pad=(20, 20))],
            [sg.Button('终止TR', pad=(20, 20))],
            [sg.Button('浮动', pad=(20, 20))],
        ]

        textractor_layout = [
            [
                sg.Text('进程：'),
                sg.Combo(
                    [],
                    key='process',
                    size=(70, 1),
                ),
                sg.Button('刷新', pad=(20, 20)),
            ],
            [
                sg.Text('钩子：'),
                sg.Combo(
                    [],
                    key='hook',
                    size=(70, 1),
                    readonly=True,
                ),
                sg.Button('固定', pad=(20, 0)),
            ],
            [
                sg.Frame(
                    '',
                    [[sg.Multiline('', key='content', size=(75, 16), autoscroll=True)]],
                ),
                sg.Column(textractor_buttons),
            ]
        ]

        OCR_display = [
            [
                sg.Frame(
                    'Image',
                    [[sg.Image('', key='image')]],
                )
            ],
            [
                sg.Frame(
                    '提取文本',
                    [[sg.Multiline('', key='text_OCR', size=(75, 16))]],
                ),
            ],
        ]

        OCR_buttons = [
            [sg.Button('截取', pad=(20, 20))],
            [sg.Button('连续', pad=(20, 20))],
            [sg.Button('结束', pad=(20, 20))],
            [sg.Button('浮动', pad=(20, 20))],
        ]

        OCR_layout = [
            [
                sg.Column(OCR_display, element_justification='center'),
                sg.Column(OCR_buttons),
            ],
        ]

        translate_jbeijing = [
            [
                sg.Frame(
                    'JBeijing',
                    [
                        [
                            sg.Text('JBeijing：    '),
                            sg.Checkbox(
                                '启用',
                                key='jbeijing',
                                default=self.config['jbeijing'],
                            )
                        ],
                        [
                            sg.Text('JBeijing路径：'),
                            sg.Input(
                                key='jbeijing_path',
                                default_text=self.config['jbeijing_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='jbeijing_dir'),
                        ],
                        [
                            sg.Text('翻译语言：    '),
                            sg.Combo(
                                jbeijing_translate,
                                key='jbeijing_to',
                                default_value=self.config['jbeijing_to'],
                                size=(14, 1),
                                readonly=True,
                            ),
                        ],
                    ],
                    pad=(10, 10),
                ),
            ],
        ]

        translate_youdao = [
            [
                sg.Frame(
                    '有道',
                    [
                        [
                            sg.Text('有道词典：'),
                            sg.Button('启动有道'),
                            sg.Button('终止有道', pad=(20, 0)),
                        ],
                        [
                            sg.Text('有道路径：'),
                            sg.Input(
                                key='youdao_path',
                                default_text=self.config['youdao_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='youdao_dir'),
                        ],
                        [
                            sg.Text('抓取翻译：'),
                            sg.Checkbox(
                                '启用',
                                key='youdao_get_translate',
                                default=self.config['youdao_get_translate'],
                            )
                        ],
                        [
                            sg.Text('抓取间隔：'),
                            sg.Input(
                                key='youdao_interval',
                                default_text=self.config['youdao_interval'],
                                size=(16, 1),
                            ),
                            sg.Text('秒'),
                        ],
                    ],
                    pad=(10, 10),
                ),
            ],
        ]

        translate_baidu = [
            [
                sg.Frame(
                    '百度翻译',
                    [
                        [
                            sg.Text('百度翻译：'),
                            sg.Checkbox(
                                '启用',
                                key='baidu',
                                default=self.config['baidu'],
                            )
                        ],
                        [
                            sg.Text('APP ID：  '),
                            sg.Input(
                                key='baidu_appid',
                                default_text=self.config['baidu_appid'],
                                size=(50, 1),
                            ),
                        ],
                        [
                            sg.Text('密钥：    '),
                            sg.Input(
                                key='baidu_key',
                                default_text=self.config['baidu_key'],
                                size=(50, 1),
                            ),
                        ],
                    ],
                    pad=(10, 10),
                ),
            ],
        ]

        translate_layout = [
            [
                sg.Column(
                    [
                        [
                            sg.TabGroup(
                                [
                                    [
                                        sg.Tab('有道', translate_youdao),
                                        sg.Tab('百度', translate_baidu),
                                        sg.Tab('北京', translate_jbeijing),
                                    ]
                                ],
                                tab_location='lefttop',
                            )
                        ],
                        [
                            sg.Button('保存'),
                        ],
                    ],
                    element_justification='center',
                )
            ],
        ]

        TTS_yukari2 = [
            [
                sg.Frame(
                    'Yukari2',
                    [
                        [
                            sg.Text('Yukari2：   '),
                            sg.Button('启动Yukari2', pad=(20, 0)),
                            sg.Button('终止Yukari2', pad=(20, 0)),
                        ],
                        [
                            sg.Text('Yukari2路径：'),
                            sg.Input(
                                key='yukari2_path',
                                default_text=self.config['yukari2_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='yukari2_dir'),
                        ],
                        [
                            sg.Text('连续阅读：   '),
                            sg.Checkbox(
                                '启用',
                                key='yukari2_constantly',
                                default=self.config['yukari2_constantly'],
                            )
                        ],
                        [
                            sg.Text('阅读内容：   '),
                            sg.Checkbox(
                                '旁白',
                                key='yukari2_aside',
                                default=self.config['yukari2_aside'],
                            ),
                            sg.Checkbox(
                                '角色',
                                key='yukari2_character',
                                default=self.config['yukari2_character'],
                            ),
                        ],
                    ],
                    pad=(10, 10),
                ),
            ],
        ]

        TTS_layout = [
            [
                sg.Column(
                    [
                        [
                            sg.TabGroup(
                                [
                                    [
                                        sg.Tab('结月', TTS_yukari2),
                                    ]
                                ],
                                tab_location='lefttop',
                            )
                        ],
                        [
                            sg.Button('保存'),
                        ],
                    ],
                    element_justification='center',
                )
            ],
        ]

        config_interface = [
            [
                sg.Frame(
                    '透明度',
                    [
                        [
                            sg.Text('透明度：'),
                            sg.Slider(
                                key='alpha',
                                default_value=self.config['alpha'],
                                size=(30, 10),
                                range=(0, 1.0),
                                orientation='h',
                                resolution=0.01,
                                tick_interval=1,
                            ),
                        ],
                    ],
                    pad=(10, 10),
                ),
            ],
            [
                sg.Frame(
                    '剪切板',
                    [
                        [
                            sg.Text('复制到剪切板：'),
                            sg.Checkbox(
                                '复制',
                                key='copy',
                                default=self.config['copy'],
                            )
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
        ]

        config_game = [
            [
                sg.Frame(
                    'Locale Emulator',
                    [
                        [
                            sg.Text('Locale Emulator路径：'),
                            sg.Input(
                                key='locale_emulator_path',
                                default_text=self.config['locale_emulator_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='locale_emulator_dir'),
                        ],
                    ],
                    pad=(10, 10),
                )
            ]
        ]

        config_textractor = [
            [
                sg.Frame(
                    'Textractor',
                    [
                        [
                            sg.Text('Textractor路径：'),
                            sg.Input(
                                key='textractor_path',
                                default_text=self.config['textractor_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='textractor_dir'),
                        ],
                        [
                            sg.Text('Textractor间隔：'),
                            sg.Input(
                                key='textractor_interval',
                                default_text=self.config['textractor_interval'],
                                size=(16, 1),
                            ),
                            sg.Text('秒'),
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
        ]

        config_OCR = [
            [
                sg.Frame(
                    'Tesseract-OCR',
                    [
                        [
                            sg.Text('Tesseract-OCR路径：'),
                            sg.Input(
                                key='tesseract_OCR_path',
                                default_text=self.config['tesseract_OCR_path'],
                                size=(50, 1),
                            ),
                            sg.FolderBrowse('目录', key='tesseract_OCR_dir'),
                        ],
                        [
                            sg.Text('识别语言：'),
                            sg.Combo(
                                lang_translate,
                                key='OCR_language',
                                default_value=self.config['OCR_language'],
                                size=(14, 1),
                                readonly=True,
                            ),
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
            [
                sg.Frame(
                    '截屏',
                    [
                        [
                            sg.Text('截屏间隔：'),
                            sg.Input(
                                key='OCR_interval',
                                default_text=self.config['OCR_interval'],
                                size=(16, 1),
                            ),
                            sg.Text('秒'),
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
            [
                sg.Frame(
                    '处理',
                    [
                        [
                            sg.Text('阈值化方法：'),
                            sg.Combo(
                                threshold_name,
                                key='threshold_way',
                                default_value=self.config['threshold_way'],
                                size=(12, 1),
                                readonly=True,
                            ),
                        ],
                        [
                            sg.Text('阈值：'),
                            sg.Slider(
                                key='threshold',
                                default_value=self.config['threshold'],
                                size=(40, 10),
                                range=(0, 255),
                                orientation='h',
                                resolution=1,
                                tick_interval=255,
                            ),
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
        ]

        config_text = [
            [
                sg.Frame(
                    '文本',
                    [
                        [
                            sg.Text('文本去重数：'),
                            sg.Input(
                                key='deduplication',
                                default_text=self.config['deduplication'],
                                size=(16, 1),
                            ),
                            sg.Text('    智能去重：'),
                            sg.Checkbox(
                                '启用',
                                key='deduplication_auto',
                                default=self.config['deduplication_auto'],
                            )
                        ],
                        [
                            sg.Text('垃圾字符表：'),
                            sg.Input(
                                key='garbage_chars',
                                default_text=self.config['garbage_chars'],
                                size=(50, 1),
                            ),
                        ],
                        [
                            sg.Text('正则表达式：'),
                            sg.Input(
                                key='re',
                                default_text=self.config['re'],
                                size=(50, 1),
                            ),
                        ],
                    ],
                    pad=(10, 10),
                )
            ]
        ]

        config_float = [
            [
                sg.Frame(
                    '浮动',
                    [
                        [
                            sg.Text('窗口间隔：'),
                            sg.Input(
                                key='float_interval',
                                default_text=self.config['float_interval'],
                                size=(16, 1),
                            ),
                            sg.Text('秒'),
                        ],
                        [
                            sg.Text('原文：    '),
                            sg.Checkbox(
                                '显示',
                                key='text_origin',
                                default=self.config['text_origin'],
                            )
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
        ]

        config_layout = [
            [
                sg.Column(
                    [
                        [
                            sg.TabGroup(
                                [
                                    [
                                        sg.Tab('界面', config_interface),
                                        sg.Tab('游戏', config_game),
                                        sg.Tab('抓取', config_textractor),
                                        sg.Tab('光学', config_OCR),
                                        sg.Tab('文本', config_text),
                                        sg.Tab('浮动', config_float),
                                    ]
                                ],
                                tab_location='lefttop',
                            )
                        ],
                        [
                            sg.Button('保存'),
                        ],
                    ],
                    element_justification='center',
                )
            ],
        ]

        help_game = [
            [
                sg.Frame(
                    '游戏',
                    [
                        [
                            sg.Text(
                                '\
填好游戏名称、程序目录、启动方式、特殊码（没有可不填）后添加即可\n\n\
程序目录、启动方式必须填，游戏名称若为空，添加时将程序名作为游戏名称\n\n\
转区运行需在设置中设置Locale Emulator路径\n\n\
修改游戏信息后按添加即可修改信息\n\n\
选择一项游戏后按删除即可删除\n\n\
选择一项游戏后按启动游戏即可启动游戏，并自动启动Textractor注入dll',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_textractor = [
            [
                sg.Frame(
                    '抓取',
                    [
                        [
                            sg.Text(
                                '\
设置Textractor目录，确保目录下有TextractorCLI.exe和texthook.dll\n\n\
点击启动TR，选择游戏进程，再Attach注入dll，之后选择钩子并固定即可\n\n\
dll注入后，游戏进程不关，则再次打开程序只需启动TR即可，无需再Attach\n\n\
特殊码使用之前必须确保dll已注入，且特殊码格式必须正确\n\n\
若文本抓取出现问题，可尝试终止TR后再启动TR',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_OCR = [
            [
                sg.Frame(
                    '光学',
                    [
                        [
                            sg.Text(
                                '\
设置Tesseract-OCR路径\n\n\
截取屏幕上的某一区域，用鼠标划定区域，划定完按Enter\n\n\
截取完会直接显示截图图片和文本\n\n\
若想取消划定操作，按ESC键\n\n\
截取一次后按连续，则开始以某一间隔在同一位置进行连续识别\n\n\
按结束则结束连续识别\n\n\
根据程序显示的图片效果，可以调整阈值和阈值化方式',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_translate = [
            [
                sg.Frame(
                    'JBeijing',
                    [
                        [
                            sg.Text(
                                'JBeijing启用并保存后，即可获得翻译文本',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    '有道',
                    [
                        [
                            sg.Text(
                                '\
注意：有道调用的不是API，而是本地的有道词典程序（不可最小化）\n\
设置好有道词典路径后，点击启动有道，并切换到词典翻译页面\n\
若本程序获取的翻译文本错位，可尝试增加翻译间隔\n\
可以取消抓取翻译，并将词典的翻译栏拖在游戏窗口下方\n\
若有道词典的翻译有问题，可尝试终止有道后再启动有道',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    '百度',
                    [
                        [
                            sg.Text(
                                '\
注意：百度翻译是在线翻译，需要使用百度账号免费申请api\n\
1.https://api.fanyi.baidu.com/ 进入百度翻译开放平台。\n\
2.按照指引完成api开通，只需要申请“通用翻译API”。\n\
3.完成申请后点击顶部"管理控制台"，在申请信息一栏可获取APP ID与密钥。”。\n\
启动百度翻译前需要填写APP ID与密钥并且保存',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_text = [
            [
                sg.Frame(
                    '文本',
                    [
                        [
                            sg.Text(
                                '\
文本去重数：文本重复的次数，比如"aabbcc"为重复2次\n\n\
智能去重：根据句子自动判断重复次数并去重，勾上后文本去重数失效\n\n\
垃圾字符表：去除文本中含的垃圾字符，垃圾字符以空格分隔\n\n\
正则表达式：将正则表达式中的所有()部分连接，剩下的去除',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_TTS = [
            [
                sg.Frame(
                    'Yukari2',
                    [
                        [
                            sg.Text(
                                '\
设置好Yukari2路径后，点击启动Yukari2即可（可最小化）\n\n\
连续阅读：连续阅读抓取文本，即抓取到新文本时读取新文本\n\n\
阅读内容：勾上的内容会读取，反之忽略\n\n\
判断依据：有「、『、（的为角色对话，反之为旁白',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        help_layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab('游戏', help_game),
                            sg.Tab('抓取', help_textractor),
                            sg.Tab('光学', help_OCR),
                            sg.Tab('翻译', help_translate),
                            sg.Tab('文本', help_text),
                            sg.Tab('语音', help_TTS),
                        ]
                    ],
                    tab_location='lefttop',
                ),
            ],
        ]

        layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab('游\n戏', game_layout),
                            sg.Tab('抓\n取', textractor_layout),
                            sg.Tab('光\n学', OCR_layout),
                            sg.Tab('翻\n译', translate_layout),
                            sg.Tab('语\n音', TTS_layout),
                            sg.Tab('设\n置', config_layout),
                            sg.Tab('帮\n助', help_layout),
                        ]
                    ],
                    tab_location='lefttop',
                ),
            ],
        ]
        return layout

    # 存储设置
    def save_config(self, values):
        confirm = sg.PopupYesNo('确认保存吗', title='确认')
        if confirm == 'Yes':
            for i in self.config:
                if i == 'alpha':
                    self.main_window.SetAlpha(values['alpha'])
                    
                if 'interval' in i:
                    self.config[i] = float(values[i])
                elif i == 'deduplication':
                    self.config[i] = int(values[i])
                else:
                    self.config[i] = values[i]

            pytesseract.pytesseract.tesseract_cmd = os.path.join(self.config['tesseract_OCR_path'], 'tesseract.exe')
            tessdata_dir_config = '--tessdata-dir "' + os.path.join(self.config['tesseract_OCR_path'], 'tessdata') + '"'

            if self.youdao:
                self.youdao.set_interval(self.config['youdao_interval'])
                self.youdao.set_get_translate(self.config['youdao_get_translate'])

            if self.baidu:
                self.baidu.enabled = self.config['baidu']
                self.baidu.set_appid(self.config['baidu_appid'])
                self.baidu.set_key(self.config['baidu_key'])

            if self.yukari2:
                self.yukari2.working = self.config['yukari2_constantly']
                self.yukari2.set_aside(self.config['yukari2_aside'])
                self.yukari2.set_character(self.config['yukari2_character'])

            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

    # 读取设置
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
            self.config = config

    # 存储游戏信息
    def save_game(self):
        with open('game.json', 'w') as f:
            json.dump(self.game, f, indent=4, ensure_ascii=False)

    # 读取游戏信息
    def load_game(self):
        if os.path.exists('game.json'):
            with open('game.json', 'r') as f:
                config = json.load(f)
            self.game = config

    # 翻译线程，以便同时翻译
    def jbeijing_thread(self, text):
        self.text_jbeijing_translate = jbeijing(
            text,
            self.config['jbeijing_path'],
            jbeijing_to[self.config['jbeijing_to']],
        )

    def youdao_thread(self, text, pid):
        self.text_youdao_translate = self.youdao.translate(text, pid=pid)

    def baidu_thread(self, text):
        self.text_baidu_translate = self.baidu.translate(text)

    # 文字处理
    def text_process(self, text):
        if self.config['deduplication_auto']:
            i = 1
            while i < len(text):
                if text[i] == text[0]:
                    i += 1
                else:
                    break
            if i > 1:
                text_one = text[::i]
                text_two = text[1::i]
                if text_one == text_two:
                    text = text_one
        else:
            text = text[::int(self.config['deduplication'])]

        for i in re.split(r'\s+', self.config['garbage_chars']):
            text = text.replace(i, '')

        rule = re.compile(self.config['re'])
        info = rule.match(text)
        if info:
            groups = info.groups()
            if len(groups):
                text = ''.join(groups)

        if self.config['copy']:
            copy(text)

        self.text = text
        text = text.replace('\n', '')

        pid = None
        try:
            pid = int(self.main_window['process'].get().split()[0])
        except:
            pass

        if self.yukari2 and self.yukari2.working:
            yukari2_thread = Thread(target=self.yukari2.read_text, args=(self.text, pid))
            yukari2_thread.start()

        if self.youdao and self.youdao.working:
            youdao_thread = Thread(target=self.youdao_thread, args=(text, pid))
            youdao_thread.start()

        if self.baidu and self.baidu.enabled:
            baidu_thread = Thread(target=self.baidu_thread, args=(text,))
            baidu_thread.start()

        if self.config['jbeijing']:
            jbeijing_thread = Thread(target=self.jbeijing_thread, args=(text,))
            jbeijing_thread.start()

    # 游戏列表点击函数
    def get_game_info(self):
        game_selected = self.main_window['game_list'].get()
        if len(game_selected):
            game_list = self.game['game_list']
            for i in game_list:
                if i['name'] == game_selected[0]:
                    self.main_window['game_name'].update(i['name'])
                    self.main_window['game_path'].update(i['path'])
                    self.main_window['game_hook_code'].update(i['hook_code'])
                    self.main_window['game_start_mode'].update(value=i['start_mode'])
                    break

    # 添加按钮函数
    def add_game(self):
        game_name = self.main_window['game_name'].get()
        game_path = self.main_window['game_path'].get()
        game_hook_code = self.main_window['game_hook_code'].get()
        game_start_mode = self.main_window['game_start_mode'].get()
        if not game_name:
            game_name = os.path.split(game_path)[1]
            game_name = os.path.splitext(game_name)[0]

        for i in self.game['game_list']:
            if i['name'] == game_name or \
               i['path'] == game_path:
                index = self.games.index(i['name'])
                self.games[index] = game_name
                self.main_window['game_list'].update(values=self.games)

                i['name'] = game_name
                i['path'] = game_path
                i['hook_code'] = game_hook_code
                i['start_mode'] = game_start_mode
                self.save_game()

                return

        game_info = {
            'name': game_name,
            'path': game_path,
            'hook_code': game_hook_code,
            'start_mode': game_start_mode,
        }
        self.game['game_list'].append(game_info)
        self.games.append(game_name)
        self.save_game()
        self.main_window['game_list'].update(values=self.games)

    # 删除按钮函数
    def delete_game(self):
        game_name = self.main_window['game_name'].get()
        for i in self.game['game_list']:
            if i['name'] == game_name:
                self.game['game_list'].remove(i)
                self.games.remove(game_name)
                self.save_game()
                self.main_window['game_list'].update(values=self.games)
                break

    # 启动游戏按钮函数
    def start_game(self):
        game_path = self.main_window['game_path'].get()
        if not os.path.exists(game_path):
            sg.Popup('提示', '游戏路径不正确')
            return

        pid = None
        name = os.path.split(game_path)[1]
        mode = self.main_window['game_start_mode'].get()

        if mode == '直接启动':
            pid = start_directly(game_path)
        elif mode == 'Locale Emulator':
            locale_emulator_path = self.config['locale_emulator_path']
            leproc_path = os.path.join(locale_emulator_path, 'LEProc.exe')
            if not os.path.exists(locale_emulator_path) or \
               not os.path.exists(leproc_path):
                sg.Popup('提示', 'Locale Emulator路径错误')
                return

            pid = start_with_locale_emulator(leproc_path, game_path, name)

        if not pid:
            return

        self.textractor_start()

        self.game['curr_game_id'] = pid
        self.game['curr_game_name'] = name
        self.save_game()
        self.main_window['process'].update(str(pid) + ' - ' + name)

        sleep(1)
        self.attach(pid)

        hook_code = self.main_window['game_hook_code'].get()
        if hook_code:
            sleep(1)
            self.hook_code(pid, hook_code)

    # 刷新按钮函数
    def refresh_process_list(self):
        processes = []
        game_process = None
        for proc in psutil.process_iter():
            try:
                p = proc.as_dict(attrs=['pid', 'name'])
                process = str(p['pid']) + ' - ' + str(p['name'])

                if p['pid'] == self.game['curr_game_id'] and \
                    p['name'] == self.game['curr_game_name']:
                    game_process = process

                processes.append(process)
            except:
                pass
        self.main_window['process'].update(values=processes)

        if game_process:
            self.main_window['process'].update(game_process)

    # 启动按钮函数
    def textractor_start(self):
        self.textractor_stop()

        TextractorCLI_path = os.path.join(self.config['textractor_path'], 'TextractorCLI.exe')
        texthook_path = os.path.join(self.config['textractor_path'], 'texthook.dll')
        if not os.path.exists(TextractorCLI_path) or \
           not os.path.exists(texthook_path):
            sg.Popup('提示', 'Textractor路径不正确')
            return

        self.refresh_process_list()

        self.textractor_working = True
        textractor_thread = Thread(target=self.textractor_work)
        textractor_thread.daemon = True
        textractor_thread.start()

    # 终止按钮函数
    def textractor_stop(self):
        self.main_window['process'].update('')
        self.main_window['process'].update(values=[])
        self.main_window['hook'].update('')
        self.main_window['hook'].update(values=[])
        self.textractor_working = False
        try:
            self.cli.kill()
        except:
            pass
        self.cli = None

    # 以一定间隔读取cli.exe的输出
    def textractor_work(self):
        self.cli = Popen(
            os.path.join(self.config['textractor_path'], 'TextractorCLI.exe'),
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            encoding='utf-16-le',
        )
        rule = re.compile(r'^(\[.+?\])\s+(.+)$')
        hooks = []
        hooks_contents = []
        for line in iter(self.cli.stdout.readline, ''):
            if self.fixed_hook:
                self.main_window['hook'].update(self.fixed_hook)

            if not self.textractor_working:
                break
            if self.textractor_pause:
                continue

            content = rule.match(line)
            if content:
                hook = content.group(1)
                text = content.group(2)

                if hook not in hooks:
                    hooks.append(hook)
                    hooks_contents.append(line)
                    self.main_window['hook'].update(values=hooks_contents)

                if self.fixed_hook:
                    curr_hook = self.fixed_hook
                else:
                    curr_hook = self.main_window['hook'].get()

                content = rule.match(curr_hook)
                if content and hook == content.group(1):
                    self.text_process(text)

                    if not self.float:
                        self.main_window['content'].update('')
                        self.main_window['content'].update(hook, append=True)
                        self.main_window['content'].update('\n\n' + self.text + '\n\n', append=True)

                        if self.config['jbeijing']:
                            self.main_window['content'].update('Jbeijing:\n' + self.text_jbeijing_translate + '\n\n', append=True)

                        if self.youdao and self.youdao.get_translate:
                            self.main_window['content'].update('有道:\n' + self.text_youdao_translate + '\n\n', append=True)

                        if self.baidu and self.baidu.enabled:
                            self.main_window['content'].update('百度:\n' + self.text_baidu_translate+ '\n\n', append=True)

            sleep(self.config['textractor_interval'])

    def attach(self, pid):
        self.cli.stdin.write('attach -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # Attach按钮函数
    def textractor_attach(self):
        if not self.cli:
            sg.Popup('提示', 'Textractor未启动')
            return

        pid = self.main_window['process'].get().split()
        if not len(pid):
            sg.Popup('提示', '进程栏缺少进程id')
            return

        pid = int(pid[0])
        p = psutil.Process(pid)
        self.game['curr_game_id'] = pid
        self.game['curr_game_name'] = p.name()
        self.save_game()
        self.attach(pid)

    def hook_code(self, pid, hook_code):
        self.cli.stdin.write(hook_code + ' -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # 特殊码按钮函数
    def textractor_hook_code(self):
        if not self.cli:
            sg.Popup('提示', 'Textractor未启动')
            return

        layout = [
            [
                sg.Column(
                    [
                        [
                            sg.Text('特殊码:'),
                            sg.Input(
                                key='hook_code',
                                size=(20, 1),
                            ),
                        ],
                        [
                            sg.Button('使用')
                        ],
                    ],
                    element_justification='center'
                )
            ]
        ]

        window = sg.Window(
            '特殊码',
            layout,
            alpha_channel=self.config['alpha'],
        )

        rule = re.compile(r'^\/.+@.+$')
        while True:
            event, values = window.read()
            if event is None:
                break
            elif event == '使用':
                hook_code = window['hook_code'].get()
                if not rule.match(hook_code):
                    sg.Popup('提示', '特殊码格式不对')
                else:
                    self.hook_code(self.game['curr_game_id'], hook_code)
                    sg.Popup('提示', '特殊码使用成功')
                    break

        window.close()

    # 截取按钮函数
    def get_area(self):
        self.main_window.Hide()

        im = screenshot()
        im.save('Screenshot.png')
        full_size = size()
        screenshot_layout = [
            [
                sg.Graph(
                    key='graph',
                    canvas_size=full_size,
                    graph_bottom_left=(0, 0),
                    graph_top_right=full_size,
                    drag_submits=True,
                    enable_events=True,
                    tooltip='按住左键划定区域\n按ESC退出',
                ),
            ],
        ]
        screenshot_window = sg.Window(
            '',
            screenshot_layout,
            finalize=True,
            margins=(0, 0),
            element_padding=(0, 0),
            return_keyboard_events=True,
            no_titlebar=True,
            keep_on_top=True,
        )
        screenshot_window.Maximize()
        graph = screenshot_window['graph']
        graph.DrawImage('Screenshot.png', location=(0, full_size[1]))

        draging = False
        area = None
        while True:
            event, values = screenshot_window.read(timeout=10)
            if event is None:
                break
            elif event == 'graph':
                if not draging:
                    self.x1, self.y1 = position()
                draging = True
            elif event == 'graph+UP':
                self.x2, self.y2 = position()
                draging = False
                graph.DeleteFigure(area)
                area = graph.DrawRectangle(
                    (self.x1, full_size[1] - self.y1),
                    (self.x2, full_size[1] - self.y2),
                    line_color='red',
                )
            elif not event.strip():
                screenshot_window.close()
                if self.x1 > self.x2:
                    self.x1, self.x2 = self.x2, self.x1
                if self.y1 > self.y2:
                    self.y1, self.y2 = self.y2, self.y1
                self.OCR_work()
            elif event == 'Escape:27':
                screenshot_window.close()

            if draging:
                graph.DeleteFigure(area)
                x, y = position()
                area = graph.DrawRectangle(
                    (self.x1, full_size[1] - self.y1),
                    (x, full_size[1] - y),
                    line_color='red',
                )

        self.main_window.UnHide()

    # 图片处理
    def image_process(self):
        im = Image.open("Area.png")
        im = im.convert("L")
        im = threshold_ways[self.config['threshold_way']](im, self.config['threshold'])
        im.save('Area.png')

    # 截取矩形区域图片，进行图片处理，并进行文字识别
    def OCR_work(self):
        bbox = [
            self.x1,
            self.y1,
            self.x2 - self.x1,
            self.y2 - self.y1,
        ]
        im = screenshot(region=bbox)
        im.save('Area.png')

        self.image_process()
        self.main_window['image'].update('Area.png')

        im = Image.open('Area.png')
        text_OCR = tesseract_OCR(im, languages[self.config['OCR_language']])
        if text_OCR != self.text:
            self.text_process(text_OCR)

            if not self.float:
                self.main_window['text_OCR'].update(self.text + '\n\n')

                if self.config['jbeijing']:
                    self.main_window['text_OCR'].update('JBeijing:\n' + self.text_jbeijing_translate + '\n\n', append=True)

                if self.youdao and self.youdao.get_translate:
                    self.main_window['text_OCR'].update('有道:\n' + self.text_youdao_translate + '\n\n', append=True)

                if self.baidu and self.baidu.enabled:
                    self.main_window['text_OCR'].update('百度:\n' + self.text_baidu_translate + '\n\n', append=True)

    # OCR连续识别线程
    def OCR_thread(self):
        while self.OCR_working:
            self.OCR_work()
            sleep(self.config['OCR_interval'])

    # 连续按钮函数
    def OCR_start(self):
        if not os.path.exists(os.path.join(os.path.abspath('.'), 'Tesseract-OCR')):
            sg.Popup('提示', '目录下缺少Tesseract-OCR')
            return

        self.OCR_working = True
        OCR_thread = Thread(target=self.OCR_thread)
        OCR_thread.daemon = True
        OCR_thread.start()

    # 结束按钮函数
    def OCR_stop(self):
        self.OCR_working = False

    # 有道启动按钮函数
    def youdao_start(self):
        youdaodict_path = os.path.join(self.config['youdao_path'], 'YoudaoDict.exe')
        if not os.path.exists(self.config['youdao_path']) or \
           not os.path.exists(youdaodict_path):
            sg.Popup('提示', '有道词典路径不正确')
        else:
            from Translator.youdao import Youdao
            self.youdao = Youdao(
                path=self.config['youdao_path'],
                interval=self.config['youdao_interval'],
                get_translate=self.config['youdao_get_translate'],
            )
            self.youdao.start()

    # yukari2启动按钮函数
    def yukari2_start(self):
        yukari2_path = os.path.join(self.config['yukari2_path'], 'VOICEROID.exe')
        if not os.path.exists(self.config['yukari2_path']) or \
           not os.path.exists(yukari2_path):
            sg.Popup('提示', 'Yukari2路径不正确')
        else:
            from TTS.yukari2 import Yukari2
            self.yukari2 = Yukari2(
                path=self.config['yukari2_path'],
                constantly=self.config['yukari2_constantly'],
                aside=self.config['yukari2_aside'],
                character=self.config['yukari2_character'],
            )
            self.yukari2.start()

    # 浮动按键函数
    def float_window(self):
        self.float = True

        text_layout = []

        if self.config['text_origin']:
            text_origin = [
                sg.Text('原文'),
                sg.Frame(
                    '',
                    [[sg.Multiline('', key='text', size=(75, 2))]],
                ),
            ]
            text_layout.append(text_origin)

        if self.config['jbeijing']:
            text_jbeijing = [
                sg.Text('北京'),
                sg.Frame(
                    '',
                    [[sg.Multiline('', key='text_jbeijing_translated', size=(75, 2))]],
                ),
            ]
            text_layout.append(text_jbeijing)

        if self.youdao and self.youdao.get_translate:
            text_youdao = [
                sg.Text('有道'),
                sg.Frame(
                    '',
                    [[sg.Multiline('', key='text_youdao_translated', size=(75, 2))]],
                ),
            ]
            text_layout.append(text_youdao)

        if self.baidu and self.baidu.enabled:
            text_baidu = [
                sg.Text('百度'),
                sg.Frame(
                    '',
                    [[sg.Multiline('', key='text_baidu_translated', size=(75, 2))]],
                ),
            ]
            text_layout.append(text_baidu)

        layout = [
            [
                sg.Column(
                    [
                        [
                            sg.Column(text_layout),
                            sg.Button('暂停', pad=(20, 0)),
                            sg.Button('阅读', pad=(0, 0)),
                        ],
                    ],
                ),
            ],
        ]

        window = sg.Window(
            '',
            layout,
            alpha_channel=self.config['alpha'],
            auto_size_text=True,
            margins=(0, 0),
            element_padding=(0, 0),
            resizable=True,
            force_toplevel=True,
            keep_on_top=True,
            grab_anywhere=True,
        )

        self.main_window.Minimize()

        prev_text = ''
        prev_text_jbeijing = ''
        prev_text_youdao = ''
        prev_text_baidu = ''

        while True:
            event, values = window.read(timeout=self.config['float_interval'] * 1000)
            if event is None:
                break
            elif event == '暂停':
                self.textractor_pause = not self.textractor_pause
            elif event == '阅读':
                if not self.yukari2:
                    self.yukari2_start()
                else:
                    self.yukari2.read(self.text)

            if self.textractor_working or self.OCR_working:
                if self.config['text_origin'] and \
                   prev_text != self.text:
                    prev_text = self.text
                    window['text'].update(self.text)
                if self.config['jbeijing'] and \
                   prev_text_jbeijing != self.text_jbeijing_translate:
                    prev_text_jbeijing = self.text_jbeijing_translate
                    window['text_jbeijing_translated'].update(self.text_jbeijing_translate)
                if self.youdao and \
                   self.youdao.get_translate and \
                   prev_text_youdao != self.text_youdao_translate:
                    prev_text_youdao = self.text_youdao_translate
                    window['text_youdao_translated'].update(self.text_youdao_translate)
                if self.baidu and \
                   self.baidu.enabled and \
                   prev_text_baidu != self.text_baidu_translate:
                    prev_text_baidu = self.text_baidu_translate
                    window['text_baidu_translated'].update(self.text_baidu_translate)

        self.float = False
        window.close()
        self.main_window.Normal()


if __name__ == '__main__':
    Main_Window()
    
    if os.path.exists('Screenshot.png'):
        os.remove('Screenshot.png')
    if os.path.exists('Area.png'):
        os.remove('Area.png')
    if os.path.exists('GPS.txt'):
        os.remove('GPS.txt')
