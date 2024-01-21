
import sys
import os

from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
from astropy.io import fits

import logging

class VATgraphics(QWidget):
    def __init__(self, parent=None):
        '''
        We plot on a figure
        The Canvas Widget displays the `figure`
        We add a navigation widget and a subplot
        '''
        logging.debug("VATgraphics __init__")

        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot()
        self.ax.set_title('Axes', loc='left', fontstyle='oblique', fontsize='medium')

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plotImage(self, imageFile, title=None):
        ''' plot an image '''
        logging.debug("VATgraphics plot")
        if title is None:
            title = os.path.basename(imageFile)
        self.figure.suptitle(title)
        data = fits.getdata(imageFile, ext=0)
        imgplot = self.ax.imshow(data)
        self.canvas.draw()

