import os
import argparse
from typing import Union, Callable
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QCheckBox, QWidget, \
    QGridLayout, QLabel, QLineEdit, QHBoxLayout, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QFileInfo, QRegularExpression
from core.common import INPUT_FILE_EXTENSIONS, call_aseprite_script, call_blender_script, get_files
from core.config import load_config, save_config
from gui.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None, args: argparse.Namespace = None):
        super(MainWindow, self).__init__(parent)
        self.settings_button: Union[QPushButton, None] = None
        self.svg_only_check_box: Union[QCheckBox, None] = None
        self.scale_line_edit: Union[QLineEdit, None] = None
        self.extrude_line_edit: Union[QLineEdit, None] = None
        self.tile_size_check_box: Union[QCheckBox, None] = None
        self.tile_height_line_edit: Union[QLineEdit, None] = None
        self.tile_width_line_edit: Union[QLineEdit, None] = None
        self.output_button: Union[QPushButton, None] = None
        self.output_line_edit: Union[QLineEdit, None] = None
        self.input_button: Union[QPushButton, None] = None
        self.input_line_edit: Union[QLineEdit, None] = None
        self.convert_button = None
        self._init_ui()
        self._fill_ui(args)

    @staticmethod
    def _validate_drag_and_drop(file_path: str) -> bool:
        return any(file_path.endswith(ext) for ext in INPUT_FILE_EXTENSIONS) or QFileInfo(file_path).isDir()

    def _check_tile_size(self, checked):
        self.tile_width_line_edit.setDisabled(not checked)
        self.tile_height_line_edit.setDisabled(not checked)

    def _check_unsigned_number(self):
        text: str = self.sender().text()
        text = text.lstrip('0')
        if text == '':
            text = '1'
        if '.' in text:
            text = text.rstrip('0')
            if text.startswith('.'):
                text = '0' + text
            if text.endswith('.'):
                text += '0'
        if self.sender().text() != text:
            self.sender().setText(text)

    def _init_ui(self):
        self.setWindowTitle('Aseprite to blender converter')
        self.setAcceptDrops(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid = QGridLayout()
        central_widget.setLayout(grid)

        grid.addWidget(QLabel('Input file path:'), 0, 0, 1, 2)
        self.input_line_edit = QLineEdit()
        self.input_line_edit.setReadOnly(True)
        grid.addWidget(self.input_line_edit, 0, 2)
        self.input_button = QPushButton('Select')
        self.input_button.clicked.connect(self.select_input_file)
        grid.addWidget(self.input_button, 0, 3)

        grid.addWidget(QLabel('Output directory path:'), 1, 0, 1, 2)
        self.output_line_edit = QLineEdit()
        self.output_line_edit.setReadOnly(True)
        grid.addWidget(self.output_line_edit, 1, 2)
        self.output_button = QPushButton('Select')
        self.output_button.clicked.connect(self.select_output_directory)
        grid.addWidget(self.output_button, 1, 3)

        regex_unsigned_int = QRegularExpression(r'^\d*$')
        validator_unsigned_int = QRegularExpressionValidator(regex_unsigned_int)
        regex_unsigned_float = QRegularExpression(r'^\d*\.?\d*$')
        validator_unsigned_float = QRegularExpressionValidator(regex_unsigned_float)

        grid.addWidget(QLabel('Tile size:'), 2, 0)
        self.tile_size_check_box = QCheckBox()
        self.tile_size_check_box.clicked.connect(self._check_tile_size)
        grid.addWidget(self.tile_size_check_box, 2, 1)

        tile_size_layout = QHBoxLayout()
        grid.addLayout(tile_size_layout, 2, 2, 1, 2)
        self.tile_width_line_edit = self._create_line_edit(width=50, validator=validator_unsigned_int,
                                                           check_method=self._check_unsigned_number)
        tile_size_layout.addWidget(self.tile_width_line_edit)
        label = QLabel('x')
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label.setMaximumWidth(label.sizeHint().width())
        tile_size_layout.addWidget(label)
        self.tile_height_line_edit = self._create_line_edit(width=50, validator=validator_unsigned_int,
                                                            check_method=self._check_unsigned_number)
        tile_size_layout.addWidget(self.tile_height_line_edit)
        tile_size_layout.setAlignment(Qt.AlignLeft)

        self.scale_line_edit = self._create_line_edit(width=None, validator=validator_unsigned_float,
                                                      check_method=self._check_unsigned_number)
        grid.addWidget(QLabel('Scale factor:'), 3, 0, 1, 2)
        grid.addWidget(self.scale_line_edit, 3, 2)

        self.extrude_line_edit = self._create_line_edit(width=None, validator=validator_unsigned_float,
                                                        check_method=self._check_unsigned_number)
        grid.addWidget(QLabel('Extrude factor:'), 4, 0, 1, 2)
        grid.addWidget(self.extrude_line_edit, 4, 2)

        self.svg_only_check_box = QCheckBox('Generate SVG only without FBX')
        grid.addWidget(self.svg_only_check_box, 5, 0, 1, 4)

        self.convert_button = QPushButton('Convert')
        self.convert_button.clicked.connect(self._process_convert)
        grid.addWidget(self.convert_button, 6, 0, 1, 4)

        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self._show_settings)
        grid.addWidget(self.settings_button, 7, 0, 1, 4, Qt.AlignRight)

    def _fill_ui(self, args: argparse.Namespace):
        config = load_config()
        if args.input is not None:
            if os.path.isfile(args.input):
                self.input_line_edit.setText(args.input)
            else:
                self._show_alert('Input file not exists', f'"{args.input}" not exists!')
        elif config.input is not None:
            self.input_line_edit.setText(config.input)

        if args.output is not None:
            if os.path.isdir(args.output):
                self.output_line_edit.setText(args.output)
            else:
                self._show_alert('Output dir not exists', f'"{args.output}" not exists!')
        elif config.output is not None:
            self.output_line_edit.setText(config.output)

        if args.size is not None:
            self.tile_size_check_box.setChecked(True)
            self._check_tile_size(True)
            [tile_width, tile_height] = args.size.split('x')
            self.tile_width_line_edit.setText(tile_width)
            self.tile_height_line_edit.setText(tile_height)
        elif config.size is not None:
            self.tile_size_check_box.setChecked(True)
            self._check_tile_size(True)
            [tile_width, tile_height] = config.size.split('x')
            self.tile_width_line_edit.setText(tile_width)
            self.tile_height_line_edit.setText(tile_height)
        else:
            self.tile_size_check_box.setChecked(False)
            self._check_tile_size(False)
            self.tile_width_line_edit.setText('32')
            self.tile_height_line_edit.setText('32')

        if args.scale is not None:
            self.scale_line_edit.setText(args.scale)
        else:
            self.scale_line_edit.setText(config.scale or '1')

        if args.extrude is not None:
            self.extrude_line_edit.setText(args.extrude)
        else:
            self.extrude_line_edit.setText(config.extrude or '1')

        self.svg_only_check_box.setChecked(config.svg_only)

    @staticmethod
    def _show_alert(title: str, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()

    @staticmethod
    def _create_line_edit(*,
                          width: Union[int, None], validator: QRegularExpressionValidator,
                          check_method: Callable[[], None]) -> QLineEdit:
        widget = QLineEdit()
        if width is not None:
            widget.setMaximumWidth(width)
        if validator is not None:
            widget.setValidator(validator)
        if check_method is not None:
            widget.editingFinished.connect(check_method)
        return widget

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and MainWindow._validate_drag_and_drop(event.mimeData().urls()[0].toLocalFile()):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        if QFileInfo(file_path).isDir():
            self.output_line_edit.setText(file_path)
        else:
            self.input_line_edit.setText(file_path)
        event.accept()

    def closeEvent(self, event):
        config = load_config()
        if self.tile_size_check_box.isChecked():
            config.size = self.tile_width_line_edit.text() + 'x' + self.tile_height_line_edit.text()
        else:
            config.size = None
        config.scale = self.scale_line_edit.text()
        config.extrude = self.extrude_line_edit.text()
        config.input = self.input_line_edit.text()
        config.output = self.output_line_edit.text()
        config.svg_only = self.svg_only_check_box.isChecked()
        save_config(config)
        event.accept()

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select input file', '',
                                                   f'Aseprite files ({" ".join(f"*{ext}" for ext in INPUT_FILE_EXTENSIONS)})')
        if file_path:
            self.input_line_edit.setText(file_path)

    def select_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select output directory', '')
        if dir_path:
            self.output_line_edit.setText(dir_path)

    @staticmethod
    def _show_settings():
        SettingsWindow().exec()

    def _run_aseprite(self):
        kwargs = {
            'file': self.input_line_edit.text(),
            'output': self.output_line_edit.text()
        }
        if self.tile_size_check_box.isChecked():
            kwargs['width'] = self.tile_width_line_edit.text()
            kwargs['height'] = self.tile_height_line_edit.text()
        call_aseprite_script('scripts/aseprite/convert_to_svg.lua', **kwargs)

    def _run_blender(self):
        kwargs = {
            '-o': self.output_line_edit.text(),
            '--scale': self.scale_line_edit.text(),
            '--extrude': self.extrude_line_edit.text(),
        }
        filename = os.path.basename(self.input_line_edit.text())
        files = get_files(self.output_line_edit.text(), f'{filename}_tile_\\d+_\\d+\\.svg$')
        for file in files:
            call_blender_script('scripts/blender/convert_svg_to_fbx.py',
                                **kwargs, **{'-i': file})

    def _process_convert(self):
        try:
            self._run_aseprite()
            if not self.svg_only_check_box.isChecked():
                self._run_blender()
        except Exception as e:
            self._show_alert('Exception occurred', f'{e}')
