from typing import List
import subprocess
import logging
import platform

# Mappatura completa dei codici Tesseract a due lettere
TESSERACT_LANGUAGE_MAP = {
    'afr': 'af', 'ara': 'ar', 'bul': 'bg', 'cat': 'ca', 'ces': 'cs', 'dan': 'da', 'deu': 'de',
    'ell': 'el', 'eng': 'en', 'spa': 'es', 'est': 'et', 'eus': 'eu', 'fra': 'fr', 'glg': 'gl',
    'heb': 'he', 'hin': 'hi', 'hrv': 'hr', 'hun': 'hu', 'ind': 'id', 'isl': 'is', 'ita': 'it',
    'jpn': 'ja', 'kor': 'ko', 'lav': 'lv', 'lit': 'lt', 'mkd': 'mk', 'msa': 'ms', 'mlt': 'mt',
    'nld': 'nl', 'nor': 'no', 'pol': 'pl', 'por': 'pt', 'ron': 'ro', 'rus': 'ru', 'slk': 'sk',
    'slv': 'sl', 'sqi': 'sq', 'srp': 'sr', 'swe': 'sv', 'swa': 'sw', 'tam': 'ta', 'tel': 'te',
    'tha': 'th', 'tur': 'tr', 'ukr': 'uk', 'vie': 'vi', 'chi_sim': 'zh', 'chi_tra': 'zh'
}

UMI_LANGUAGES = [
    'af', 'sq', 'az', 'be', 'bs', 'bg', 'ca', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'fi',
    'fr', 'gl', 'de', 'he', 'hu', 'id', 'it', 'ja', 'la', 'lv', 'lt', 'mk', 'ms', 'mt', 'mi',
    'no', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sv', 'tr', 'uk', 'uz', 'vi', 'cy', 'yo', 'ka'
]
LIBRETRANSLATE_LANGUAGES = [
    'ar', 'az', 'bg', 'bn', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'he',
    'hi', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ms', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk',
    'sl', 'sq', 'sv', 'th', 'tr', 'uk', 'vi', 'zh'
]
GOOGLE_LANGUAGES = [
    'af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'zh', 'co', 'hr',
    'cs', 'da', 'nl', 'en', 'eo', 'et', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha',
    'haw', 'he', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jv', 'kn', 'kk', 'km', 'rw',
    'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn',
    'my', 'ne', 'no', 'ny', 'or', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st',
    'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tl', 'ta', 'tt', 'te', 'th', 'tr',
    'tk', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
]
NLLB_LANGUAGES = [
    'ar', 'bn', 'ca', 'en', 'es', 'fr', 'gu', 'hi', 'id', 'it', 'ko', 'mr', 'nl', 'pa', 'pl', 'pt',
    'ro', 'ru', 'sw', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi', 'zh'
]
LOCALLY_LANGUAGES = ['en', 'it']

def get_normalized_tesseract_languages(tesseract_path: str = '') -> List[str]:
    """
    Restituisce le lingue installate per Tesseract, normalizzate ai codici a due lettere.
    Args:
        tesseract_path: Percorso dell'eseguibile Tesseract (opzionale su Ubuntu).
    Returns:
        List[str]: Lista di codici di lingua normalizzati (es. ['en', 'it', 'fr']).
    """
    tesseract_lang_map = {
        'eng': 'en', 'ita': 'it', 'fra': 'fr', 'deu': 'de', 'spa': 'es',
        'jpn': 'ja', 'kor': 'ko', 'chi_sim': 'zh', 'chi_tra': 'zh',
        'rus': 'ru', 'por': 'pt', 'nld': 'nl', 'tur': 'tr', 'ara': 'ar',
        'hin': 'hi', 'heb': 'he', 'ell': 'el', 'pol': 'pl', 'swe': 'sv',
        'ron': 'ro',     # Aggiungi altre lingue se necessario
    }
    try:
        cmd = [tesseract_path or 'tesseract', '--list-langs']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            langs = [lang.strip() for lang in result.stdout.strip().split('\n') if lang.strip()]
            if langs and langs[0].startswith('List of available languages'):
                langs = langs[1:]
            normalized_langs = []
            for lang in langs:
                normalized_lang = tesseract_lang_map.get(lang.lower(), lang.lower())
                if normalized_lang not in normalized_langs:
                    normalized_langs.append(normalized_lang)
            if not normalized_langs:
                logging.warning("Nessuna lingua Tesseract trovata, ritorno fallback")
                return ['en']
            logging.debug(f"Lingue Tesseract installate: {normalized_langs}")
            return sorted(normalized_langs)
        else:
            logging.error(f"Errore nell'esecuzione di tesseract --list-langs: {result.stderr}")
            return ['en']
    except FileNotFoundError:
        logging.error(f"Tesseract non trovato al percorso: {tesseract_path or 'PATH'}")
        return ['en']
    except subprocess.CalledProcessError as e:
        logging.error(f"Errore nell'esecuzione di tesseract --list-langs: {e.stderr}")
        return ['en']
    except Exception as e:
        logging.error(f"Errore nel recupero delle lingue di Tesseract: {e}")
        return ['en']

def get_tesseract_languages(tesseract_path: str = '') -> List[str]:
    """
    Restituisce la lista dei codici di lingua installati per Tesseract, normalizzati.
    Args:
        tesseract_path: Percorso dell'eseguibile Tesseract (opzionale su Ubuntu).
    Returns:
        List[str]: Lista di codici di lingua normalizzati.
    """
    return get_normalized_tesseract_languages(tesseract_path)

def get_ocr_languages(ocr_engine: str, tesseract_path: str = '') -> List[str]:
    """
    Restituisce le lingue supportate dal motore OCR specificato.
    Args:
        ocr_engine: Nome del motore OCR ('tesseract', 'umi-ocr', 'umi-ocr_server').
        tesseract_path: Percorso dell'eseguibile Tesseract (opzionale su Ubuntu).
    Returns:
        List[str]: Lista di codici di lingua supportati.
    """
    if ocr_engine.lower() == 'tesseract':
        langs = get_normalized_tesseract_languages(tesseract_path)
        # Normalizza ulteriormente se necessario
        return [lang.replace('eng', 'en') for lang in langs]
    elif ocr_engine.lower() in ('umi-ocr', 'umi-ocr_server'):
        from ocr.umi import get_umi_languages
        return get_umi_languages()
    logging.warning(f"Motore OCR non riconosciuto: {ocr_engine}, ritorno lingue predefinite")
    return ['en']

def get_translation_languages(translate_engine: str) -> List[str]:
    """
    Restituisce le lingue supportate dal motore di traduzione specificato.
    """
    if translate_engine.lower() == 'libretranslate':
        return LIBRETRANSLATE_LANGUAGES
    elif translate_engine.lower() == 'google':
        return GOOGLE_LANGUAGES
    elif translate_engine.lower() == 'nllb':
        return NLLB_LANGUAGES
    elif translate_engine.lower() == 'locally':
        from translation.locally import get_locally_languages
        return get_locally_languages()  # Dynamic retrieval
    logging.warning(f"Motore di traduzione non riconosciuto: {translate_engine}, ritorno lingue predefinite")
    return ['en', 'it']