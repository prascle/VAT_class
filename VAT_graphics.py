
import sys
import os

from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from astropy.visualization import astropy_mpl_style
from astropy.io import fits
from astropy.wcs import WCS

import logging

class VATgraphics(QWidget):
    def __init__(self, parent=None):
        '''
        We plot on a figure
        The Canvas Widget displays the `figure`
        We add a navigation widget
        '''
        logging.debug("VATgraphics __init__")

        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        matplotlib.style.use(astropy_mpl_style)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plotImage(self, imageFile, title=None):
        '''
        plot a .fits image
        projection is extracted from the image header
        '''
        logging.debug("VATgraphics plot")
        if title is None:
            title = os.path.basename(imageFile)
        self.figure.clear()
        self.figure.suptitle(title)
        data = fits.getdata(imageFile, ext=0)
        header = fits.getheader(imageFile)
        wcs = WCS(header)
        self.ax = self.figure.add_subplot(projection=wcs)
        imgplot = self.ax.imshow(data)
        self.canvas.draw()

