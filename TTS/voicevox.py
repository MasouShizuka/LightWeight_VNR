import os
import json
import winsound
from subprocess import Popen, PIPE
from threading import Thread

import requests

from TTS.TTS import TTS


# VOICEVOX


class VOICEVOX(TTS):
    label = 'voicevox'
    name = 'VOICEVOX'

    def __init__(self, config):
        self.working = False

        self.session = None
        self.speakers = None
        self.speaker_selected_id = None
        self.params = {
            'speedScale': 1.0,
            'pitchScale': 0.0,
            'intonationScale': 1.0,
            'volumeScale': 1.0,
            'prePhonemeLength': 0.1,
            'postPhonemeLength': 0.1,
        }

        self.update_config(config)

    def update_config(self, config, **kw):
        self.path = config['voicevox_path']
        self.path_exe = os.path.join(self.path, 'run.exe')

        self.speaker_selected = config['voicevox_speaker_selected']
        self.params['speedScale'] = config['voicevox_speed_scale']
        self.params['pitchScale'] = config['voicevox_pitch_scale']
        self.params['intonationScale'] = config['voicevox_intonation_scale']
        self.params['volumeScale'] = config['voicevox_volume_scale']
        self.params['prePhonemeLength'] = config['voicevox_pre_phoneme_length']
        self.params['postPhonemeLength'] = config['voicevox_post_phoneme_length']
        if self.speakers:
            self.speaker_selected_id = self.speakers[self.speaker_selected]

    def start(self, main_window=None):
        self.stop()

        if os.path.exists(self.path):
            try:
                thread = Thread(target=self.thread, args=(main_window,), daemon=True)
                thread.start()
                self.working = True
            except:
                pass

    def stop(self):
        try:
            self.app.kill()
        except:
            pass
        self.working = False

        if os.path.exists('audio.wav'):
            os.remove('audio.wav')

    def thread(self, main_window=None):
        self.app = Popen(
            self.path_exe, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8',
        )
        for line in iter(self.app.stderr.readline, ''):
            if 'Application startup complete' in line:
                self.startup_complete(main_window=main_window)
                break

    def startup_complete(self, main_window=None):
        self.session = requests.Session()
        self.get_speakers()
        self.speaker_selected_id = self.speakers[self.speaker_selected]
        if main_window:
            main_window['voicevox_speaker_selected'].update(
                values=list(self.speakers.keys())
            )
            main_window['voicevox_speaker_selected'].update(self.speaker_selected)

    def get_speakers(self):
        try:
            r = self.session.get(
                'http://localhost:50021/speakers', timeout=(10.0, 300.0),
            )
            if r.status_code == 200:
                self.speakers = {}
                speakers_data = r.json()
                for speaker in speakers_data:
                    speaker_name = speaker['name']
                    styles = speaker['styles']
                    for style in styles:
                        style_name = style['name']
                        self.speakers[f'{speaker_name}（{style_name}）'] = style['id']
        except:
            pass

    def read(self, text):
        try:
            audio_query_params = {'text': text, 'speaker': self.speaker_selected_id}
            r = self.session.post(
                'http://localhost:50021/audio_query',
                params=audio_query_params,
                timeout=(10.0, 300.0),
            )
            if r.status_code == 200:
                audio_query = r.json()
                for param, value in self.params.items():
                    audio_query[param] = value

                synthesis_params = {'speaker': self.speaker_selected_id}
                r = self.session.post(
                    'http://localhost:50021/synthesis',
                    data=json.dumps(audio_query),
                    params=synthesis_params,
                    timeout=(10.0, 300.0),
                )
                if r.status_code == 200:
                    with open('audio.wav', 'wb') as fp:
                        fp.write(r.content)

                    winsound.PlaySound(
                        'audio.wav', winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
        except:
            pass
