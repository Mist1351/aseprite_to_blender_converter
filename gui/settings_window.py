from typing import Optional
from core.config import load_config, save_config
from PyQt5.QtWidgets import QFileDialog, QPushButton, QGridLayout, QLabel, QLineEdit, QDialog, QDialogButtonBox


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.button_box: Optional[QPushButton] = None
        self.blender_button: Optional[QPushButton] = None
        self.blender_line_edit: Optional[QLineEdit] = None
        self.aseprite_button: Optional[QPushButton] = None
        self.aseprite_line_edit: Optional[QLineEdit] = None
        self._init_ui()
        self._fill_ui()

    def _init_ui(self):
        self.setWindowTitle('Settings')

        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QLabel('Aseprite file path:'), 0, 0)
        self.aseprite_line_edit = QLineEdit()
        self.aseprite_line_edit.setReadOnly(True)
        grid.addWidget(self.aseprite_line_edit, 0, 1)
        self.aseprite_button = QPushButton('Select')
        self.aseprite_button.clicked.connect(self.select_aseprite_file)
        grid.addWidget(self.aseprite_button, 0, 2)

        grid.addWidget(QLabel('Blender file path:'), 1, 0)
        self.blender_line_edit = QLineEdit()
        self.blender_line_edit.setReadOnly(True)
        grid.addWidget(self.blender_line_edit, 1, 1)
        self.blender_button = QPushButton('Select')
        self.blender_button.clicked.connect(self.select_blender_file)
        grid.addWidget(self.blender_button, 1, 2)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._before_accept)
        self.button_box.rejected.connect(self.reject)
        grid.addWidget(self.button_box, 2, 0, 1, 3)

    def _fill_ui(self):
        config = load_config()
        self.aseprite_line_edit.setText(config.aseprite)
        self.blender_line_edit.setText(config.blender)

    def _before_accept(self):
        config = load_config()
        config.aseprite = self.aseprite_line_edit.text()
        config.blender = self.blender_line_edit.text()
        save_config(config)
        self.accept()

    def select_aseprite_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Aseprite app', '',
                                                   'Executable (*.exe);;All files (*)')
        if file_path:
            self.aseprite_line_edit.setText(file_path)

    def select_blender_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Blender app', '',
                                                   'Executable (*.exe);;All files (*)')
        if file_path:
            self.blender_line_edit.setText(file_path)
