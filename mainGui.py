#!/usr/bin/env python

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

from ui_mainwindow import Ui_MainWindow

import logging

import VAT_interface
import VAT_graphics

class VATGui(QMainWindow, Ui_MainWindow):
    """
    Python Qt GUI for VAT_class
    """

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        logging.basicConfig(level=logging.DEBUG) #INFO
        self.vati = VAT_interface.VAT_interface()

        self.graphLayout = QVBoxLayout(self.frame)
        self.graphics = VAT_graphics.VATgraphics()
        self.graphLayout.addWidget(self.graphics)

        self.tbw.setTabText(0, "Target overview")
        self.tbw.setTabText(1, "Fits specifications")
        self.tbw.setTabText(2, "Download data")
        for i in range(self.tbw.count()):
            self.tbw.setTabEnabled(i, False)
        self.tbw.setTabEnabled(0, True)
        self.tbw.setCurrentIndex(0)
        self.pb_generateOverview.setEnabled(False)
        self.pb_importFits.setEnabled(False)
        self.le_target.setText("M31")
        self.pb_getData.clicked.connect(self.pb_getData_clicked)
        self.pb_generateOverview.clicked.connect(self.pb_generateOverview_clicked)
        self.pb_calculateTiles.clicked.connect(self.pb_calculateTiles_clicked)
        self.pb_previewTiles.clicked.connect(self.pb_previewTiles_clicked)
        self.pb_selectFolder.clicked.connect(self.pb_selectFolder_clicked)
        self.pb_importFits.clicked.connect(self.pb_importFits_clicked)
        self.le_target.textChanged.connect(self.le_target_textChanged)

    def le_target_textChanged(self):
        logging.debug("le_target_textChanged")
        self.pb_generateOverview.setEnabled(False)
        self.tbw.setTabEnabled(1, False)
        self.tbw.setTabEnabled(2, False)
        self.pb_importFits.setEnabled(False)
        self.tbw.setCurrentIndex(0)

    def pb_getData_clicked(self):
        logging.debug("pb_getData_clicked")
        isOk = self.vati.checkObjName(self.le_target.text())
        self.pb_generateOverview.setEnabled(isOk)

    def pb_generateOverview_clicked(self):
        logging.debug("pb_generateOverview_clicked")
        isOk = self.vati.generateOverview(self.le_target.text())
        res = QFileDialog.getOpenFileName(self,
            "Open Image", "../M31/Images",  "Fits Image Files (*.fits)");
        imageFile = res[0]
        logging.debug("imageFile: %s"%imageFile)
        if len(imageFile) > 0:
            self.graphics.plotImage(imageFile)
            self.tbw.setTabEnabled(1, True)

    def pb_calculateTiles_clicked(self):
        logging.debug("pb_calculateTiles_clicked")
        self.tbw.setTabEnabled(2, True)

    def pb_previewTiles_clicked(self):
        logging.debug("pb_previewTiles_clicked")

    def pb_selectFolder_clicked(self):
        logging.debug("pb_selectFolder_clicked")
        dialog = QFileDialog(self, directory="..")
        dialog.setFileMode(QFileDialog.Directory)
        if (dialog.exec()):
            res = dialog.selectedFiles()
            self.folder = res[0]
            logging.debug("folder: %s"%self.folder)
            self.pb_importFits.setEnabled(True)

    def pb_importFits_clicked(self):
        logging.debug("pb_importFits_clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VATGui()
    window.show()

    sys.exit(app.exec_())
