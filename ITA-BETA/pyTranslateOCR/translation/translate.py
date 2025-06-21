import logging
from .libretranslate import is_libretranslate_available, translate_libre
from .nllb import is_nllb_available, translate_nllb
from .locally import is_translate_locally_available, translate_locally, check_translate_locally_availability
from .google import is_google_translate_available, translate_google
from PyQt5.QtWidgets import QMessageBox

# logging.basicConfig(level=logging.INFO)

def translate_text(translate_engine: str, text: str, source_lang: str, target_lang: str, unique_text: bool, translate_locally_path: str = '') -> str:
    """
    Traduce il testo usando il motore specificato, con fallback su LibreTranslate se necessario.
    Args:
        translate_engine: Motore di traduzione ('LibreTranslate', 'NLLB', 'Locally', 'Google').
        text: Testo da tradurre.
        source_lang: Codice della lingua di origine.
        target_lang: Codice della lingua di destinazione.
        unique_text: Se True, unisce il testo in una singola linea.
        translate_locally_path: Percorso opzionale per translateLocally (necessario per Locally su Windows).
    Returns:
        str: Testo tradotto.
    Raises:
        ValueError: Se nessun motore di traduzione è disponibile.
    """
    if not text.strip():
        return ""
    if unique_text:
        text = text.replace('\n', ' ')
    
    # Funzione helper per provare un motore con fallback
    def try_translate(engine, fallback_engine=None):
        try:
            if engine == "LibreTranslate" and is_libretranslate_available():
                return translate_libre(text, source_lang, target_lang)
            elif engine == "NLLB" and is_nllb_available():
                return translate_nllb(text, source_lang, target_lang)
            elif engine == "Locally":
                if not is_translate_locally_available():
                    check_translate_locally_availability(translate_locally_path)
                if is_translate_locally_available():
                    return translate_locally(text, source_lang, target_lang)
                else:
                    raise ValueError("translateLocally non disponibile. Verifica il percorso o l'installazione.")
            elif engine == "Google" and is_google_translate_available():
                return translate_google(text, source_lang, target_lang)
            else:
                raise ValueError(f"Motore di traduzione {engine} non disponibile.")
        except ValueError as e:
            logging.warning(f"Errore con {engine}: {e}")
            if fallback_engine:
                logging.info(f"Fallback su {fallback_engine}")
                return try_translate(fallback_engine)
            raise

    try:
        return try_translate(translate_engine, fallback_engine="LibreTranslate")
    except ValueError as e:
        raise ValueError(f"Traduzione fallita: {e}")