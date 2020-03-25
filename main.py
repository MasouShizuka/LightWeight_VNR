import PySimpleGUI as sg
import os
import json
from PIL import Image
from pyautogui import position, screenshot, size
from pyperclip import copy
from time import sleep
from OCR_thread import OCR_thread
from tesseract_ocr import languages, lang_translate, OCR
from threshold_ways import threshold_ways, threshold_name
from jbeijing import jbeijing, DLL

sg.theme('DarkGrey5')
sg.set_options(font=('微软雅黑', 15))

class OCR_window(object):
    def __init__(self):
        super().__init__()

        # 默认设置参数
        self.alpha = 1.0
        self.language = '日文'
        self.continuously = False
        self.interval = 1
        self.copy = True
        self.threshold_way = 'BINARY'
        self.threshold = 127
        self.jbeijing = False
        self.jbeijing_path = None

        # 读取设置
        self.load_config()

        self.screenshot = None
        self.OCR_thread = None
        self.working = False
        self.text = None
        self.text_translated = None

        # 起始坐标
        self.x1 = 0
        self.y1 = 0
        # 终止坐标
        self.x2 = 0
        self.y2 = 0

        main_OCR = [
            [
                sg.Frame(
                    'Image',
                    [[sg.Image('', key='image')]],
                )
            ],
            [
                sg.Frame(
                    '提取文本',
                    [[sg.Multiline('提取文本', key='text_extract', size=(70, 15))]],
                )
            ],
        ]

        main_buttons = [
            [sg.Button('截取', pad=(0, 20))],
            [sg.Button('开始', pad=(0, 20))],
            [sg.Button('结束', pad=(0, 20))],
            [sg.Button('设置', pad=(0, 20))],
            [sg.Button('帮助', pad=(0, 20))],
            [sg.Button('依附', pad=(0, 20))],
        ]

        main_layout = [
            [
                sg.Column(main_OCR, element_justification='center'),
                sg.Column(main_buttons),
            ],
        ]

        self.main_window = sg.Window(
            'VNR_OCR',
            main_layout,
            size=(1280, 720),
            resizable=True,
            alpha_channel=self.alpha,
        )

        while True:
            event, values = self.main_window.read()
            if event in (None,):
                break
            elif event == '截取':
                self.get_area()
            elif event == '开始':
                self.start_extracting()
            elif event == '结束':
                self.stop_extracting()
            elif event == '设置':
                self.config()
            elif event == '帮助':
                self.help()
            elif event == '依附':
                self.attach()

        self.main_window.close()

    # 存储设置
    def save_config(self):
        configs = {
            'alpha': self.alpha,
            'language': self.language,
            'continuously': self.continuously,
            'interval': self.interval,
            'copy': self.copy,
            'threshold_way': self.threshold_way,
            'threshold': self.threshold,
            'jbeijing': self.jbeijing,
            'jbeijing_path': self.jbeijing_path,
        }
        with open('config.json', 'w') as f:
            json.dump(configs, f, indent=4)

    # 读取设置
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                configs = json.load(f)
            self.alpha = configs['alpha']
            self.language = configs['language']
            self.continuously = configs['continuously']
            self.interval = configs['interval']
            self.copy = configs['copy']
            self.threshold_way = configs['threshold_way']
            self.threshold = configs['threshold']
            self.jbeijing = configs['jbeijing']
            self.jbeijing_path = configs['jbeijing_path']

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
                self.start_extracting()
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
    def start_extracting(self):
        if self.continuously:
            self.working = True
            self.OCR_thread = OCR_thread(target=self.extracting)
            self.OCR_thread.daemon = True
            self.OCR_thread.start()
        else:
            self.extracting()

    # 结束按钮函数
    def stop_extracting(self):
        self.working = False
        if self.continuously:
            self.OCR_thread.stop()

    # 图片处理
    def image_process(self):
        im = Image.open("Area.png")
        im = im.convert("L")
        im = threshold_ways[self.threshold_way](im, self.threshold)
        im.save('Area.png')

    # 文字处理
    def text_process(self, text):
        text = text.replace('|', '')
        text = text.replace('「', '')
        text = text.replace('」', '')
        text = text.replace('[', '')
        text = text.replace(']', '')
        self.text = text
        if self.jbeijing:
            dll_path = os.path.join(self.jbeijing_path, DLL)
            if os.path.exists(dll_path):
                self.text_translated = jbeijing(text.replace('\n', ''), dll_path)
                text += '\n\n' + self.text_translated
        return text

    # 截取矩形区域图片，进行图片处理，并进行文字识别
    def extracting(self):
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
        text_extract = OCR(im, languages[self.language])
        text = self.text_process(text_extract)
        self.main_window['text_extract'].update(text)

        if self.copy:
            copy(text_extract)

        if self.continuously:
            sleep(self.interval)

    # 设置按钮函数
    def config(self):
        config_configs = [
            [
                sg.Text('透明度：'),
                sg.Slider(
                    key='alpha',
                    default_value=self.alpha,
                    size=(100, 10),
                    range=(0, 1.0),
                    orientation='h',
                    resolution=0.01,
                    tick_interval=1,
                ),
            ],
            [
                sg.Text('识别语言：'),
                sg.OptionMenu(
                    lang_translate,
                    key='language',
                    default_value=self.language,
                    size=(14,),
                ),
            ],
            [
                sg.Text('截屏方式：'),
                sg.Radio(
                    '单次截屏',
                    'continuously',
                    key='once',
                    default=not self.continuously,
                ),
                sg.Radio(
                    '连续截屏',
                    'continuously',
                    default=self.continuously,
                ),
            ],
            [
                sg.Text('截屏间隔：'),
                sg.Input(
                    key='interval',
                    default_text=self.interval,
                    size=(17,),
                ),
            ],
            [
                sg.Text('复制到剪切板：'),
                sg.Checkbox(
                    '',
                    key='copy',
                    default=self.copy,
                )
            ],
            [
                sg.Text('阈值化方法：'),
                sg.OptionMenu(
                    threshold_name,
                    key='threshold_way',
                    default_value=self.threshold_way,
                    size=(12,),
                ),
            ],
            [
                sg.Text('阈值：'),
                sg.Slider(
                    key='threshold',
                    default_value=self.threshold,
                    size=(100, 10),
                    range=(0, 255),
                    orientation='h',
                    resolution=1,
                    tick_interval=255,
                ),
            ],
            [
                sg.Text('Jbeijing：'),
                sg.Checkbox(
                    '',
                    key='jbeijing',
                    default=self.jbeijing,
                )
            ],
            [
                sg.Text('Jbeijing路径：'),
                sg.Input(
                    key='jbeijing_path',
                    default_text=self.jbeijing_path,
                    size=(18,),
                ),
                sg.FolderBrowse(
                    '目录',
                    key='jbeijing_dir',
                ),
            ],
            [sg.Button('更改')],
        ]
        config_layout = [
            [sg.Column(config_configs, element_justification='l')],
        ]
        config_window = sg.Window(
            '设置',
            config_layout,
            size=(600, 600),
            alpha_channel=self.alpha,
        )

        while True:
            event, values = config_window.read(timeout=10)
            if event is None:
                break
            self.alpha = values['alpha']
            self.main_window.SetAlpha(self.alpha)
            config_window.SetAlpha(self.alpha)
            if event == '更改':
                confirm = sg.PopupYesNo('确认更改吗', title='确认')
                if confirm == 'Yes':
                    self.alpha = values['alpha']
                    self.language = values['language']
                    self.continuously = not values['once']
                    self.interval = int(values['interval'])
                    self.copy = values['copy']
                    self.threshold_way = values['threshold_way']
                    self.threshold = values['threshold']
                    self.jbeijing = values['jbeijing']
                    self.jbeijing_path = values['jbeijing_path']

                    self.save_config()
                    break
        config_window.close()

    # 帮助按钮函数
    def help(self):
        info = '\
截取屏幕上的某一区域，用鼠标划定区域，划定完按回车；若想取消划定操作，按ESC键。\n\n\
若设置中选择单次截屏，则截取完直接显示。\n\n\
若设置中选择连续截屏，则截取完后按开始，进行某一间隔的连续识别；按结束则结束识别。\n\n\
根据程序显示的图片效果，可以调整阈值和阈值化方式来使得图片中的文字更加容易被识别。'
        sg.Popup(info, title='帮助')

    def attach(self):
        self.main_window.Hide()

        float_layout = [
            [
                sg.Text(
                    self.text,
                    key='text',
                )
            ],
            [
                sg.Text(
                    '',
                )
            ],
            [
                sg.Text(
                    self.text,
                    key='text_translated',
                )
            ],
        ]
        float_window = sg.Window(
            '',
            float_layout,
            alpha_channel=self.alpha,
            auto_size_text=True,
            margins=(0, 0),
            element_padding=(0, 0),
            resizable=True,
            force_toplevel=True,
            keep_on_top=True,
            grab_anywhere=True
        )

        while True:
            event, values = float_window.read(timeout=self.interval*1000)
            if event is None:
                break
            if self.working:
                text = self.text
                text_translated = self.text_translated
                float_window['text'].update(text)
                float_window['text_translated'].update(text_translated)

        float_window.close()
        self.main_window.UnHide()


if __name__ == '__main__':
    OCR_window()
    if os.path.exists('Screenshot.png'):
        os.remove('Screenshot.png')
    if os.path.exists('Area.png'):
        os.remove('Area.png')
    if os.path.exists('GPS.txt'):
        os.remove('GPS.txt')
