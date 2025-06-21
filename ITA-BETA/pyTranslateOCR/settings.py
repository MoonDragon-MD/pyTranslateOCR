import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QDialogButtonBox, QLineEdit, QSlider, QFileDialog)
from ini_controll import save_preferences, load_preferences
from tts import get_available_voices
from translation.locally import check_translate_locally_availability
import platform

# logging.basicConfig(level=logging.DEBUG)

class KeySelectionDialog(QDialog):
    def __init__(self, parent, ocr_temp, ocr_fixed, ocr_set_fixed):
        super().__init__(parent)
        self.setWindowTitle("Imposta Scorciatoie")
        layout = QVBoxLayout()
        self.ocr_temp_input = QLineEdit(ocr_temp.replace('<alt>+', 'alt+'))
        self.ocr_fixed_input = QLineEdit(ocr_fixed.replace('<alt>+', 'alt+'))
        self.ocr_set_fixed_input = QLineEdit(ocr_set_fixed.replace('<alt>+', 'alt+'))
        layout.addWidget(QLabel("Scorciatoia OCR Temporaneo (es. alt+c):"))
        layout.addWidget(self.ocr_temp_input)
        layout.addWidget(QLabel("Scorciatoia OCR Fisso (es. alt+f):"))
        layout.addWidget(self.ocr_fixed_input)
        layout.addWidget(QLabel("Scorciatoia Area Fissa (es. alt+s):"))
        layout.addWidget(self.ocr_set_fixed_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected_key_ocr_temp(self):
        return self.ocr_temp_input.text().replace('alt+', '<alt>+')

    def get_selected_key_ocr_fixed(self):
        return self.ocr_fixed_input.text().replace('alt+', '<alt>+')

    def get_selected_key_ocr_set_fixed(self):
        return self.ocr_set_fixed_input.text().replace('alt+', '<alt>+')

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Impostazioni Avanzate")
        self.setGeometry(150, 150, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Selezione motore OCR
        ocr_layout = QHBoxLayout()
        ocr_layout.addWidget(QLabel("Motore OCR:"))
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems(["Tesseract", "Umi-OCR", "Umi-OCR_server"])
        self.ocr_engine_combo.setCurrentText(self.parent.ocr_engine)
        ocr_layout.addWidget(self.ocr_engine_combo)
        layout.addLayout(ocr_layout)

        # Percorso Umi-OCR
        umi_layout = QHBoxLayout()
        umi_layout.addWidget(QLabel("Percorso Umi-OCR:"))
        self.umi_ocr_path_input = QLineEdit(self.parent.umi_ocr_path)
        umi_layout.addWidget(self.umi_ocr_path_input)
        umi_browse_button = QPushButton("Sfoglia")
        umi_browse_button.clicked.connect(self.browse_umi_ocr)
        umi_layout.addWidget(umi_browse_button)
        layout.addLayout(umi_layout)

        # Percorso Tesseract
        tesseract_layout = QHBoxLayout()
        tesseract_layout.addWidget(QLabel("Percorso Tesseract:"))
        self.tesseract_path_input = QLineEdit(self.parent.tesseract_path)
        tesseract_layout.addWidget(self.tesseract_path_input)
        tesseract_browse_button = QPushButton("Sfoglia")
        tesseract_browse_button.clicked.connect(self.browse_tesseract)
        tesseract_layout.addWidget(tesseract_browse_button)
        layout.addLayout(tesseract_layout)

        # Selezione motore di traduzione
        translate_layout = QHBoxLayout()
        translate_layout.addWidget(QLabel("Motore Traduzione:"))
        self.translate_engine_combo = QComboBox()
        self.translate_engine_combo.addItems(["Google", "LibreTranslate", "NLLB", "Locally"])
        self.translate_engine_combo.setCurrentText(self.parent.translate_engine)
        translate_layout.addWidget(self.translate_engine_combo)
        layout.addLayout(translate_layout)

        # Percorso traduzione locale
        locally_layout = QHBoxLayout()
        locally_layout.addWidget(QLabel("Percorso translateLocally (WIN):"))
        self.translate_locally_path_input = QLineEdit(self.parent.translate_locally_path)
        locally_layout.addWidget(self.translate_locally_path_input)
        locally_browse_button = QPushButton("Sfoglia")
        locally_browse_button.clicked.connect(self.browse_locally)
        locally_layout.addWidget(locally_browse_button)
        layout.addLayout(locally_layout)

        # Pulsante per scorciatoie da tastiera
        shortcuts_button = QPushButton("Imposta Scorciatoie da Tastiera")
        shortcuts_button.clicked.connect(self.open_key_selection)
        layout.addWidget(shortcuts_button)

        # Pulsanti OK/Annulla
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def browse_umi_ocr(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleziona la cartella di Umi-OCR")
        if directory:
            self.umi_ocr_path_input.setText(directory)

    def browse_tesseract(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleziona l'eseguibile di Tesseract")
        if file:
            self.tesseract_path_input.setText(file)

    def browse_locally(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleziona il file di traduzione locale")
        if file:
            self.translate_locally_path_input.setText(file)

    def open_key_selection(self):
        try:
            dialog = KeySelectionDialog(
                self,
                self.parent.shortcuts.get('ocr_temp', '<alt>+c'),
                self.parent.shortcuts.get('ocr_fixed', '<alt>+f'),
                self.parent.shortcuts.get('ocr_set_fixed', '<alt>+s')
            )
            if dialog.exec_():
                # Aggiorna le scorciatoie
                self.parent.shortcuts = {
                    'ocr_temp': dialog.get_selected_key_ocr_temp(),
                    'ocr_fixed': dialog.get_selected_key_ocr_fixed(),
                    'ocr_set_fixed': dialog.get_selected_key_ocr_set_fixed()
                }
                self.parent.setup_shortcuts()
                # Salva le preferenze immediatamente
                save_preferences(
                    self.parent.umi_ocr_path,
                    self.parent.tesseract_path,
                    self.parent.source_lang_combo.currentText(),
                    self.parent.target_lang_combo.currentText(),
                    self.parent.ocr_engine,
                    self.parent.translate_engine,
                    self.parent.translate_locally_path,
                    self.parent.shortcuts,
                    self.parent.fixed_area,
                    self.parent.area_temp,
                    self.parent.tts_voice,
                    self.parent.tts_rate,
                    self.parent.contrast,
                    self.parent.sharpness,
                    self.parent.invert
                )
                logging.info(f"Shortcuts updated: {self.parent.shortcuts}")
        except Exception as e:
            logging.error(f"Error opening shortcut dialog: {e}")

    def save_settings(self):
        try:
            # Aggiorna i valori nel parent
            self.parent.umi_ocr_path = self.umi_ocr_path_input.text()
            self.parent.tesseract_path = self.tesseract_path_input.text()
            self.parent.ocr_engine = self.ocr_engine_combo.currentText()
            self.parent.translate_engine = self.translate_engine_combo.currentText()
            self.parent.translate_locally_path = self.translate_locally_path_input.text()

            # Salva le preferenze
            save_preferences(
                self.parent.umi_ocr_path,
                self.parent.tesseract_path,
                self.parent.source_lang_combo.currentText(),
                self.parent.target_lang_combo.currentText(),
                self.parent.ocr_engine,
                self.parent.translate_engine,
                self.parent.translate_locally_path,
                self.parent.shortcuts,
                self.parent.fixed_area,
                self.parent.area_temp,
                self.parent.tts_voice,
                self.parent.tts_rate,
                self.parent.contrast,
                self.parent.sharpness,
                self.parent.invert
            )
            logging.info("Impostazioni avanzate salvate correttamente")
            self.accept()
        except Exception as e:
            logging.error(f"Errore nel salvataggio delle impostazioni avanzate: {e}")

class TTSSettingsWindow(QDialog):
    def __init__(self, current_voice, current_rate, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configura TTS")
        layout = QVBoxLayout()
        self.voice_label = QLabel("Seleziona voce:")
        layout.addWidget(self.voice_label)
        self.voices = get_available_voices()
        self.voice_options = [voice.name for voice in self.voices]
        self.voice_combobox = QComboBox()
        self.voice_combobox.addItems(self.voice_options)
        if current_voice in self.voice_options:
            self.voice_combobox.setCurrentText(current_voice)
        else:
            self.voice_combobox.setCurrentIndex(0)
        layout.addWidget(self.voice_combobox)
        self.speed_label = QLabel("Velocit? (Parole al minuto):")
        layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(current_rate)
        layout.addWidget(self.speed_slider)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_settings(self):
        voice_name = self.voice_combobox.currentText()
        voice_id = next((voice.id for voice in self.voices if voice.name == voice_name), None)
        return voice_id, self.speed_slider.value()

class ImageSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Immagine")
        layout = QVBoxLayout()
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(5, 30)
        self.contrast_slider.setValue(int(parent.contrast * 10))
        layout.addWidget(QLabel("Contrasto (0.5 - 3.0):"))
        layout.addWidget(self.contrast_slider)
        self.sharpness_slider = QSlider(Qt.Horizontal)
        self.sharpness_slider.setRange(0, 5)
        self.sharpness_slider.setValue(parent.sharpness)
        layout.addWidget(QLabel("Nitidezza:"))
        layout.addWidget(self.sharpness_slider)
        self.invert_checkbox = QCheckBox("Inverti colore")
        self.invert_checkbox.setChecked(parent.invert)
        layout.addWidget(self.invert_checkbox)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_settings(self):
        parent = self.parent()
        parent.contrast = self.contrast_slider.value() / 10.0
        parent.sharpness = self.sharpness_slider.value()
        parent.invert = self.invert_checkbox.isChecked()
        save_preferences(parent.umi_ocr_path, parent.tesseract_path, parent.source_lang,
                         parent.target_lang, parent.ocr_engine, parent.translate_engine,
                         parent.translate_locally_path, parent.shortcuts, parent.fixed_area,
                         parent.area_temp, parent.tts_voice, parent.tts_rate,
                         parent.contrast, parent.sharpness, parent.invert)
        self.accept()