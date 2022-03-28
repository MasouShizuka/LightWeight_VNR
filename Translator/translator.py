class Translator:
    label = None
    name = None
    key = None

    working = None
    get_translate = True

    def update_config(self, config):
        pass

    def translate(self, text, **kw):
        pass

    def thread(self, text, is_floating, textarea, game_focus):
        text_translate = self.translate(text, game_focus=game_focus)

        if self.get_translate:
            try:
                # 更新界面中对应翻译的文本
                if not is_floating:
                    textarea.update(
                        self.name + '：\n' + text_translate + '\n\n', append=True,
                    )
                # 更新浮动窗口中对应翻译的文本
                else:
                    textarea.update(text_translate)
            except:
                pass

    def stop(self):
        pass