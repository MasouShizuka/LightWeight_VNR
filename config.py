import os

default_config = {
    # 界面相关
    'font_size': 24,
    'top': False,
    'copy': False,
    # 游戏相关
    'locale_emulator_path': os.path.join(os.path.abspath('.'), 'Locale Emulator'),
    # Textractor相关
    'textractor_path': os.path.join(os.path.abspath('.'), 'Textractor'),
    'textractor_interval': 0,
    # OCR相关
    'tesseract_OCR_path': os.path.join(os.path.abspath('.'), 'Tesseract-OCR'),
    'tesseract_OCR_language': '日文',
    'OCR_interval': 1,
    'threshold_way': 'BINARY',
    'threshold': 127,
    # 翻译相关
    'youdao_path': os.path.join(os.path.abspath('.'), '有道词典'),
    'youdao_get_translate': True,
    'youdao_interval': 1.0,
    'baidu': False,
    'baidu_appid': '',
    'baidu_key': '',
    # TTS相关
    'TTS_continuous': False,
    'TTS_continuous_feature': '',
    'TTS_character_feature': '「 『 （ (',
    'TTS_character': False,
    'TTS_narration': False,
    'TTS_continuous': False,
    'yukari_path': os.path.join(os.path.abspath('.'), 'Yukari'),
    'tamiyasu_path': os.path.join(os.path.abspath('.'), 'Tamiyasu'),
    'voiceroid2': False,
    'voiceroid2_path': os.path.join(os.path.abspath('.'), 'VOICEROID2'),
    'voiceroid2_voice_selected': '',
    'voiceroid2_master_volume': 1.0,
    'voiceroid2_volume': 1.0,
    'voiceroid2_speed': 1.0,
    'voiceroid2_pitch': 1.0,
    'voiceroid2_emphasis': 1.0,
    'voiceroid2_pause_middle': 150,
    'voiceroid2_pause_long': 370,
    'voiceroid2_pause_sentence': 800,
    'voicevox_path': os.path.join(os.path.abspath('.'), 'VOICEVOX'),
    'voicevox_speaker_selected': '',
    'voicevox_speed_scale': 1.0,
    'voicevox_pitch_scale': 0.0,
    'voicevox_intonation_scale': 1.0,
    'voicevox_volume_scale': 1.0,
    'voicevox_pre_phoneme_length': 0.1,
    'voicevox_post_phoneme_length': 0.1,
    # 文本相关
    'deduplication_aabbcc': 1,
    'deduplication_aabbcc_auto': True,
    'deduplication_abcabc': 1,
    'deduplication_abcabc_auto': True,
    'garbage_chars': '',
    're': '',
    # 小窗口相关
    'show_floating_text_original': False,
}
