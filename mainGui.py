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
        # set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). matplotlib is very verbose with DEBUG...
        logging.basicConfig(level=logging.INFO)
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
        self.dsb_visionField.valueChanged.connect(self.dsb_visionField_valueChanged)
        self.dsb_percentCoverage.valueChanged.connect(self.resetPreviewTiles)
        self.dsb_resolution.valueChanged.connect(self.resetPreviewTiles)
        self.sb_nbPixels.valueChanged.connect(self.resetPreviewTiles)
        self.reset()

    def reset(self):
        logging.info("reset")
        self.tileCoordinatesCenters = []
        self.nbTiles = 0
        self.tileFov = 0
        self.tileCoordinatesCenters = []
        self.tbw.setTabEnabled(1, False)
        self.tbw.setTabEnabled(2, False)
        self.pb_importFits.setEnabled(False)
        self.tbw.setCurrentIndex(0)
        self.graphics.reset()

    def le_target_textChanged(self):
        logging.info("le_target_textChanged")
        self.reset()
        self.pb_generateOverview.setEnabled(False)

    def dsb_visionField_valueChanged(self):
        logging.info("dsb_visionField_valueChanged")
        self.reset()

    def resetPreviewTiles(self):
        logging.info("resetPreviewTiles")
        self.nbTiles =0
        self.tileFov = 0
        self.graphics.resetOverviewTiles()

    def pb_getData_clicked(self):
        logging.info("pb_getData_clicked")
        isOk = self.vati.checkObjName(self.le_target.text())
        self.pb_generateOverview.setEnabled(isOk)

    def openExistingImageFile(self):
        logging.info("openExistingImageFile")
        res = QFileDialog.getOpenFileName(self,
            "Open Image", "../M31/Images",  "Fits Image Files (*.fit *.fits)");
        imageFile = res[0]
        logging.info("imageFile: %s"%imageFile)
        return imageFile

    def pb_generateOverview_clicked(self):
        logging.info("pb_generateOverview_clicked")
        previewOK = False
        hdu = self.vati.generateOverview(self.le_target.text(),
                                         self.dsb_visionField.value(),
                                         2000)
        if hdu is not None:
            self.graphics.plotHDU(hdu, self.le_target.text())
            previewOK = True
        else:
            # if generateOverview is not connected, search a local image
            imageFile = self.openExistingImageFile()
            logging.info("imageFile: %s"%imageFile)
            if len(imageFile) > 0:
                self.graphics.plotImage(imageFile)
                previewOK = True
        if previewOK:
            self.tbw.setTabEnabled(1, True)

    def pb_calculateTiles_clicked(self):
        logging.info("pb_calculateTiles_clicked")
        self.nbTiles, self.tileFov, cover = self.vati.calculateNbTiles(self.dsb_visionField.value(),
                                                                       self.dsb_percentCoverage.value(),
                                                                       self.dsb_resolution.value(),
                                                                       self.sb_nbPixels.value())
        self.tileCoordinatesCenters = self.vati.tilesCoordinates(self.le_target.text(),
                                                                 self.nbTiles,
                                                                 self.tileFov,
                                                                 self.dsb_percentCoverage.value())
        self.tbw.setTabEnabled(2, True)

    def pb_previewTiles_clicked(self):
        logging.info("pb_previewTiles_clicked")
        if self.nbTiles == 0:
            self.pb_calculateTiles.click()
        self.graphics.plotOverviewTiles(self.tileCoordinatesCenters,
                                        self.nbTiles,
                                        self.tileFov)

    def pb_selectFolder_clicked(self):
        logging.info("pb_selectFolder_clicked")
        dialog = QFileDialog(self, directory="..")
        dialog.setFileMode(QFileDialog.Directory)
        if (dialog.exec()):
            res = dialog.selectedFiles()
            self.folder = res[0]
            logging.info("folder: %s"%self.folder)
            self.pb_importFits.setEnabled(True)

    def pb_importFits_clicked(self):
        logging.info("pb_importFits_clicked")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VATGui()
    window.show()

    sys.exit(app.exec_())
