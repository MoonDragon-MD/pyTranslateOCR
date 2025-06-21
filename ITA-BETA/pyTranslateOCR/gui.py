import logging
import sys
import os
import json
import time
import subprocess
from PyQt5.QtCore import Qt, QRect, QTimer, QPoint, QSize, QMetaObject, Q_ARG
from PyQt5.QtGui import QColor, QPen, QFont
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QComboBox, QCheckBox, QLabel, QHBoxLayout, QDialog, QLineEdit, QDialogButtonBox, QSlider, QApplication)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
from ocr.ocr import perform_ocr
from translation.translate import translate_text
from tts import tts_output, stop_tts
from keyboard_listener import KeyboardListener
from ini_controll import save_preferences, load_preferences
from settings import AdvancedSettingsDialog, TTSSettingsWindow
from translation.locally import get_locally_languages
from ocr.umi import get_umi_languages
from language_utils import get_tesseract_languages
from PyQt5.QtCore import QEventLoop
import configparser
from ocr.tesseract import map_to_tesseract_language
from ini_controll import get_ocr_languages

# logging.basicConfig(level=logging.DEBUG)

class InfoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Informazioni")
        self.setGeometry(200, 200, 300, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("pyTranslateOCR"))
        layout.addWidget(QLabel("Versione 0.5.8"))
        layout.addWidget(QLabel("Creato da MoonDragon"))
        layout.addWidget(QLabel("Sito: https://github.com/MoonDragon-MD/pyTranslateOCR"))
        self.setLayout(layout)

class ImageSettingsDialog(QDialog):
    def __init__(self, umi_ocr_path, tesseract_path, source_lang, target_lang,
                 ocr_engine, translate_engine, translate_locally_path, shortcuts,
                 fixed_area, area_temp, tts_voice, tts_rate, contrast, sharpness, invert,
                 parent=None):
        super().__init__(parent)
        self.umi_ocr_path = umi_ocr_path
        self.tesseract_path = tesseract_path
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.ocr_engine = ocr_engine
        self.translate_engine = translate_engine
        self.translate_locally_path = translate_locally_path
        self.shortcuts = shortcuts
        self.fixed_area = fixed_area
        self.area_temp = area_temp
        self.tts_voice = tts_voice
        self.tts_rate = tts_rate
        self.contrast = contrast
        self.sharpness = sharpness
        self.invert = invert
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Impostazioni Immagine")
        layout = QVBoxLayout()
        # Contrast
        layout.addWidget(QLabel("Contrasto:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(int(self.contrast * 100))
        layout.addWidget(self.contrast_slider)
        # Sharpness
        layout.addWidget(QLabel("Nitidezza:"))
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setMinimum(0)
        self.sharpness_slider.setMaximum(200)
        self.sharpness_slider.setValue(int(self.sharpness * 100))
        layout.addWidget(self.sharpness_slider)
        # Invert
        self.invert_checkbox = QCheckBox("Inverti colori")
        self.invert_checkbox.setChecked(self.invert)
        layout.addWidget(self.invert_checkbox)
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept(self):
        self.contrast = self.contrast_slider.value() / 100.0
        self.sharpness = self.sharpness_slider.value() / 100.0
        self.invert = self.invert_checkbox.isChecked()
        super().accept()

class OCRApp(QMainWindow):
    def __init__(self, umi_ocr_path, tesseract_path, source_lang, target_lang,
                 ocr_engine, translate_engine, translate_locally_path, shortcuts,
                 fixed_area, area_temp, tts_voice, tts_rate, contrast, sharpness, invert,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyTranslateOCR")
        self.setGeometry(100, 100, 385, 500)
        self.umi_ocr_path = umi_ocr_path
        self.tesseract_path = tesseract_path
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.ocr_engine = ocr_engine
        self.translate_engine = translate_engine
        self.translate_locally_path = translate_locally_path
        self.shortcuts = shortcuts
        self.fixed_area = fixed_area
        self.area_temp = area_temp
        self.tts_voice = tts_voice
        self.tts_rate = tts_rate
        self.contrast = contrast
        self.sharpness = sharpness
        self.invert = invert
        self.tts_enabled = False
        self.overlay_open = False
        self.config = configparser.ConfigParser()
        self.config.read('ocrqt.ini')
        self.init_ui()
        try:
            self.keyboard_listener = KeyboardListener(
                self.shortcuts,
                self.perform_ocr_temp,
                self.perform_fixed_ocr,
                self.set_fixed_area,
                lambda: self.overlay_open
            )
            self.keyboard_listener.start()
            logging.info(f"Keyboard listener avviato con scorciatoie: {self.shortcuts}")
        except Exception as e:
            logging.error(f"Errore nell'inizializzazione del keyboard listener: {e}")
        self.show()  

    def init_ui(self):
        layout = QVBoxLayout()
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Lingua Ingresso:"))
        self.source_lang_combo = QComboBox()
        lang_layout.addWidget(self.source_lang_combo)
        lang_layout.addWidget(QLabel("Lingua Uscita:"))
        self.target_lang_combo = QComboBox()
        lang_layout.addWidget(self.target_lang_combo)
        self.update_language_combos()
        self.source_lang_combo.setCurrentText(self.source_lang)
        self.target_lang_combo.setCurrentText(self.target_lang)
        layout.addLayout(lang_layout)
        self.ocr_text_area = QTextEdit()
        self.ocr_text_area.setPlaceholderText("Testo OCR...")
        layout.addWidget(self.ocr_text_area)
        self.translated_text_area = QTextEdit()
        self.translated_text_area.setPlaceholderText("Traduzione...")
        layout.addWidget(self.translated_text_area)
        self.create_buttons(layout)
        due_layout = QHBoxLayout()
        self.overlay_checkbox = QCheckBox("Sovrimpressione")
        due_layout.addWidget(self.overlay_checkbox)
        self.unique_text_checkbox = QCheckBox("Testo Unico")
        due_layout.addWidget(self.unique_text_checkbox)
        layout.addLayout(due_layout)
        tre_layout = QHBoxLayout()
        self.tts_checkbox = QCheckBox("TTS")
        self.tts_checkbox.stateChanged.connect(self.toggle_tts)
        tre_layout.addWidget(self.tts_checkbox)
        self.gear_button = QPushButton("⚙️")
        self.gear_button.clicked.connect(self.open_tts_settings)
        tre_layout.addWidget(self.gear_button)
        self.tts_settings_button = QPushButton("Impostazioni TTS")
        self.tts_settings_button.clicked.connect(self.open_tts_settings)
        layout.addLayout(tre_layout)
        qua_layout = QHBoxLayout()
        self.enhance_img_checkbox = QCheckBox("Migliora img")
        qua_layout.addWidget(self.enhance_img_checkbox)
        self.img_gear_button = QPushButton("⚙️")
        self.img_gear_button.clicked.connect(self.open_img_settings)
        qua_layout.addWidget(self.img_gear_button)
        layout.addLayout(qua_layout)
        self.settings_button = QPushButton("Impostazioni")
        self.settings_button.clicked.connect(self.open_advanced_settings)
        layout.addWidget(self.settings_button)
        self.info_button = QPushButton("Info")
        self.info_button.clicked.connect(self.show_info)
        layout.addWidget(self.info_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
		
    def setup_shortcuts(self):
        """Configure Qt shortcuts for OCR actions."""
        try:
            # OCR Temporary
            shortcut_temp = QShortcut(QKeySequence(self.shortcuts.get('ocr_temp', '<alt>+c')), self)
            shortcut_temp.activated.connect(self.perform_ocr_temp)
            # OCR Fixed
            shortcut_fixed = QShortcut(QKeySequence(self.shortcuts.get('ocr_fixed', '<alt>+f')), self)
            shortcut_fixed.activated.connect(self.perform_fixed_ocr)
            # Set Fixed Area
            shortcut_set_fixed = QShortcut(QKeySequence(self.shortcuts.get('ocr_set_fixed', '<alt>+s')), self)
            shortcut_set_fixed.activated.connect(self.set_fixed_area)
            logging.info(f"Qt shortcuts configured: {self.shortcuts}")
        except Exception as e:
            logging.error(f"Error setting up Qt shortcuts: {e}")
            # Fallback to KeyboardListener if needed
            self.keyboard_listener = KeyboardListener(
                self.shortcuts,
                self.perform_ocr_temp,
                self.perform_fixed_ocr,
                self.set_fixed_area,
                lambda: self.overlay_open
            )
            self.keyboard_listener.start()

    def update_language_combos(self):
        """
        Aggiorna le combo delle lingue leggendo da ocrqt.ini o calcolandole dinamicamente.
        """
        # Ottieni lingue OCR installate
        ocr_langs = get_ocr_languages(self.config, self.ocr_engine, self.tesseract_path)
        logging.debug(f"Lingue OCR installate: {ocr_langs}")

        # Ottieni lingue di traduzione
        translate_langs = self.config.get('Translate_Languages', self.translate_engine, fallback='')
        if not translate_langs:
            if self.translate_engine == 'Locally':
                try:
                    translate_langs = get_locally_languages(self.translate_locally_path)
                    logging.debug(f"Lingue di traduzione Locally: {translate_langs}")
                except Exception as e:
                    logging.error(f"Errore nel recupero delle lingue di Locally: {e}")
                    translate_langs = ['en']
            elif self.translate_engine == 'Google':
                    translate_langs = get_google_languages()
            elif self.translate_engine == 'LibreTranslate':
                    translate_langs = get_libre_languages()
            elif self.translate_engine == 'NLLB':
                    translate_langs = get_nllb_languages()
            else:
                translate_langs = ['en']
            self.config['Translate_Languages'][self.translate_engine] = ','.join(translate_langs)
        else:
            translate_langs = translate_langs.split(',')

        # Normalizza le lingue di traduzione (rimuovi asterischi e mappa 'eng' a 'en')
        translate_langs = [lang.lstrip('*').replace('eng', 'en') for lang in translate_langs]

        # Crea lista per source_lang_combo con asterischi solo per lingue non installate
        display_langs = []
        for lang in sorted(set(translate_langs)):  # Usa set per evitare duplicati
            # Normalizza lingua per confronto
            normalized_lang = lang.replace('eng', 'en')
            # Controlla se la lingua è installata per l'OCR
            is_installed = normalized_lang in ocr_langs or map_to_tesseract_language(normalized_lang) in ocr_langs
            display_langs.append(lang if is_installed else f"*{lang}")

        # Aggiorna combo box
        self.source_lang_combo.clear()
        self.source_lang_combo.addItems(display_langs)
        self.target_lang_combo.clear()
        self.target_lang_combo.addItems(sorted(translate_langs))  # Nessun asterisco per target

        logging.debug(f"Combo lingua sorgente: {display_langs}")
        logging.debug(f"Combo lingua destinazione: {translate_langs}")

        # Salva configurazione
        with open('ocrqt.ini', 'w') as configfile:
            self.config.write(configfile)

    def create_buttons(self, layout):
        self.ri_traduci_button = QPushButton("Ri-Traduci")
        self.ri_traduci_button.clicked.connect(self.ri_traduci)
        layout.addWidget(self.ri_traduci_button)
        self.ocr_temp_button = QPushButton("OCR Momentaneo")
        self.ocr_temp_button.clicked.connect(self.perform_ocr_temp)
        layout.addWidget(self.ocr_temp_button)
        self.fixed_ocr_button = QPushButton("OCR Fisso")
        self.fixed_ocr_button.clicked.connect(self.perform_fixed_ocr)
        layout.addWidget(self.fixed_ocr_button)
        self.set_fixed_button = QPushButton("Imposta Area Fissa")
        self.set_fixed_button.clicked.connect(self.set_fixed_area)
        layout.addWidget(self.set_fixed_button)

    def ri_traduci(self):
        try:
            self.close_overlay()
            ocr_text = self.ocr_text_area.toPlainText()
            translated_text = translate_text(self.translate_engine, ocr_text,
                                            self.source_lang_combo.currentText(),
                                            self.target_lang_combo.currentText(),
                                            self.unique_text_checkbox.isChecked(),
                                            self.translate_locally_path)
            self.translated_text_area.setPlainText(translated_text)
            logging.info("Ri-traduzione completata")
        except Exception as e:
            logging.error(f"Errore in ri_traduci: {e}")

    def open_img_settings(self):
        try:
            self.close_overlay()
            img_settings = ImageSettingsDialog(
                self.umi_ocr_path, self.tesseract_path, self.source_lang, self.target_lang,
                self.ocr_engine, self.translate_engine, self.translate_locally_path,
                self.shortcuts, self.fixed_area, self.area_temp, self.tts_voice,
                self.tts_rate, self.contrast, self.sharpness, self.invert, self
            )
            if img_settings.exec_():
                self.contrast = img_settings.contrast
                self.sharpness = img_settings.sharpness
                self.invert = img_settings.invert
                save_preferences(
                    self.umi_ocr_path, self.tesseract_path, self.source_lang_combo.currentText(),
                    self.target_lang_combo.currentText(), self.ocr_engine, self.translate_engine,
                    self.translate_locally_path, self.shortcuts, self.fixed_area, self.area_temp,
                    self.tts_voice, self.tts_rate, self.contrast, self.sharpness, self.invert
                )
                logging.info("Impostazioni immagine salvate")
        except Exception as e:
            logging.error(f"Errore nell'apertura delle impostazioni immagine: {e}")

    def perform_ocr_temp(self):
        try:
            logging.info("Avvio OCR temporaneo")
            self.set_area_temp()
            if self.area_temp != [0, 0, 0, 0]:
                selected_lang = self.source_lang_combo.currentText().lstrip('*')
                ocr_lang = map_to_tesseract_language(selected_lang) if self.ocr_engine.lower() == 'tesseract' else selected_lang
                ocr_text = perform_ocr(self.ocr_engine, self.umi_ocr_path, self.tesseract_path,
                                       self.area_temp, ocr_lang,
                                       self.enhance_img_checkbox.isChecked(),
                                       self.contrast, self.sharpness, self.invert)
                if not ocr_text:
                    logging.warning("Nessun testo estratto dall'OCR")
                QMetaObject.invokeMethod(self.ocr_text_area, "setPlainText",
                                        Qt.QueuedConnection, Q_ARG(str, ocr_text))
                translated_text = translate_text(self.translate_engine, ocr_text,
                                                selected_lang, self.target_lang_combo.currentText(),
                                                self.unique_text_checkbox.isChecked(),
                                                self.translate_locally_path)
                QMetaObject.invokeMethod(self.translated_text_area, "setPlainText",
                                        Qt.QueuedConnection, Q_ARG(str, translated_text))
                if self.tts_enabled and translated_text.strip():
                    tts_output(translated_text, self.tts_rate, self.tts_voice)
                if self.overlay_checkbox.isChecked():
                    self.display_overlay_window(QRect(*self.area_temp), translated_text)
        except Exception as e:
            logging.error(f"Errore nell'OCR temporaneo: {e}", exc_info=True)

    def set_area_temp(self):
        try:
            if not self.overlay_open:
                self.overlay_open = True
                logging.info("Avvio overlay per OCR temporaneo")
                self.setDisabled(True)
                ini_file = "ocrqt.ini"
                cmd = [sys.executable, "selection.py", "--ini", ini_file, "--section", "area_temp"]
                logging.debug(f"Esecuzione comando: {cmd}")
                process = subprocess.Popen(cmd)
                timeout = 30
                start_time = time.time()
                initial_mtime = os.path.getmtime(ini_file) if os.path.exists(ini_file) else 0
                while time.time() - start_time < timeout:
                    if os.path.exists(ini_file):
                        current_mtime = os.path.getmtime(ini_file)
                        if current_mtime > initial_mtime:
                            break
                    time.sleep(0.1)
                    QApplication.processEvents()
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        logging.warning("Processo di selezione terminato forzatamente")
                preferences = load_preferences(QApplication.instance())
                if preferences:
                    self.umi_ocr_path, self.tesseract_path, self.source_lang, self.target_lang, \
                    self.ocr_engine, self.translate_engine, self.translate_locally_path, \
                    self.shortcuts, self.fixed_area, self.area_temp, self.tts_voice, \
                    self.tts_rate, self.contrast, self.sharpness, self.invert = preferences
                    logging.info(f"Area temporanea letta: {self.area_temp}")
                else:
                    logging.error("Impossibile ricaricare le preferenze, area non aggiornata")
                    self.area_temp = [0, 0, 0, 0]
            else:
                logging.warning("Overlay già aperto, ignorata richiesta")
        except Exception as e:
            logging.error(f"Errore nell'apertura dell'overlay per OCR temporaneo: {e}", exc_info=True)
        finally:
            self.overlay_open = False
            self.setEnabled(True)
            logging.debug("overlay_open resettato in set_area_temp")

    def perform_fixed_ocr(self):
        try:
            if self.fixed_area == [0, 0, 0, 0]:
                self.set_fixed_area()
            if self.fixed_area != [0, 0, 0, 0]:
                selected_lang = self.source_lang_combo.currentText().lstrip('*')
                ocr_lang = map_to_tesseract_language(selected_lang) if self.ocr_engine.lower() == 'tesseract' else selected_lang
                ocr_text = perform_ocr(self.ocr_engine, self.umi_ocr_path, self.tesseract_path,
                                       self.fixed_area, ocr_lang,
                                       self.enhance_img_checkbox.isChecked(),
                                       self.contrast, self.sharpness, self.invert)
                QMetaObject.invokeMethod(self.ocr_text_area, "setPlainText",
                                        Qt.QueuedConnection, Q_ARG(str, ocr_text))
                translated_text = translate_text(self.translate_engine, ocr_text,
                                                selected_lang, self.target_lang_combo.currentText(),
                                                self.unique_text_checkbox.isChecked(),
                                                self.translate_locally_path)
                QMetaObject.invokeMethod(self.translated_text_area, "setPlainText",
                                        Qt.QueuedConnection, Q_ARG(str, translated_text))
                if self.tts_enabled and translated_text.strip():
                    tts_output(translated_text, self.tts_rate, self.tts_voice)
                if self.overlay_checkbox.isChecked():
                    self.display_overlay_window(QRect(*self.fixed_area), translated_text)
        except Exception as e:
            logging.error(f"Errore nell'OCR fisso: {e}")

    def toggle_tts(self, state):
        self.tts_enabled = state == Qt.Checked
        logging.debug(f"TTS {'abilitato' if self.tts_enabled else 'disabilitato'}")

    def display_overlay_window(self, selected_area, translated_text):
        if not self.overlay_checkbox.isChecked() or self.overlay_open:
            logging.debug("Overlay non aperto: checkbox disattivata o overlay già aperto")
            return
        try:
            self.overlay_window = QWidget()
            self.overlay_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            left = int(selected_area.left())
            top = int(selected_area.top())
            width = int(selected_area.width())
            height = int(selected_area.height())
            self.overlay_window.setGeometry(left, top, width, height)
            background = QWidget(self.overlay_window)
            background.setGeometry(0, 0, width, height)
            background.setStyleSheet("background-color: #333333;")
            text_edit = QTextEdit(self.overlay_window)
            text_edit.setText(translated_text)
            text_edit.setStyleSheet("color: white; background: transparent; border: none;")
            text_edit.setWordWrapMode(True)
            text_edit.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            text_edit.setReadOnly(True)
            text_edit.setGeometry(10, 10, width - 20, height - 50)
            font = QFont()
            font.setPointSize(12)
            text_edit.setFont(font)
            close_button = QPushButton("Chiudi", self.overlay_window)
            close_button.setStyleSheet("background-color: rgba(255, 0, 0, 200); color: white;")
            close_button.move(width - 80, height - 30)
            close_button.clicked.connect(self.overlay_window.close)
            self.overlay_window.show()
            self.overlay_window.raise_()
            self.overlay_open = True
            logging.info("Overlay finestra aperto")
            self.overlay_timer = QTimer(self)
            self.overlay_timer.timeout.connect(self.check_overlay_closed)
            self.overlay_timer.start(1000)
            loop = QEventLoop()
            self.overlay_window.destroyed.connect(loop.quit)
            loop.exec_()
            self.overlay_open = False
            logging.debug("Overlay finestra chiuso")
            if self.overlay_timer.isActive():
                self.overlay_timer.stop()
                logging.debug("Overlay timer fermato")
        except Exception as e:
            logging.error(f"Errore nell'apertura dell'overlay finestra: {e}", exc_info=True)
            self.overlay_open = False
            if hasattr(self, 'overlay_timer') and self.overlay_timer and self.overlay_timer.isActive():
                self.overlay_timer.stop()
                logging.debug("Overlay timer fermato in eccezione")

    def check_overlay_closed(self):
        try:
            if not self.overlay_window.isVisible():
                self.overlay_timer.stop()
                self.overlay_open = False
                logging.debug("Overlay finestra chiuso")
        except Exception as e:
            logging.error(f"Errore in check_overlay_closed: {e}")

    def close_overlay(self):
        try:
            if self.overlay_open and hasattr(self, 'overlay_window'):
                self.overlay_window.close()
                self.overlay_open = False
                logging.debug("Overlay chiuso manualmente")
        except Exception as e:
            logging.error(f"Errore in close_overlay: {e}")

    def open_advanced_settings(self):
        try:
            dialog = AdvancedSettingsDialog(self)
            if dialog.exec_():
                preferences = load_preferences(QApplication.instance())
                if preferences:
                    self.umi_ocr_path, self.tesseract_path, self.source_lang, self.target_lang, \
                    self.ocr_engine, self.translate_engine, self.translate_locally_path, \
                    self.shortcuts, self.fixed_area, self.area_temp, self.tts_voice, \
                    self.tts_rate, self.contrast, self.sharpness, self.invert = preferences
                    self.update_language_combos()
                    self.source_lang_combo.setCurrentText(self.source_lang)
                    self.target_lang_combo.setCurrentText(self.target_lang)
                    # Riavvia il KeyboardListener per applicare le nuove scorciatoie
                    if hasattr(self, 'keyboard_listener') and self.keyboard_listener.is_alive():
                        self.keyboard_listener.stop()
                        self.keyboard_listener.join(timeout=0.5)
                    self.keyboard_listener = KeyboardListener(
                        self.shortcuts,
                        self.perform_ocr_temp,
                        self.perform_fixed_ocr,
                        self.set_fixed_area,
                        lambda: self.overlay_open
                    )
                    self.keyboard_listener.start()
                    logging.info(f"Impostazioni avanzate applicate: ocr_engine={self.ocr_engine}, translate_engine={self.translate_engine}, shortcuts={self.shortcuts}")
        except Exception as e:
            logging.error(f"Errore nell'apertura delle impostazioni avanzate: {e}")

    def show_info(self):
        try:
            info_dialog = InfoDialog()
            info_dialog.exec_()
        except Exception as e:
            logging.error(f"Errore nell'apertura del dialogo info: {e}")

    def open_tts_settings(self):
        try:
            logging.debug("Apertura impostazioni TTS")
            dialog = TTSSettingsWindow(self.tts_voice, self.tts_rate, self)
            if dialog.exec_():
                self.tts_voice, self.tts_rate = dialog.get_settings()
                logging.debug(f"Impostazioni TTS aggiornate: voce={self.tts_voice}, rate={self.tts_rate}")
                save_preferences(
                    self.umi_ocr_path, self.tesseract_path, self.source_lang_combo.currentText(),
                    self.target_lang_combo.currentText(), self.ocr_engine, self.translate_engine,
                    self.translate_locally_path, self.shortcuts, self.fixed_area, self.area_temp,
                    self.tts_voice, self.tts_rate, self.contrast, self.sharpness, self.invert
                )
        except Exception as e:
            logging.error(f"Errore nell'apertura delle impostazioni TTS: {e}", exc_info=True)

    def set_fixed_area(self):
        try:
            if not self.overlay_open:
                self.overlay_open = True
                logging.info("Avvio overlay per area fissa")
                self.setDisabled(True)
                ini_file = "ocrqt.ini"
                cmd = [sys.executable, "selection.py", "--ini", ini_file, "--section", "fixed_area"]
                logging.debug(f"Esecuzione comando: {cmd}")
                process = subprocess.Popen(cmd)
                timeout = 30
                start_time = time.time()
                initial_mtime = os.path.getmtime(ini_file) if os.path.exists(ini_file) else 0
                while time.time() - start_time < timeout:
                    if os.path.exists(ini_file):
                        current_mtime = os.path.getmtime(ini_file)
                        if current_mtime > initial_mtime:
                            break
                    time.sleep(0.1)
                    QApplication.processEvents()
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        logging.warning("Processo di selezione terminato forzatamente")
                preferences = load_preferences(QApplication.instance())
                if preferences:
                    self.umi_ocr_path, self.tesseract_path, self.source_lang, self.target_lang, \
                    self.ocr_engine, self.translate_engine, self.translate_locally_path, \
                    self.shortcuts, self.fixed_area, self.area_temp, self.tts_voice, \
                    self.tts_rate, self.contrast, self.sharpness, self.invert = preferences
                    logging.info(f"Area fissa letta: {self.fixed_area}")
                else:
                    logging.error("Impossibile ricaricare le preferenze, area non aggiornata")
                    self.fixed_area = [0, 0, 0, 0]
            else:
                logging.warning("Overlay già aperto, ignorata richiesta")
        except Exception as e:
            logging.error(f"Errore nell'apertura dell'overlay per area fissa: {e}", exc_info=True)
        finally:
            self.overlay_open = False
            self.setEnabled(True)
            logging.debug("overlay_open resettato in set_fixed_area")

    def closeEvent(self, event):
        import time
        logging.info("Chiusura della finestra principale")
        start_time = time.time()
        try:
            self.close_overlay()
            logging.debug(f"Overlay chiuso: {time.time() - start_time:.2f}s")
            if hasattr(self, 'overlay_timer') and self.overlay_timer and self.overlay_timer.isActive():
                self.overlay_timer.stop()
                logging.debug(f"Overlay timer fermato: {time.time() - start_time:.2f}s")
            if hasattr(self, 'keyboard_listener') and self.keyboard_listener.is_alive():
                self.keyboard_listener.stop()
                self.keyboard_listener.join(timeout=0.5)
                if self.keyboard_listener.is_alive():
                    logging.warning("KeyboardListener non terminato completamente")
                else:
                    logging.debug(f"KeyboardListener terminato: {time.time() - start_time:.2f}s")
            stop_tts()
            logging.debug(f"Motore TTS fermato: {time.time() - start_time:.2f}s")
            save_preferences(
                self.umi_ocr_path, self.tesseract_path, self.source_lang_combo.currentText(),
                self.target_lang_combo.currentText(), self.ocr_engine, self.translate_engine,
                self.translate_locally_path, self.shortcuts, self.fixed_area, self.area_temp,
                self.tts_voice, self.tts_rate, self.contrast, self.sharpness, self.invert
            )
            logging.debug(f"Preferenze salvate: {time.time() - start_time:.2f}s")
            logging.debug("Inizio terminazione processi")
            subprocess.run(["pkill", "-9", "-f", "selection.py"], check=False)
            subprocess.run(["pkill", "-9", "-f", "translateLocally"], check=False)
            logging.debug(f"Fine terminazione processi: {time.time() - start_time:.2f}s")
            QApplication.processEvents()
            logging.debug(f"ProcessEvents completato: {time.time() - start_time:.2f}s")
            event.accept()
        except Exception as e:
            logging.error(f"Errore durante la chiusura della finestra: {e}", exc_info=True)
            event.accept()
        finally:
            logging.info(f"Chiusura completata: {time.time() - start_time:.2f}s")