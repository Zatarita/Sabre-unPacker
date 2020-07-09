# This Python file uses the following encoding: utf-8
import sys
from os import system
from PyQt5.QtWidgets import QApplication

from UI.logic.SuP import SuP


if __name__ == "__main__":
    system("mkdir TMP")
    app = QApplication([])
    window = SuP()

    window.show()
    sys.exit(app.exec_())
