import pytesseract

languages = {
    '日文': 'jpn',
    '简体中文': 'chi_sim',
    '繁体中文': 'chi_tra',
    '英文': 'eng'
}
lang_translate = [i for i in languages]


def tesseract_OCR(im, language):
    text_extract = ""
    try:
        text_extract = pytesseract.image_to_string(
            im,
            lang=language,
            config='--psm 6',
        )
    except:
        pass
    return text_extract
