import dearpygui.dearpygui as dpg

from game import start_mode
from OCR.threshold_ways import threshold_name


def _help(message):
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text('(?)', color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)
    dpg.move_item(last_item, parent=group)


def popup(message):
    if dpg.does_item_exist('popup'):
        dpg.set_value('popup', message)
        dpg.configure_item('popup', show=True)
    else:
        with dpg.window(
            label='提示',
            tag='popup',
            pos=dpg.get_mouse_pos(local=False),
        ):
            dpg.add_text(
                message,
                tag='popup_text',
            )
            dpg.add_separator()
            dpg.add_button(
                label='确定',
                callback=lambda: dpg.configure_item('popup', show=False),
            )


def registry_font(font_size):
    with dpg.font_registry():
        with dpg.font('fonts/msyh.ttc', font_size) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Thai)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)

        dpg.bind_font(default_font)


def main_window():
    with dpg.window(tag='main_window'):
        with dpg.group(horizontal=True):
            with dpg.child_window(tag='navigation', width=160):

                def callback(sender, app_data, user_data):
                    for child in dpg.get_item_children('main')[1]:
                        dpg.configure_item(child, show=False)
                    dpg.configure_item(app_data, show=True)

                dpg.add_listbox(
                    items=['Game', 'Textractor', 'OCR', 'Translator', 'TTS', 'Setting'],
                    tag='navigation_list',
                    callback=callback,
                    num_items=6,
                )

            with dpg.child_window(tag='main'):
                with dpg.group(tag='Game'):
                    dpg.add_listbox(
                        items=[],
                        tag='game_list',
                        width=-1,
                        num_items=16,
                    )
                    dpg.add_separator()
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            dpg.add_text('游戏名称：')
                            dpg.add_text('程序目录：')
                            dpg.add_text('启动方式：')
                            dpg.add_text('特殊码：')
                        with dpg.group():
                            dpg.add_input_text(
                                tag='game_name',
                                width=-1,
                            )
                            dpg.add_input_text(
                                tag='game_path',
                                width=-1,
                            )
                            dpg.add_combo(
                                items=start_mode,
                                tag='game_start_mode',
                                width=-1,
                            )
                            dpg.add_input_text(
                                tag='game_hook_code',
                                width=-1,
                            )
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label='添加/修改',
                            tag='game_add_game',
                        )
                        dpg.add_button(
                            label='删除',
                            tag='game_delete_game',
                        )
                        dpg.add_button(
                            label='启动游戏',
                            tag='game_start_game',
                        )
                    dpg.add_separator()

                with dpg.group(tag='Textractor', show=False):
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label='进程',
                            tag='textractor_refresh_process',
                            width=64,
                        )
                        dpg.add_combo(
                            tag='textractor_process',
                            width=-1,
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label='钩子',
                            width=64,
                            enabled=False,
                        )
                        dpg.add_combo(
                            tag='textractor_hook',
                            width=-1,
                        )
                    dpg.add_separator()
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            dpg.add_button(
                                label='启动TR',
                                tag='textractor_start',
                                width=64,
                            )
                            dpg.add_button(
                                label='Attach',
                                tag='textractor_attach',
                                width=64,
                            )
                            dpg.add_button(
                                label='特殊码',
                                width=64,
                            )
                            with dpg.popup(
                                dpg.last_item(),
                                mousebutton=dpg.mvMouseButton_Left,
                                modal=True,
                                tag='textractor_hook_code_popup',
                            ):
                                with dpg.group(horizontal=True):
                                    t = dpg.add_text(
                                        '(?)',
                                        tag='textractor_hook_code_wrong',
                                        show=False,
                                        color=[255, 0, 0],
                                    )
                                    with dpg.tooltip(t):
                                        dpg.add_text('特殊码格式不正确')
                                    dpg.add_text('特殊码：')
                                    dpg.add_input_text(tag='hook_code')
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label='使用',
                                        tag='textractor_hook_code',
                                    )
                                    dpg.add_button(
                                        label='取消',
                                        callback=lambda: dpg.configure_item(
                                            'textractor_hook_code_popup',
                                            show=False,
                                        ),
                                    )
                            dpg.add_button(
                                label='暂停',
                                tag='textractor_pause',
                                width=64,
                            )
                            dpg.add_button(
                                label='终止TR',
                                tag='textractor_stop',
                                width=64,
                            )
                            dpg.add_button(
                                label='小窗口',
                                tag='textractor_floating',
                                width=64,
                            )
                        dpg.add_input_text(
                            tag='textractor_text',
                            width=-1,
                            height=480,
                            multiline=True,
                        )

                with dpg.group(tag='OCR', show=False):
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            dpg.add_button(
                                label='截取',
                                tag='OCR_get_area',
                                width=64,
                            )
                            dpg.add_button(
                                label='连续',
                                tag='OCR_start',
                                width=64,
                            )
                            dpg.add_button(
                                label='暂停',
                                tag='OCR_pause',
                                width=64,
                            )
                            dpg.add_button(
                                label='终止',
                                tag='OCR_stop',
                                width=64,
                            )
                            dpg.add_button(
                                label='小窗口',
                                tag='OCR_floating',
                                width=64,
                            )
                        with dpg.group():
                            with dpg.child_window(
                                tag='OCR_image_window', width=1, height=1
                            ):
                                dpg.add_text(tag='OCR_image', show=False)
                            dpg.add_input_text(
                                tag='OCR_text',
                                width=-1,
                                height=480,
                                multiline=True,
                            )

                with dpg.group(tag='Translator', show=False):
                    with dpg.collapsing_header(label='有道', default_open=True):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('程序：')
                                dpg.add_text('路径：')
                                dpg.add_text('抓取翻译：')
                                dpg.add_text('抓取间隔：')
                            with dpg.group():
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label='启动',
                                        tag='youdao_start',
                                    )
                                    dpg.add_button(
                                        label='终止',
                                        tag='youdao_stop',
                                    )
                                dpg.add_input_text(
                                    tag='youdao_path',
                                    width=-1,
                                )
                                dpg.add_checkbox(tag='youdao_get_translate')
                                dpg.add_input_float(
                                    tag='youdao_interval',
                                    width=-1,
                                )
                    with dpg.collapsing_header(label='百度'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('启用：')
                                dpg.add_text('APPID：')
                                dpg.add_text('密钥：')
                            with dpg.group():
                                dpg.add_checkbox(tag='baidu')
                                dpg.add_input_text(
                                    tag='baidu_appid',
                                    width=-1,
                                )
                                dpg.add_input_text(
                                    tag='baidu_key',
                                    width=-1,
                                )

                with dpg.group(tag='TTS', show=False):
                    with dpg.collapsing_header(label='通用', default_open=True):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('连续阅读：')
                                _help('自动阅读符合条件的文本')
                                dpg.add_text('连续阅读特征：')
                                _help('若文本中含有指定字符，则自动阅读，以空格分隔')
                                dpg.add_text('连续阅读内容：')
                                _help('若文本中不含有连续阅读特征，则自动阅读所选内容')
                                dpg.add_text('角色对话特征：')
                                _help('若文本中含有指定字符，则判断为角色对话特征，否则判断为旁白')
                            with dpg.group():
                                dpg.add_checkbox(tag='TTS_continuous')
                                dpg.add_input_text(
                                    tag='TTS_continuous_feature',
                                    width=-1,
                                )
                                with dpg.group(horizontal=True):
                                    dpg.add_checkbox(
                                        label='角色对话',
                                        tag='TTS_character',
                                    )
                                    dpg.add_checkbox(
                                        label='旁白',
                                        tag='TTS_narration',
                                    )
                                dpg.add_input_text(
                                    tag='TTS_character_feature',
                                    width=-1,
                                )
                    with dpg.collapsing_header(label='Yukari'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('程序：')
                                dpg.add_text('路径：')
                            with dpg.group():
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label='启动',
                                        tag='yukari_start',
                                    )
                                    dpg.add_button(
                                        label='终止',
                                        tag='yukari_stop',
                                    )
                                dpg.add_input_text(
                                    tag='yukari_path',
                                    width=-1,
                                )
                    with dpg.collapsing_header(label='Tamiyasu'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('程序：')
                                dpg.add_text('路径：')
                            with dpg.group():
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label='启动',
                                        tag='tamiyasu_start',
                                    )
                                    dpg.add_button(
                                        label='终止',
                                        tag='tamiyasu_stop',
                                    )
                                dpg.add_input_text(
                                    tag='tamiyasu_path',
                                    width=-1,
                                )
                    with dpg.collapsing_header(label='VOICEROID2'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('启用：')
                                dpg.add_text('路径：')
                                dpg.add_text('Voice：')
                            with dpg.group():
                                dpg.add_checkbox(tag='voiceroid2')
                                dpg.add_input_text(
                                    tag='voiceroid2_path',
                                    width=-1,
                                )
                                dpg.add_combo(
                                    items=[],
                                    tag='voiceroid2_voice_selected',
                                    width=-1,
                                )
                        dpg.add_separator()
                        dpg.add_text('参数设置：')
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('マスター音量：')
                                dpg.add_text('音量：')
                                dpg.add_text('話速：')
                                dpg.add_text('高さ：')
                                dpg.add_text('抑揚：')
                                dpg.add_text('短ポーズ時間：')
                                dpg.add_text('長ポーズ時間')
                                dpg.add_text('文末ポーズ時間')
                            with dpg.group():
                                dpg.add_slider_float(
                                    tag='voiceroid2_master_volume',
                                    width=-1,
                                    min_value=0.0,
                                    max_value=5.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voiceroid2_volume',
                                    width=-1,
                                    min_value=0.0,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voiceroid2_speed',
                                    width=-1,
                                    min_value=0.5,
                                    max_value=4.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voiceroid2_pitch',
                                    width=-1,
                                    min_value=0.5,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voiceroid2_emphasis',
                                    width=-1,
                                    min_value=0.5,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_int(
                                    tag='voiceroid2_pause_middle',
                                    width=-1,
                                    min_value=80,
                                    max_value=500,
                                )
                                dpg.add_slider_int(
                                    tag='voiceroid2_pause_long',
                                    width=-1,
                                    min_value=100,
                                    max_value=2000,
                                )
                                dpg.add_slider_int(
                                    tag='voiceroid2_pause_sentence',
                                    width=-1,
                                    min_value=200,
                                    max_value=10000,
                                )
                    with dpg.collapsing_header(label='VOICEVOX'):
                        dpg.add_loading_indicator(
                            tag='voicevox_loading_indicator',
                            show=False,
                        )
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('程序：')
                                dpg.add_text('路径：')
                                dpg.add_text('Speaker：')
                            with dpg.group():
                                with dpg.group(horizontal=True):
                                    dpg.add_button(
                                        label='启动',
                                        tag='voicevox_start',
                                    )
                                    dpg.add_button(
                                        label='终止',
                                        tag='voicevox_stop',
                                    )
                                dpg.add_input_text(
                                    tag='voicevox_path',
                                    width=-1,
                                )
                                dpg.add_combo(
                                    items=[],
                                    tag='voicevox_speaker_selected',
                                    width=-1,
                                )
                        dpg.add_separator()
                        dpg.add_text('参数设置：')
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('話速：')
                                dpg.add_text('音高：')
                                dpg.add_text('抑揚：')
                                dpg.add_text('音量：')
                                dpg.add_text('開始無音：')
                                dpg.add_text('終了無音：')
                            with dpg.group():
                                dpg.add_slider_float(
                                    tag='voicevox_speed_scale',
                                    width=-1,
                                    min_value=0.5,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voicevox_pitch_scale',
                                    width=-1,
                                    min_value=-0.15,
                                    max_value=0.15,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voicevox_intonation_scale',
                                    width=-1,
                                    min_value=0,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voicevox_volume_scale',
                                    width=-1,
                                    min_value=0,
                                    max_value=2.0,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voicevox_pre_phoneme_length',
                                    width=-1,
                                    min_value=0,
                                    max_value=1.5,
                                    format='%.2f',
                                )
                                dpg.add_slider_float(
                                    tag='voicevox_post_phoneme_length',
                                    width=-1,
                                    min_value=0,
                                    max_value=1.5,
                                    format='%.2f',
                                )
                        dpg.add_separator()
                with dpg.group(tag='Setting', show=False):
                    with dpg.collapsing_header(label='界面', default_open=True):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('字体大小：')
                                _help('需重启')
                                dpg.add_text('置顶：')
                                _help('需重启')
                            with dpg.group():
                                dpg.add_input_int(
                                    tag='font_size',
                                    width=-1,
                                )
                                dpg.add_checkbox(tag='top')
                    with dpg.collapsing_header(label='Locale Emulator'):
                        with dpg.group(horizontal=True):
                            dpg.add_text('路径：')
                            dpg.add_input_text(
                                tag='locale_emulator_path',
                                width=-1,
                            )
                    with dpg.collapsing_header(label='Textractor'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('路径：')
                                dpg.add_text('抓取间隔：')
                            with dpg.group():
                                dpg.add_input_text(
                                    tag='textractor_path',
                                    width=-1,
                                )
                                dpg.add_input_float(
                                    tag='textractor_interval',
                                    width=-1,
                                )
                    with dpg.collapsing_header(label='Tesseract-OCR'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('路径：')
                                dpg.add_text('识别语言：')
                                dpg.add_text('截屏间隔：')
                                dpg.add_text('阈值化方法：')
                                dpg.add_text('阈值：')
                            with dpg.group():
                                dpg.add_input_text(
                                    tag='tesseract_OCR_path',
                                    width=-1,
                                )
                                dpg.add_combo(
                                    items=[],
                                    tag='tesseract_OCR_language',
                                    width=-1,
                                )
                                dpg.add_input_float(
                                    tag='OCR_interval',
                                    width=-1,
                                )
                                dpg.add_combo(
                                    items=threshold_name,
                                    tag='threshold_way',
                                    width=-1,
                                )
                                dpg.add_slider_int(
                                    tag='threshold',
                                    width=-1,
                                    min_value=0,
                                    max_value=255,
                                )
                    with dpg.collapsing_header(label='文本'):
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                dpg.add_text('智能去重：')
                                _help('aabbcc -> abc，选中后下面失效')
                                dpg.add_text('文本去重数：')
                                _help('aabbcc -> abc : 2')
                                dpg.add_text('智能去重：')
                                _help('abcabc -> abc，选中后下面失效')
                                dpg.add_text('文本去重数：')
                                _help('abcabc -> abc : 2')
                                dpg.add_text('垃圾字符表：')
                                _help('需要去除的字符，以空格分隔')
                                dpg.add_text('正则表达式：')
                                _help('拼接正则表达式的所有括号部分')
                                dpg.add_text('复制到剪切板：')
                            with dpg.group():
                                dpg.add_checkbox(tag='deduplication_aabbcc_auto')
                                dpg.add_input_int(
                                    tag='deduplication_aabbcc',
                                    width=-1,
                                )
                                dpg.add_checkbox(tag='deduplication_abcabc_auto')
                                dpg.add_input_int(
                                    tag='deduplication_abcabc',
                                    width=-1,
                                )
                                dpg.add_input_text(
                                    tag='garbage_chars',
                                    width=-1,
                                )
                                dpg.add_input_text(
                                    tag='re',
                                    width=-1,
                                )
                                dpg.add_checkbox(tag='copy')
                    with dpg.collapsing_header(label='小窗口'):
                        with dpg.group(horizontal=True):
                            dpg.add_text('显示原文：')
                            dpg.add_checkbox(tag='show_floating_text_original')


def floating_window():
    with dpg.window(tag='floating_window', show=False):

        # 恢复主窗口
        def exit():
            dpg.configure_item('main_window', show=True),
            dpg.configure_item('floating_window', show=False),
            dpg.set_primary_window('main_window', True),
            dpg.set_viewport_decorated(True),
            dpg.configure_viewport('LightWeight_VNR', width=1280),
            dpg.configure_viewport('LightWeight_VNR', height=720),
            dpg.configure_viewport('LightWeight_VNR', x_pos=100),
            dpg.configure_viewport('LightWeight_VNR', y_pos=100),

        with dpg.menu_bar(tag='floating_menu_bar'):
            dpg.add_button(
                label='x',
                width=32,
                callback=exit,
            )
            dpg.add_button(
                label='暂停',
                tag='floating_pause',
            )
            dpg.add_button(
                label='阅读',
                tag='floating_read',
            )
