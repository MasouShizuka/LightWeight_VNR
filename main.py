import os
import cv2
import json
import pytesseract
from tkinter import ttk, IntVar, DoubleVar, StringVar, Toplevel, Tk, messagebox, PhotoImage, Text, Scale
from pyautogui import position, screenshot
from pyperclip import copy
from time import sleep
from OCR_thread import OCR_thread

# 若系统未安装Tesseract-OCR,则需要指定位置
path = os.path.abspath('.')
path_cmd = path + '/Tesseract-OCR/tesseract.exe'
path_tessdata = path + '/Tesseract-OCR/tessdata'

pytesseract.pytesseract.tesseract_cmd = path_cmd
tessdata_dir_config = '--tessdata-dir "' + path_tessdata + '"'

# 语言种类
languages = {
    '日文': 'jpn',
    '简体中文': 'chi_sim',
    '繁体中文': 'chi_tra',
    '英文': 'eng'
}
lang_translate = [i for i in languages]
lang = [i for i in languages.values()]

# 图片处理方式
threshold_ways = {
    'TOZERO': cv2.THRESH_TOZERO,
    'TOZERO_INV': cv2.THRESH_TOZERO_INV,
    'BINARY': cv2.THRESH_BINARY,
    'BINARY_INV': cv2.THRESH_BINARY_INV,
    'TRUNC': cv2.THRESH_TRUNC,
}
threshold_name = [i for i in threshold_ways]
threshold_way = [i for i in threshold_ways.values()]

class OCR_window(Tk):
    def __init__(self):
        super().__init__()

        # 读取设置
        self.load_config()

        # 起始坐标
        self.x1 = 0
        self.y1 = 0
        # 终止坐标
        self.x2 = 0
        self.y2 = 0

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side='right', fill='y', padx=20)

        self.button_choose = ttk.Button(
            self.button_frame,
            text='截取',
            width=10,
            command=self.get_area,
        )
        self.button_choose.grid(row=0, pady=50)

        self.button_start = ttk.Button(
            self.button_frame,
            text='开始',
            width=10,
            command=self.start_extracting,
        )
        self.button_start.grid(row=1, pady=50)

        self.button_stop = ttk.Button(
            self.button_frame,
            text='结束',
            width=10,
            command=self.stop_extracting,
        )
        self.button_stop.grid(row=2, pady=50)

        self.button_config = ttk.Button(
            self.button_frame,
            text='设置',
            width=10,
            command=self.config,
        )
        self.button_config.grid(row=3, pady=50)

        self.button_help = ttk.Button(
            self.button_frame,
            text='帮助',
            width=10,
            command=self.help,
        )
        self.button_help.grid(row=4, pady=50)

        self.label_pic = ttk.Label(self)
        self.label_pic.pack()
        self.label_info = ttk.Label(self, text='提取文本', font=('微软雅黑', 12))
        self.label_info.pack()
        self.frame_text = ttk.Frame(self, relief='ridge', borderwidth=10)
        self.frame_text.pack()
        self.scrollbar_text = ttk.Scrollbar(self.frame_text)
        self.scrollbar_text.pack(side='right', fill='y')
        self.text_text = Text(
            self.frame_text,
            font=('微软雅黑', 15),
            yscrollcommand=self.scrollbar_text.set,
        )
        self.text_text.pack()
        self.scrollbar_text.config(command=self.text_text.yview)
    
    # 存储设置
    def save_config(self):
        configs = {
            'alpha': self.alpha,
            'language': self.language,
            'times': self.times,
            'interval': self.interval,
            'copy': self.copy,
            'threshold_way': self.threshold_way,
            'threshold': self.threshold,
        }
        with open('config.json', 'w') as f:
            json.dump(configs, f, indent = 4)

    # 读取设置
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                configs = json.load(f)
            self.alpha = configs['alpha']
            self.language = configs['language']
            self.times = configs['times']
            self.interval = configs['interval']
            self.copy = configs['copy']
            self.threshold_way = configs['threshold_way']
            self.threshold = configs['threshold']
        else:
            self.alpha = 1.0
            self.language = 'jpn'
            self.times = 'constant'
            self.interval = 1
            self.copy = 1
            self.threshold_way = cv2.THRESH_TOZERO
            self.threshold = 127
            

    # 划定矩形区域
    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x1, self.y1 = position()

        elif event == cv2.EVENT_LBUTTONUP:
            self.x2, self.y2 = position()
            cv2.rectangle(
                self.screenshot,
                (self.x1, self.y1),
                (self.x2, self.y2),
                (0, 0, 255),
                0,
            )

        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            im = self.screenshot.copy()
            cv2.rectangle(
                im,
                (self.x1, self.y1),
                (x, y),
                (0, 0, 255),
                0,
            )
            cv2.imshow('image', im)

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.screenshot = cv2.imread('screenshot.png')
            cv2.imshow('image', self.screenshot)

    # 截取按钮函数
    def get_area(self):
        self.withdraw()
        im = screenshot()
        im.save('screenshot.png')

        self.screenshot = cv2.imread('screenshot.png')
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback('image', self.draw_rectangle)
        cv2.imshow('image', self.screenshot)

        key = cv2.waitKey(0) & 0xFF
        if key == 13:
            if self.x1 > self.x2:
                self.x1, self.x2 = self.x2, self.x1

            if self.y1 > self.y2:
                self.y1, self.y2 = self.y2, self.y1

        cv2.destroyAllWindows()

        if self.times == 'once':
            self.extracting()

        self.deiconify()

    # 开始按钮函数
    def start_extracting(self):
        if self.times == 'constant':
            self.OCR_thread = OCR_thread(target=self.extracting)
            self.OCR_thread.daemon = True
            self.OCR_thread.start()

        elif self.times == 'once':
            self.extracting()

    # 结束按钮函数
    def stop_extracting(self):
        if self.times == 'constant':
            self.OCR_thread.stop()

    # 图片处理
    def image_process(self):
        im = cv2.imread('area.png')
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, im = cv2.threshold(im, self.threshold, 255, self.threshold_way)
        cv2.imwrite('area.png', im)

    # 截取矩形区域图片，进行图片处理，并进行文字识别
    def extracting(self):
        bbox = [
            self.x1,
            self.y1,
            self.x2 - self.x1,
            self.y2 - self.y1,
        ]
        im = screenshot(region=bbox)
        im.save('area.png')

        self.image_process()

        global photoimage_img
        photoimage_img = PhotoImage(file='area.png')
        self.label_pic.config(image=photoimage_img)

        im = cv2.imread('area.png')
        text_extract = pytesseract.image_to_string(
            im,
            lang=self.language,
            config='--psm 6',
        )

        self.text_text.delete('1.0', 'end')
        self.text_text.insert('1.0', text_extract)

        if self.copy:
            copy(text_extract)

        if self.times == 'constant':
            sleep(self.interval)

    # 设置按钮函数
    def config(self):
        def config_alpha(value):
            alpha_get = alpha.get()
            self.alpha = alpha_get
            self.attributes('-alpha', alpha_get)
            window_config.attributes('-alpha', alpha_get)

        def config_configure():
            configure = messagebox.askyesno('Configure', '确定更改吗')
            if configure:
                self.interval = interval.get()
                self.threshold = threshold.get()
                self.copy = copy.get()
                self.times = times.get()
                self.language = languages[combobox_language.get()]
                self.threshold_way = threshold_ways[combobox_threshold_way.get()]

                window_config.destroy()
                self.save_config()
            else:
                window_config.attributes('-topmost', True)
                window_config.attributes('-topmost', False)

        global window_config
        try:
            window_config.destroy()
        except:
            pass

        window_config = Toplevel(self)
        window_config.title('Config')
        window_config.geometry('400x500')
        window_config.attributes('-alpha', self.alpha)

        configs = ttk.Frame(window_config)
        configs.pack(side='top')

        label_alpha = ttk.Label(configs, text='透明度:')
        label_alpha.grid(row=0, column=0, sticky='e')
        alpha = DoubleVar()
        alpha.set(self.alpha)
        scale_alpha = Scale(
            configs,
            length=250,
            variable=alpha,
            from_=0,
            to=1,
            resolution=0.01,
            tickinterva=1,
            orient='horizontal',
            command=config_alpha,
        )
        scale_alpha.grid(row=0, column=1, columnspan=2, padx=30, sticky='w')

        label_language = ttk.Label(configs, text='识别语言:')
        label_language.grid(row=1, column=0, sticky='e')
        combobox_language = ttk.Combobox(
            configs,
            values=lang_translate,
            width=10,
        )
        combobox_language.grid(row=1, column=1, padx=30, pady=15, sticky='w')
        combobox_language.current(lang.index(self.language))

        label_times = ttk.Label(configs, text='截屏方式:')
        label_times.grid(row=2, column=0, sticky='e')
        times = StringVar()
        times.set(self.times)

        way_once = ttk.Radiobutton(
            configs,
            text='单次截屏',
            variable=times,
            value='once',
        )
        way_once.grid(row=2, column=1, padx=30, pady=15, sticky='w')

        way_constant = ttk.Radiobutton(
            configs,
            text='连续截屏',
            variable=times,
            value='constant',
        )
        way_constant.grid(row=2, column=2, padx=30, pady=15, sticky='w')

        label_interval = ttk.Label(configs, text='截屏间隔:')
        label_interval.grid(row=3, column=0, sticky='e')
        interval = DoubleVar()
        interval.set(self.interval)
        entry_interval = ttk.Entry(
            configs,
            width=10,
            textvariable=interval,
        )
        entry_interval.grid(row=3, column=1, padx=30, pady=15, sticky='w')

        label_copy = ttk.Label(configs, text='复制到剪切板:')
        label_copy.grid(row=4, column=0, sticky='e')
        copy = IntVar()
        copy.set(self.copy)
        checkbutton_copy = ttk.Checkbutton(
            configs,
            variable=copy,
            onvalue=1,
            offvalue=0,
        )
        checkbutton_copy.grid(row=4, column=1, padx=30, pady=15, sticky='w')

        label_threshold_way = ttk.Label(configs, text='阈值化方式:')
        label_threshold_way.grid(row=5, column=0, sticky='e')
        combobox_threshold_way = ttk.Combobox(
            configs,
            values=threshold_name,
            width=10,
        )
        combobox_threshold_way.grid(row=5, column=1, padx=30, pady=15, sticky='w')
        combobox_threshold_way.current(threshold_way.index(self.threshold_way))

        label_threshold = ttk.Label(configs, text='阈值:')
        label_threshold.grid(row=6, column=0, sticky='e')
        threshold = IntVar()
        threshold.set(self.threshold)
        scale_threshold = Scale(
            configs,
            length=250,
            variable=threshold,
            from_=0,
            to=255,
            resolution=1,
            tickinterva=255,
            orient='horizontal',
        )
        scale_threshold.grid(row=6, column=1, columnspan=2, padx=30, sticky='w')

        config_change = ttk.Frame(window_config)
        config_change.pack(side='bottom')
        button_configure = ttk.Button(
            config_change,
            text='更改',
            width=10,
            command=config_configure,
        )
        button_configure.pack()

        window_config.mainloop()

    # 帮助按钮函数
    def help(self):
        info = '\
截取屏幕上的某一区域，用鼠标划定区域，划定时可按右键撤销划定区域，划定完按回车；若想取消划定操作，按ESC键。\n\n\
若设置中选择单次截屏，则截取完直接显示。\n\n\
若设置中选择连续截屏，则截取完后按开始，进行某一间隔的连续识别；按结束则结束识别。\n\n\
根据程序显示的图片效果，可以调整阈值和阈值化方式来使得图片中的文字更加容易被识别。'
        messagebox.showinfo('帮助', info)


if __name__ == '__main__':
    window = OCR_window()
    window.title('VNR OCR')
    window.geometry('1280x720')
    window.attributes('-alpha', 1.0)
    window.mainloop()

    if os.path.exists('screenshot.png'):
        os.remove('screenshot.png')
    if os.path.exists('area.png'):
        os.remove('area.png')
