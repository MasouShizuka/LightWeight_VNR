import json
import os
from subprocess import Popen
from time import sleep

import psutil

game_info = {
    'curr_game_id': 0,
    'curr_game_name': '',
    'curr_game_hook': '',
    'game_list': [],
}

start_mode = [
    '直接启动',
    'Locale Emulator',
]


# 存储游戏信息
def save_game(game_info):
    with open('game.json', 'w', encoding='utf-8') as f:
        json.dump(game_info, f, indent=4, ensure_ascii=False)


# 读取游戏信息
def load_game():
    game = game_info
    running = False
    if os.path.exists('game.json'):
        with open('game.json', 'r', encoding='utf-8') as f:
            game = json.load(f)
        try:
            pid = game['curr_game_id']
            name = game['curr_game_name']
            process = psutil.Process(pid)
            if process.name() == name:
                running = True
        except:
            pass

    return game, running


# 直接启动游戏
def start_directly(game_path):
    if os.path.exists(game_path):
        try:
            p = Popen(game_path, shell=False)
            return p.pid
        except:
            pass
    return None


# 用 Locale Emulator 打开游戏
def start_with_locale_emulator(locale_emulator_path, game_path, game_name):
    leproc_path = os.path.join(locale_emulator_path, 'LEProc.exe')
    if os.path.exists(leproc_path) and os.path.exists(game_path):
        try:
            Popen([leproc_path, game_path], shell=True)
            i = 0
            while i < 10:
                for proc in psutil.process_iter():
                    process = proc.as_dict(attrs=['pid', 'name'])
                    if process['name'] == game_name:
                        return process['pid']
                sleep(1)
                i += 1
        except:
            pass
    return None
