import sys
import os
import random
import string
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect

# === Pfade ===
ASSET_DIR = "assets"
IMAGE_DIR = os.path.join(ASSET_DIR, "images")
SOUND_PATH = os.path.join(ASSET_DIR, "sounds", "nostromo.wav")

class MatrixIntro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KaiLa4000 Initialisierung")
        self.showFullScreen()
        self.setStyleSheet("background-color: black; color: #00FF00;")

        self.labels = []
        self.lines = [[] for _ in range(4)]  # Weniger Spalten, aber mehr Zeilen nach unten
        self.max_lines = 50  # Erhöht für mehr vertikale Matrix-Zeilen
        self.frames_to_run = 120
        self.counter = 0

        self.layout_container = QHBoxLayout()
        self.setLayout(self.layout_container)

        font = QFont("Courier", 24)
        for _ in range(4):
            lbl = QLabel()
            lbl.setFont(font)
            lbl.setStyleSheet("color: #00FF00;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.labels.append(lbl)
            self.layout_container.addWidget(lbl)

        self.play_sound()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(70)

    def generate_data(self, length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def update_labels(self):
        for i, label in enumerate(self.labels):
            new_line = self.generate_data(20)
            self.lines[i].append(new_line)
            if len(self.lines[i]) > self.max_lines:
                self.lines[i].pop(0)
            label.setText("\n".join(self.lines[i]))

        self.counter += 1
        if self.counter >= self.frames_to_run:
            self.timer.stop()
            self.show_logo()

    def play_sound(self):
        try:
            self.sound = QSoundEffect()
            self.sound.setSource(QUrl.fromLocalFile(os.path.abspath(SOUND_PATH)))
            self.sound.setLoopCount(1)
            self.sound.setVolume(0.25)
            self.sound.play()
        except Exception as e:
            print("Soundfehler:", e)

    def show_logo(self):
        for i in reversed(range(self.layout_container.count())):
            widget = self.layout_container.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("Wähle 1 = alexscreen | 2 = aluscreen | 3 = alexplace | 4 = Escape" )
        self.text_label.setFont(QFont("Courier", 22, QFont.Weight.Bold))
        self.text_label.setStyleSheet("color: #00FF00;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(self.image_label)
        vbox.addWidget(self.text_label)

        QWidget().setLayout(self.layout())  # Vorheriges Layout lösen
        self.setLayout(vbox)

        self.keyPressEvent = self.handle_key

    def handle_key(self, event):
        key = event.key()
        image_file = None

        if key == Qt.Key.Key_1:
            image_file = "alexscreen.jpg"
        elif key == Qt.Key.Key_2:
            image_file = "aluscreen.jpg"
        elif key == Qt.Key.Key_3:
            image_file = "alexplace.jpg"
        elif key == Qt.Key.Key_4 or key == Qt.Key.Key_Escape:
            QApplication.quit()

        if image_file:
            full_path = os.path.join(IMAGE_DIR, image_file)
            pixmap = QPixmap(full_path)
            if pixmap.isNull():
                print(f"⚠️ Bild konnte nicht geladen werden: {full_path}")
            else:
                pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                self.text_label.setText(f"Bereich '{image_file[:-4]}' geladen – ENTER zum Start")
                self.next_view = image_file[:-4]

        if key == Qt.Key.Key_Return:
            if hasattr(self, 'next_view'):
                self.start_main(self.next_view)

    def start_main(self, view_name):
        from router.navigation import get_view
        self.close()
        self.main_window = QWidget()
        self.main_window.setWindowTitle(f"KaiLa4000 | {view_name}")
        layout = QVBoxLayout()
        layout.addWidget(get_view(view_name))
        self.main_window.setLayout(layout)
        self.main_window.show()

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    try:
        from utils.helpers import apply_stylesheet
        apply_stylesheet(app, "assets/styles/dark_theme.qss")
    except Exception as e:
        print("Stylesheet konnte nicht geladen werden:", e)
    window = MatrixIntro()
    window.show()
    sys.exit(app.exec())
