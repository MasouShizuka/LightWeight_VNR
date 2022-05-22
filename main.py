import json
import os
import re
from subprocess import PIPE, Popen
from threading import Thread
from time import sleep

import dearpygui.dearpygui as dpg
import psutil
from pyautogui import screenshot
from pynput import keyboard
from pyperclip import copy
from pywinauto.application import Application

from config import default_config
from game import (
    game_info,
    load_game,
    save_game,
    start_directly,
    start_with_locale_emulator,
)
from OCR.tesseract_OCR import Tesseract_OCR
from textractor import Textractor
from Translator.baidu import Baidu
from Translator.youdao import Youdao
from TTS.tamiyasu import Tamiyasu
from TTS.voiceroid2 import VOICEROID2
from TTS.voicevox import VOICEVOX
from TTS.yukari import Yukari
from ui import floating_window, main_window, popup, registry_font


class LightWeight_VNR:
    def __init__(self) -> None:
        # 默认设置参数
        self.config = default_config
        # 读取设置
        self.load_config()

        dpg.create_context()

        # 设置字体
        registry_font(self.config['font_size'])

        # 主窗口
        main_window()
        # 配置主窗口中 item 的 value 和 callback
        for k, v in self.config.items():
            if dpg.does_item_exist(k):
                dpg.set_value(k, v)
                dpg.set_item_callback(k, self.save_config)
        for attr in dir(self):
            if dpg.does_item_exist(attr):
                dpg.set_item_callback(attr, getattr(self, attr))

        # 小窗口
        self.floating_working = False
        floating_window()
        dpg.set_item_callback('floating_pause', self.pause_or_resume)
        dpg.set_item_callback('floating_read', self.read_curr_text)
        # 小窗口拖动
        with dpg.handler_registry():

            def callback(sender, app_data, user_data):
                if dpg.is_item_shown('floating_window'):
                    x_pos, y_pos = dpg.get_viewport_pos()
                    x, y = app_data[1:]
                    dpg.set_viewport_pos([x_pos + x, y_pos + y])

            dpg.add_mouse_drag_handler(callback=callback)

        # 截屏窗口
        with dpg.window(tag='screenshot_window', show=False):
            dpg.add_text(
                tag='OCR_screenshot',
                show=False,
            )

        # 默认游戏信息
        self.game_info = game_info
        self.game_pid = None
        self.game_window = None
        # 读取游戏信息
        self.game_info, running = load_game()
        self.games = [i['name'] for i in self.game_info['game_list']]
        if len(self.games) > 0:
            dpg.configure_item('game_list', items=self.games)
            self.game_list(None, self.games[0], None)

        # 文本相关变量
        self.text_unprocessed = ''
        self.text = ''

        # Textractor相关变量
        self.textractor = Textractor(self.config)

        # OCR相关变量
        self.tesseract_OCR = Tesseract_OCR(self.config)
        dpg.configure_item(
            'tesseract_OCR_language',
            items=list(self.tesseract_OCR.languages.keys()),
        )

        # 翻译器相关变量
        self.youdao = Youdao(self.config)
        self.baidu = Baidu(self.config)

        self.translators = {
            self.youdao.label: self.youdao,
            self.baidu.label: self.baidu,
        }

        # TTS相关变量
        self.yukari = Yukari(self.config)
        self.tamiyasu = Tamiyasu(self.config)
        self.voiceroid2 = VOICEROID2(
            self.config,
            set_voice=lambda items, voice: (
                dpg.configure_item('voiceroid2_voice_selected', items=items),
                dpg.set_value('voiceroid2_voice_selected', voice),
            ),
        )
        self.voicevox = VOICEVOX(self.config)

        self.TTS = {
            self.yukari.label: self.yukari,
            self.tamiyasu.label: self.tamiyasu,
            self.voiceroid2.label: self.voiceroid2,
            self.voicevox.label: self.voicevox,
        }

        # 快捷键监听
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # 若游戏正在运行，则更新信息
        if running:
            self.game_update(
                self.game_info['curr_game_id'],
                self.game_info['curr_game_name'],
                self.game_info['curr_game_hook'],
            )

        dpg.create_viewport(
            title='LightWeight_VNR',
            width=1280,
            height=720,
            min_width=1,
            min_height=1,
            always_on_top=self.config['top'],
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('main_window', True)
        dpg.start_dearpygui()
        dpg.destroy_context()

        # 退出程序时，关闭所有打开的程序
        self.textractor.stop()

        self.tesseract_OCR.stop()

        for translator_label in self.translators:
            translator = self.translators[translator_label]
            translator.stop()

        for speaker_label in self.TTS:
            speaker = self.TTS[speaker_label]
            speaker.stop()

    # 保存设置
    def save_config(self, sender, app_data, user_data):
        if self.config.__contains__(sender):
            self.config[sender] = app_data

            # Textractor更新设置
            self.textractor.update_config(self.config)

            # Tesseract_OCR更新设置
            self.tesseract_OCR.update_config(self.config)

            # 各种翻译器更新设置
            for translator_label in self.translators:
                translator = self.translators[translator_label]
                translator.update_config(self.config)

            # 各种TTS更新设置
            for speaker_label in self.TTS:
                speaker = self.TTS[speaker_label]
                speaker.update_config(self.config)

            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

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
            for i in re.split(r'\s+', garbage_chars):
                text = text.replace(i, '')

        # TTS 连续阅读条件
        read = False
        # 若文本包含连续阅读特征，则阅读
        if self.config['TTS_continuous']:
            TTS_continuous_feature = self.config['TTS_continuous_feature']
            if len(TTS_continuous_feature) > 0:
                for i in re.split(r'\s+', TTS_continuous_feature):
                    if i in text:
                        read = True
                        break
            # 判断文本是角色对话还是旁白，再判断是否阅读
            if not read:
                character = False
                TTS_character_feature = self.config['TTS_character_feature']
                if len(TTS_character_feature) > 0:
                    for i in re.split(r'\s+', TTS_character_feature):
                        if i in text:
                            character = True
                            break
                if character and self.config['TTS_character']:
                    read = True
                elif not character and self.config['TTS_narration']:
                    read = True

        # 正则表达式，若规则匹配正确，则拼接各个()的内容
        re_config = self.config['re']
        if len(re_config) > 0:
            rule = re.compile(re_config)
            info = rule.match(text)
            if info:
                groups = info.groups()
                if len(groups) > 0:
                    text = ''.join(groups)

        # 复制处理后的原文
        if self.config['copy']:
            copy(text)

        self.text = text.replace('　', '\n')

        # 传给翻译器的原文去除换行符
        text = text.replace('\n', '')

        # 更新浮动窗口的原文
        if self.floating_working and self.config['show_floating_text_original']:
            dpg.set_value('floating_text_original', text)
        elif self.textractor.working:
            dpg.set_value('textractor_text', f'原文：\n{self.text}\n\n')
        elif self.tesseract_OCR.working:
            dpg.set_value('OCR_text', f'原文：\n{self.text}\n\n')

        # TTS 阅读
        if read:
            self.read_curr_text()

        # 翻译器翻译
        for translator_label in self.translators:
            translator = self.translators[translator_label]
            if translator.working:
                textarea = None
                if self.floating_working and translator.get_translate:
                    textarea = lambda x, translator_key=translator.key: dpg.set_value(
                        f'floating_text_{translator_key}',
                        x,
                    )
                elif self.textractor.working:
                    textarea = lambda x, translator_name=translator.name: dpg.set_value(
                        'textractor_text',
                        dpg.get_value('textractor_text')
                        + f'{translator_name}：\n{x}\n\n',
                    )
                elif self.tesseract_OCR.working:
                    textarea = lambda x, translator_name=translator.name: dpg.set_value(
                        'OCR_text',
                        dpg.get_value('OCR_text') + f'{translator_name}：\n{x}\n\n',
                    )

                thread = Thread(
                    target=translator.thread,
                    args=(
                        text,
                        textarea,
                        self.game_focus,
                    ),
                    daemon=True,
                )
                thread.start()

    # 游戏列表点击函数
    def game_list(self, sender, app_data, user_data):
        # 界面更新所选游戏的相关信息
        for game in self.game_info['game_list']:
            if game['name'] == app_data:
                dpg.set_value('game_name', game['name'])
                dpg.set_value('game_path', game['path'])
                dpg.set_value('game_hook_code', game['hook_code'])
                dpg.set_value('game_start_mode', game['start_mode'])
                break

    # 添加按钮函数
    def game_add_game(self):
        game_name = dpg.get_value('game_name')
        game_path = dpg.get_value('game_path')
        game_hook_code = dpg.get_value('game_hook_code')
        game_start_mode = dpg.get_value('game_start_mode')
        # 若游戏名称未填写，则以程序名为游戏名，去掉exe后缀
        if not game_name:
            game_name = os.path.split(game_path)[1]
            game_name = os.path.splitext(game_name)[0]

        for game in self.game_info['game_list']:
            # 若已存在，则修改游戏列表
            if game['name'] == game_name or game['path'] == game_path:
                index = self.games.index(game['name'])
                self.games[index] = game_name
                dpg.configure_item('game_list', items=self.games)

                game['name'] = game_name
                game['path'] = game_path
                game['hook_code'] = game_hook_code
                game['start_mode'] = game_start_mode
                save_game(self.game_info)
                return

        # 若不存在，则添加到游戏列表
        self.games.append(game_name)
        dpg.configure_item('game_list', items=self.games)

        game = {
            'name': game_name,
            'path': game_path,
            'hook_code': game_hook_code,
            'start_mode': game_start_mode,
        }
        self.game_info['game_list'].append(game)
        save_game(self.game_info)

    # 删除按钮函数
    def game_delete_game(self):
        # 删除所选游戏的相关信息
        game_name = dpg.get_value('game_name')
        for i in self.game_info['game_list']:
            if i['name'] == game_name:
                self.games.remove(game_name)
                dpg.configure_item('game_list', items=self.games)

                self.game_info['game_list'].remove(i)
                save_game(self.game_info)
                break

    # 启动游戏按钮函数
    def game_start_game(self):
        game_path = dpg.get_value('game_path')
        if not os.path.exists(game_path):
            popup('游戏路径不正确')
            return

        name = os.path.split(game_path)[1]
        mode = dpg.get_value('game_start_mode')

        game_pid = None
        if mode == '直接启动':
            game_pid = start_directly(game_path)
        elif mode == 'Locale Emulator':
            locale_emulator_path = self.config['locale_emulator_path']
            if not os.path.exists(locale_emulator_path):
                popup('Locale Emulator路径错误')
                return

            game_pid = start_with_locale_emulator(locale_emulator_path, game_path, name)

        # 若游戏未启动，则直接返回
        if not game_pid:
            return None

        # 更新当前游戏信息
        self.game_update(game_pid, name)

        # 注入dll
        sleep(1)
        self.textractor.attach(game_pid)

        # 若游戏有特殊码，则写入
        hook_code = dpg.get_value('game_hook_code')
        if hook_code:
            sleep(1)
            self.textractor.hook_code(game_pid, hook_code)

    # 更新正在运行的游戏信息，并启动 Textractor
    def game_update(self, pid, name, hook=None):
        self.game_pid = pid

        self.game_info['curr_game_id'] = pid
        self.game_info['curr_game_name'] = name
        if hook:
            self.game_info['curr_game_hook'] = hook
        save_game(self.game_info)

        self.game_get_window()

        if not self.textractor.app:
            self.textractor_start()

        dpg.set_value('textractor_process', str(pid) + ' - ' + name)
        if hook:
            dpg.set_value('textractor_hook', hook)
        dpg.set_value('navigation_list', 'Textractor')
        for child in dpg.get_item_children('main')[1]:
            dpg.configure_item(child, show=False)
        dpg.configure_item('Textractor', show=True)

    # 获取游戏的窗口
    def game_get_window(self):
        if self.game_pid:
            try:
                app = Application(backend='uia').connect(process=self.game_pid)
                self.game_window = app.top_window()
            except:
                pass

    # 聚焦游戏窗口
    def game_focus(self):
        if not self.game_window:
            self.game_get_window()

        if self.game_window:
            try:
                self.game_window.set_focus()
            except:
                pass

    # 刷新按钮函数
    def textractor_refresh_process(self):
        # 获取任务管理器中的应用列表的进程和pid
        rule = re.compile('(\d+)')
        cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Id'
        try:
            processes = []
            proc = Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                shell=True,
            )
            for line in proc.stdout:
                line = line.decode().strip()
                result = rule.match(line)
                if result:
                    id = result.group(1)
                    process_name = psutil.Process(int(id)).name()
                    process = id + ' - ' + process_name

                    processes.append(process)

            if self.game_pid:
                process = self.game_pid
            else:
                process = processes[0]
            dpg.configure_item('textractor_process', items=processes)
            dpg.set_value('textractor_process', process)
        except:
            pass

    # 钩子列表函数
    def textractor_hook(self, sender, app_data, user_data):
        if app_data:
            self.game_info['curr_game_hook'] = app_data.split()[0]
            self.game_update(
                self.game_info['curr_game_id'],
                self.game_info['curr_game_name'],
                self.game_info['curr_game_hook'],
            )

    # 启动按钮函数
    def textractor_start(self):
        if not os.path.exists(self.textractor.path_exe) or not os.path.exists(
            self.textractor.path_dll
        ):
            popup('Textractor路径不正确')
            return

        # 启动时自动更新进程列表
        self.textractor_refresh_process()

        self.textractor.start(
            get_hook=lambda: dpg.get_value('textractor_hook'),
            set_hook=lambda hooks, hook: (
                dpg.configure_item('textractor_hook', items=hooks),
                dpg.set_value('textractor_hook', hook),
            ),
            text_process=self.text_process,
        )

    # Attach按钮函数
    def textractor_attach(self):
        if not self.textractor.app:
            popup('Textractor未启动')
            return

        pid = dpg.get_value('textractor_process').split()
        if len(pid) == 0 or not pid[0].isdigit():
            popup('进程栏缺少进程id')
            return

        try:
            game_pid = int(pid[0])
            name = psutil.Process(game_pid).name()

            self.textractor.attach(game_pid)
            self.game_update(game_pid, name)
        except:
            pass

    # 特殊码按钮函数
    def textractor_hook_code(self):
        # 特殊码需满足特定的格式
        rule = re.compile(r'^/.+@.+$')

        hook_code = dpg.get_value('hook_code')
        if rule.match(hook_code):
            self.textractor.hook_code(self.game_info['curr_game_id'], hook_code)
            dpg.configure_item(
                'textractor_hook_code_popup',
                show=False,
            )
        else:
            dpg.configure_item('textractor_hook_code_wrong', show=True)

    # Textractor 暂停按钮函数
    def textractor_pause(self):
        if self.textractor.working:
            self.textractor.pause = not self.textractor.pause

            if self.textractor.pause:
                dpg.configure_item('textractor_pause', label='继续')
            else:
                dpg.configure_item('textractor_pause', label='暂停')

    # 终止按钮函数
    def textractor_stop(self):
        self.textractor.stop()

    # Textractor 小窗口按扭函数
    def textractor_floating(self):
        self.floating()

    # OCR 更新截取图片
    def OCR_update_image(self, image):
        dpg.delete_item('OCR_image')
        if dpg.does_item_exist('OCR_image_texture'):
            dpg.delete_item('OCR_image_texture')
        width, height, channels, data = dpg.load_image(image)
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag='OCR_image_texture')
        dpg.add_image(
            'OCR_image_texture',
            tag='OCR_image',
            parent='OCR_image_window',
            pos=(0, 0),
        )
        dpg.configure_item('OCR_image_window', width=width)
        dpg.configure_item('OCR_image_window', height=height)

    # 截取按钮函数
    def OCR_get_area(self):
        # 最小化
        dpg.minimize_viewport()

        # 截取全屏
        sleep(1)
        screenshot('Screenshot.png')

        # 更新全屏图片
        dpg.delete_item('OCR_screenshot')
        if dpg.does_item_exist('OCR_screenshot_texture'):
            dpg.delete_item('OCR_screenshot_texture')
        width, height, channels, data = dpg.load_image('Screenshot.png')
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag='OCR_screenshot_texture')
        dpg.add_image(
            'OCR_screenshot_texture',
            tag='OCR_screenshot',
            parent='screenshot_window',
            pos=(0, 0),
        )

        # 显示 screenshot_window
        dpg.configure_item('main_window', show=False)
        dpg.configure_item('screenshot_window', show=True)
        dpg.set_primary_window('screenshot_window', True),
        dpg.set_viewport_decorated(False)
        dpg.maximize_viewport()

        # 绘制矩形
        with dpg.viewport_drawlist():
            dpg.draw_rectangle(
                (0, 0),
                (0, 0),
                tag='OCR_area',
                color=[255, 0, 0],
            )
            position1 = dpg.get_mouse_pos(local=False)
            position2 = dpg.get_mouse_pos(local=False)
            while True:
                # 按住左键，不断绘制矩形
                if dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
                    position1 = dpg.get_mouse_pos(local=False)
                    while True:
                        position2 = dpg.get_mouse_pos(local=False)
                        dpg.configure_item('OCR_area', pmin=position1, pmax=position2)
                        if not dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
                            break

                # 按下回车，记住截取区域
                if dpg.is_key_down(dpg.mvKey_Return):
                    dpg.delete_item('OCR_area')

                    x1, y1 = position1
                    x2, y2 = position2
                    if x1 > x2:
                        x1, x2 = x2, x1
                    if y1 > y2:
                        y1, y2 = y2, y1
                    bbox = [
                        x1,
                        y1,
                        x2 - x1,
                        y2 - y1,
                    ]
                    self.tesseract_OCR.thread(
                        update_image=self.OCR_update_image,
                        text_process=self.text_process,
                        bbox=bbox,
                    )

                    break
                # 按下 ESC，退出
                if dpg.is_key_down(dpg.mvKey_Escape):
                    dpg.delete_item('OCR_area')
                    break

        if os.path.exists('Screenshot.png'):
            os.remove('Screenshot.png')

        # 恢复主窗口
        dpg.configure_item('main_window', show=True),
        dpg.configure_item('screenshot_window', show=False),
        dpg.set_primary_window('main_window', True),
        dpg.set_viewport_decorated(True),
        dpg.configure_viewport('LightWeight_VNR', width=1280),
        dpg.configure_viewport('LightWeight_VNR', height=720),
        dpg.configure_viewport('LightWeight_VNR', x_pos=100),
        dpg.configure_viewport('LightWeight_VNR', y_pos=100),

    # 连续按钮函数
    def OCR_start(self):
        if not os.path.exists(self.tesseract_OCR.path):
            popup('Tesseract-OCR路径不正确')
            return

        self.tesseract_OCR.start(
            update_image=self.OCR_update_image,
            text_process=self.text_process,
        )

    # OCR 暂停按钮函数
    def OCR_pause(self):
        self.pause_or_resume()

    # 终止按钮函数
    def OCR_stop(self):
        self.tesseract_OCR.stop()

    # OCR 小窗口按扭函数
    def OCR_floating(self):
        self.floating()

    # 有道启动按钮函数
    def youdao_start(self):
        if not os.path.exists(self.youdao.path_exe):
            popup('有道词典路径不正确')
            return

        self.youdao.start()

    # 有道终止按钮函数
    def youdao_stop(self):
        self.youdao.stop()

    # yukari启动按钮函数
    def yukari_start(self):
        if not os.path.exists(self.yukari.path_exe):
            popup('Yukari路径不正确')
            return

        self.yukari.start()

    # yukari终止按钮函数
    def yukari_stop(self):
        self.yukari.stop()

    # tamiyasu启动按钮函数
    def tamiyasu_start(self):
        if not os.path.exists(self.tamiyasu.path_exe):
            popup('Tamiyasu路径不正确')
            return

        self.tamiyasu.start()

    # tamiyasu终止按钮函数
    def tamiyasu_stop(self):
        self.tamiyasu.stop()

    # voicevox启动按钮函数
    def voicevox_start(self):
        if not os.path.exists(self.voicevox.path_exe):
            popup('VOICEVOX路径不正确')
            return

        self.voicevox.start(
            show_loading=lambda show: dpg.configure_item(
                'voicevox_loading_indicator',
                show=show,
            ),
            set_speaker=lambda items, speaker: (
                dpg.configure_item(
                    'voicevox_speaker_selected',
                    items=items,
                ),
                dpg.set_value('voicevox_speaker_selected', speaker),
            ),
        )

    # voicevox终止按钮函数
    def voicevox_stop(self):
        self.voicevox.stop()

    # 暂停按钮函数
    def pause_or_resume(self):
        if self.textractor.working:
            self.textractor.pause = not self.textractor.pause
            if self.textractor.pause:
                dpg.configure_item('textractor_pause', label='继续')
                dpg.configure_item('floating_pause', label='继续')
            else:
                dpg.configure_item('textractor_pause', label='暂停')
                dpg.configure_item('floating_pause', label='暂停')
        elif self.tesseract_OCR.working:
            self.tesseract_OCR.pause = not self.tesseract_OCR.pause
            if self.tesseract_OCR.pause:
                dpg.configure_item('OCR_pause', label='继续')
                dpg.configure_item('floating_pause', label='继续')
            else:
                dpg.configure_item('OCR_pause', label='暂停')
                dpg.configure_item('floating_pause', label='暂停')

    # 阅读按钮函数
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
            popup('请先启动TTS')

    # 快捷键设置
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

    # 小窗口按扭函数
    def floating(self):
        # 显示小窗口
        dpg.configure_item('main_window', show=False)
        dpg.configure_item('floating_window', show=True)
        dpg.set_primary_window('floating_window', True),
        dpg.set_viewport_decorated(False)

        # 添加原文以及各种翻译
        if dpg.does_item_exist('floating_text'):
            dpg.delete_item('floating_text')
        with dpg.group(
            tag='floating_text',
            parent='floating_window',
            horizontal=True,
        ):
            text_height = 32
            total_height = dpg.get_item_height('floating_menu_bar') + text_height
            with dpg.group(horizontal=True):
                with dpg.group():
                    if self.config['show_floating_text_original']:
                        dpg.add_text('原文：')
                        for translator_label in self.translators:
                            translator = self.translators[translator_label]
                            if translator.working and translator.get_translate:
                                dpg.add_text(f'{translator.name}：')
                with dpg.group():
                    if self.config['show_floating_text_original']:
                        dpg.add_text(tag='floating_text_original')
                    total_height += text_height
                    for translator_label in self.translators:
                        translator = self.translators[translator_label]
                        if translator.working and translator.get_translate:
                            dpg.add_text(tag=f'floating_text_{translator.key}')
                            total_height += text_height

        dpg.configure_viewport('LightWeight_VNR', height=total_height)
        # 设定小窗口宽度与游戏窗口宽度相同，并位于游戏窗口左下角
        if self.game_window:
            rectangle = self.game_window.rectangle()
            dpg.configure_viewport('LightWeight_VNR', width=rectangle.width())
            dpg.configure_viewport('LightWeight_VNR', x_pos=rectangle.left)
            dpg.configure_viewport('LightWeight_VNR', y_pos=rectangle.bottom)

        self.floating_working = True


if __name__ == '__main__':
    LightWeight_VNR()
