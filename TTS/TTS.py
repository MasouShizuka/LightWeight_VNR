class TTS():
    label = None
    name = None

    working = None
    constantly = None
    aside = None
    character = None

    def update_config(self, config, **kw):
        pass

    def read(self, text):
        pass

    def read_text(self, text):
        if '「' in text or \
           '『' in text or \
           '（' in text or \
           '(' in text:
            if self.character:
                self.read(text)
        else:
            if self.aside:
                self.read(text)
