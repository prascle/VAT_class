
import sys
import os

from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import astropy_mpl_style
from astropy.visualization.wcsaxes import Quadrangle
from astropy import units as u
from astropy.coordinates import SkyCoord

import logging

class VATgraphics(QWidget):
    def __init__(self, parent=None):
        '''
        We plot on a figure
        The Canvas Widget displays the `figure`
        We add a navigation widget
        '''
        logging.info("VATgraphics.__init__")

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
        self.reset()

    def reset(self):
        logging.info("VATgraphics.reset")
        self.overviewTiles = False
        self.hdu = None
        self.title = ""
        self.figure.clear()
        self.canvas.draw()

    def resetOverviewTiles(self):
        if self.overviewTiles:
            self.plotOverviewTiles([], 0, 0)

    def plotImage(self, imageFile, title=None):
        '''
        plot a .fits image
        projection is extracted from the image header
        '''
        logging.info("VATgraphics plot fits image")
        if title is None:
            title = os.path.basename(imageFile)
        self.figure.clear()
        self.figure.suptitle(title)
        data = fits.getdata(imageFile, ext=0)
        header = fits.getheader(imageFile)
        wcs = WCS(header)
        self.ax = self.figure.add_subplot(projection=wcs)
        imgplot = self.ax.imshow(data, cmap='binary_r', origin='lower')
        self.canvas.draw()


    def plotHDU(self, hdu=None, title=None):
        '''
        plot an HDU
        if hdu is None, retrieve stored HDU, otherwise store HDU
        projection is extracted from the image header
        '''
        logging.info("VATgraphics plot HDU")
        if hdu is None:
            hdu = self.hdu
            title = self.title
        else:
            self.hdu = hdu
            if title is None:
                title = "no name"
            self.title = title
        self.figure.clear()
        if hdu is not None:
            self.figure.suptitle(title)
            data = hdu.data
            header = hdu.header
            wcs = WCS(header)
            self.ax = self.figure.add_subplot(projection=wcs)
            imgplot = self.ax.imshow(data, cmap='binary_r', origin='lower')
        self.canvas.draw()

    def plotOverviewTiles(self, tileCoordinatesCenters, nbTiles, tileFov):
        """
        """
        logging.info("VATgraphics plotOverviewTiles")
        self.plotHDU()
        self.overviewTiles = not self.overviewTiles
        if self.overviewTiles:
            self.ax.grid(color='black',ls='solid')
            colors = ["red", "green", "blue", "yellow"] # --- pour que tous les voisins aient des couleurs différentes
            for i in range(len(tileCoordinatesCenters)):
                c1 = SkyCoord("0h0m0s", tileCoordinatesCenters[i].dec.degree*u.deg)
                c2 = SkyCoord("0h4m0s", tileCoordinatesCenters[i].dec.degree*u.deg)
                sep = c1.separation(c2).arcmin/60.
                decal = 2*((i // nbTiles)%2) # --- pour decaler de 2 couleurs d'une rangée à l'autre
                r = Quadrangle( tuple([tileCoordinatesCenters[i].ra.degree -0.5/sep*tileFov,
                                       tileCoordinatesCenters[i].dec.degree -0.5*tileFov])*u.deg,
                                (1./sep)*tileFov*u.deg,
                                tileFov*u.deg,
                                edgecolor=colors[(i%nbTiles+decal)%len(colors)],
                                facecolor='none',
                                transform=self.ax.get_transform('world'))
                self.ax.add_patch(r)
            self.canvas.draw()
