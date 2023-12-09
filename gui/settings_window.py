from typing import Optional
from core.config import load_config, save_config
from PyQt5.QtWidgets import QGridLayout, QLabel, QDialog, QDialogButtonBox, QWidget, QSizePolicy
from gui.file_path_widget import FilePathWidget


class SettingsWindow(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super(SettingsWindow, self).__init__(parent)

        self.setWindowTitle('Settings')

        grid = QGridLayout(self)

        self.__aseprite_file_widget = FilePathWidget(
            select_type=FilePathWidget.SelectType.FILE
        )
        self.__aseprite_file_widget.add_file_filter('Aseprite app', ['Aseprite.exe'])
        self.__aseprite_file_widget.add_file_filter('Executable files', ['*.exe'])
        self.__aseprite_file_widget.add_file_filter('All files', [''])
        grid.addWidget(QLabel('Aseprite app:'), 0, 0)
        grid.addWidget(self.__aseprite_file_widget, 0, 1)

        self.__blender_file_widget = FilePathWidget(
            select_type=FilePathWidget.SelectType.FILE
        )
        self.__blender_file_widget.add_file_filter('Blender app', ['blender.exe'])
        self.__blender_file_widget.add_file_filter('Executable files', ['*.exe'])
        self.__blender_file_widget.add_file_filter('All files', [''])
        grid.addWidget(QLabel('Blender app:'), 1, 0)
        grid.addWidget(self.__blender_file_widget, 1, 1)

        self.__button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.__button_box.accepted.connect(self.__before_accept)
        self.__button_box.rejected.connect(self.reject)
        grid.addWidget(self.__button_box, 2, 0, 1, 2)

        self.adjustSize()
        self.setFixedSize(self.size())

        self.__fill_ui()

    def __fill_ui(self):
        config = load_config()
        self.__aseprite_file_widget.line_edit.setText(config.aseprite)
        self.__blender_file_widget.line_edit.setText(config.blender)

    def __before_accept(self):
        config = load_config()
        config.aseprite = self.__aseprite_file_widget.line_edit.text()
        config.blender = self.__blender_file_widget.line_edit.text()
        save_config(config)
        self.accept()
