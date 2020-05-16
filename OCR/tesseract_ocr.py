import pytesseract
import os

# 若系统未安装Tesseract-OCR,则需要指定位置
path_tesseract = os.path.abspath('.')
path_cmd = os.path.join(path_tesseract, r'Tesseract-OCR\tesseract.exe')
path_tessdata = os.path.join(path_tesseract, r'Tesseract-OCR\tessdata')

pytesseract.pytesseract.tesseract_cmd = path_cmd
tessdata_dir_config = '--tessdata-dir "' + path_tessdata + '"'

languages = {
    '日文': 'jpn',
    '简体中文': 'chi_sim',
    '繁体中文': 'chi_tra',
    '英文': 'eng'
}
lang_translate = [i for i in languages]


def tesseract_OCR(im, language):
    text_extract = pytesseract.image_to_string(
        im,
        lang=language,
        config='--psm 6',
    )
    return text_extract
