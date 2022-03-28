import os
import re
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep


class Textractor:
    def __init__(self, config):
        self.working = False
        self.pause = False
        self.app = None
        self.fixed_hook = None
        self.rule = re.compile(r'^(\[.+?\])\s?(.*)$')

        self.update_config(config)

    def update_config(self, config):
        self.path = config['textractor_path']
        self.path_exe = os.path.join(self.path, 'TextractorCLI.exe')
        self.interval = config['textractor_interval']

    # 启动TR
    def start(self, main_window=None, text_process=None):
        self.stop(main_window)

        if os.path.exists(self.path_exe):
            thread = Thread(
                target=self.thread, args=(main_window, text_process), daemon=True
            )
            thread.start()
            self.working = True

    # 终止TR
    def stop(self, main_window=None):
        try:
            self.app.kill()
        except:
            pass
        self.app = None
        self.working = False

        # 终止时将抓取界面清空
        main_window['textractor_process'].update('')
        main_window['textractor_process'].update(values=[])
        main_window['textractor_hook'].update('')
        main_window['textractor_hook'].update(values=[])
        main_window['textractor_text'].update('')

    # 以一定间隔读取每一行的输出
    def thread(self, main_window, text_process):
        self.app = Popen(
            self.path_exe, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-16-le',
        )
        hooks = {}
        for line in iter(self.app.stdout.readline, ''):
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

                # 将当前钩子修改为固定钩子，若未固定则读取界面钩子列表当前的钩子
                textractor_hook = main_window['textractor_hook'].get()
                curr_hook = None
                if self.fixed_hook:
                    curr_hook = self.fixed_hook
                else:
                    content = self.rule.match(textractor_hook)
                    if content:
                        curr_hook = content.group(1)

                # 更新界面钩子列表
                main_window['textractor_hook'].update(values=list(hooks.values()))
                main_window['textractor_hook'].update(curr_hook)

                # 读取所选钩子的内容
                if curr_hook == hook:
                    text_process(text)

            sleep(float(self.interval))

    # Attach
    def attach(self, pid):
        self.app.stdin.write('attach -P' + str(pid) + '\n')
        self.app.stdin.flush()

    # 特殊码
    def hook_code(self, pid, hook_code):
        self.app.stdin.write(hook_code + ' -P' + str(pid) + '\n')
        self.app.stdin.flush()

    # 固定
    def fix_hook(self, main_window=None):
        content = self.rule.match(main_window['textractor_hook'].get())
        if content:
            self.fixed_hook = content.group(1)
