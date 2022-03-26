import os
import winsound

from TTS.TTS import TTS
from TTS.pyvcroid2 import VcRoid2


# VOICEROID2


class VOICEROID2(TTS):
    label = 'voiceroid2'
    name = 'VOICEROID2'

    def __init__(self, config):
        self.update_config(config)

    def update_config(self, config, main_window=None, **kw):
        self.working = config['voiceroid2']
        self.constantly = config['voiceroid2_constantly']
        self.aside = config['voiceroid2_aside']
        self.character = config['voiceroid2_character']

        self.path = config['voiceroid2_path']
        self.voice_selected = config['voiceroid2_voice_selected']

        self.vc = None
        self.voice_list = []
        if self.working:
            self.load_pyvcroid2(config, main_window)
        elif main_window:
            main_window['voiceroid2_voice_selected'].update(values=[])

    def load_pyvcroid2(self, config, main_window=None):
        try:
            self.vc = VcRoid2(install_path=self.path, install_path_x86=self.path)
            # Load language library
            lang_list = self.vc.listLanguages()
            if "standard" in lang_list:
                self.vc.loadLanguage("standard")
            elif 0 < len(lang_list):
                self.vc.loadLanguage(lang_list[0])
            else:
                raise Exception("No language library")

            # Load Voice
            self.voice_list = self.vc.listVoices()
            if 0 < len(self.voice_list):
                if self.voice_selected not in self.voice_list:
                    self.voice_selected = self.voice_list[0]

                self.vc.loadVoice(self.voice_selected)
            else:
                raise Exception("No voice library")
            if main_window:
                main_window['voiceroid2_voice_selected'].update(values=self.voice_list)
                main_window['voiceroid2_voice_selected'].update(self.voice_selected)

            # Set Params
            self.vc.param.masterVolume = config['voiceroid2_master_volume']
            self.vc.param.volume = config['voiceroid2_volume']
            self.vc.param.speed = config['voiceroid2_speed']
            self.vc.param.pitch = config['voiceroid2_pitch']
            self.vc.param.emphasis = config['voiceroid2_emphasis']
            self.vc.param.pauseMiddle = config['voiceroid2_pause_middle']
            self.vc.param.pauseLong = config['voiceroid2_pause_long']
            self.vc.param.pauseSentence = config['voiceroid2_pause_sentence']
        except:
            pass

    def text_process(self, text):
        # 包含以下字符会影响音频生成，因此去除
        text = text.replace('～', ' ')
        text = text.replace('。', ' ')
        text = text.replace('？', ' ')

        return text

    def read(self, text):
        text = self.text_process(text)
        try:
            speech, tts_events = self.vc.textToSpeech(text)
            with open('audio.wav', 'wb') as f:
                f.write(speech)
            winsound.PlaySound('audio.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

    def stop(self):
        if os.path.exists('audio.wav'):
            os.remove('audio.wav')
