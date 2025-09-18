import os
import json
import sys
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QGraphicsBlurEffect,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QFont, QIcon, QFontDatabase
from PyQt6.QtCore import Qt, QRect

# --------------------------
# JSON Processing Functions
# --------------------------
def clean_json(file_path, mod_name="", workshop_id=""):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "RequiredMods" in data:
            before = len(data["RequiredMods"])
            data["RequiredMods"] = [
                mod for mod in data["RequiredMods"]
                if not (
                    (mod_name and mod_name.lower() == mod.get("Name","").lower()) or
                    (workshop_id and str(workshop_id) == str(mod.get("WorkshopId","")))
                )
            ]
            after = len(data["RequiredMods"])

            if before != after:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                return True
    except Exception as e:
        print(f"Error with {file_path}: {e}")
    return False

def process_folders(folders, mod_name="", workshop_id=""):
    changed_files = []
    for folder in folders:
        folder = folder.strip("{}")
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(".json"):
                        file_path = os.path.join(root, file)
                        if clean_json(file_path, mod_name, workshop_id):
                            changed_files.append(file_path)
        elif folder.endswith(".json") and os.path.isfile(folder):
            if clean_json(folder, mod_name, workshop_id):
                changed_files.append(folder)
    return changed_files

# --------------------------
# Main Application
# --------------------------
class DragDropApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 4:5 window
        self.window_width = 480
        self.window_height = 600
        self.setWindowTitle("People Playground Mod Remover | Nayu.xyz")
        self.setFixedSize(self.window_width, self.window_height)
        self.setAcceptDrops(True)

        # App icon
        try:
            self.setWindowIcon(QIcon(resource_path("icon.ico")))
        except Exception as e:
            print(f"Could not load icon: {e}")

        # Load and crop background
        try:
            bg = QPixmap(resource_path("background.png"))
            bg_width = bg.width()
            bg_height = bg.height()
            target_ratio = self.window_width / self.window_height
            current_ratio = bg_width / bg_height

            if current_ratio > target_ratio:
                new_width = int(bg_height * target_ratio)
                x_offset = (bg_width - new_width) // 2
                crop_rect = QRect(x_offset, 0, new_width, bg_height)
            else:
                new_height = int(bg_width / target_ratio)
                y_offset = (bg_height - new_height) // 2
                crop_rect = QRect(0, y_offset, bg_width, new_height)

            bg_cropped = bg.copy(crop_rect).scaled(self.window_width, self.window_height)
            self.bg_label = QLabel(self)
            self.bg_label.setPixmap(bg_cropped)
            self.bg_label.setGeometry(0, 0, self.window_width, self.window_height)
        except Exception as e:
            print(f"Could not load background: {e}")

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(resource_path("RampartOne-Regular.ttf"))
        if font_id == -1:
            header_font = QFont("Arial", 20, QFont.Weight.Bold)
            desc_font = QFont("Arial", 12)
            input_font = QFont("Arial", 12)
            drop_font = QFont("Arial", 14)
            button_font = QFont("Arial", 14)
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            header_font = QFont(font_family, 20)
            desc_font = QFont(font_family, 12)
            input_font = QFont(font_family, 12)
            drop_font = QFont(font_family, 14)
            button_font = QFont(font_family, 14)

        # --------------------------
        # Header
        # --------------------------
        self.header_bg = QLabel(self)
        self.header_bg.setGeometry(90, 20, 300, 50)
        self.header_bg.setStyleSheet("background-color: rgba(255,255,255,120); border-radius: 10px;")
        blur_header = QGraphicsBlurEffect()
        blur_header.setBlurRadius(8)
        self.header_bg.setGraphicsEffect(blur_header)

        self.header_text = QLabel("PPG Mod Remover", self)
        self.header_text.setGeometry(90, 20, 300, 50)
        self.header_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_text.setFont(header_font)

        # --------------------------
        # Description
        # --------------------------
        self.desc_bg = QLabel(self)
        self.desc_bg.setGeometry(90, 85, 300, 25)
        self.desc_bg.setStyleSheet("background-color: rgba(255,255,255,150); border-radius: 5px;")
        blur_desc = QGraphicsBlurEffect()
        blur_desc.setBlurRadius(6)
        self.desc_bg.setGraphicsEffect(blur_desc)

        self.desc_text = QLabel("Input Mod Name OR Workshop ID", self)
        self.desc_text.setGeometry(90, 85, 300, 25)
        self.desc_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_text.setFont(desc_font)

        # --------------------------
        # Input boxes (more opaque)
        # --------------------------
        self.mod_name_bg = QLabel(self)
        self.mod_name_bg.setGeometry(90, 120, 140, 30)
        self.mod_name_bg.setStyleSheet("background-color: rgba(255,255,255,220); border-radius: 5px;")
        blur_mod = QGraphicsBlurEffect()
        blur_mod.setBlurRadius(8)
        self.mod_name_bg.setGraphicsEffect(blur_mod)

        self.workshop_id_bg = QLabel(self)
        self.workshop_id_bg.setGeometry(250, 120, 140, 30)
        self.workshop_id_bg.setStyleSheet("background-color: rgba(255,255,255,220); border-radius: 5px;")
        blur_ws = QGraphicsBlurEffect()
        blur_ws.setBlurRadius(8)
        self.workshop_id_bg.setGraphicsEffect(blur_ws)

        self.mod_name_input = QLineEdit(self)
        self.mod_name_input.setPlaceholderText("Mod Name")
        self.mod_name_input.setGeometry(90, 120, 140, 30)
        self.mod_name_input.setFont(input_font)
        self.mod_name_input.setStyleSheet("background: transparent; border: none; padding-left:5px;")

        self.workshop_id_input = QLineEdit(self)
        self.workshop_id_input.setPlaceholderText("Workshop ID")
        self.workshop_id_input.setGeometry(250, 120, 140, 30)
        self.workshop_id_input.setFont(input_font)
        self.workshop_id_input.setStyleSheet("background: transparent; border: none; padding-left:5px;")

        # --------------------------
        # Drag box
        # --------------------------
        self.drop_bg = QLabel(self)
        self.drop_bg.setGeometry(90, 170, 300, 250)
        self.drop_bg.setStyleSheet("""
            background-color: rgba(255,255,255,120);
            border: 3px dashed rgba(0,0,0,180);
            border-radius: 10px;
        """)
        self.blur_drop = QGraphicsBlurEffect()
        self.blur_drop.setBlurRadius(10)
        self.drop_bg.setGraphicsEffect(self.blur_drop)

        self.drop_text = QLabel("Drag Files Here", self)
        self.drop_text.setGeometry(90, 170, 300, 250)
        self.drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_text.setFont(drop_font)

        # --------------------------
        # File counter
        # --------------------------
        self.counter_label = QLabel("Files: 0", self)
        self.counter_label.setGeometry(90, 390, 300, 25)
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.counter_label.setFont(input_font)

        # --------------------------
        # Buttons (centered + bright white hover)
        # --------------------------
        button_width = 160
        button_height = 65
        spacing = 20
        total_width = button_width * 2 + spacing
        start_x = (self.window_width - total_width) // 2
        y_pos = 430

        # Clear / Reset Button
        self.clear_button_bg = QLabel(self)
        self.clear_button_bg.setGeometry(start_x, y_pos, button_width, button_height)
        self.clear_button_bg.setStyleSheet("background-color: rgba(255,255,255,180); border-radius: 15px;")
        blur_clear = QGraphicsBlurEffect()
        blur_clear.setBlurRadius(6)
        self.clear_button_bg.setGraphicsEffect(blur_clear)

        self.clear_button = QPushButton("Clear Files", self)
        self.clear_button.setGeometry(start_x, y_pos, button_width, button_height)
        self.clear_button.setFont(button_font)
        self.clear_button.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: black; }
            QPushButton:hover { background-color: rgba(255,255,255,220); border-radius: 15px; }
        """)
        self.clear_button.clicked.connect(self.clear_or_reset)

        # Start Removal Button
        self.start_button_bg = QLabel(self)
        self.start_button_bg.setGeometry(start_x + button_width + spacing, y_pos, button_width, button_height)
        self.start_button_bg.setStyleSheet("background-color: rgba(255,255,255,180); border-radius: 15px;")
        blur_button = QGraphicsBlurEffect()
        blur_button.setBlurRadius(6)
        self.start_button_bg.setGraphicsEffect(blur_button)

        self.start_button = QPushButton("Start Removal", self)
        self.start_button.setGeometry(start_x + button_width + spacing, y_pos, button_width, button_height)
        self.start_button.setFont(button_font)
        self.start_button.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: black; }
            QPushButton:hover { background-color: rgba(255,255,255,220); border-radius: 15px; }
        """)
        self.start_button.clicked.connect(self.start_removal)

        self.dragged_paths = []

    # --------------------------
    # Drag & Drop Events
    # --------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.drop_bg.setStyleSheet("""
                background-color: rgba(255,255,255,150);
                border: 3px dashed #4A90E2;
                border-radius: 10px;
            """)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.drop_bg.setStyleSheet("""
            background-color: rgba(255,255,255,120);
            border: 3px dashed rgba(0,0,0,180);
            border-radius: 10px;
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            f = url.toLocalFile()
            if f not in self.dragged_paths:
                self.dragged_paths.append(f)
        self.counter_label.setText(f"Files: {len(self.dragged_paths)}")
        self.dragLeaveEvent(event)

    # --------------------------
    # Start Removal
    # --------------------------
    def start_removal(self):
        mod_name = self.mod_name_input.text().strip()
        workshop_id = self.workshop_id_input.text().strip()
        if not mod_name and not workshop_id:
            QMessageBox.warning(self, "Input Required", "Input Mod Name OR Workshop ID First")
            return

        if not self.dragged_paths:
            return

        process_folders(self.dragged_paths, mod_name, workshop_id)
        self.start_button.setText("Done")
        self.clear_button.setText("Reset")
        QMessageBox.information(self, "Contraption Updated", "Mod Removed Successfully!")

    # --------------------------
    # Clear/Reset Button
    # --------------------------
    def clear_or_reset(self):
        if self.start_button.text() == "Done":
            self.dragged_paths = []
            self.counter_label.setText("Files: 0")
            self.start_button.setText("Start Removal")
            self.clear_button.setText("Clear Files")
        else:
            self.dragged_paths = []
            self.counter_label.setText("Files: 0")

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropApp()
    window.show()
    sys.exit(app.exec())

#Last Edit: at 2025-09-18 01:48:00 EST - Nayu.xyz