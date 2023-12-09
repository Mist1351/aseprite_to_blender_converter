import os
import argparse
from typing import Optional
from PyQt5.QtWidgets import QMainWindow, QPushButton, QCheckBox, QWidget, \
    QGridLayout, QLabel, QHBoxLayout, QSizePolicy, QMessageBox, QApplication, QComboBox
from PyQt5.QtCore import Qt, QFileInfo
from core.common import INPUT_FILE_EXTENSIONS, call_aseprite_script, call_blender_script, get_files, VERSION
from core.config import load_config, save_config, Size, PIVOT_VALUES
from gui.file_path_widget import FilePathWidget
from gui.line_edit_number_widget import LineEditNumberWidget
from gui.settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None, args: Optional[argparse.Namespace] = None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('Aseprite to blender converter')
        self.setAcceptDrops(True)

        self.setCentralWidget(QWidget())
        grid = QGridLayout(self.centralWidget())

        self.__input_file_widget = FilePathWidget(
            select_type=FilePathWidget.SelectType.FILE
        )
        self.__input_file_widget.add_file_filter('Aseprite files', [f'*{ext}' for ext in INPUT_FILE_EXTENSIONS])
        grid.addWidget(QLabel('Input file:'), 0, 0)
        grid.addWidget(self.__input_file_widget, 0, 1)

        self.__output_dir_widget = FilePathWidget(
            select_type=FilePathWidget.SelectType.DIRECTORY
        )
        grid.addWidget(QLabel('Output dir:'), 1, 0)
        grid.addWidget(self.__output_dir_widget, 1, 1)

        self.__tile_size_check_box = QCheckBox('Tile size:')
        self.__tile_size_check_box.toggled.connect(self.__switch_tile_size)
        grid.addWidget(self.__tile_size_check_box, 2, 0)

        self.__tile_width_line_edit = LineEditNumberWidget(LineEditNumberWidget.NumberType.UNSIGNED_INT)
        self.__tile_width_line_edit.setMaximumWidth(50)
        self.__tile_height_line_edit = LineEditNumberWidget(LineEditNumberWidget.NumberType.UNSIGNED_INT)
        self.__tile_height_line_edit.setMaximumWidth(50)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setAlignment(Qt.AlignLeft)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self.__tile_width_line_edit)
        delim = QLabel('x')
        delim.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        row_layout.addWidget(delim)
        row_layout.addWidget(self.__tile_height_line_edit)
        grid.addWidget(row_widget, 2, 1)
        self.__switch_tile_size(self.__tile_size_check_box.isChecked())

        self.__scale_line_edit = LineEditNumberWidget(LineEditNumberWidget.NumberType.UNSIGNED_FLOAT)
        grid.addWidget(QLabel('Scale factor:'), 3, 0)
        grid.addWidget(self.__scale_line_edit, 3, 1)

        self.__extrude_line_edit = LineEditNumberWidget(LineEditNumberWidget.NumberType.UNSIGNED_FLOAT)
        grid.addWidget(QLabel('Extrude factor:'), 4, 0)
        grid.addWidget(self.__extrude_line_edit, 4, 1)

        self.__pivot_combobox = QComboBox()
        for pivot in PIVOT_VALUES:
            self.__pivot_combobox.addItem(pivot)
        grid.addWidget(QLabel('Pivot:'), 5, 0)
        grid.addWidget(self.__pivot_combobox, 5, 1)

        self.__svg_only_check_box = QCheckBox('Generate SVG only without FBX')
        grid.addWidget(self.__svg_only_check_box, 6, 0, 1, 2)

        self.__convert_button = QPushButton('Convert')
        self.__convert_button.clicked.connect(self.__process_convert)
        grid.addWidget(self.__convert_button, 7, 0, 1, 2)

        self.__settings_button = QPushButton('Settings')
        self.__settings_button.clicked.connect(self.__show_settings)
        grid.addWidget(self.__settings_button, 8, 0, 1, 2, Qt.AlignRight | Qt.AlignBottom)

        grid.setRowStretch(8, 1)

        version_label = QLabel(f'Version: {VERSION}')
        font = version_label.font()
        font.setPointSize(8)
        version_label.setFont(font)
        grid.addWidget(version_label, 9, 0, 1, 2, Qt.AlignLeft)

        self.__fill_ui(args)

    def __switch_tile_size(self, checked: bool):
        self.__tile_width_line_edit.setDisabled(not checked)
        self.__tile_height_line_edit.setDisabled(not checked)

    def __run_aseprite(self):
        kwargs = {
            'file': self.__input_file_widget.line_edit.text(),
            'output': self.__output_dir_widget.line_edit.text()
        }
        if self.__tile_size_check_box.isChecked():
            kwargs['width'] = self.__tile_width_line_edit.text()
            kwargs['height'] = self.__tile_height_line_edit.text()
        call_aseprite_script('scripts/aseprite/convert_to_svg.lua', **kwargs)

    def __run_blender(self):
        kwargs = {
            '-o': self.__output_dir_widget.line_edit.text(),
            '--scale': self.__scale_line_edit.text(),
            '--extrude': self.__extrude_line_edit.text(),
            '--pivot': self.__pivot_combobox.currentText(),
        }
        filename = os.path.basename(self.__input_file_widget.line_edit.text())
        files = get_files(self.__output_dir_widget.line_edit.text(), f'{filename}_tile_\\d+_\\d+\\.svg$')
        for file in files:
            call_blender_script('scripts/blender/convert_svg_to_fbx.py',
                                **kwargs, **{'-i': file})

    def __process_convert(self):
        try:
            self.__convert_button.setEnabled(False)
            QApplication.processEvents()
            self.__run_aseprite()
            if not self.__svg_only_check_box.isChecked():
                self.__run_blender()
        except Exception as e:
            self.__show_alert('Exception occurred', f'{e}')
        finally:
            self.__convert_button.setEnabled(True)

    @staticmethod
    def __show_settings():
        SettingsWindow().exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and MainWindow.__validate_drag_and_drop(event.mimeData().urls()[0].toLocalFile()):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        if QFileInfo(file_path).isDir():
            self.__output_dir_widget.line_edit.setText(file_path)
        else:
            self.__input_file_widget.line_edit.setText(file_path)
        event.accept()

    def closeEvent(self, event):
        self.setFocus()
        config = load_config()
        if self.__tile_size_check_box.isChecked():
            config.size = Size(int(self.__tile_width_line_edit.text()),
                               int(self.__tile_height_line_edit.text()))
        else:
            config.size = None
        config.scale = self.__scale_line_edit.text()
        config.extrude = self.__extrude_line_edit.text()
        config.input = self.__input_file_widget.line_edit.text()
        config.output = self.__output_dir_widget.line_edit.text()
        config.svg_only = self.__svg_only_check_box.isChecked()
        config.pivot = self.__pivot_combobox.currentText()
        save_config(config)
        event.accept()

    @staticmethod
    def __validate_drag_and_drop(file_path: str) -> bool:
        return any(file_path.endswith(ext) for ext in INPUT_FILE_EXTENSIONS) or QFileInfo(file_path).isDir()

    def __fill_ui(self, args: argparse.Namespace):
        config = load_config()
        if args.input is not None:
            if os.path.isfile(args.input):
                self.__input_file_widget.line_edit.setText(args.input)
            else:
                self.__show_alert('Input file not exists', f'"{args.input}" not exists!')
        elif config.input is not None:
            self.__input_file_widget.line_edit.setText(config.input)

        if args.output is not None:
            if os.path.isdir(args.output):
                self.__output_dir_widget.line_edit.setText(args.output)
            else:
                self.__show_alert('Output dir not exists', f'"{args.output}" not exists!')
        elif config.output is not None:
            self.__output_dir_widget.line_edit.setText(config.output)

        if args.size is not None:
            self.__tile_size_check_box.setChecked(True)
            [tile_width, tile_height] = args.size.split('x')
            self.__tile_width_line_edit.setText(tile_width)
            self.__tile_height_line_edit.setText(tile_height)
        elif config.size is not None:
            self.__tile_size_check_box.setChecked(True)
            self.__tile_width_line_edit.setText(str(config.size.width))
            self.__tile_height_line_edit.setText(str(config.size.height))
        else:
            self.__tile_size_check_box.setChecked(False)
            self.__tile_width_line_edit.setText('32')
            self.__tile_height_line_edit.setText('32')

        if args.scale is not None:
            self.__scale_line_edit.setText(args.scale)
        else:
            self.__scale_line_edit.setText(config.scale or '1')

        if args.extrude is not None:
            self.__extrude_line_edit.setText(args.extrude)
        else:
            self.__extrude_line_edit.setText(config.extrude or '1')

        pivot = args.pivot or config.pivot
        if pivot is not None:
            self.__pivot_combobox.setCurrentText(pivot)

        self.__svg_only_check_box.setChecked(config.svg_only)

    @staticmethod
    def __show_alert(title: str, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec_()
