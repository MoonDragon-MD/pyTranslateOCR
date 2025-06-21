from .tesseract import tesseract_ocr
from language_utils import get_tesseract_languages
from .umi import umi_ocr, umi_ocr_server, get_umi_languages
from PIL import ImageGrab
import os
import sys
import logging
from language_utils import get_ocr_languages

# logging.basicConfig(level=logging.DEBUG)

# Mappa delle lingue affini per l'OCR
LANGUAGE_AFFINITY = {
    'it': ['en', 'es', 'fr'],  # Italiano → Inglese, Spagnolo, Francese
    'uk': ['ru', 'pl'],        # Ucraino → Russo, Polacco
    'zh': ['zh', 'ja'],        # Cinese mandarino → Cinese semplificato, Giapponese
    'ja': ['zh', 'ko'],        # Giapponese → Cinese semplificato, Coreano
    'ru': ['uk', 'be'],        # Russo → Ucraino, Bielorusso
    # Aggiungi altre mappature se necessario
}

def get_affine_language(lang: str, supported_langs: list) -> str:
    """
    Restituisce una lingua supportata affine a quella richiesta.
    Args:
        lang: Codice lingua richiesto.
        supported_langs: Lista delle lingue supportate.
    Returns:
        str: Codice lingua affine o 'en' come fallback.
    """
    if lang in supported_langs:
        return lang
    for affine_lang in LANGUAGE_AFFINITY.get(lang.lower(), []):
        if affine_lang in supported_langs:
            logging.info(f"Lingua {lang} non supportata, usata lingua affine {affine_lang}")
            return affine_lang
    logging.warning(f"Nessuna lingua affine trovata per {lang}, usato fallback 'en'")
    return 'en' if 'en' in supported_langs else supported_langs[0]

def capture_screenshot(area, output_path="ocrqt.png"):
    left, top, width, height = area
    right = left + width
    bottom = top + height
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    screenshot.save(output_path)
    logging.debug(f"Screenshot salvato in: {output_path}")
    return output_path

def preprocess_image(input_path, output_path, contrast, sharpness, invert):
    from PIL import Image, ImageEnhance, ImageFilter
    logging.info(f"Pre-elaborazione immagine: contrasto={contrast}, nitidezza={sharpness}, inverti={invert}")
    with Image.open(input_path) as img:
        img = img.convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
        if sharpness > 0:
            img = img.filter(ImageFilter.SHARPEN)
        if invert:
            img = Image.eval(img, lambda x: 255 - x)
        img.save(output_path)
        logging.info(f"Immagine salvata in {output_path}")

def perform_ocr(ocr_engine, umi_ocr_path, tesseract_path, area, language_code,
                enhance_image, contrast, sharpness, invert):
    try:
        logging.debug(f"Parametri OCR: engine={ocr_engine}, area={area}, lang={language_code}, "
                      f"enhance={enhance_image}, contrast={contrast}, sharpness={sharpness}, invert={invert}")
        if ocr_engine == 'Umi-OCR' and sys.platform.startswith('linux'):
            logging.error("Umi-OCR non supportato su Linux")
            return "Errore: Umi-OCR non supportato su Linux. Usa Umi-OCR_server o Tesseract."
        
        # Ottieni le lingue supportate e seleziona una lingua affine se necessario
        supported_langs = get_ocr_languages(ocr_engine, tesseract_path)
        effective_lang = get_affine_language(language_code, supported_langs)
        logging.debug(f"Lingua effettiva usata per OCR: {effective_lang}")

        screenshot_path = capture_screenshot(area)
        if enhance_image:
            preprocess_image(screenshot_path, screenshot_path, contrast, sharpness, invert)
        if ocr_engine == 'Umi-OCR':
            result = umi_ocr(umi_ocr_path, area)
        elif ocr_engine == 'Umi-OCR_server':
            result = umi_ocr_server(screenshot_path, effective_lang)
        elif ocr_engine == 'Tesseract':
            result = tesseract_ocr(screenshot_path, effective_lang, tesseract_path)
        else:
            result = "Errore: motore OCR non riconosciuto."
        if os.path.exists(screenshot_path):
            os.unlink(screenshot_path)
            logging.debug(f"Screenshot rimosso: {screenshot_path}")
        return result
    except Exception as e:
        logging.error(f"Errore in perform_ocr: {e}", exc_info=True)
        return ""