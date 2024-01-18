#!/usr/bin/env python

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, QIODevice
from ui_mainwindow import Ui_MainWindow

class VATGui(QMainWindow, Ui_MainWindow):
    """
    Python Qt GUI for VAT_class
    """

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.tbw.setTabText(0, "Target overview")
        self.tbw.setTabText(1, "Fits contents specifications")
        self.tbw.setTabText(2, "Download data")
        for i in range(self.tbw.count()):
            self.tbw.setTabEnabled(i, False)
        self.tbw.setTabEnabled(0, True)
        self.tbw.setCurrentIndex(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VATGui()
    window.show()

    sys.exit(app.exec_())
