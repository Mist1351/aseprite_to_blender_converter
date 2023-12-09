from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QGridLayout, QFileDialog


@dataclass
class FileFilter:
    title: str
    extensions: List[str]


class FilePathWidget(QWidget):
    class SelectType(Enum):
        FILE = 1
        DIRECTORY = 2

    def __init__(self, select_button_text: str = 'Select', callback: Optional[Callable[[], None]] = None,
                 select_type: SelectType = SelectType.FILE, parent: Optional[QWidget] = None):
        super(FilePathWidget, self).__init__(parent)

        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)

        self.__file_filters: List[FileFilter] = []
        self.button = QPushButton(select_button_text)
        if callback is not None:
            self.button.clicked.connect(callback)
        else:
            if select_type == FilePathWidget.SelectType.FILE:
                self.button.clicked.connect(self.__select_file)
            elif select_type == FilePathWidget.SelectType.DIRECTORY:
                self.button.clicked.connect(self.__select_directory)

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(self.line_edit, 0, 0)
        grid.addWidget(self.button, 0, 1)

    def add_file_filter(self, title: str, extensions: List[str]):
        self.__file_filters.append(FileFilter(title, extensions))

    def __select_directory(self):
        dir_path = self.line_edit.text()
        if QFileInfo(dir_path).isDir():
            dir_path = QFileInfo(dir_path).absoluteDir().path()
        else:
            dir_path = ''

        dir_path = QFileDialog.getExistingDirectory(self, 'Select directory', dir_path)
        if dir_path:
            self.line_edit.setText(dir_path)

    def __select_file(self):
        dir_path = self.line_edit.text()
        if QFileInfo(dir_path).isFile():
            dir_path = QFileInfo(dir_path).absoluteDir().path()
        else:
            dir_path = ''

        dialog_filters = []
        for file_filter in self.__file_filters:
            extensions = ' '.join(file_filter.extensions)
            dialog_filters.append(f'{file_filter.title} ({extensions})')

        if len(dialog_filters) == 0:
            dialog_filters.append('All files (*)')

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select file', dir_path, f'{";;".join(dialog_filters)}')
        if file_path:
            self.line_edit.setText(file_path)
