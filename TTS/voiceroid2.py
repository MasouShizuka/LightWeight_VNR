import os
from subprocess import PIPE, Popen

from TTS.TTS import TTS


# VOICEROID2
class VOICEROID2(TTS):
    label = 'voiceroid2'
    name = 'VOICEROID2'

    def __init__(self, config, set_voice=None, **kw):
        self.update_config(config, set_voice=set_voice)

    def update_config(self, config, set_voice=None, **kw):
        self.working = config['voiceroid2']
        self.path = config['voiceroid2_path']
        self.voice_selected = config['voiceroid2_voice_selected']
        self.masterVolume = config['voiceroid2_master_volume']
        self.volume = config['voiceroid2_volume']
        self.speed = config['voiceroid2_speed']
        self.pitch = config['voiceroid2_pitch']
        self.emphasis = config['voiceroid2_emphasis']
        self.pauseMiddle = config['voiceroid2_pause_middle']
        self.pauseLong = config['voiceroid2_pause_long']
        self.pauseSentence = config['voiceroid2_pause_sentence']

        try:
            if set_voice:
                voice_list = []
                path_voice = os.path.join(self.path, 'Voice')
                for i in os.listdir(path_voice):
                    file_path = os.path.join(path_voice, i)
                    if os.path.isdir(file_path):
                        voice_list.append(i)
                if len(voice_list) > 0 and self.voice_selected not in voice_list:
                    self.voice_selected = voice_list[0]
                set_voice(voice_list, self.voice_selected)
        except:
            pass

    def read(self, text):
        cmd = [
            'python-win32\python.exe',
            'voiceroid2_read.py',
            text,
            self.path,
            self.voice_selected,
            str(self.masterVolume),
            str(self.volume),
            str(self.speed),
            str(self.pitch),
            str(self.emphasis),
            str(self.pauseMiddle),
            str(self.pauseLong),
            str(self.pauseSentence),
        ]
        Popen(cmd, shell=True)
