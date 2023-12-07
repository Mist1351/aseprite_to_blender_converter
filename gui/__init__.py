import sys
import argparse
from PyQt5.QtWidgets import QApplication

from core.common import parse_args
from gui.main_window import MainWindow


def run_gui(args: argparse.Namespace):
    app = QApplication([])
    win = MainWindow(args=args)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    args, parser = parse_args()
    run_gui(args)
