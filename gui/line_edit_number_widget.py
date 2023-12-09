from enum import Enum
from typing import Optional
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QLineEdit, QWidget


class LineEditNumberWidget(QLineEdit):
    class NumberType(Enum):
        UNSIGNED_FLOAT = 1
        UNSIGNED_INT = 2

    def __init__(self, number_type: NumberType, parent: Optional[QWidget] = None):
        super(LineEditNumberWidget, self).__init__(parent)

        self.setText('0')

        pattern = None
        editing_finished_callback = None
        if number_type == LineEditNumberWidget.NumberType.UNSIGNED_FLOAT:
            pattern = r'^\d*\.?\d*$'
            editing_finished_callback = self.__editing_finished_unsigned
        elif number_type == LineEditNumberWidget.NumberType.UNSIGNED_INT:
            pattern = r'^\d*$'
            editing_finished_callback = self.__editing_finished_unsigned

        if pattern is not None:
            regex = QRegularExpression(pattern)
            validator = QRegularExpressionValidator(regex)
            self.setValidator(validator)
        if editing_finished_callback is not None:
            self.editingFinished.connect(editing_finished_callback)

    def __editing_finished_unsigned(self):
        text: str = self.sender().text()
        text = text.lstrip('0')
        if '.' in text:
            text = text.rstrip('0')
            if text.startswith('.'):
                text = '0' + text
            if text.endswith('.'):
                text += '0'
        elif text == '':
            text = '0'

        if self.sender().text() != text:
            self.sender().setText(text)
