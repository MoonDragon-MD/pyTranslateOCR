import requests
import logging

# logging.basicConfig(level=logging.INFO)

LIBRETRANSLATE_URL = "http://localhost:5000"

# Lista statica delle lingue supportate da LibreTranslate
LIBRETRANSLATE_LANGUAGES = [
    'ar', 'az', 'bg', 'bn', 'ca', 'cs', 'da', 'de', 'el', 'en', 'eo', 'es', 'et',
    'eu', 'fa', 'fi', 'fr', 'ga', 'gl', 'he', 'hi', 'hu', 'id', 'it', 'ja', 'ko',
    'lt', 'lv', 'ms', 'nb', 'nl', 'pb', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sq',
    'sv', 'th', 'tl', 'tr', 'uk', 'ur', 'zh', 'zt'
]

def get_supported_languages() -> list:
    """
    Restituisce la lista dei codici di lingua supportati da LibreTranslate.
    Returns:
        list: Lista di codici di lingua.
    """
    return LIBRETRANSLATE_LANGUAGES

def is_libretranslate_available() -> bool:
    """
    Verifica se il server LibreTranslate ? disponibile.
    Returns:
        bool: True se il server risponde, False altrimenti.
    """
    try:
        response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=2)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.warning(f"Server LibreTranslate non disponibile: {e}")
        return False

def translate_libre(text: str, source: str, target: str) -> str:
    """
    Traduce il testo usando LibreTranslate.
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
    try:
        response = requests.post(
            f"{LIBRETRANSLATE_URL}/translate",
            json={"q": text, "source": source, "target": target},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("translatedText", "")
        else:
            raise ValueError(f"Errore nella traduzione con LibreTranslate: {response.text}")
    except requests.RequestException as e:
        raise ValueError(f"Errore nella connessione a LibreTranslate: {e}")