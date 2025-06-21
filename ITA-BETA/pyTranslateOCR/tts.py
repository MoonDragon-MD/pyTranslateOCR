import pyttsx3
import logging

# Configura il logging
# logging.basicConfig(level=logging.DEBUG)

# Mantieni un riferimento globale al motore TTS
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            logging.debug("Motore TTS inizializzato")
        except Exception as e:
            logging.error(f"Errore nell'inizializzazione di pyttsx3: {e}")
            raise
    return _engine

def get_available_voices():
    try:
        engine = get_engine()
        voices = engine.getProperty('voices')
        logging.debug(f"Voci TTS disponibili: {len(voices)}")
        return voices
    except Exception as e:
        logging.error(f"Errore nel recupero delle voci TTS: {e}")
        return []

def tts_output(text, rate=150, voice_id=None):
    try:
        engine = get_engine()
        engine.setProperty('rate', rate)
        if voice_id:
            engine.setProperty('voice', voice_id)
            logging.debug(f"Voce TTS impostata: {voice_id}")
        engine.say(text)
        engine.runAndWait()
        logging.debug("Riproduzione TTS completata")
    except Exception as e:
        logging.error(f"Errore durante la riproduzione TTS: {e}")

def stop_tts():
    global _engine
    try:
        if _engine is not None:
            _engine.stop()
            _engine = None
            logging.debug("Motore TTS fermato e resettato")
    except Exception as e:
        logging.error(f"Errore durante l'arresto del motore TTS: {e}")