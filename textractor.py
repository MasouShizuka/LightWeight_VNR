import os
import re
from subprocess import PIPE, Popen
from threading import Thread
from time import sleep


class Textractor:
    def __init__(self, config):
        self.working = False
        self.pause = False
        self.app = None
        self.rule = re.compile(r'^(\[.+?\])\s?(.*)$')

        self.update_config(config)

    def update_config(self, config):
        self.path = config['textractor_path']
        self.path_exe = os.path.join(self.path, 'TextractorCLI.exe')
        self.path_dll = os.path.join(self.path, 'texthook.dll')
        self.interval = float(config['textractor_interval'])

    # 启动TR
    def start(self, get_hook=None, set_hook=None, text_process=None):
        self.stop()

        if os.path.exists(self.path_exe):
            thread = Thread(
                target=self.thread,
                args=(get_hook, set_hook, text_process),
                daemon=True,
            )
            thread.start()
            self.working = True

    # 终止TR
    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.app = None
        self.working = False

    # 以一定间隔读取每一行的输出
    def thread(self, get_hook, set_hook, text_process):
        hooks = {}
        self.app = Popen(
            self.path_exe,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            encoding='utf-16-le',
        )
        for line in iter(self.app.stdout.readline, ''):
            try:
                # 停止则跳出
                if not self.working:
                    break
                # 暂停则跳过
                if self.pause:
                    continue

                # 匹配每行的输出，分成钩子和内容的两部分
                content = self.rule.match(line)
                if content:
                    hook = content.group(1)
                    text = content.group(2)

                    if hooks.__contains__(hook) and hooks[hook] == line:
                        continue

                    # 存入字典
                    hooks[hook] = line

                    # 读取界面钩子列表当前的钩子
                    curr_hook = get_hook()
                    content = self.rule.match(curr_hook)
                    if content:
                        curr_hook = content.group(1)

                    # 更新界面钩子列表
                    set_hook(list(hooks.values()), curr_hook)
                    # dpg.configure_item('textractor_hook', items=list(hooks.values()))
                    # dpg.set_value('textractor_hook', curr_hook)

                    # 读取所选钩子的内容
                    if curr_hook == hook:
                        text_process(text)

                sleep(self.interval)
            except:
                pass

    # Attach
    def attach(self, pid):
        self.app.stdin.write('attach -P' + str(pid) + '\n')
        self.app.stdin.flush()

    # 特殊码
    def hook_code(self, pid, hook_code):
        self.app.stdin.write(hook_code + ' -P' + str(pid) + '\n')
        self.app.stdin.flush()
