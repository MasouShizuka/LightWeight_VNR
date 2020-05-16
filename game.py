import psutil
from time import sleep
from subprocess import Popen

game = {
    'curr_game_id': 0,
    'curr_game_name': '',
    'game_list': [],
}

start_mode = [
    '直接启动',
    'Locale Emulator',
]


def start_directly(game_path):
    try:
        p = Popen(
            game_path,
            shell=False,
        )
        return p.pid
    except:
        pass
    return None

def start_with_locale_emulator(leproc_path, game_path, game_name):
    try:
        p = Popen(
            r'"' + leproc_path + r'"' + r' -run ' + r'"' + game_path + r'"',
            shell=True,
        )
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
