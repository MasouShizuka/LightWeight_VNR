import os
import re
import json
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE

import PySimpleGUI as sg
import psutil
from PIL import Image
from pyautogui import position, screenshot, size
from pynput import keyboard
from pyperclip import copy
from pywinauto.application import Application

from UI import UI, textractor_hook_code_layout, voiceload2_layout, floating_layout
from config import default_config
from game import (
    game_info,
    save_game,
    load_game,
    start_directly,
    start_with_locale_emulator,
)

from OCR.tesseract_OCR import pytesseract, languages, tesseract_OCR
from OCR.threshold_ways import threshold_ways

from Translator.jbeijing import JBeijing
from Translator.youdao import Youdao
from Translator.baidu import Baidu

from TTS.yukari import Yukari
from TTS.tamiyasu import Tamiyasu
from TTS.voiceroid2 import VOICEROID2


font_name = 'Microsoft Yahei'
font_size = 15
font = (font_name, font_size)

sg.theme('DarkGrey5')
sg.set_options(font=font)


def px_to_size(width, height):
    from tkinter.font import Font

    tkfont = Font(font=font)
    w, h = tkfont.measure('A'), tkfont.metrics('linespace')

    return width // w, height // h


class Main_Window:
    def __init__(self):
        # 默认设置参数
        self.config = default_config
        # 读取设置
        self.load_config()

        # 默认游戏信息
        self.game = game_info
        self.game_pid = None
        self.game_window = None
        # 读取游戏信息
        self.game, running = load_game()
        if running:
            self.game_update_curr(
                self.game['curr_game_id'], self.game['curr_game_name']
            )
        self.games = [i['name'] for i in self.game['game_list']]

        # Textractor相关变量
        self.textractor_working = False
        self.textractor_pause = False
        self.cli = None
        self.fixed_hook = None

        # OCR相关变量
        pytesseract.pytesseract.tesseract_cmd = os.path.join(
            self.config['tesseract_OCR_path'], 'tesseract.exe'
        )
        self.OCR_working = False
        self.OCR_pause = False
        self.screenshot = None
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        # 文本相关变量
        self.text_unprocessed = ''
        self.text = ''

        # JBeijing相关变量
        self.jbeijing = JBeijing(self.config)
        # 有道相关变量
        self.youdao = Youdao(self.config)
        # 百度相关变量
        self.baidu = Baidu(self.config)

        self.translators = {
            self.jbeijing.label: self.jbeijing,
            self.youdao.label: self.youdao,
            self.baidu.label: self.baidu,
        }
        self.text_translate = {
            translator.label: '' for translator in self.translators.values()
        }

        # TTS相关变量
        self.yukari = Yukari(self.config)
        self.tamiyasu = Tamiyasu(self.config)
        self.voiceroid2 = VOICEROID2(self.config)

        self.TTS = {
            self.yukari.label: self.yukari,
            self.tamiyasu.label: self.tamiyasu,
            self.voiceroid2.label: self.voiceroid2,
        }

        # 浮动窗口相关变量
        self.floating_working = False
        self.floating_window = None

        # 添加快捷键
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # 主窗口
        self.main_window = sg.Window(
            'LightWeight_VNR',
            UI(self.config, games=self.games, voiceroid2=self.voiceroid2),
            alpha_channel=self.config['alpha'],
            keep_on_top=self.config['top'],
            margins=(0, 0),
            resizable=True,
        )

        while True:
            event, values = self.main_window.read()
            if event is None:
                break

            # 游戏界面
            elif event == 'game_list':
                self.game_get_info()
            elif event == 'game_add':
                self.game_add_game()
            elif event == 'game_delete':
                self.game_delete_game()
            elif event == 'game_start':
                self.game_start_game()
            # 抓取界面
            elif event == 'textractor_refresh':
                self.textractor_refresh_process_list()
            elif event == 'textractor_fix':
                self.textractor_fix_hook()
            elif event == 'textractor_start':
                self.textractor_start()
            elif event == 'textractor_attach':
                self.textractor_attach()
            elif event == 'textractor_hook_code':
                self.textractor_hook_code()
            elif event == 'textractor_stop':
                self.textractor_stop()

            # 光学界面
            elif event == 'OCR_area':
                self.OCR_get_area()
            elif event == 'OCR_start':
                self.OCR_start()
            elif event == 'OCR_stop':
                self.OCR_stop()

            elif 'pause' in event:
                self.pause_or_resume()

            # 翻译界面
            elif event == 'youdao_start':
                self.youdao_start()
            elif event == 'youdao_stop':
                self.translators[self.youdao.label].stop()

            # 语音界面
            elif event == 'yukari_start':
                self.yukari_start()
            elif event == 'yukari_stop':
                self.TTS[self.yukari.label].stop()
            elif event == 'tamiyasu_start':
                self.tamiyasu_start()
            elif event == 'tamiyasu_stop':
                self.TTS[self.tamiyasu.label].stop()
            elif event == 'voiceroid2_modify':
                self.voiceroid2_modify()

            # 设置界面
            elif event.startswith('save'):
                self.save_config(values)

            # 浮动相关
            elif event.startswith('floating'):
                self.floating()

        # 退出程序时，关闭所有打开的程序
        for translator_label in self.translators:
            translator = self.translators[translator_label]
            try:
                translator.stop()
            except:
                pass
        for speaker_label in self.TTS:
            speaker = self.TTS[speaker_label]
            try:
                speaker.stop()
            except:
                pass

        if os.path.exists('Screenshot.png'):
            os.remove('Screenshot.png')
        if os.path.exists('Area.png'):
            os.remove('Area.png')

        # 关闭主窗口
        self.main_window.close()

    # 保存设置
    def save_config(self, values):
        confirm = sg.PopupYesNo('确认保存吗', title='确认', keep_on_top=True)
        flag = confirm == 'Yes'
        if flag:
            for k, v in values.items():
                if self.config.__contains__(k):
                    # 更新界面透明度
                    if k == 'alpha':
                        self.main_window.SetAlpha(v)
                    # 更新界面置顶状态
                    elif k == 'top':
                        self.main_window.TKroot.wm_attributes("-topmost", v)
                    else:
                        self.config[k] = v

            # 更新Tesseract_OCR路径
            pytesseract.pytesseract.tesseract_cmd = os.path.join(
                self.config['tesseract_OCR_path'], 'tesseract.exe'
            )

            # 各种翻译器更新设置
            for translator_label in self.translators:
                translator = self.translators[translator_label]
                translator.update_config(self.config)

            # 各种TTS更新设置
            for speaker_label in self.TTS:
                speaker = self.TTS[speaker_label]
                speaker.update_config(self.config, main_window=self.main_window)

            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

        return flag

    # 读取设置
    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.config = config

    # 文字处理
    def text_process(self, text):
        # 判断文本是不是与上一句重复
        if text == self.text_unprocessed:
            return
        self.text_unprocessed = text

        # 文本去重，aabbcc -> abc
        deduplication_aabbcc = int(self.config['deduplication_aabbcc'])
        if self.config['deduplication_aabbcc_auto']:
            l = len(text)
            i = 1
            while i < l:
                if text[i] == text[0]:
                    i += 1
                else:
                    break
            if i > 1:
                text_one = text[::i]
                text_two = text[1::i]
                if text_one == text_two:
                    text = text_one
        elif deduplication_aabbcc > 1:
            text = text[::deduplication_aabbcc]
        # 文本去重，abcabc -> abc
        deduplication_abcabc = int(self.config['deduplication_abcabc'])
        if self.config['deduplication_abcabc_auto']:
            l = len(text)
            i = 2
            while True:
                n = int(l / i)
                if n < 2:
                    break
                if l % i != 0:
                    i += 1
                    continue
                text_one = text[:n]
                flag = True
                for k in range(1, i):
                    if text[k * n : k * n + n] != text_one:
                        flag = False
                        break
                if flag:
                    text = text_one
                    break
                i += 1
        elif deduplication_abcabc > 1:
            text = text[: int(len(text) / deduplication_abcabc)]

        # 去除垃圾字符
        garbage_chars = self.config['garbage_chars']
        if len(garbage_chars) > 0:
            for i in re.split(r'\s+', self.config['garbage_chars']):
                text = text.replace(i, '')

        # 正则表达式，若规则匹配正确，则拼接各个()的内容
        re_config = self.config['re']
        if len(re_config) > 0:
            rule = re.compile(re_config)
            info = rule.match(text)
            if info:
                groups = info.groups()
                if len(groups) > 0:
                    text = ''.join(groups)

        self.text = text

        # 复制处理后的原文
        if self.config['copy']:
            copy(text)

        # 传给翻译器的原文去除换行符
        text = text.replace('\n', '')

        # 更新浮动窗口的原文
        if self.floating_working and self.config['floating_text_original']:
            self.floating_window['text_original'].update(text)
        # 更新抓取界面的原文
        elif not self.floating_working:
            self.main_window['textractor_text'].update('')
            self.main_window['textractor_text'].update('原文：', append=True)
            self.main_window['textractor_text'].update(
                '\n' + self.text + '\n\n', append=True
            )

        # TTS阅读
        for speaker_label in self.TTS:
            speaker = self.TTS[speaker_label]
            if speaker.working and speaker.constantly:
                thread = Thread(target=speaker.read_text, args=(text,), daemon=True)
                thread.start()

        # 翻译器翻译
        for translator_label in self.translators:
            translator = self.translators[translator_label]
            if translator.working:
                textarea = None
                if self.floating_working and translator.get_translate:
                    textarea = self.floating_window[translator.key]
                elif self.textractor_working:
                    textarea = self.main_window['textractor_text']
                elif self.OCR_working:
                    textarea = self.main_window['OCR_text']
                thread = Thread(
                    target=translator.thread,
                    args=(
                        text,
                        self.text_translate,
                        self.floating_working,
                        textarea,
                        self.game_focus,
                    ),
                    daemon=True,
                )
                thread.start()

    # 游戏列表点击函数
    def game_get_info(self):
        # 界面更新所选游戏的相关信息
        game_selected = self.main_window['game_list'].get()
        if len(game_selected) > 0:
            for game in self.game['game_list']:
                if game['name'] == game_selected[0]:
                    self.main_window['game_name'].update(game['name'])
                    self.main_window['game_path'].update(game['path'])
                    self.main_window['game_hook_code'].update(game['hook_code'])
                    self.main_window['game_start_mode'].update(value=game['start_mode'])
                    break

    # 添加按钮函数
    def game_add_game(self):
        game_name = self.main_window['game_name'].get()
        game_path = self.main_window['game_path'].get()
        game_hook_code = self.main_window['game_hook_code'].get()
        game_start_mode = self.main_window['game_start_mode'].get()
        # 若游戏名称未填写，则以程序名为游戏名，去掉exe后缀
        if not game_name:
            game_name = os.path.split(game_path)[1]
            game_name = os.path.splitext(game_name)[0]

        for game in self.game['game_list']:
            # 若已存在，则修改游戏列表
            if game['name'] == game_name or game['path'] == game_path:
                index = self.games.index(game['name'])
                self.games[index] = game_name
                self.main_window['game_list'].update(values=self.games)

                game['name'] = game_name
                game['path'] = game_path
                game['hook_code'] = game_hook_code
                game['start_mode'] = game_start_mode
                save_game(self.game)

                return

        # 若不存在，则添加到游戏列表
        self.games.append(game_name)
        self.main_window['game_list'].update(values=self.games)

        game = {
            'name': game_name,
            'path': game_path,
            'hook_code': game_hook_code,
            'start_mode': game_start_mode,
        }
        self.game['game_list'].append(game)
        save_game(self.game)

    # 删除按钮函数
    def game_delete_game(self):
        # 删除所选游戏的相关信息
        game_name = self.main_window['game_name'].get()
        for i in self.game['game_list']:
            if i['name'] == game_name:
                self.games.remove(game_name)
                self.main_window['game_list'].update(values=self.games)

                self.game['game_list'].remove(i)
                save_game(self.game)

                break

    # 启动游戏按钮函数
    def game_start_game(self):
        game_path = self.main_window['game_path'].get()
        if not os.path.exists(game_path):
            sg.Popup('提示', '游戏路径不正确', keep_on_top=True)
            return

        name = os.path.split(game_path)[1]
        mode = self.main_window['game_start_mode'].get()

        game_pid = None
        if mode == '直接启动':
            game_pid = start_directly(game_path)
        elif mode == 'Locale Emulator':
            locale_emulator_path = self.config['locale_emulator_path']
            if not os.path.exists(locale_emulator_path):
                sg.Popup('提示', 'Locale Emulator路径错误', keep_on_top=True)
                return
            game_pid = start_with_locale_emulator(locale_emulator_path, game_path, name)

        # 若游戏未启动，则直接返回
        if not game_pid:
            return None

        # 更新当前游戏信息
        self.game_update_curr(game_pid, name)
        self.main_window['textractor_process'].update(str(game_pid) + ' - ' + name)

        # 启动Textractor
        sleep(1)
        self.textractor_start()

        # 注入dll
        sleep(1)
        self.attach(game_pid)

        # 若游戏有特殊码，则写入
        hook_code = self.main_window['game_hook_code'].get()
        if hook_code:
            sleep(1)
            self.hook_code(game_pid, hook_code)

    # 更新正在运行的游戏信息
    def game_update_curr(self, pid, name):
        self.game_pid = pid

        self.game['curr_game_id'] = pid
        self.game['curr_game_name'] = name
        save_game(self.game)

        self.game_get_window()

    # 获取游戏的窗口
    def game_get_window(self):
        if self.game_pid:
            app = Application(backend='uia').connect(process=self.game_pid)
            self.game_window = app.top_window()

    # 聚焦游戏窗口
    def game_focus(self):
        if not self.game_window:
            self.game_get_window()

        if self.game_window:
            self.game_window.set_focus()

    # 刷新按钮函数
    def textractor_refresh_process_list(self):
        processes = []

        # 获取任务管理器中的应用列表的进程和pid
        rule = re.compile('(\d+)')
        cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Id'
        proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in proc.stdout:
            try:
                line = line.decode().strip()
                result = rule.match(line)
                if result:
                    id = result.group(1)
                    process_name = psutil.Process(int(id)).name()
                    process = id + ' - ' + process_name

                    processes.append(process)
            except:
                pass

        self.main_window['textractor_process'].update(values=processes)

        if self.game_window:
            game_process = str(self.game_pid) + ' - ' + self.game['curr_game_name']
            self.main_window['textractor_process'].update(game_process)

    # 固定钩子
    def textractor_fix_hook(self):
        rule = re.compile(r'^(\[.+?\])\s+(.+)$')
        content = rule.match(self.main_window['textractor_hook'].get())
        if content:
            self.fixed_hook = content.group(1)

    # 启动按钮函数
    def textractor_start(self):
        self.textractor_stop()

        TextractorCLI_path = os.path.join(
            self.config['textractor_path'], 'TextractorCLI.exe'
        )
        texthook_path = os.path.join(self.config['textractor_path'], 'texthook.dll')
        if not os.path.exists(TextractorCLI_path) or not os.path.exists(texthook_path):
            sg.Popup('提示', 'Textractor路径不正确', keep_on_top=True)
            return

        # 启动时自动更新进程列表
        self.textractor_refresh_process_list()

        textractor_thread = Thread(target=self.textractor_work, daemon=True)
        textractor_thread.start()
        self.textractor_working = True

    # 终止按钮函数
    def textractor_stop(self):
        # 终止时将抓取界面清空
        try:
            self.cli.kill()
        except:
            pass

        self.main_window['textractor_process'].update('')
        self.main_window['textractor_process'].update(values=[])
        self.main_window['textractor_hook'].update('')
        self.main_window['textractor_hook'].update(values=[])
        self.cli = None
        self.textractor_working = False

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
        rule = re.compile(r'^(\[.+?\])\s?(.*)$')
        hooks = {}
        for line in iter(self.cli.stdout.readline, ''):
            # 停止则跳出
            if not self.textractor_working:
                break
            # 暂停则跳过
            if self.textractor_pause:
                continue

            # 匹配每行的输出，分成钩子和内容的两部分
            content = rule.match(line)
            if content:
                hook = content.group(1)
                text = content.group(2)

                if hooks.__contains__(hook) and hooks[hook] == line:
                    continue

                # 存入字典
                hooks[hook] = line

                # 将当前钩子修改为固定钩子，若未固定则读取界面钩子列表当前的钩子
                textractor_hook = self.main_window['textractor_hook'].get()
                curr_hook = None
                if self.fixed_hook:
                    curr_hook = self.fixed_hook
                else:
                    content = rule.match(textractor_hook)
                    if content:
                        curr_hook = content.group(1)

                # 更新界面钩子列表
                self.main_window['textractor_hook'].update(values=list(hooks.values()))
                self.main_window['textractor_hook'].update(curr_hook)

                # 读取所选钩子的内容
                if curr_hook == hook:
                    self.text_process(text)

            sleep(float(self.config['textractor_interval']))

    def attach(self, pid):
        self.cli.stdin.write('attach -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # Attach按钮函数
    def textractor_attach(self):
        if not self.cli:
            sg.Popup('提示', 'Textractor未启动', keep_on_top=True)
            return

        pid = self.main_window['textractor_process'].get().split()
        if len(pid) == 0 or not pid[0].isdigit():
            sg.Popup('提示', '进程栏缺少进程id', keep_on_top=True)
            return

        try:
            game_pid = int(pid[0])
            name = psutil.Process(self.game_pid).name()

            self.attach(game_pid)
            self.game_update_curr(game_pid, name)
        except:
            pass

    def hook_code(self, pid, hook_code):
        self.cli.stdin.write(hook_code + ' -P' + str(pid) + '\n')
        self.cli.stdin.flush()

    # 特殊码按钮函数
    def textractor_hook_code(self):
        if not self.cli:
            sg.Popup('提示', 'Textractor未启动', keep_on_top=True)
            return

        layout = textractor_hook_code_layout

        window = sg.Window(
            '特殊码', layout, alpha_channel=self.config['alpha'], keep_on_top=True,
        )

        # 特殊码需满足特定的格式
        rule = re.compile(r'^/.+@.+$')
        while True:
            event, values = window.read()
            if event is None:
                break

            elif event == '使用':
                hook_code = window['hook_code'].get()
                if not rule.match(hook_code):
                    sg.Popup('提示', '特殊码格式不对', keep_on_top=True)
                else:
                    self.hook_code(self.game['curr_game_id'], hook_code)
                    sg.Popup('提示', '特殊码使用成功', keep_on_top=True)
                    break

        window.close()

    # 截取按钮函数
    def OCR_get_area(self):
        # 隐藏主窗口
        self.main_window.Hide()

        # 截取全屏
        im = screenshot()
        im.save('Screenshot.png')

        full_size = size()
        screenshot_layout = [
            [
                sg.Graph(
                    key='graph',
                    canvas_size=full_size,
                    drag_submits=True,
                    enable_events=True,
                    graph_bottom_left=(0, 0),
                    graph_top_right=full_size,
                    tooltip='按住左键划定区域\n按ESC退出',
                ),
            ],
        ]
        screenshot_window = sg.Window(
            '',
            screenshot_layout,
            element_padding=(0, 0),
            finalize=True,
            keep_on_top=True,
            margins=(0, 0),
            no_titlebar=True,
            return_keyboard_events=True,
        )
        screenshot_window.Maximize()
        graph = screenshot_window['graph']
        graph.DrawImage('Screenshot.png', location=(0, full_size[1]))

        dragging = False
        area = None
        while True:
            event, values = screenshot_window.read(timeout=10)
            if event is None:
                break

            # 鼠标按下，则记录起始坐标，并进入拖拽
            elif event == 'graph':
                if not dragging:
                    self.x1, self.y1 = position()
                dragging = True
            # 鼠标抬起，则记录终止坐标，并结束拖拽
            elif event == 'graph+UP':
                self.x2, self.y2 = position()
                dragging = False
                graph.DeleteFigure(area)
                area = graph.DrawRectangle(
                    (self.x1, full_size[1] - self.y1),
                    (self.x2, full_size[1] - self.y2),
                    line_color='red',
                )
            # 若按下回车，则完成截取
            elif not event.strip():
                screenshot_window.close()
                if self.x1 > self.x2:
                    self.x1, self.x2 = self.x2, self.x1
                if self.y1 > self.y2:
                    self.y1, self.y2 = self.y2, self.y1
                self.OCR_work()
            # 若按下ESC，则退出
            elif event == 'Escape:27':
                screenshot_window.close()

            # 若处于拖拽状态，则不断更新矩形的绘制
            if dragging:
                graph.DeleteFigure(area)
                x, y = position()
                area = graph.DrawRectangle(
                    (self.x1, full_size[1] - self.y1),
                    (x, full_size[1] - y),
                    line_color='red',
                )

        # 恢复主窗口
        self.main_window.UnHide()

    # 图片处理
    def image_process(self):
        im = Image.open("Area.png")
        # 转成灰度图
        im = im.convert("L")
        # 按指定方式处理图片
        im = threshold_ways[self.config['threshold_way']](im, self.config['threshold'])
        im.save('Area.png')

    # 截取矩形区域图片，进行图片处理，并进行文字识别
    def OCR_work(self):
        if not os.path.exists(self.config['tesseract_OCR_path']):
            sg.Popup('提示', 'Tesseract-OCR路径不正确', keep_on_top=True)
            return

        # 取得指定区域的图片
        bbox = [
            self.x1,
            self.y1,
            self.x2 - self.x1,
            self.y2 - self.y1,
        ]
        im = screenshot(region=bbox)
        im.save('Area.png')

        # 界面显示图片
        self.image_process()
        self.main_window['OCR_image'].update('Area.png')

        # 取得识别文本
        im = Image.open('Area.png')
        text_OCR = tesseract_OCR(im, languages[self.config['OCR_language']])

        if self.text_process(text_OCR):
            if not self.floating_working:
                self.main_window['OCR_text'].update(self.text + '\n\n')

    # OCR连续识别线程
    def OCR_thread(self):
        while self.OCR_working:
            if not self.OCR_pause:
                self.OCR_work()
            sleep(float(self.config['OCR_interval']))

    # 连续按钮函数
    def OCR_start(self):
        self.OCR_working = True
        OCR_thread = Thread(target=self.OCR_thread, daemon=True)
        OCR_thread.start()

    # 结束按钮函数
    def OCR_stop(self):
        self.OCR_working = False

    # Textractor和OCR的暂停按钮函数
    def pause_or_resume(self):
        button = None
        if self.textractor_working:
            self.textractor_pause = not self.textractor_pause

            if self.floating_working:
                button = self.floating_window['pause']
            else:
                button = self.main_window['textractor_pause']

            if self.textractor_pause:
                button.update('继续')
            else:
                button.update('暂停')
        elif self.OCR_working:
            self.OCR_pause = not self.OCR_pause

            if self.floating_working:
                button = self.floating_window['pause']
            else:
                button = self.main_window['OCR_pause']

            if self.OCR_pause:
                button.update('继续')
            else:
                button.update('暂停')

    # 有道启动按钮函数
    def youdao_start(self):
        youdaodict_path = os.path.join(self.config['youdao_path'], 'YoudaoDict.exe')
        if not os.path.exists(youdaodict_path):
            sg.Popup('提示', '有道词典路径不正确', keep_on_top=True)
        else:
            self.translators[self.youdao.label].start()

    # yukari启动按钮函数
    def yukari_start(self):
        yukari_path = os.path.join(self.config['yukari_path'], 'VOICEROID.exe')
        if not os.path.exists(yukari_path):
            sg.Popup('提示', 'Yukari路径不正确', keep_on_top=True)
        else:
            self.TTS[self.yukari.label].start()

    # tamiyasu启动按钮函数
    def tamiyasu_start(self):
        tamiyasu_path = os.path.join(self.config['tamiyasu_path'], 'VOICEROID.exe')
        if not os.path.exists(tamiyasu_path):
            sg.Popup('提示', 'Tamiyasu路径不正确', keep_on_top=True)
        else:
            self.TTS[self.tamiyasu.label].start()

    # VOICEROID2修改具体数值按钮函数
    def voiceroid2_modify(self):
        layout = voiceload2_layout(self.config)

        window = sg.Window(
            'VOICEROID2修改具体数值',
            layout,
            alpha_channel=self.config['alpha'],
            element_justification='center',
            keep_on_top=True,
        )

        while True:
            event, values = window.read()
            if event is None:
                break

            elif event == '保存':
                if self.save_config(values):
                    for k, v in values.items():
                        value = float(window[k].get())
                        values[k] = value
                        self.main_window[k].update(value)

        window.close()

    def read_curr_text(self):
        text = self.text.replace('\n', '')

        flag = True
        # 对于所有已启动TTS，则调用其阅读
        for speaker_label in self.TTS:
            speaker = self.TTS[speaker_label]
            if speaker.working:
                thread = Thread(target=speaker.read, args=(text,), daemon=True)
                thread.start()

                flag = False
        if flag:
            sg.Popup('提示', '请先启动TTS', keep_on_top=True)

    def on_press(self, key):
        # ; -> 暂停
        # ' -> 阅读当前文本
        try:
            k = key.char
            if k == ';':
                self.pause_or_resume()
            elif k == '\'':
                self.read_curr_text()
        except:
            pass

    # 浮动按键函数
    def floating(self):
        multiline_width = 96
        # 设定浮动窗口宽度与游戏宽度相同
        if self.game_window:
            rectangle = self.game_window.rectangle()
            multiline_width, _ = px_to_size(rectangle.width(), 0)

        layout = floating_layout(self.config, self.translators, multiline_width)
        right_click_menu = ['&Right', ['关闭']]
        self.floating_window = sg.Window(
            '',
            layout,
            alpha_channel=self.config['alpha'],
            auto_size_text=True,
            element_padding=(0, 0),
            grab_anywhere=True,
            keep_on_top=True,
            margins=(0, 0),
            no_titlebar=True,
            resizable=True,
            return_keyboard_events=True,
            right_click_menu=right_click_menu,
        )

        # 设定浮动窗口初始位置为游戏窗口左下角
        if self.game_window:
            rectangle = self.game_window.rectangle()
            left = rectangle.left + 10
            bottom = rectangle.bottom
            self.floating_window.Location = (left, bottom)

        # 最小化主窗口
        self.main_window.Minimize()

        self.floating_working = True
        while True:
            event, values = self.floating_window.read()
            if event is None:
                break

            elif event == '关闭' or event == 'Escape:27':
                break
            elif event == 'pause':
                self.pause_or_resume()
            elif event == 'read':
                self.read_curr_text()

        # 关闭浮动窗口并恢复主窗口
        self.floating_window.close()
        self.floating_window = None
        self.floating_working = False

        # 更新主界面的暂停状态
        self.pause_or_resume()
        self.pause_or_resume()

        self.main_window.Normal()


if __name__ == '__main__':
    Main_Window()
