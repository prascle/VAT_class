#!/usr/bin/env python

import sys
import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore

from ui_mainwindow import Ui_MainWindow

import logging
import json

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

        self.actionSave_Specs.triggered.connect(self.dumpTargetSpecs)
        self.actionLoad_Specs.triggered.connect(self.loadTargetSpecs)
        self.actionLoad_fits.triggered.connect(self.overviewExistingImageFile)

        self.le_target.textChanged.connect(self.le_target_textChanged)
        self.dsb_visionField.valueChanged.connect(self.dsb_visionField_valueChanged)
        self.dsb_percentCoverage.valueChanged.connect(self.resetPreviewTiles)
        self.dsb_resolution.valueChanged.connect(self.resetPreviewTiles)
        self.sb_nbPixels.valueChanged.connect(self.resetPreviewTiles)

        self.cb_surveyChannel1.currentTextChanged.connect(self.resetImport)
        self.cb_surveyChannel2.currentTextChanged.connect(self.resetImport)
        self.cb_surveyChannel3.currentTextChanged.connect(self.resetImport)
        self.cb_surveyChannel4.currentTextChanged.connect(self.resetImport)

        listSurveys = ['none', 'DSS', 'DSS1 Blue', 'DSS2 Blue', 'DSS1 Red', 'DSS2 Red', 'DSS2 IR']
        self.cb_surveyChannel1.insertItems(0, listSurveys)
        self.cb_surveyChannel2.insertItems(0, listSurveys)
        self.cb_surveyChannel3.insertItems(0, listSurveys)
        self.cb_surveyChannel4.insertItems(0, listSurveys)
        self.cb_surveyChannel1.setEditable(True)
        self.cb_surveyChannel2.setEditable(True)
        self.cb_surveyChannel3.setEditable(True)
        self.cb_surveyChannel4.setEditable(True)
        self.cb_surveyChannel1.setCurrentText('DSS')
        self.cb_surveyChannel2.setCurrentText('DSS2 Blue')
        self.cb_surveyChannel3.setCurrentText('DSS2 Red')
        self.cb_surveyChannel4.setCurrentText('DSS2 IR')
        self.target = {}
        self.targetSpecsFile = ""
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

    def resetImport(self):
        self.pb_importFits.setEnabled(False)

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
        self.tbw.setTabEnabled(2, False)
        self.resetImport()
        self.graphics.resetOverviewTiles()

    def pb_getData_clicked(self):
        logging.info("pb_getData_clicked")
        isOk = self.vati.checkObjName(self.le_target.text())
        self.pb_generateOverview.setEnabled(isOk)

    def openExistingImageFile(self):
        logging.info("openExistingImageFile")
        res = QFileDialog.getOpenFileName(self,
            "Open Image", "..",  "Fits Image Files (*.fit *.fits)");
        imageFile = res[0]
        logging.info("imageFile: %s"%imageFile)
        return imageFile

    def overviewExistingImageFile(self):
        imageFile  = self.openExistingImageFile()
        logging.info("imageFile: %s"%imageFile)
        if len(imageFile) > 0:
            self.graphics.plotImage(imageFile)


    def pb_generateOverview_clicked(self):
        logging.info("pb_generateOverview_clicked")
        previewOK = False
        hdu = self.vati.generateOverview(self.le_target.text(),
                                         self.dsb_visionField.value(),
                                         1000)
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
        res = self.dumpTargetSpecs()
        if res:
            self.pb_importFits.setEnabled(True)

    def pb_importFits_clicked(self):
        logging.info("pb_importFits_clicked")
        jsonSpecs = self.jsonDump()
        self.vati.importFits(jsonSpecs, self.tileCoordinatesCenters, self.tileFov)

    def jsonDump(self):
        logging.info("jsonDump")
        self.target["le_target"] = self.le_target.text()
        self.target["dsb_visionField"] = self.dsb_visionField.value()
        self.target["sb_nbPixels"] = self.sb_nbPixels.value()
        self.target["dsb_resolution"] = self.dsb_resolution.value()
        self.target["dsb_percentCoverage"] = self.dsb_percentCoverage.value()
        self.target["cb_surveyChannel1"] = self.cb_surveyChannel1.currentText()
        self.target["cb_surveyChannel2"] = self.cb_surveyChannel2.currentText()
        self.target["cb_surveyChannel3"] = self.cb_surveyChannel3.currentText()
        self.target["cb_surveyChannel4"] = self.cb_surveyChannel4.currentText()
        self.target["targetSpecsFile"] = self.targetSpecsFile
        val = json.dumps(self.target, sort_keys=True, indent=4)
        print(val)
        return val


    def dumpTargetSpecs(self):
        logging.info("dumpTargetSpecs")
        directory = '..'
        target = self.le_target.text()
        if len(self.targetSpecsFile):
            directory = os.path.dirname(self.targetSpecsFile)
        dialog = QFileDialog(self, directory=directory)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("json files (*.jsn *.json)")
        dialog.setDefaultSuffix("json")
        dialog.selectFile( target + ".json")
        dialog.setLabelText(QFileDialog.Accept, 'Save')
        if (dialog.exec()):
            fileNames = dialog.selectedFiles()
            fileName = fileNames[0]
            self.targetSpecsFile = fileName
            val = self.jsonDump()
            print(fileName)
            with open(fileName, 'w', encoding="utf-8") as f:
                f.write(val)
            return True
        return False

    def loadTargetSpecs(self):
        logging.info("loadTargetSpecs")
        res = QFileDialog.getOpenFileName(self,
            "Open target specifications", "..",  "json files (*.jsn *.json)");
        fileName = res[0]
        print("filename", fileName)
        if len(fileName):
            resu = ""
            with open(fileName, encoding="utf-8") as f:
                resu = f.read()
            val = json.loads(resu)
            print(val)
            self.le_target.setText(val["le_target"])
            self.dsb_visionField.setValue(val["dsb_visionField"])
            self.sb_nbPixels.setValue(val["sb_nbPixels"])
            self.dsb_resolution.setValue(val["dsb_resolution"])
            self.dsb_percentCoverage.setValue(val["dsb_percentCoverage"])
            self.cb_surveyChannel1.setCurrentText(val["cb_surveyChannel1"])
            self.cb_surveyChannel2.setCurrentText(val["cb_surveyChannel2"])
            self.cb_surveyChannel3.setCurrentText(val["cb_surveyChannel3"])
            self.cb_surveyChannel4.setCurrentText(val["cb_surveyChannel4"])
            self.targetSpecsFile = val["targetSpecsFile"]

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VATGui()
    window.show()

    sys.exit(app.exec_())
