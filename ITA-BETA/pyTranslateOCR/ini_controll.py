import configparser
import subprocess
import logging
import os
from typing import List
from language_utils import get_ocr_languages as get_langs
from PyQt5.QtWidgets import QApplication

def get_default_preferences():
    return {
        'umi_ocr_path': '',
        'tesseract_path': '/usr/bin/tesseract' if os.name != 'nt' else '',
        'source_lang': 'en',
        'target_lang': 'it',
        'ocr_engine': 'Tesseract',
        'translate_engine': 'LibreTranslate',
        'translate_locally_path': '',
        'shortcuts': {
            'ocr_temp': '<alt>+c',
            'ocr_fixed': '<alt>+f',
            'ocr_set_fixed': '<alt>+s'
        },
        'fixed_area': [0, 0, 0, 0],
        'area_temp': [0, 0, 0, 0],
        'tts_voice': '',
        'tts_rate': 150,
        'contrast': 1.0,
        'sharpness': 1,
        'invert': False
    }

def load_preferences(app: QApplication):
    """
    Carica le preferenze da ocrqt.ini.
    """
    logging.debug("Inizio caricamento preferenze da ocrqt.ini")
    config = configparser.ConfigParser()
    defaults = get_default_preferences()
    if os.path.isfile('ocrqt.ini'):
        logging.debug("File ocrqt.ini trovato, lettura in corso")
        config.read('ocrqt.ini')
        if 'Settings' not in config:
            logging.error("Sezione [Settings] mancante in ocrqt.ini, usando valori predefiniti")
            return create_default_preferences(app)
        
        umi_ocr_path = config['Settings'].get('umi_ocr_path', defaults['umi_ocr_path'])
        tesseract_path = config['Settings'].get('tesseract_path', defaults['tesseract_path'])
        source_lang = config['Settings'].get('source_lang', defaults['source_lang'])
        target_lang = config['Settings'].get('target_lang', defaults['target_lang'])
        ocr_engine = config['Settings'].get('ocr_engine', defaults['ocr_engine'])
        translate_engine = config['Settings'].get('translate_engine', defaults['translate_engine'])
        translate_locally_path = config['Settings'].get('translate_locally_path', defaults['translate_locally_path'])
        shortcuts = {
            'ocr_temp': config['Settings'].get('ocr_shortcut_temp', defaults['shortcuts']['ocr_temp']).replace('alt+', '<alt>+'),
            'ocr_fixed': config['Settings'].get('ocr_shortcut_fixed', defaults['shortcuts']['ocr_fixed']).replace('alt+', '<alt>+'),
            'ocr_set_fixed': config['Settings'].get('ocr_set_fixed', defaults['shortcuts']['ocr_set_fixed']).replace('alt+', '<alt>+')
        }
        try:
            fixed_area = eval(config['Settings'].get('fixed_area', str(defaults['fixed_area'])))
            if not isinstance(fixed_area, list) or len(fixed_area) != 4 or not all(isinstance(x, (int, float)) for x in fixed_area):
                raise ValueError("fixed_area deve essere una lista di 4 numeri")
        except Exception as e:
            logging.error(f"Errore in fixed_area: {e}, usando valore predefinito")
            fixed_area = defaults['fixed_area']
        try:
            area_temp = eval(config['Settings'].get('area_temp', str(defaults['area_temp'])))
            if not isinstance(area_temp, list) or len(area_temp) != 4 or not all(isinstance(x, (int, float)) for x in area_temp):
                raise ValueError("area_temp deve essere una lista di 4 numeri")
        except Exception as e:
            logging.error(f"Errore in area_temp: {e}, usando valore predefinito")
            area_temp = defaults['area_temp']
        tts_voice = config['Settings'].get('tts_voice', defaults['tts_voice'])
        try:
            tts_rate = config.getint('Settings', 'tts_rate', fallback=defaults['tts_rate'])
        except ValueError as e:
            logging.error(f"Errore in tts_rate: {e}, usando valore predefinito")
            tts_rate = defaults['tts_rate']
        try:
            contrast = config.getfloat('Settings', 'imgMod_con', fallback=defaults['contrast'])
        except ValueError as e:
            logging.error(f"Errore in imgMod_con: {e}, usando valore predefinito")
            contrast = defaults['contrast']
        try:
            sharpness = config.getint('Settings', 'imgMod_nit', fallback=defaults['sharpness'])
        except ValueError as e:
            logging.error(f"Errore in imgMod_nit: {e}, usando valore predefinito")
            sharpness = defaults['sharpness']
        try:
            invert = config.getboolean('Settings', 'imgMod_in', fallback=defaults['invert'])
        except ValueError as e:
            logging.error(f"Errore in imgMod_in: {e}, usando valore predefinito")
            invert = defaults['invert']
        
        preferences = (umi_ocr_path, tesseract_path, source_lang, target_lang, ocr_engine,
                       translate_engine, translate_locally_path, shortcuts, fixed_area,
                       area_temp, tts_voice, tts_rate, contrast, sharpness, invert)
        logging.debug(f"Preferences caricate: {preferences}")
        logging.debug(f"Numero di elementi in preferences: {len(preferences)}")
        logging.debug(f"Tipi degli elementi in preferences: {[type(x).__name__ for x in preferences]}")
        return preferences
    else:
        logging.info("ocrqt.ini non trovato, creando preferenze predefinite")
        return create_default_preferences(app)

def create_default_preferences(app: QApplication):
    """
    Crea preferenze predefinite e salva in ocrqt.ini.
    """
    defaults = get_default_preferences()
    config = configparser.ConfigParser()
    config['Settings'] = {}
    config['Settings']['umi_ocr_path'] = defaults['umi_ocr_path']
    config['Settings']['tesseract_path'] = defaults['tesseract_path']
    config['Settings']['source_lang'] = defaults['source_lang']
    config['Settings']['target_lang'] = defaults['target_lang']
    config['Settings']['ocr_engine'] = defaults['ocr_engine']
    config['Settings']['translate_engine'] = defaults['translate_engine']
    config['Settings']['translate_locally_path'] = defaults['translate_locally_path']
    config['Settings']['ocr_shortcut_temp'] = defaults['shortcuts']['ocr_temp']
    config['Settings']['ocr_shortcut_fixed'] = defaults['shortcuts']['ocr_fixed']
    config['Settings']['ocr_set_fixed'] = defaults['shortcuts']['ocr_set_fixed']
    config['Settings']['fixed_area'] = str(defaults['fixed_area'])
    config['Settings']['area_temp'] = str(defaults['area_temp'])
    config['Settings']['tts_voice'] = defaults['tts_voice']
    config['Settings']['tts_rate'] = str(defaults['tts_rate'])
    config['Settings']['imgMod_con'] = str(defaults['contrast'])
    config['Settings']['imgMod_nit'] = str(defaults['sharpness'])
    config['Settings']['imgMod_in'] = str(defaults['invert'])
    
    # Aggiungi sezioni per le lingue
    config['OCR_Languages'] = {}
    for engine in ['tesseract', 'umi-ocr', 'umi-ocr_server']:
        langs = get_langs(engine)
        config['OCR_Languages'][engine] = ','.join(langs)
    
    config['Translate_Languages'] = {}
    from language_utils import get_translation_languages
    for engine in ['LibreTranslate', 'Google', 'NLLB', 'Locally']:
        langs = get_translation_languages(engine.lower())
        config['Translate_Languages'][engine] = ','.join(langs)
    
    with open('ocrqt.ini', 'w') as configfile:
        config.write(configfile)
    
    preferences = (defaults['umi_ocr_path'], defaults['tesseract_path'], defaults['source_lang'],
                   defaults['target_lang'], defaults['ocr_engine'], defaults['translate_engine'],
                   defaults['translate_locally_path'], defaults['shortcuts'], defaults['fixed_area'],
                   defaults['area_temp'], defaults['tts_voice'], defaults['tts_rate'],
                   defaults['contrast'], defaults['sharpness'], defaults['invert'])
    logging.debug(f"Preferences predefinite create: {preferences}")
    return preferences

def get_langs(ocr_engine: str, tesseract_path: str = '') -> List[str]:
    """
    Restituisce le lingue supportate dal motore OCR specificato.
    Args:
        ocr_engine: Nome del motore OCR (es. 'tesseract', 'umi-ocr').
        tesseract_path: Percorso dell'eseguibile Tesseract.
    Returns:
        List[str]: Lista di codici di lingua.
    """
    langs = []
    if ocr_engine.lower() == 'tesseract':
        try:
            tesseract_cmd = tesseract_path if tesseract_path and os.path.exists(tesseract_path) else 'tesseract'
            # Use stdout and stderr instead of capture_output for Python 3.6 compatibility
            result = subprocess.run([tesseract_cmd, '--list-langs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                langs = [lang.strip() for lang in result.stdout.splitlines()[1:] if lang.strip()]
            else:
                logging.error(f"Errore nell'esecuzione di Tesseract: {result.stderr}")
                langs = ['eng']  # Fallback
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logging.error(f"Errore nel recupero delle lingue di Tesseract: {e}")
            langs = ['eng']  # Fallback
    elif ocr_engine.lower() in ['umi-ocr', 'umi-ocr_server']:
        langs = ['jpn', 'eng', 'zho']  # Adatta in base a Umi-OCR
    else:
        langs = ['eng']  # Fallback
    return langs

def get_ocr_languages(config: configparser.ConfigParser, ocr_engine: str, tesseract_path: str = '') -> List[str]:
    """
    Restituisce le lingue OCR dal file di configurazione o dal motore OCR.
    """
    if 'OCR_Languages' not in config:
        config['OCR_Languages'] = {}
    langs = config['OCR_Languages'].get(ocr_engine.lower(), '')
    if langs:
        return langs.split(',')
    langs = get_langs(ocr_engine, tesseract_path)
    config['OCR_Languages'][ocr_engine.lower()] = ','.join(langs)
    return langs

def save_preferences(
    umi_ocr_path: str,
    tesseract_path: str,
    source_lang: str,
    target_lang: str,
    ocr_engine: str,
    translate_engine: str,
    translate_locally_path: str,
    shortcuts: dict,
    fixed_area: list,
    area_temp: list,
    tts_voice: str,
    tts_rate: int,
    contrast: float,
    sharpness: int,
    invert: bool
):
    """
    Salva le preferenze in ocrqt.ini.
    """
    config = configparser.ConfigParser()
    config.read('ocrqt.ini')
    # Aggiorna la sezione [Settings]
    if 'Settings' not in config:
        config['Settings'] = {}
    config['Settings']['umi_ocr_path'] = umi_ocr_path
    config['Settings']['tesseract_path'] = tesseract_path
    config['Settings']['source_lang'] = source_lang.lstrip('*')  # Rimuovi asterisco
    config['Settings']['target_lang'] = target_lang.lstrip('*')  # Rimuovi asterisco
    config['Settings']['ocr_engine'] = ocr_engine
    config['Settings']['translate_engine'] = translate_engine
    config['Settings']['translate_locally_path'] = translate_locally_path
    config['Settings']['ocr_shortcut_temp'] = shortcuts.get('ocr_temp', '<alt>+c')
    config['Settings']['ocr_shortcut_fixed'] = shortcuts.get('ocr_fixed', '<alt>+f')
    config['Settings']['ocr_set_fixed'] = shortcuts.get('ocr_set_fixed', '<alt>+s')
    config['Settings']['fixed_area'] = str(fixed_area)
    config['Settings']['area_temp'] = str(area_temp)
    config['Settings']['tts_voice'] = tts_voice
    config['Settings']['tts_rate'] = str(tts_rate)
    config['Settings']['imgMod_con'] = str(contrast)
    config['Settings']['imgMod_nit'] = str(int(sharpness))
    config['Settings']['imgMod_in'] = str(invert)
    # Preserva o aggiorna [OCR_Languages]
    if 'OCR_Languages' not in config:
        config['OCR_Languages'] = {}
    langs = get_langs(ocr_engine.lower())
    config['OCR_Languages'][ocr_engine.lower()] = ','.join(langs)
    # Preserva o aggiorna [Translate_Languages]
    if 'Translate_Languages' not in config:
        config['Translate_Languages'] = {}
    from language_utils import get_translation_languages
    langs = get_translation_languages(translate_engine.lower())
    config['Translate_Languages'][translate_engine] = ','.join([lang.lstrip('*') for lang in langs])
    # Salva il file
    with open('ocrqt.ini', 'w') as configfile:
        config.write(configfile)
    logging.debug("Preferenze salvate con successo")