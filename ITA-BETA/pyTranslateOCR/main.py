import sys
import logging
import argparse
import platform
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui import OCRApp
from ini_controll import load_preferences, create_default_preferences
from translation.locally import check_translate_locally_availability

## V 0.5.8 by MoonDragon  - https://github.com/MoonDragon-MD/pyTranslateOCR

## Dipendendenze
# Gnu/Linux - Debian/Ubuntu
# sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-*LANG [espeak]  (*LANG sostituire con le lingue che volete, espeak dovrebbe già essere integrato in Ubuntu)
# pip3 install PyQt5 pyttsx3 pytesseract pillow requests pynput python-xlib googletrans==3.1.0a0 httpx httpcore
# Windows
# pip install PyQt5 pyttsx3 pytesseract pillow requests keyboard pynput googletrans==3.1.0a0 httpx httpcore


def setup_logging(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    if not debug:
        for logger_name in ['hpack', 'httpx', 'httpcore']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

def main():
    print(f"Starting OCR Application on {platform.system()}")
    parser = argparse.ArgumentParser(description="OCR Application")
    parser.add_argument('--debug', action='store_true', help='Abilita i messaggi di debug')
    args = parser.parse_args()
    
    setup_logging(debug=args.debug)
    
    app = QApplication(sys.argv)
    preferences = load_preferences(app)
    if preferences is None or len(preferences) != 15:
        logging.error(f"Errore nel caricamento delle preferenze: {preferences}")
        print("Impossibile caricare le preferenze. Creazione preferenze predefinite.")
        preferences = create_default_preferences(app)
        if preferences is None or len(preferences) != 15:
            print("Impossibile creare preferenze predefinite. Uscita.")
            sys.exit(1)
    
    # Verifica disponibilità di translateLocally
    translate_engine = preferences[5]  # translate_engine
    translate_locally_path = preferences[6]  # translate_locally_path
    if translate_engine == 'Locally':
        if not check_translate_locally_availability(translate_locally_path):
            logging.warning("translateLocally non disponibile, passaggio a LibreTranslate")
            QMessageBox.warning(
                None,
                "Errore translateLocally",
                "translateLocally non è disponibile. Verifica il percorso o l'installazione. Passaggio a LibreTranslate."
            )
            preferences = list(preferences)
            preferences[5] = 'LibreTranslate'  # Cambia a LibreTranslate
            preferences = tuple(preferences)
    
    logging.debug(f"Creazione OCRApp con preferenze: {preferences}")
    try:
        window = OCRApp(*preferences)
        window.show()
        sys.exit(app.exec_())
    except TypeError as e:
        logging.error(f"Errore nella creazione di OCRApp: {e}")
        print(f"Errore nella creazione della finestra: {e}")
        sys.exit(1)
    finally:
        print("OCR Application closed")

if __name__ == "__main__":
    main()