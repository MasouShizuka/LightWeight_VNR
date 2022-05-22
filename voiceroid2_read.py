import os
import sys
import winsound

sys.path.append(os.path.split(os.path.realpath(__file__))[0])

from pyvcroid2 import VcRoid2


def text_process(text):
    # 包含以下字符会影响音频生成，因此去除
    text = text.replace('～', ' ')
    text = text.replace('。', ' ')
    text = text.replace('？', ' ')
    text = text.replace('！', ' ')

    return text


def read(
    text,
    path,
    voice_selected,
    masterVolume,
    volume,
    speed,
    pitch,
    emphasis,
    pauseMiddle,
    pauseLong,
    pauseSentence,
    *args,
):
    with VcRoid2(install_path=path, install_path_x86=path) as vc:
        # Load language library
        lang_list = vc.listLanguages()
        if "standard" in lang_list:
            vc.loadLanguage("standard")
        elif 0 < len(lang_list):
            vc.loadLanguage(lang_list[0])
        else:
            raise Exception("No language library")

        # Load Voice
        voice_list = vc.listVoices()
        if 0 < len(voice_list):
            if voice_selected not in voice_list:
                voice_selected = voice_list[0]

            vc.loadVoice(voice_selected)
        else:
            raise Exception("No voice library")

        # Set Params
        vc.param.masterVolume = masterVolume
        vc.param.volume = volume
        vc.param.speed = speed
        vc.param.pitch = pitch
        vc.param.emphasis = emphasis
        vc.param.pauseMiddle = pauseMiddle
        vc.param.pauseLong = pauseLong
        vc.param.pauseSentence = pauseSentence

        text = text_process(text)

        speech, tts_events = vc.textToSpeech(text)
        winsound.PlaySound(speech, winsound.SND_MEMORY)


if __name__ == '__main__':
    read(*sys.argv[1:])
