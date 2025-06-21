import platform
import logging
import os
from threading import Thread
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

if platform.system() == "Windows":
    import keyboard
else:
    from pynput import keyboard

# Configura il logging
# logging.basicConfig(level=logging.DEBUG)

# Classe di supporto per emettere segnali Qt
class SignalEmitter(QObject):
    ocr_temp_signal = pyqtSignal()
    ocr_fixed_signal = pyqtSignal()
    set_fixed_signal = pyqtSignal()

class KeyboardListener(Thread):
    def __init__(self, shortcuts, ocr_temp_callback, ocr_fixed_callback, set_fixed_callback, overlay_open_flag):
        super().__init__()
        self.shortcuts = shortcuts
        self.overlay_open_flag = overlay_open_flag
        self.running = True
        self.listener = None
        self.alt_pressed = False
        
        # Crea un emettitore di segnali
        self.signal_emitter = SignalEmitter()
        # Collega i segnali alle callback
        self.signal_emitter.ocr_temp_signal.connect(ocr_temp_callback)
        self.signal_emitter.ocr_fixed_signal.connect(ocr_fixed_callback)
        self.signal_emitter.set_fixed_signal.connect(set_fixed_callback)
        
        logging.debug(f"KeyboardListener inizializzato con scorciatoie: {self.shortcuts}")

    def run(self):
        if platform.system() == "Windows":
            self.run_windows()
        else:
            self.run_linux()

    def run_windows(self):
        try:
            hotkeys = {
                self.shortcuts['ocr_temp'].replace('<alt>+', 'alt+'): lambda: self.signal_emitter.ocr_temp_signal.emit(),
                self.shortcuts['ocr_fixed'].replace('<alt>+', 'alt+'): lambda: self.signal_emitter.ocr_fixed_signal.emit(),
                self.shortcuts['ocr_set_fixed'].replace('<alt>+', 'alt+'): lambda: self.signal_emitter.set_fixed_signal.emit()
            }
            for key, func in hotkeys.items():
                keyboard.add_hotkey(key, func)
            keyboard.wait()
        except Exception as e:
            logging.error(f"Errore nel keyboard listener (Windows): {e}")
        finally:
            keyboard.unhook_all()
            logging.debug("Hotkey rimossi (Windows)")

    def run_linux(self):
        try:
            def on_press(key):
                if not self.running or self.overlay_open_flag() or self._is_dialog_open():
                    return
                try:
                    if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                        self.alt_pressed = True
                        return
                    key_str = str(key).replace("'", "").lower()
                    if key_str.startswith('key.'):
                        key_str = f"<{key_str[4:]}>"
                    mods = '<alt>+' if self.alt_pressed else ''
                    shortcut = f"{mods}{key_str}"
                    if shortcut in self.shortcuts.values():
                        logging.debug(f"Scorciatoia rilevata: {shortcut}")
                        if shortcut == self.shortcuts.get('ocr_temp', '<alt>+c'):
                            logging.info("Esecuzione callback OCR temporaneo")
                            self.signal_emitter.ocr_temp_signal.emit()
                        elif shortcut == self.shortcuts.get('ocr_fixed', '<alt>+f'):
                            logging.info("Esecuzione callback OCR fisso")
                            self.signal_emitter.ocr_fixed_signal.emit()
                        elif shortcut == self.shortcuts.get('ocr_set_fixed', '<alt>+s'):
                            logging.info("Esecuzione callback impostazione area fissa")
                            self.signal_emitter.set_fixed_signal.emit()
                except Exception as e:
                    logging.error(f"Errore nella gestione della scorciatoia: {e}")

            def on_release(key):
                if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    self.alt_pressed = False

            self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self.listener.start()
            while self.running:
                self.listener.wait()
        except Exception as e:
            logging.error(f"Errore nel keyboard listener (Linux): {e}")
        finally:
            if self.listener:
                self.listener.stop()
                logging.debug("KeyboardListener (Linux) fermato")

    def _is_dialog_open(self):
        active_window = QApplication.activeWindow()
        return active_window is not None and active_window != QApplication.activeModalWidget()

    def stop(self):
        self.running = False
        if platform.system() == "Windows":
            try:
                keyboard.unhook_all()
                logging.debug("KeyboardListener (Windows) fermato")
            except Exception as e:
                logging.error(f"Errore durante l'arresto (Windows): {e}")
        else:
            if self.listener:
                self.listener.stop()
                self.listener.join(timeout=0.1)
                logging.debug("KeyboardListener (Linux) fermato")