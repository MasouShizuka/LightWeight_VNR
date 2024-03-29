import os
from threading import Thread
from time import sleep

import pytesseract
from PIL import Image
from pyautogui import screenshot

from OCR.threshold_ways import threshold_ways


class Tesseract_OCR:
    languages = {
        '日文': 'jpn',
        '日文（竖）': 'jpn_vert',
        '简体中文': 'chi_sim',
        '简体中文（竖）': 'chi_sim_vert',
        '繁体中文': 'chi_tra',
        '繁体中文（竖）': 'chi_tra_vert',
        '英文': 'eng',
    }

    def __init__(self, config):
        self.working = False
        self.pause = False
        self.bbox = [0, 0, 0, 0]

        self.update_config(config)

    def update_config(self, config):
        self.path = config['tesseract_OCR_path']
        self.language = self.languages[config['tesseract_OCR_language']]
        self.interval = float(config['OCR_interval'])
        self.threshold_way = config['threshold_way']
        self.threshold = config['threshold']

        # 更新Tesseract_OCR路径
        pytesseract.pytesseract.tesseract_cmd = os.path.join(self.path, 'tesseract.exe')

    # 识别图片文字
    def OCR(self, im):
        text_extract = ''
        try:
            config = '-c preserve_interword_spaces=1'
            if 'vert' in self.language:
                config += ' --psm 5'
            else:
                config += ' --psm 6'
            text_extract = pytesseract.image_to_string(
                im, lang=self.language, config=config
            )
        except:
            pass

        return text_extract

    # 图片处理
    def image_process(self, image):
        # 转成灰度图
        image = image.convert('L')
        # 按指定方式处理图片
        image = threshold_ways[self.threshold_way](image, self.threshold)
        image.save('Area.png')

        return image

    # 截取矩形区域图片，进行图片处理，并进行文字识别
    def thread(self, update_image=None, text_process=None, bbox=None):
        try:
            # 取得指定区域的位置
            if bbox:
                self.bbox = bbox
                self.working = True

            image = screenshot(region=self.bbox)
            image = self.image_process(image)

            # 界面显示图片
            update_image('Area.png')

            # 取得识别文本
            text_OCR = self.OCR(image)
            text_process(text_OCR)

            if bbox:
                self.working = False
        except:
            pass

    # 连续截取识别
    def thread_continuous(self, update_image, text_process):
        while self.working:
            if not self.pause:
                self.thread(update_image=update_image, text_process=text_process)
            sleep(self.interval)

    # 连续
    def start(self, update_image=None, text_process=None):
        self.working = True
        thread = Thread(
            target=self.thread_continuous, args=(update_image, text_process), daemon=True
        )
        thread.start()

    # 结束
    def stop(self):
        self.working = False

        if os.path.exists('Area.png'):
            os.remove('Area.png')
