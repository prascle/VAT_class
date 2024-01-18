#!/usr/bin/env python

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

from ui_mainwindow import Ui_MainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
from astropy.io import fits

import random

import logging

import VAT_interface

class VATgraphics(QWidget):
    def __init__(self, parent=None):
        '''
        We plot on a figure
        The Canvas Widget displays the `figure`
        We add a navigation widget
        '''
        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self):
        ''' plot an image '''
        self.figure.suptitle('A nice Matplotlib Figure')
        ax = self.figure.add_subplot()
        ax.set_title('Axes', loc='left', fontstyle='oblique', fontsize='medium')
        imageFile = '../M31/Images/M31_DSS_tile_6.fits'
        data = fits.getdata(imageFile, ext=0)
        imgplot = ax.imshow(data)
        self.canvas.draw()


class VATGui(QMainWindow, Ui_MainWindow):
    """
    Python Qt GUI for VAT_class
    """

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        logging.basicConfig(level=logging.INFO)
        self.vati = VAT_interface.VAT_interface()

        self.graphLayout = QVBoxLayout(self.frame)
        self.graphics = VATgraphics()
        self.graphLayout.addWidget(self.graphics)

        self.tbw.setTabText(0, "Target overview")
        self.tbw.setTabText(1, "Fits contents specifications")
        self.tbw.setTabText(2, "Download data")
        for i in range(self.tbw.count()):
            self.tbw.setTabEnabled(i, False)
        self.tbw.setTabEnabled(0, True)
        self.tbw.setCurrentIndex(0)
        self.pb_generateOverview.setEnabled(False)
        self.le_target.setText("M31")
        self.pb_getData.clicked.connect(self.pb_getData_clicked)
        self.pb_generateOverview.clicked.connect(self.pb_generateOverview_clicked)
        self.le_target.textChanged.connect(self.le_target_textChanged)

    def le_target_textChanged(self):
        logging.debug("le_target_textChanged")
        self.pb_generateOverview.setEnabled(False)

    def pb_getData_clicked(self):
        logging.debug("pb_getData_clicked")
        isOk = self.vati.checkObjName(self.le_target.text())
        self.pb_generateOverview.setEnabled(isOk)

    def pb_generateOverview_clicked(self):
        logging.debug("pb_generateOverview_clicked")
        isOk = self.vati.generateOverview(self.le_target.text())
        self.graphics.plot()




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VATGui()
    window.show()

    sys.exit(app.exec_())
