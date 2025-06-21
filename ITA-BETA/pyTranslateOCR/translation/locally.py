import subprocess
import os
import platform
import logging
from typing import Dict, List, Optional, Tuple

# Configura il logging
# logging.basicConfig(level=logging.INFO)

def get_locally_languages(translate_locally_path: str = '') -> List[str]:
    """
    Restituisce la lista univoca dei codici di lingua a due lettere supportati da translateLocally.
    Args:
        translate_locally_path: Percorso dell'eseguibile translateLocally (opzionale su Ubuntu).
    Returns:
        List[str]: Lista di codici di lingua a due lettere (es. ['af', 'sq', 'ar', ...]).
    """
    try:
        # Determina il comando
        if platform.system() == 'Windows' and translate_locally_path:
            cmd = [translate_locally_path, '-l']
        else:
            cmd = ['translateLocally', '-l']
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        
        # Mappa estesa per convertire nomi completi in codici a due lettere
        language_map = {
            "afrikaans": "af", "albanian": "sq", "arabic": "ar", "basque": "eu",
            "bulgarian": "bg", "catalan": "ca", "czech": "cs", "english": "en",
            "estonian": "et", "french": "fr", "galician": "gl", "german": "de",
            "greek": "el", "hebrew": "he", "hindi": "hi", "icelandic": "is",
            "italian": "it", "japanese": "ja", "korean": "ko", "macedonian": "mk",
            "malay": "ml", "maltese": "mt", "norwegian": "no", "polish": "pl",
            "serbo-croatian": "hbs", "sinhala": "si", "slovak": "sk", "slovene": "sl",
            "spanish": "es", "swahili": "sw", "thai": "th", "turkish": "tr",
            "ukrainian": "uk", "vietnamese": "vi"
        }
        
        languages = set()
        for line in result.stdout.splitlines():
            if "To invoke do -m" in line and any(model in line.lower() for model in ["tiny", "base", "transformer-tiny11", "full"]):
                start_idx = line.find("do -m") + 6
                if start_idx != -1 and start_idx < len(line):
                    translation_spec = line[start_idx:].strip().split("-")
                    if len(translation_spec) >= 3:
                        source_lang = translation_spec[0].lower()
                        target_lang = translation_spec[1].lower()
                        source_code = next((code for full, code in language_map.items() if full in source_lang), source_lang)
                        target_code = next((code for full, code in language_map.items() if full in target_lang), target_lang)
                        languages.add(source_code)
                        languages.add(target_code)
        
        if not languages:
            logging.warning("Nessuna lingua valida trovata nell'output di translateLocally")
            return ['en', 'it']
        
        return sorted(languages)
    except subprocess.CalledProcessError as e:
        logging.error(f"Errore nell'esecuzione di translateLocally -l: {e.stderr}")
        return ['en', 'it']
    except FileNotFoundError:
        logging.error(f"translateLocally non trovato al percorso: {translate_locally_path or 'PATH'}")
        return ['en', 'it']
    except Exception as e:
        logging.error(f"Errore nel recupero delle lingue di translateLocally: {e}")
        return ['en', 'it']  # Fallback

def get_supported_languages(translate_locally_path: str = '') -> list:
    """
    Restituisce la lista dei codici di lingua supportati da translateLocally.
    Args:
        translate_locally_path: Percorso dell'eseguibile translateLocally (opzionale su Ubuntu).
    Returns:
        list: Lista di codici di lingua.
    """
    # Deprecato: usa get_locally_languages per codici a due lettere
    return get_locally_languages(translate_locally_path)

# Variabili globali
TRANSLATE_LOCALLY_AVAILABLE: Optional[bool] = None
TRANSLATE_LOCALLY_MODELS: Optional[Dict[str, List[Tuple[str, str]]]] = None
TRANSLATE_LOCALLY_PATH: Optional[str] = None

def check_translate_locally_availability(custom_path: Optional[str] = None) -> bool:
    """
    Verifica se translateLocally è disponibile e inizializza i modelli supportati.
    Args:
        custom_path: Percorso opzionale per l'eseguibile translateLocally (necessario su Windows).
    Returns:
        bool: True se translateLocally è disponibile, False altrimenti.
    """
    global TRANSLATE_LOCALLY_AVAILABLE, TRANSLATE_LOCALLY_MODELS, TRANSLATE_LOCALLY_PATH

    if TRANSLATE_LOCALLY_AVAILABLE is not None and TRANSLATE_LOCALLY_MODELS is not None:
        return TRANSLATE_LOCALLY_AVAILABLE

    # Su Linux, cerca translateLocally nel PATH
    if platform.system() != "Windows":
        try:
            result_list = subprocess.run(
                ["translateLocally", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result_list.returncode == 0:
                TRANSLATE_LOCALLY_PATH = "translateLocally"
            else:
                logging.warning(f"translateLocally non trovato nel PATH: {result_list.stderr}")
                TRANSLATE_LOCALLY_AVAILABLE = False
                return False
        except FileNotFoundError:
            logging.warning("translateLocally non trovato nel PATH su Linux. Disabilitato.")
            TRANSLATE_LOCALLY_AVAILABLE = False
            return False
    else:  # Su Windows
        if not custom_path or not os.path.isfile(custom_path):
            logging.warning(f"Percorso translateLocally non valido o non specificato: {custom_path}")
            TRANSLATE_LOCALLY_AVAILABLE = False
            return False
        TRANSLATE_LOCALLY_PATH = custom_path
        try:
            result_list = subprocess.run(
                [TRANSLATE_LOCALLY_PATH, "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result_list.returncode != 0:
                logging.warning(f"translateLocally non funzionante: {result_list.stderr}")
                TRANSLATE_LOCALLY_AVAILABLE = False
                return False
        except Exception as e:
            logging.warning(f"Errore nel verificare translateLocally: {e}")
            TRANSLATE_LOCALLY_AVAILABLE = False
            return False

    # Parsa i modelli disponibili
    try:
        language_models: Dict[str, List[Tuple[str, str]]] = {}
        output_lines = result_list.stdout.strip().splitlines()
        language_map = {
            "afrikaans": "af", "arabic": "ar", "bulgarian": "bg", "catalan": "ca", "czech": "cs",
            "german": "de", "greek": "el", "english": "en", "spanish": "es", "estonian": "et",
            "basque": "eu", "french": "fr", "galician": "gl", "serbo-croatian": "hbs", "hebrew": "he",
            "hindi": "hi", "icelandic": "is", "italian": "it", "japanese": "ja", "korean": "ko",
            "macedonian": "mk", "malay": "ml", "maltese": "mt", "norwegian": "no", "polish": "pl",
            "sinhala": "si", "slovak": "sk", "slovene": "sl", "albanian": "sq", "swahili": "sw",
            "thai": "th", "turkish": "tr", "ukrainian": "uk", "vietnamese": "vi"
        }
        for line in output_lines:
            if "To invoke do -m" in line and any(model in line.lower() for model in ["tiny", "base", "transformer-tiny11", "full"]):
                start_idx = line.find("do -m") + 6
                if start_idx != -1 and start_idx < len(line):
                    translation_spec = line[start_idx:].strip().split("-")
                    if len(translation_spec) >= 3:
                        source_lang = translation_spec[0].lower()
                        target_lang = translation_spec[1].lower()
                        model = translation_spec[2].lower()
                        normalized_source = next((code for full, code in language_map.items() if full in source_lang), source_lang)
                        normalized_target = next((code for full, code in language_map.items() if full in target_lang), target_lang)
                        if normalized_source not in language_models:
                            language_models[normalized_source] = []
                        language_models[normalized_source].append((normalized_target, model))
        TRANSLATE_LOCALLY_MODELS = language_models
        TRANSLATE_LOCALLY_AVAILABLE = True
        logging.debug(f"Modelli disponibili: {TRANSLATE_LOCALLY_MODELS}")
        return True
    except Exception as e:
        logging.warning(f"Errore nel parsare i modelli di translateLocally: {e}")
        TRANSLATE_LOCALLY_AVAILABLE = False
        return False

def is_translate_locally_available() -> bool:
    """Restituisce True se translateLocally è disponibile."""
    return TRANSLATE_LOCALLY_AVAILABLE if TRANSLATE_LOCALLY_AVAILABLE is not None else False

def translate_locally(text: str, source: str, target: str) -> str:
    """
    Traduce il testo usando translateLocally.
    Args:
        text: Testo da tradurre.
        source: Codice della lingua di origine (es. 'en').
        target: Codice della lingua di destinazione (es. 'it').
    Returns:
        str: Testo tradotto.
    Raises:
        ValueError: Se translateLocally non è disponibile o la traduzione fallisce.
    """
    if not TRANSLATE_LOCALLY_AVAILABLE:
        raise ValueError("translateLocally non è disponibile su questo sistema.")

    language_models = TRANSLATE_LOCALLY_MODELS
    if source.lower() not in language_models:
        raise ValueError(f"Nessun modello disponibile per la lingua di origine: {source}")

    # Traduzione diretta
    direct_translation = next((model for target_lang, model in language_models[source.lower()] if target_lang == target.lower()), None)
    if direct_translation:
        max_chunk_size = 500
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        translated_chunks = []

        for chunk in chunks:
            if not chunk.strip() or all(ord(c) in {0x200B, 0xFEFF, 0x00A0, 32} for c in chunk):
                translated_chunks.append("")
                logging.debug(f"Chunk vuoto ignorato: {repr(chunk)}")
                continue

            command = [TRANSLATE_LOCALLY_PATH, "-m", f"{source.lower()}-{target.lower()}-{direct_translation}"]
            logging.debug(f"Esecuzione: {' '.join(command)}") 
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=chunk)

            if process.returncode == 0:
                translated_chunk = stdout.strip()
                translated_chunk = "\n".join(line for line in translated_chunk.splitlines() if not line.startswith("QVariant"))
                translated_chunks.append(translated_chunk or "")
            else:
                logging.error(f"Errore nella traduzione: {stderr}")
                raise ValueError(f"Errore nella traduzione: {stderr}")

        return " ".join(translated_chunks)

    # Traduzione con lingua intermedia (inglese)
    intermediate_lang = "en"
    if intermediate_lang not in language_models:
        raise ValueError(f"Lingua intermedia {intermediate_lang} non supportata")

    # Prima traduzione: source -> en
    en_model = next((model for t, model in language_models[source.lower()] if t == intermediate_lang), None)
    if not en_model:
        raise ValueError(f"Nessun modello per {source.lower()} -> {intermediate_lang}")

    command = [TRANSLATE_LOCALLY_PATH, "-m", f"{source.lower()}-{intermediate_lang}-{en_model}"]
    logging.info(f"Esecuzione (source -> en): {' '.join(command)}")
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=text)

    if process.returncode != 0:
        raise ValueError(f"Errore nella prima traduzione: {stderr}")
    intermediate_text = "\n".join(line for line in stdout.strip().splitlines() if not line.startswith("QVariant"))
    if not intermediate_text:
        raise ValueError("Output non valido per la prima traduzione.")

    # Seconda traduzione: en -> target
    target_model = next((model for t, model in language_models[intermediate_lang] if t == target.lower()), None)
    if not target_model:
        raise ValueError(f"Nessun modello per {intermediate_lang} -> {target.lower()}")

    command = [TRANSLATE_LOCALLY_PATH, "-m", f"{intermediate_lang}-{target.lower()}-{target_model}"]
    logging.info(f"Esecuzione (en -> target): {' '.join(command)}")
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=intermediate_text)

    if process.returncode != 0:
        raise ValueError(f"Errore nella seconda traduzione: {stderr}")
    translated_text = "\n".join(line for line in stdout.strip().splitlines() if not line.startswith("QVariant"))
    if not translated_text:
        raise ValueError("Output non valido per la seconda traduzione.")

    return translated_text