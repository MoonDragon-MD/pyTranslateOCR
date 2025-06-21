import logging
import sys
import os
import argparse
import configparser
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QColor, QPen, QFont
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QApplication

# logging.basicConfig(level=logging.DEBUG)

def run_ocr(engine: str, image_path: str, lang: str, tesseract_path: str) -> str:
    from ocr.tesseract import map_to_tesseract_language
    tesseract_lang = map_to_tesseract_language(lang)
    cmd = [tesseract_path or 'tesseract', image_path, '-', '-l', tesseract_lang, 'txt']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logging.debug(f"OCR eseguito con lingua: {tesseract_lang}")
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Errore nell'esecuzione di Tesseract: {e}")
        return ""

def load_preferences(ini_file: str, section: str) -> tuple:
    try:
        config = configparser.ConfigParser()
        config.read(ini_file)
        # ... (other preference loading)
        sharpness = config.get(section, 'imgMod_nit', fallback='1')
        try:
            sharpness = int(float(sharpness))  # Convert to float, then int
        except ValueError:
            logging.error(f"Errore in imgMod_nit: invalid literal for int() with base 10: '{sharpness}', usando valore predefinito")
            sharpness = 1
        # ... (rest of preferences)
        return (..., sharpness, ...)
    except Exception as e:
        logging.error(f"Errore nel caricamento delle preferenze: {e}")
        return default_preferences()

class SelectionView(QGraphicsView):
    def __init__(self, ini_file="ocrqt.ini", section="area_temp"):
        super().__init__()
        self.ini_file = ini_file
        self.section = section
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5)
        try:
            screen_geometry = QApplication.instance().desktop().availableGeometry()
        except AttributeError:
            logging.error("QApplication non inizializzata correttamente")
            sys.exit(1)
        self.setGeometry(screen_geometry)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, self.width(), self.height())
        font = QFont("Arial", 20)
        font.setBold(True)
        self.text_black = QGraphicsTextItem("Seleziona un'area")
        self.text_black.setFont(font)
        self.text_black.setDefaultTextColor(QColor("black"))
        self.text_black.setPos(50, 50)
        self.scene.addItem(self.text_black)
        self.text_white = QGraphicsTextItem("Seleziona un'area")
        self.text_white.setFont(font)
        self.text_white.setDefaultTextColor(QColor("white"))
        self.text_white.setPos(50, 80)
        self.scene.addItem(self.text_white)
        self.start_point = None
        self.end_point = None
        self.rect_item = QGraphicsRectItem()
        self.rect_item.setPen(QPen(QColor(255, 0, 0), 2))
        self.rect_item.setBrush(QColor(0, 0, 0, 50))
        self.scene.addItem(self.rect_item)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        logging.debug("SelectionView inizializzato")

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.rect_item.setRect(QRectF(self.start_point, self.end_point))
                self.rect_item.setVisible(True)
                self.update()
                logging.debug(f"Selezione iniziata a: {self.start_point}")
        except Exception as e:
            logging.error(f"Errore in mousePressEvent: {e}")

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() & Qt.LeftButton:
                self.end_point = event.pos()
                self.rect_item.setRect(QRectF(self.start_point, self.end_point).normalized())
                self.update()
                # Logging disabilitato per ridurre verbosità
                # logging.debug(f"Mouse spostato a: {self.end_point}")
        except Exception as e:
            logging.error(f"Errore in mouseMoveEvent: {e}")

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.end_point = event.pos()
                rect = self.rect_item.rect().normalized()
                if rect.width() > 5 and rect.height() > 5:
                    global_start = self.mapToGlobal(self.start_point)
                    global_end = self.mapToGlobal(self.end_point)
                    global_rect = QRect(
                        min(global_start.x(), global_end.x()),
                        min(global_start.y(), global_end.y()),
                        abs(global_end.x() - global_start.x()),
                        abs(global_end.y() - global_start.y())
                    )
                    area = [int(global_rect.left()), int(global_rect.top()),
                            int(global_rect.width()), int(global_rect.height())]
                    config = configparser.ConfigParser()
                    if os.path.exists(self.ini_file):
                        config.read(self.ini_file)
                    if 'Settings' not in config:
                        config['Settings'] = {}
                    config['Settings'][self.section] = str(area)
                    with open(self.ini_file, 'w') as f:
                        config.write(f)
                    logging.info(f"Area salvata in {self.ini_file} [{self.section}]: {area}")
                else:
                    logging.warning("Area troppo piccola, non salvata")
                self.close()
        except Exception as e:
            logging.error(f"Errore in mouseReleaseEvent: {e}")

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                logging.debug("Selezione annullata con Esc")
                self.close()
        except Exception as e:
            logging.error(f"Errore in keyPressEvent: {e}")

    def closeEvent(self, event):
        logging.debug("SelectionView chiuso")
        event.accept()

def main():
    parser = argparse.ArgumentParser(description="Selezione area dello schermo")
    parser.add_argument("--ini", default="ocrqt.ini", help="File INI per salvare le coordinate")
    parser.add_argument("--section", default="area_temp", choices=["area_temp", "fixed_area"],
                        help="Sezione INI da aggiornare (area_temp o fixed_area)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    view = SelectionView(ini_file=args.ini, section=args.section)
    view.showFullScreen()
    view.activateWindow()
    view.raise_()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()