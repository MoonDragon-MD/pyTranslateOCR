import sys
import os
import shutil
import pytesseract
from PyQt5.QtWidgets import QFileDialog
from PIL import Image
import subprocess
import logging

def find_tesseract_path():
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        if sys.platform == "win32":
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if not os.path.exists(tesseract_path):
                tesseract_path = QFileDialog.getOpenFileName(None, "Seleziona il file tesseract.exe", "", "Eseguibili (*.exe)")[0]
        elif sys.platform == "darwin":
            tesseract_path = "/usr/local/bin/tesseract"
            if not os.path.exists(tesseract_path):
                tesseract_path = QFileDialog.getOpenFileName(None, "Seleziona il file tesseract", "")[0]
        elif sys.platform == "linux":
            tesseract_path = "/usr/bin/tesseract"
            if not os.path.exists(tesseract_path):
                tesseract_path = QFileDialog.getOpenFileName(None, "Seleziona il file tesseract", "")[0]
        else:
            return None
        if not tesseract_path:
            return None
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Errore: Tesseract non trovato nel sistema.")
        return None
    return tesseract_path

def tesseract_ocr(image_path, language_code, tesseract_path: str = ''):
    """
    Esegue l'OCR con Tesseract.
    Args:
        image_path: Percorso dell'immagine.
        language_code: Codice lingua normalizzato (es. 'en').
        tesseract_path: Percorso dell'eseguibile Tesseract.
    Returns:
        str: Testo estratto.
    """
    LANGUAGE_MAP = {
        'en': 'eng', 'it': 'ita', 'fr': 'fra', 'de': 'deu', 'es': 'spa',
        'ja': 'jpn', 'ko': 'kor', 'zh': 'chi_sim', 'ru': 'rus', 'pt': 'por',
        'nl': 'nld', 'tr': 'tur', 'ar': 'ara', 'hi': 'hin', 'he': 'heb',
        'el': 'ell', 'pl': 'pol', 'sv': 'swe', 'ro': 'ron',
    }
    lang = LANGUAGE_MAP.get(language_code, language_code)
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    return pytesseract.image_to_string(Image.open(image_path), lang=lang)

def map_to_tesseract_language(lang_code):
    """
    Mappa codici normalizzati a codici Tesseract.
    Args:
        lang_code: Codice lingua normalizzato (es. 'en').
    Returns:
        str: Codice lingua Tesseract (es. 'eng').
    """
    LANGUAGE_MAP = {
        'en': 'eng', 'it': 'ita', 'fr': 'fra', 'de': 'deu', 'es': 'spa',
        'ja': 'jpn', 'ko': 'kor', 'zh': 'chi_sim', 'ru': 'rus', 'pt': 'por',
        'nl': 'nld', 'tr': 'tur', 'ar': 'ara', 'hi': 'hin', 'he': 'heb',
        'el': 'ell', 'pl': 'pol', 'sv': 'swe', 'ro': 'ron',
    }
    return LANGUAGE_MAP.get(lang_code, lang_code)