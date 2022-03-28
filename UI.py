import PySimpleGUI as sg

from game import start_mode

from OCR.tesseract_OCR import lang_translate
from OCR.threshold_ways import threshold_name

from Translator.jbeijing import jbeijing_translate


font_name = 'Microsoft Yahei'
font_size = 15


def UI(config, **kw):
    games = kw['games']
    voiceroid2 = kw['voiceroid2']

    game_list = [
        [sg.Listbox(key='game_list', values=games, enable_events=True, size=(80, 10),)],
    ]

    game_info_widget = sg.Column(
        [
            [
                sg.Text('游戏名称：', size=(8, 1)),
                sg.Input(key='game_name', default_text='', size=(72, 1),),
            ],
            [
                sg.Text('程序目录：', size=(8, 1)),
                sg.Input(key='game_path', default_text='', size=(68, 1),),
                sg.FileBrowse('目录', key='game_dir', font=(font_name, 10), size=(4, 1),),
            ],
            [
                sg.Text('启动方式：', size=(8, 1)),
                sg.Combo(
                    start_mode,
                    key='game_start_mode',
                    default_value='',
                    readonly=True,
                    size=(71, 1),
                ),
            ],
            [
                sg.Text('特殊码：', size=(8, 1)),
                sg.Input(key='game_hook_code', default_text='', size=(72, 1),),
            ],
        ],
    )

    game_info_buttons = sg.Column(
        [
            [
                sg.Button('添加', key='game_add', pad=((0, 20), 0)),
                sg.Button('删除', key='game_delete', pad=((0, 20), 0)),
                sg.Button('启动游戏', key='game_start'),
            ],
        ],
    )

    game_info = [
        [game_info_widget],
        [game_info_buttons],
    ]

    game_layout = [
        [sg.Frame('游戏列表', layout=game_list,)],
        [sg.Frame('游戏信息', layout=game_info, element_justification='center',)],
    ]

    textractor_buttons = sg.Column(
        [
            [sg.Button('启动TR', key='textractor_start', pad=(20, 20))],
            [sg.Button('Attach', key='textractor_attach', pad=(20, 20))],
            [sg.Button('暂停', key='textractor_pause', pad=(20, 20))],
            [sg.Button('特殊码', key='textractor_hook_code', pad=(20, 20))],
            [sg.Button('终止TR', key='textractor_stop', pad=(20, 20))],
            [sg.Button('浮动', key='floating', pad=(20, 20))],
        ],
    )

    textractor_layout = [
        [
            sg.Text('进程：', size=(4, 1)),
            sg.Combo([], key='textractor_process', size=(70, 1),),
            sg.Button('刷新', key='textractor_refresh', pad=(20, 20)),
        ],
        [
            sg.Text('钩子：', size=(4, 1)),
            sg.Combo([], key='textractor_hook', readonly=True, size=(70, 1),),
            sg.Button('固定', key='textractor_fix', pad=(20, 0)),
        ],
        [
            sg.Frame(
                '提取文本',
                [
                    [
                        sg.Multiline(
                            '', key='textractor_text', autoscroll=True, size=(72, 16)
                        )
                    ]
                ],
            ),
            textractor_buttons,
        ],
    ]

    OCR_display = sg.Column(
        [
            [sg.Frame('截取区域', [[sg.Image('', key='OCR_image')]],)],
            [
                sg.Frame(
                    '提取文本',
                    [
                        [
                            sg.Multiline(
                                '', key='OCR_text', autoscroll=True, size=(72, 16)
                            )
                        ]
                    ],
                ),
            ],
        ],
        element_justification='center',
    )

    OCR_buttons = sg.Column(
        [
            [sg.Button('截取', key='OCR_area', pad=(20, 20))],
            [sg.Button('连续', key='OCR_start', pad=(20, 20))],
            [sg.Button('暂停', key='OCR_pause', pad=(20, 20))],
            [sg.Button('结束', key='OCR_stop', pad=(20, 20))],
            [sg.Button('浮动', key='floating', pad=(20, 20))],
        ],
    )

    OCR_layout = [
        [OCR_display, OCR_buttons,],
    ]

    translate_jbeijing = [
        [
            sg.Frame(
                'JBeijing',
                [
                    [
                        sg.Text('JBeijing：', size=(8, 1)),
                        sg.Checkbox('启用', key='jbeijing', default=config['jbeijing'],),
                    ],
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='jbeijing_path',
                            default_text=config['jbeijing_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse('目录', key='jbeijing_dir', font=(font_name, 10)),
                    ],
                    [
                        sg.Text('翻译语言：', size=(8, 1)),
                        sg.Combo(
                            jbeijing_translate,
                            key='jbeijing_to',
                            default_value=config['jbeijing_to'],
                            readonly=True,
                            size=(12, 1),
                        ),
                    ],
                ],
            ),
        ],
    ]

    translate_youdao = [
        [
            sg.Frame(
                '有道',
                [
                    [
                        sg.Text('有道词典：', size=(8, 1)),
                        sg.Button('启动', key='youdao_start'),
                        sg.Button('终止', key='youdao_stop', pad=(20, 0)),
                    ],
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='youdao_path',
                            default_text=config['youdao_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse('目录', key='youdao_dir', font=(font_name, 10)),
                    ],
                    [
                        sg.Text('抓取翻译：', size=(8, 1)),
                        sg.Checkbox(
                            '启用',
                            key='youdao_get_translate',
                            default=config['youdao_get_translate'],
                        ),
                    ],
                    [
                        sg.Text('抓取间隔：', size=(8, 1)),
                        sg.Input(
                            key='youdao_interval',
                            default_text=config['youdao_interval'],
                            size=(6, 1),
                        ),
                        sg.Text('秒'),
                    ],
                ],
            ),
        ],
    ]

    translate_baidu = [
        [
            sg.Frame(
                '百度翻译',
                [
                    [
                        sg.Text('百度翻译：', size=(8, 1)),
                        sg.Checkbox('启用', key='baidu', default=config['baidu'],),
                    ],
                    [
                        sg.Text('APPID：', size=(8, 1)),
                        sg.Input(
                            key='baidu_appid',
                            default_text=config['baidu_appid'],
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Text('密钥：', size=(8, 1)),
                        sg.Input(
                            key='baidu_key',
                            default_text=config['baidu_key'],
                            size=(50, 1),
                        ),
                    ],
                ],
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
                                    sg.Tab('北京', translate_jbeijing),
                                    sg.Tab('有道', translate_youdao),
                                    sg.Tab('百度', translate_baidu),
                                ]
                            ],
                            tab_location='lefttop',
                        )
                    ],
                    [sg.Button('保存', key='save'),],
                ],
                element_justification='center',
            )
        ],
    ]

    TTS_general = [
        [
            sg.Frame(
                '通用',
                [
                    [
                        sg.Text('连续阅读：', size=(12, 1)),
                        sg.Checkbox(
                            '启用',
                            key='TTS_continuous',
                            default=config['TTS_continuous'],
                        ),
                    ],
                    [
                        sg.Text('连续阅读特征：', size=(12, 1)),
                        sg.Input(
                            key='TTS_continuous_feature',
                            default_text=config['TTS_continuous_feature'],
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Text('角色对话特征：', size=(12, 1)),
                        sg.Input(
                            key='TTS_character_feature',
                            default_text=config['TTS_character_feature'],
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Text('连续阅读内容：', size=(12, 1)),
                        sg.Checkbox(
                            '角色', key='TTS_character', default=config['TTS_character'],
                        ),
                        sg.Checkbox(
                            '旁白', key='TTS_narration', default=config['TTS_narration'],
                        ),
                    ],
                ],
            ),
        ],
    ]

    TTS_yukari = [
        [
            sg.Frame(
                'Yukari',
                [
                    [
                        sg.Text('Yukari：', size=(8, 1)),
                        sg.Button('启动', key='yukari_start'),
                        sg.Button('终止', key='yukari_stop', pad=(20, 0)),
                    ],
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='yukari_path',
                            default_text=config['yukari_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse('目录', key='yukari_dir', font=(font_name, 10)),
                    ],
                ],
            ),
        ],
    ]

    TTS_tamiyasu = [
        [
            sg.Frame(
                'Tamiyasu',
                [
                    [
                        sg.Text('Tamiyasu：', size=(8, 1)),
                        sg.Button('启动', key='tamiyasu_start'),
                        sg.Button('终止', key='tamiyasu_stop', pad=(20, 0)),
                    ],
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='tamiyasu_path',
                            default_text=config['tamiyasu_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse('目录', key='tamiyasu_dir', font=(font_name, 10)),
                    ],
                ],
            ),
        ],
    ]

    TTS_voiceroid2 = [
        [
            sg.Frame(
                'VOICEROID2',
                [
                    [
                        sg.Text('VOICEROID2：', size=(12, 1)),
                        sg.Checkbox(
                            '启用', key='voiceroid2', default=config['voiceroid2'],
                        ),
                    ],
                    [
                        sg.Text('路径：', size=(12, 1)),
                        sg.Input(
                            key='voiceroid2_path',
                            default_text=config['voiceroid2_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse(
                            '目录', key='voiceroid2_dir', font=(font_name, 10)
                        ),
                    ],
                    [
                        sg.Text('启用Voice：', size=(12, 1)),
                        sg.Combo(
                            voiceroid2.voice_list,
                            key='voiceroid2_voice_selected',
                            default_value=voiceroid2.voice_selected,
                            readonly=True,
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Frame(
                            '参数设置',
                            [
                                [
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_master_volume',
                                                    default_value=config[
                                                        'voiceroid2_master_volume'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 5.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=1,
                                                ),
                                            ],
                                            [sg.Text('マスター音量', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_volume',
                                                    default_value=config[
                                                        'voiceroid2_volume'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('音量', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_speed',
                                                    default_value=config[
                                                        'voiceroid2_speed'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0.5, 4.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=1.0,
                                                ),
                                            ],
                                            [sg.Text('話速', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_pitch',
                                                    default_value=config[
                                                        'voiceroid2_pitch'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0.5, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('高さ', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_emphasis',
                                                    default_value=config[
                                                        'voiceroid2_emphasis'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0.5, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('抑揚', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_pause_middle',
                                                    default_value=config[
                                                        'voiceroid2_pause_middle'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(80, 500),
                                                    resolution=1,
                                                    size=(10, 10),
                                                    tick_interval=100,
                                                ),
                                            ],
                                            [sg.Text('短ポーズ時間', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_pause_long',
                                                    default_value=config[
                                                        'voiceroid2_pause_long'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(100, 2000),
                                                    resolution=1,
                                                    size=(10, 10),
                                                    tick_interval=500,
                                                ),
                                            ],
                                            [sg.Text('長ポーズ時間', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voiceroid2_pause_sentence',
                                                    default_value=config[
                                                        'voiceroid2_pause_sentence'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(200, 10000),
                                                    resolution=1,
                                                    size=(10, 10),
                                                    tick_interval=2000,
                                                ),
                                            ],
                                            [sg.Text('文末ポーズ時間', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                ],
                                [sg.Button('修改具体数值', key='voiceroid2_modify'),],
                            ],
                            element_justification='center',
                        ),
                    ],
                ],
            ),
        ],
    ]

    TTS_voicevox = [
        [
            sg.Frame(
                'VOICEVOX',
                [
                    [
                        sg.Text('VOICEVOX：', size=(12, 1)),
                        sg.Button('启动', key='voicevox_start'),
                        sg.Button('终止', key='voicevox_stop', pad=(20, 0)),
                    ],
                    [
                        sg.Text('路径：', size=(12, 1)),
                        sg.Input(
                            key='voicevox_path',
                            default_text=config['voicevox_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse('目录', key='voicevox_dir', font=(font_name, 10)),
                    ],
                    [
                        sg.Text('启用Speaker：', size=(12, 1)),
                        sg.Combo(
                            [],
                            key='voicevox_speaker_selected',
                            default_value=config['voicevox_speaker_selected'],
                            readonly=True,
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Frame(
                            '参数设置',
                            [
                                [
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_speed_scale',
                                                    default_value=config[
                                                        'voicevox_speed_scale'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0.5, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('話速', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_pitch_scale',
                                                    default_value=config[
                                                        'voicevox_pitch_scale'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(-0.15, 0.15),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.1,
                                                ),
                                            ],
                                            [sg.Text('音高', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_intonation_scale',
                                                    default_value=config[
                                                        'voicevox_intonation_scale'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('抑揚', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_volume_scale',
                                                    default_value=config[
                                                        'voicevox_volume_scale'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 2.0),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('音量', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_pre_phoneme_length',
                                                    default_value=config[
                                                        'voicevox_pre_phoneme_length'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 1.5),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('開始無音', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                    sg.Column(
                                        [
                                            [
                                                sg.Slider(
                                                    key='voicevox_post_phoneme_length',
                                                    default_value=config[
                                                        'voicevox_post_phoneme_length'
                                                    ],
                                                    font=(font_name, 8),
                                                    orientation='v',
                                                    range=(0, 1.5),
                                                    resolution=0.01,
                                                    size=(10, 10),
                                                    tick_interval=0.5,
                                                ),
                                            ],
                                            [sg.Text('終了無音', font=(font_name, 8)),],
                                        ],
                                        element_justification='right',
                                        pad=(15, 0),
                                    ),
                                ],
                                [sg.Button('修改具体数值', key='voicevox_modify'),],
                            ],
                            element_justification='center',
                        ),
                    ],
                ],
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
                                    sg.Tab('通用', TTS_general),
                                    sg.Tab('Yukari', TTS_yukari),
                                    sg.Tab('Tamiyasu', TTS_tamiyasu),
                                    sg.Tab('VOICEROID2', TTS_voiceroid2),
                                    sg.Tab('VOICEVOX', TTS_voicevox),
                                ]
                            ],
                            tab_location='lefttop',
                        )
                    ],
                    [sg.Button('保存', key='save'),],
                ],
                element_justification='center',
            ),
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
                            default_value=config['alpha'],
                            orientation='h',
                            range=(0, 1.0),
                            resolution=0.01,
                            size=(25, 10),
                            tick_interval=1,
                        ),
                    ],
                ],
            ),
        ],
        [
            sg.Frame(
                '置顶',
                [
                    [
                        sg.Text('窗口置顶：'),
                        sg.Checkbox('启用', key='top', default=config['top'],),
                    ],
                ],
            )
        ],
        [
            sg.Frame(
                '剪切板',
                [
                    [
                        sg.Text('复制到剪切板：'),
                        sg.Checkbox('启用', key='copy', default=config['copy'],),
                    ],
                ],
            )
        ],
    ]

    config_game = [
        [
            sg.Frame(
                'Locale Emulator',
                [
                    [
                        sg.Text('路径：'),
                        sg.Input(
                            key='locale_emulator_path',
                            default_text=config['locale_emulator_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse(
                            '目录', key='locale_emulator_dir', font=(font_name, 10)
                        ),
                    ],
                ],
            )
        ]
    ]

    config_textractor = [
        [
            sg.Frame(
                'Textractor',
                [
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='textractor_path',
                            default_text=config['textractor_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse(
                            '目录', key='textractor_dir', font=(font_name, 10)
                        ),
                    ],
                    [
                        sg.Text('抓取间隔：', size=(8, 1)),
                        sg.Input(
                            key='textractor_interval',
                            default_text=config['textractor_interval'],
                            size=(6, 1),
                        ),
                        sg.Text('秒'),
                    ],
                ],
            )
        ],
    ]

    config_OCR = [
        [
            sg.Frame(
                'Tesseract-OCR',
                [
                    [
                        sg.Text('路径：', size=(8, 1)),
                        sg.Input(
                            key='tesseract_OCR_path',
                            default_text=config['tesseract_OCR_path'],
                            size=(50, 1),
                        ),
                        sg.FolderBrowse(
                            '目录', key='tesseract_OCR_dir', font=(font_name, 10)
                        ),
                    ],
                    [
                        sg.Text('识别语言：', size=(8, 1)),
                        sg.Combo(
                            lang_translate,
                            key='OCR_language',
                            default_value=config['OCR_language'],
                            readonly=True,
                            size=(14, 1),
                        ),
                    ],
                ],
            )
        ],
        [
            sg.Frame(
                '截屏',
                [
                    [
                        sg.Text('截屏间隔：', size=(8, 1)),
                        sg.Input(
                            key='OCR_interval',
                            default_text=config['OCR_interval'],
                            size=(6, 1),
                        ),
                        sg.Text('秒'),
                    ],
                ],
            )
        ],
        [
            sg.Frame(
                '图片处理',
                [
                    [
                        sg.Text('阈值化方法：', size=(10, 1)),
                        sg.Combo(
                            threshold_name,
                            key='threshold_way',
                            default_value=config['threshold_way'],
                            readonly=True,
                            size=(12, 1),
                        ),
                    ],
                    [
                        sg.Text('阈值：', size=(10, 1)),
                        sg.Slider(
                            key='threshold',
                            default_value=config['threshold'],
                            orientation='h',
                            range=(0, 255),
                            resolution=1,
                            size=(40, 10),
                            tick_interval=255,
                        ),
                    ],
                ],
            )
        ],
    ]

    config_text = [
        [
            sg.Frame(
                '文本',
                [
                    [
                        sg.Text('文本去重数（aabbcc）：'),
                        sg.Input(
                            key='deduplication_aabbcc',
                            default_text=config['deduplication_aabbcc'],
                            size=(6, 1),
                        ),
                        sg.Text('    智能去重：'),
                        sg.Checkbox(
                            '启用',
                            key='deduplication_aabbcc_auto',
                            default=config['deduplication_aabbcc_auto'],
                        ),
                    ],
                    [
                        sg.Text('文本去重数（abcabc）：'),
                        sg.Input(
                            key='deduplication_abcabc',
                            default_text=config['deduplication_abcabc'],
                            size=(6, 1),
                        ),
                        sg.Text('    智能去重：'),
                        sg.Checkbox(
                            '启用',
                            key='deduplication_abcabc_auto',
                            default=config['deduplication_abcabc_auto'],
                        ),
                    ],
                    [
                        sg.Text('垃圾字符表：'),
                        sg.Input(
                            key='garbage_chars',
                            default_text=config['garbage_chars'],
                            size=(50, 1),
                        ),
                    ],
                    [
                        sg.Text('正则表达式：'),
                        sg.Input(key='re', default_text=config['re'], size=(50, 1),),
                    ],
                ],
            )
        ]
    ]

    config_floating = [
        [
            sg.Frame(
                '浮动',
                [
                    [
                        sg.Text('显示原文：'),
                        sg.Checkbox(
                            '启用',
                            key='floating_text_original',
                            default=config['floating_text_original'],
                        ),
                    ],
                ],
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
                                    sg.Tab('浮动', config_floating),
                                ]
                            ],
                            tab_location='lefttop',
                        )
                    ],
                    [sg.Button('保存', key='save'),],
                ],
                element_justification='center',
            )
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
                    ]
                ],
                tab_location='lefttop',
            ),
        ],
    ]
    return layout


def textractor_hook_code_layout():
    layout = [
        [
            sg.Column(
                [
                    [sg.Text('特殊码:'), sg.Input(key='hook_code', size=(20, 1),),],
                    [sg.Button('使用')],
                ],
                element_justification='center',
            )
        ]
    ]

    return layout


def voiceload2_layout(config):
    layout = [
        [
            sg.Text('マスター音量：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_master_volume',
                default_text=str(config['voiceroid2_master_volume']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('音量：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_volume',
                default_text=str(config['voiceroid2_volume']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('話速：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_speed',
                default_text=str(config['voiceroid2_speed']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('高さ：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_pitch',
                default_text=str(config['voiceroid2_pitch']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('抑揚：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_emphasis',
                default_text=str(config['voiceroid2_emphasis']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('短ポーズ時間：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_pause_middle',
                default_text=str(config['voiceroid2_pause_middle']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('長ポーズ時間：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_pause_long',
                default_text=str(config['voiceroid2_pause_long']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('文末ポーズ時間：', size=(14, 1)),
            sg.Input(
                key='voiceroid2_pause_sentence',
                default_text=str(config['voiceroid2_pause_sentence']),
                size=(10, 1),
            ),
        ],
        [sg.Button('保存'),],
    ]

    return layout


def voicevox_layout(config):
    layout = [
        [
            sg.Text('話速：', size=(8, 1)),
            sg.Input(
                key='voicevox_speed_scale',
                default_text=str(config['voicevox_speed_scale']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('音高：', size=(8, 1)),
            sg.Input(
                key='voicevox_pitch_scale',
                default_text=str(config['voicevox_pitch_scale']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('抑揚：', size=(8, 1)),
            sg.Input(
                key='voicevox_intonation_scale',
                default_text=str(config['voicevox_intonation_scale']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('音量：', size=(8, 1)),
            sg.Input(
                key='voicevox_volume_scale',
                default_text=str(config['voicevox_volume_scale']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('開始無音：', size=(8, 1)),
            sg.Input(
                key='voicevox_pre_phoneme_length',
                default_text=str(config['voicevox_pre_phoneme_length']),
                size=(10, 1),
            ),
        ],
        [
            sg.Text('終了無音：', size=(8, 1)),
            sg.Input(
                key='voicevox_post_phoneme_length',
                default_text=str(config['voicevox_post_phoneme_length']),
                size=(10, 1),
            ),
        ],
        [sg.Button('保存'),],
    ]

    return layout


def floating_layout(config, translators, multiline_width):
    text_layout = []

    if config['floating_text_original']:
        floating_text_original = [
            sg.Text('原文'),
            sg.Frame(
                '',
                [
                    [
                        sg.Multiline(
                            '',
                            key='text_original',
                            size=(multiline_width, 2),
                            disabled=True,
                        )
                    ]
                ],
            ),
        ]
        text_layout.append(floating_text_original)
    for translator_label in translators:
        translator = translators[translator_label]
        if translator.working:
            if not translator.get_translate:
                pass
            else:
                layout = [
                    sg.Text(translator.name),
                    sg.Frame(
                        '',
                        [
                            [
                                sg.Multiline(
                                    '',
                                    key=translator.key,
                                    size=(multiline_width, 2),
                                    disabled=True,
                                )
                            ]
                        ],
                    ),
                ]
                text_layout.append(layout)

    # 若未选择任何文本栏，则放置一片区域，方便拖动和右键菜单
    if len(text_layout) == 0:
        blank = [
            sg.Text('空白'),
        ]
        text_layout.append(blank)

    layout = [
        [
            sg.Column(
                [
                    [
                        sg.Column(text_layout),
                        sg.Button('暂停', key='pause', pad=(10, 0), font=(font_name, 12)),
                        sg.Button('阅读', key='read', pad=(10, 0), font=(font_name, 12)),
                    ],
                ],
            ),
        ],
    ]

    return layout
