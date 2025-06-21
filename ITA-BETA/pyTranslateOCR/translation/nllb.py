import requests
import json
import logging
from typing import Union, List

# logging.basicConfig(level=logging.INFO)

NLLB_URL = "http://localhost:6060/"

# Lista statica delle lingue supportate da NLLB
NLLB_LANGUAGES = [
    'af', 'ak', 'am', 'ar', 'as', 'ay', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'cs',
    'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga',
    'gl', 'gu', 'ha', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw', 'ka',
    'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lg', 'ln', 'lo', 'lt', 'lv',
    'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny',
    'pa', 'pl', 'pt', 'qu', 'ro', 'ru', 'rw', 'sa', 'sd', 'si', 'sk', 'sl', 'sm',
    'sn', 'so', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tr', 'uk',
    'ur', 'uz', 'vi', 'xh', 'yi', 'yo', 'zu'
]

def get_supported_languages() -> list:
    """
    Restituisce la lista dei codici di lingua supportati da NLLB.
    Returns:
        list: Lista di codici di lingua.
    """
    return NLLB_LANGUAGES

def format_language(lang: str) -> str:
    """
    Mappa il codice lingua standard (es. 'en') al formato NLLB (es. 'eng_Latn').
    Args:
        lang: Codice lingua (es. 'en', 'it').
    Returns:
        str: Codice lingua formattato per NLLB.
    """
    language_mapping = {
        'af': 'afr_Latn', 'ak': 'aka_Latn', 'am': 'amh_Ethi', 'ar': 'arb_Arab',
        'as': 'asm_Beng', 'ay': 'ayr_Latn', 'az': 'azj_Latn', 'be': 'bel_Cyrl',
        'bg': 'bul_Cyrl', 'bn': 'ben_Beng', 'bs': 'bos_Latn', 'ca': 'cat_Latn',
        'cs': 'ces_Latn', 'cy': 'cym_Latn', 'da': 'dan_Latn', 'de': 'deu_Latn',
        'el': 'ell_Grek', 'en': 'eng_Latn', 'eo': 'epo_Latn', 'es': 'spa_Latn',
        'et': 'est_Latn', 'eu': 'eus_Latn', 'fa': 'fao_Latn', 'fi': 'fin_Latn',
        'fr': 'fra_Latn', 'ga': 'gla_Latn', 'gl': 'gle_Latn', 'gu': 'guj_Gujr',
        'ha': 'hau_Latn', 'hi': 'hin_Deva', 'hr': 'hrv_Latn', 'hu': 'hun_Latn',
        'hy': 'hye_Armn', 'id': 'ind_Latn', 'is': 'isl_Latn', 'it': 'ita_Latn',
        'ja': 'jav_Latn', 'jw': 'jv_Latn', 'ka': 'kat_Geor', 'kk': 'kaz_Cyrl',
        'km': 'khm_Khmr', 'kn': 'kan_Knda', 'ko': 'kor_Hang', 'ku': 'kuw_Latn',
        'ky': 'kir_Cyrl', 'la': 'lat_Latn', 'lb': 'ltz_Latn', 'lg': 'lug_Latn',
        'ln': 'lin_Latn', 'lo': 'lao_Laoo', 'lt': 'lit_Latn', 'lv': 'lvs_Latn',
        'mg': 'mlg_Latn', 'mi': 'mri_Latn', 'mk': 'mkd_Cyrl', 'ml': 'mlt_Latn',
        'mn': 'mnk_Cyrl', 'mr': 'mar_Deva', 'ms': 'msa_Latn', 'mt': 'mlt_Latn',
        'my': 'mya_Mymr', 'ne': 'nep_Deva', 'nl': 'nld_Latn', 'no': 'nob_Latn',
        'ny': 'nya_Latn', 'pa': 'pan_Guru', 'pl': 'pol_Latn', 'pt': 'por_Latn',
        'qu': 'quy_Latn', 'ro': 'ron_Latn', 'ru': 'rus_Cyrl', 'rw': 'kin_Latn',
        'sa': 'san_Deva', 'sd': 'snd_Arab', 'si': 'sin_Sinh', 'sk': 'slk_Latn',
        'sl': 'slv_Latn', 'sm': 'smo_Latn', 'sn': 'sna_Latn', 'so': 'som_Latn',
        'sq': 'sqi_Latn', 'sr': 'srp_Cyrl', 'sv': 'swe_Latn', 'sw': 'swh_Latn',
        'ta': 'tam_Taml', 'te': 'tel_Telu', 'tg': 'tgk_Cyrl', 'th': 'tha_Thai',
        'ti': 'tir_Ethi', 'tr': 'tur_Latn', 'uk': 'ukr_Cyrl', 'ur': 'urd_Arab',
        'uz': 'uzn_Latn', 'vi': 'vie_Latn', 'xh': 'xho_Latn', 'yi': 'yid_Hebr',
        'yo': 'yor_Latn', 'zu': 'zul_Latn',
    }
    return language_mapping.get(lang.lower(), f"{lang.lower()}_Latn")

def is_nllb_available() -> bool:
    """
    Verifica se il server NLLB è disponibile.
    Returns:
        bool: True se il server risponde, False altrimenti.
    """
    try:
        response = requests.get(f"{NLLB_URL}", timeout=2)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.warning(f"Server NLLB non disponibile: {e}")
        return False

def translate_nllb(text: Union[str, List[str]], source: str, target: str) -> Union[str, List[str]]:
    """
    Traduce il testo usando NLLB.
    Args:
        text: Testo da tradurre (stringa o lista di stringhe).
        source: Codice della lingua di origine (es. 'en').
        target: Codice della lingua di destinazione (es. 'it').
    Returns:
        Union[str, List[str]]: Testo tradotto (stringa se input è stringa, lista se input è lista).
    Raises:
        ValueError: Se la traduzione fallisce.
    """
    if not text:
        return "" if isinstance(text, str) else []
    
    texts = [text] if isinstance(text, str) else text
    translations = []
    
    for single_text in texts:
        if not single_text.strip():
            translations.append("")
            continue
            
        is_single_word = ' ' not in single_text.strip()
        params = {
            'source': [single_text] if is_single_word else single_text,
            'src_lang': format_language(source),
            'tgt_lang': format_language(target),
        }
        
        try:
            response = requests.post(
                f"{NLLB_URL}/translate",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(params),
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                translation = data.get('translation', '')
                translations.append(translation)
            else:
                raise ValueError(f"Errore nella traduzione con NLLB: {response.text}")
        except requests.RequestException as e:
            raise ValueError(f"Errore nella connessione a NLLB: {e}")
    
    return translations[0] if isinstance(text, str) else translations