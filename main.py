import PySimpleGUI as sg
import os
import re
import json
import psutil
import subprocess
from My_Thread import My_Thread
from PIL import Image
from pyautogui import position, screenshot, size
from pyperclip import copy
from time import sleep
from tesseract_ocr import languages, lang_translate, OCR
from threshold_ways import threshold_ways, threshold_name
from jbeijing import jbeijing, DLL, jbeijing_to, jbeijing_translate

sg.theme('DarkGrey5')
sg.set_options(font=('微软雅黑', 15))

class Main_Window(object):
    def __init__(self):
        super().__init__()

        # 默认设置参数
        self.configs = {
            'alpha': 1.0,
            'copy': False,
            'textractor_path': os.path.abspath('.') + r'\Textractor',
            'textractor_interval': 0.1,
            'language': '日文',
            'continuously': False,
            'OCR_interval': 1,
            'threshold_way': 'BINARY',
            'threshold': 127,
            'jbeijing': False,
            'jbeijing_path': os.path.abspath('.') + r'\jbeijing',
            'jbeijing_to': '简体中文',
        }

        # Textractor相关
        self.processes = []
        self.hooks = ['']
        self.textractor_thread = None
        self.cli = None
        self.textractor_working = False

        # OCR相关
        self.screenshot = None
        self.OCR_thread = None
        self.OCR_working = False
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        # 文本相关
        self.text = None
        self.text_translated = None

        # 读取设置
        self.load_config()

        self.main_window = sg.Window(
            'VNR_OCR',
            self.interface(),
            resizable=True,
            alpha_channel=self.configs['alpha'],
            margins=(0, 0),
        )

        while True:
            event, values = self.main_window.read(timeout=10)
            if values and values['alpha']:
                self.configs['alpha'] = values['alpha']
                self.main_window.SetAlpha(self.configs['alpha'])
            if event is None:
                break
            elif event == '刷新':
                self.refresh_process_list()
            elif event == '启动':
                self.textractor_start()
            elif event == 'Attach':
                self.textractor_attach()
            elif event == 'Detach':
                self.textractor_detach()
            elif event == '终止':
                self.textractor_stop()
            elif event == '截取':
                self.get_area()
            elif event == '开始':
                self.OCR_start()
            elif event == '结束':
                self.OCR_stop()
            elif event == '保存':
                self.save_config(values)
            elif event == '浮动':
                self.float_window()

        self.main_window.close()

    # 界面设置
    def interface(self):
        textractor_buttons = [
            [sg.Button('启动', pad=(20, 20))],
            [sg.Button('Attach', pad=(20, 20))],
            [sg.Button('Detach', pad=(20, 20))],
            [sg.Button('终止', pad=(20, 20))],
            [sg.Button('浮动', pad=(20, 20))],
        ]

        textractor_layout = [
            [
                sg.Text('进程：'),
                sg.Combo(
                    self.processes,
                    key='process',
                    size=(71, 1),
                ),
                sg.Button('刷新', pad=(20, 20)),
            ],
            [
                sg.Text('钩子：'),
                sg.Combo(
                    self.hooks,
                    key='hook',
                    size=(71, 1),
                ),
            ],
            [
                sg.Frame(
                    '钩子',
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
                    [[sg.Multiline('提取文本', key='text_extract', size=(75, 16))]],
                ),
            ],
        ]

        OCR_buttons = [
            [sg.Button('截取', pad=(20, 20))],
            [sg.Button('开始', pad=(20, 20))],
            [sg.Button('结束', pad=(20, 20))],
            [sg.Button('浮动', pad=(20, 20))],
        ]

        OCR_layout = [
            [
                sg.Column(OCR_display, element_justification='center'),
                sg.Column(OCR_buttons),
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
                                default_value=self.configs['alpha'],
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
                                default=self.configs['copy'],
                            )
                        ],
                    ],
                    pad=(10, 10),
                )
            ],
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
                                default_text=self.configs['textractor_path'],
                                size=(57, 1),
                            ),
                            sg.FolderBrowse('目录', key='textractor_dir'),
                        ],
                        [
                            sg.Text('Textractor间隔：'),
                            sg.Input(
                                key='textractor_interval',
                                default_text=self.configs['textractor_interval'],
                                size=(17, 1),
                            ),
                        ],
                    ],
                    pad=(10, 10),
                )
            ]
        ]

        config_OCR = [
            [
                sg.Frame(
                    '语言',
                    [
                        [
                            sg.Text('识别语言：'),
                            sg.Combo(
                                lang_translate,
                                key='language',
                                default_value=self.configs['language'],
                                size=(14, 1),
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
                            sg.Text('截屏方式：'),
                            sg.Radio(
                                '单次截屏',
                                'once_or_continuously',
                                key='once',
                                default=not self.configs['continuously'],
                            ),
                            sg.Radio(
                                '连续截屏',
                                'once_or_continuously',
                                key='continuously',
                                default=self.configs['continuously'],
                            ),
                        ],
                        [
                            sg.Text('截屏间隔：'),
                            sg.Input(
                                key='OCR_interval',
                                default_text=self.configs['OCR_interval'],
                                size=(17, 1),
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
                            sg.Text('阈值化方法：'),
                            sg.Combo(
                                threshold_name,
                                key='threshold_way',
                                default_value=self.configs['threshold_way'],
                                size=(12, 1),
                            ),
                        ],
                        [
                            sg.Text('阈值：'),
                            sg.Slider(
                                key='threshold',
                                default_value=self.configs['threshold'],
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

        config_translate = [
            [
                sg.Frame(
                    'Jbeijing',
                    [
                        [
                            sg.Text('Jbeijing：'),
                            sg.Checkbox(
                                '启用',
                                key='jbeijing',
                                default=self.configs['jbeijing'],
                            )
                        ],
                        [
                            sg.Text('Jbeijing路径：'),
                            sg.Input(
                                key='jbeijing_path',
                                default_text=self.configs['jbeijing_path'],
                                size=(57, 1),
                            ),
                            sg.FolderBrowse('目录', key='jbeijing_dir'),
                        ],
                        [
                            sg.Text('翻译语言：'),
                            sg.Combo(
                                jbeijing_translate,
                                key='jbeijing_to',
                                default_value=self.configs['jbeijing_to'],
                                size=(14, 1),
                            ),
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
                                        sg.Tab('抓取', config_textractor),
                                        sg.Tab('光学', config_OCR),
                                        sg.Tab('翻译', config_translate),
                                    ]
                                ],
                                tab_location='lefttop',
                            )
                        ],
                        [
                            sg.Button('保存'),
                        ],
                    ],
                    element_justification='center'
                )
            ],
        ]

        help_layout = [
            [
                sg.Frame(
                    '抓取',
                    [
                        [
                            sg.Text(
                                '\
设置Textractor目录，确保目录下有TextractorCLI.exe和texthook.dll\n\n\
启动Textractor，选择游戏线程，再Attach注入dll，之后选择钩子即可\n\n\
Attach和Detach时线程框必须对应游戏线程\n\n\
dll注入后，游戏线程不关，则再次打开程序只需启动Textractor即可，无需再Attach\n\n\
若文本抓取出现问题，可尝试终止后再启动',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    '光学',
                    [
                        [
                            sg.Text(
                                '\
截取屏幕上的某一区域，用鼠标划定区域，划定完按回车；若想取消划定操作，按ESC键\n\n\
若设置中选择单次截屏，则截取完直接显示\n\n\
若设置中选择连续截屏，则截取完开始以某一间隔进行连续识别；按结束则结束识别\n\n\
根据程序显示的图片效果，可以调整阈值和阈值化方式来使得图片中的文字更加容易被识别',
                                pad=(10, 10),
                            ),
                        ],
                    ],
                ),
            ],
        ]

        layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab('抓\n取', textractor_layout),
                            sg.Tab('光\n学', OCR_layout),
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
            for i in self.configs:
                if 'interval' in i:
                    self.configs[i] = float(values[i])
                else:
                    self.configs[i] = values[i]
            with open('config.json', 'w') as f:
                json.dump(self.configs, f, indent=4)

    # 读取设置
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                configs = json.load(f)
            for i in configs:
                self.configs[i] = configs[i]

    # 文字处理
    def text_process(self, text):
        self.text = text.replace('\n', '')

        if self.configs['copy']:
            copy(self.text)

        self.text_translated = ''
        if self.configs['jbeijing']:
            dll_path = os.path.join(self.configs['jbeijing_path'], DLL)
            if os.path.exists(dll_path):
                self.text_translated = jbeijing(
                    self.text,
                    dll_path,
                    jbeijing_to[self.configs['jbeijing_to']],
                )

    # 刷新按钮函数
    def refresh_process_list(self):
        self.processes = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
                self.processes.append(str(pinfo['pid']) + ' - ' + str(pinfo['name']))
            except psutil.NoSuchProcess:
                pass
        self.main_window['process'].update(values=self.processes)

    # 启动按钮函数
    def textractor_start(self):
        try:
            self.textractor_stop()
        except:
            pass
        TextractorCLI_path = os.path.join(self.configs['textractor_path'], 'TextractorCLI.exe')
        texthook_path = os.path.join(self.configs['textractor_path'], 'texthook.dll')
        if os.path.exists(TextractorCLI_path) and os.path.exists(texthook_path):
            self.textractor_working = True
            self.textractor_thread = My_Thread(target=self.textractor_work)
            self.textractor_thread.daemon = True
            self.textractor_thread.start()

    # 终止按钮函数
    def textractor_stop(self):
        self.textractor_working = False
        self.cli.kill()
        self.textractor_thread.stop()

    # 以一定间隔读取cli.exe的输出
    def textractor_work(self):
        self.cli = subprocess.Popen(
            os.path.join(self.configs['textractor_path'], 'TextractorCLI.exe'),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-16-le',
        )
        rule = re.compile(r'^(\[.+?\]) (.+)$')
        hooks = {}
        for line in iter(self.cli.stdout.readline, ''):
            if not self.textractor_working:
                break
            content = rule.match(line)
            if content:
                hook = content.group(1)
                text = content.group(2)
                if not hook in hooks:
                    self.hooks.append(hook)
                    self.main_window['hook'].update(values=self.hooks)
                hooks[hook] = text
                if hook == self.main_window['hook'].get() and text != self.text:
                    self.main_window['content'].update('')
                    self.text_process(text)
                    self.main_window['content'].update(hook, append=True)
                    self.main_window['content'].update('\n' + self.text + '\n', append=True)
                    self.main_window['content'].update(self.text_translated, append=True)

            sleep(self.configs['textractor_interval'])

    # Attach按钮函数
    def textractor_attach(self):
        pid = self.main_window['process'].get().split()[0]
        self.cli.stdin.write('attach -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # Detach按钮函数
    def textractor_detach(self):
        pid = self.main_window['process'].get().split()[0]
        self.cli.stdin.write('detach -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # 截取按钮函数
    def get_area(self):
        self.main_window.Hide()

        im = screenshot()
        im.save('Screenshot.png')

        full_size = size()
        screenshot_layout = [
            [sg.Graph(
                key='graph',
                canvas_size=full_size,
                graph_bottom_left=(0, 0),
                graph_top_right=full_size,
                drag_submits=True,
                enable_events=True,
            )],
        ]
        screenshot_window = sg.Window(
            'Canvas test',
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
            if event == 'graph':
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
                )
            elif not event.strip():
                screenshot_window.close()
                if self.x1 > self.x2:
                    self.x1, self.x2 = self.x2, self.x1
                if self.y1 > self.y2:
                    self.y1, self.y2 = self.y2, self.y1
                self.OCR_start()
            elif event == 'Escape:27':
                screenshot_window.close()

            if draging:
                x, y = position()
                graph.DeleteFigure(area)
                area = graph.DrawRectangle(
                    (self.x1, full_size[1] - self.y1),
                    (x, full_size[1] - y),
                )

        self.main_window.UnHide()

    # 开始按钮函数
    def OCR_start(self):
        if self.configs['continuously']:
            self.OCR_working = True
            self.OCR_thread = My_Thread(target=self.OCR_work)
            self.OCR_thread.daemon = True
            self.OCR_thread.start()
        else:
            self.OCR_work()

    # 结束按钮函数
    def OCR_stop(self):
        self.OCR_working = False
        if self.configs['continuously']:
            self.OCR_thread.stop()

    # 图片处理
    def image_process(self):
        im = Image.open("Area.png")
        im = im.convert("L")
        im = threshold_ways[self.configs['threshold_way']](im, self.configs['threshold'])
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
        text_extract = OCR(im, languages[self.configs['language']])
        self.text_process(text_extract)
        self.main_window['text_extract'].update(self.text)

        if self.configs['continuously']:
            sleep(self.configs['OCR_interval'])

    # 浮动按键函数
    def float_window(self):
        float_layout = [
            [
                sg.Frame(
                    '原文',
                    [[sg.Multiline('', key='text')]],
                ),
            ],
            [
                sg.Frame(
                    'jbeijing',
                    [[sg.Multiline('', key='text_translated')]],
                ),
            ],
        ]
        float_window = sg.Window(
            '',
            float_layout,
            alpha_channel=self.configs['alpha'],
            auto_size_text=True,
            margins=(0, 0),
            element_padding=(0, 0),
            resizable=True,
            force_toplevel=True,
            keep_on_top=True,
            grab_anywhere=True,
        )

        if self.textractor_working:
            interval = self.configs['textractor_interval']
        else:
            interval = self.configs['OCR_interval']

        text = ''
        while True:
            event, values = float_window.read(timeout=interval * 1000)
            if event is None:
                break
            if self.textractor_working or self.OCR_working:
                float_window['text'].update(self.text)
                float_window['text_translated'].update(self.text_translated)

        float_window.close()


if __name__ == '__main__':
    Main_Window()
    
    if os.path.exists('Screenshot.png'):
        os.remove('Screenshot.png')
    if os.path.exists('Area.png'):
        os.remove('Area.png')
    if os.path.exists('GPS.txt'):
        os.remove('GPS.txt')
