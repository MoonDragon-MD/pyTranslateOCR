import os
import subprocess
import requests
import base64
import json
import logging

# Lista statica delle lingue supportate da Umi-OCR
UMI_LANGUAGES = [
    'af', 'sq', 'az', 'be', 'bs', 'bg', 'ca', 'hr', 'cs', 'da', 'nl', 'en', 'eo',
    'et', 'fi', 'fr', 'gl', 'de', 'he', 'hu', 'id', 'it', 'ja', 'la', 'lv', 'lt',
    'mk', 'ms', 'mt', 'mi', 'no', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es',
    'sv', 'tr', 'uk', 'uz', 'vi', 'cy', 'yo', 'ka'
]

def get_umi_languages() -> list:
    """
    Restituisce la lista dei codici di lingua supportati da Umi-OCR/Umi-OCR_server.
    Returns:
        list: Lista di codici di lingua.
    """
    return UMI_LANGUAGES

def umi_ocr(umi_ocr_path, area):
    if not os.path.isdir(umi_ocr_path):
        return f"Errore: il percorso {umi_ocr_path} non è una cartella valida."
    umi_ocr_exe = os.path.join(umi_ocr_path, "Umi-OCR.exe")
    if not os.path.isfile(umi_ocr_exe):
        return f"Errore: il file 'Umi-OCR.exe' non è stato trovato in {umi_ocr_path}."
    output_file = os.path.join(os.path.dirname(umi_ocr_path), "pyLibOCRqt.txt")
    if os.path.isfile(output_file):
        os.remove(output_file)
    x, y, width, height = area
    screenshot_command = [umi_ocr_exe, '--screenshot', f'screen=0', f'rect={x},{y},{width},{height}', '--output', output_file]
    process = subprocess.Popen(screenshot_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        if os.path.isfile(output_file):
            with open(output_file, 'r', encoding='utf-8') as file:
                return file.read()
        return "Errore: il file di output non è stato creato."
    return f"Errore nell'OCR: {stderr}"

def umi_ocr_server(image_path, language_code):
    LANGUAGE_CONFIG_MAP = {
        "zh": "models/config_chinese.txt",
        "en": "models/config_en.txt",
        "zh-tw": "models/config_chinese_cht(v2).txt",
        "ja": "models/config_japan.txt",
        "ko": "models/config_korean.txt",
        "ru": "models/config_cyrillic.txt"
    }
    url = "http://127.0.0.1:1224/api/ocr"
    language_config = LANGUAGE_CONFIG_MAP.get(language_code, "models/config_en.txt")
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    payload = {
        "base64": image_base64,
        "options": {
            "ocr.language": language_config,
            "ocr.cls": False,
            "ocr.limit_side_len": 960,
            "tbpu.parser": "multi_para",
            "data.format": "dict"
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        ocr_result = response.json()
        return "\n".join([item['text'] for item in ocr_result.get('data', [])])
    return f"Error: {response.status_code} {response.text}"