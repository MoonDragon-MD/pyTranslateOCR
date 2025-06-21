import logging
from googletrans import Translator
from urllib.parse import unquote

# logging.basicConfig(level=logging.INFO)

# Lista statica delle lingue supportate da Google Translate
GOOGLE_LANGUAGES = [
    'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'bn', 'bh', 'be', 'my',
    'bs', 'bg', 'ca', 'ceb', 'cs', 'ny', 'ky', 'zh', 'zh-TW', 'ko', 'co', 'ht', 'hr', 'ku',
    'ckb', 'da', 'dv', 'doi', 'he', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gd', 'gl',
    'cy', 'ka', 'ja', 'jv', 'el', 'gn', 'gu', 'ha', 'haw', 'hi', 'hmn', 'ig', 'ilo', 'id',
    'en', 'ga', 'is', 'it', 'kn', 'kk', 'km', 'rw', 'kok', 'kr', 'lo', 'la', 'lv', 'ln',
    'lt', 'lg', 'lb', 'mk', 'ml', 'ms', 'mg', 'mt', 'mi', 'mr', 'mh', 'lus', 'mn', 'ne',
    'no', 'or', 'nl', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa',
    'st', 'sr', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sv', 'sw', 'tlh', 'ta',
    'tt', 'de', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'uk', 'ug', 'hu', 'ur', 'uz', 'vi',
    'xh', 'yi', 'yo', 'zu'
]

def get_supported_languages() -> list:
    """
    Restituisce la lista dei codici di lingua supportati da Google Translate.
    Returns:
        list: Lista di codici di lingua.
    """
    return GOOGLE_LANGUAGES

def is_google_translate_available() -> bool:
    """
    Verifica se Google Translate è disponibile.
    Returns:
        bool: True se il servizio è accessibile, False altrimenti.
    """
    try:
        translator = Translator()
        # Test con una traduzione semplice
        result = translator.translate("test", src="en", dest="it")
        return result.text.strip() != ""
    except Exception as e:
        logging.warning(f"Google Translate non disponibile: {e}")
        return False

def translate_google(text: str, source: str, target: str) -> str:
    """
    Traduce il testo usando Google Translate.
    Args:
        text: Testo da tradurre.
        source: Codice della lingua di origine (es. 'en').
        target: Codice della lingua di destinazione (es. 'it').
    Returns:
        str: Testo tradotto.
    Raises:
        ValueError: Se la traduzione fallisce.
    """
    if not text.strip():
        return ""
    
    # Decodifica eventuali caratteri URL-encoded
    try:
        text = unquote(text)
    except Exception as e:
        logging.warning(f"Errore nella decodifica del testo: {e}")
    
    try:
        translator = Translator()
        # Suddividi il testo in chunk per evitare problemi con testi lunghi
        max_chunk_size = 5000  # Limite massimo per Google Translate
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        translated_chunks = []

        for chunk in chunks:
            if not chunk.strip():
                translated_chunks.append("")
                continue
            result = translator.translate(chunk, src=source, dest=target)
            translated_chunks.append(result.text)
        
        translated_text = " ".join(translated_chunks)
        logging.debug(f"Tradotto con Google: {translated_text}")
        return translated_text
    except Exception as e:
        logging.error(f"Errore nella traduzione con Google Translate: {e}")
        raise ValueError(f"Errore nella traduzione con Google Translate: {e}")