import logging

import numpy as np

from astroquery.simbad import Simbad
from astroquery.skyview import SkyView

from astropy.coordinates import SkyCoord
from astropy import units as u

class VAT_interface:
    """
    interface d'acces VAT_Class, AstroQuery
    """

    def __init__(self):
        logging.info("init VAT_interface")

    def checkObjName(self, objName):
        """
        Verifier si le nom de l'objet est connu
        """
        logging.info("checkObjName")
        catalogues_supportes = ['NGC', 'M', 'IC']
        catalogue = None
        for c in catalogues_supportes:
            if objName.startswith(c):
                catalogue = c
                break
        if catalogue is None:
            logging.warning("Catalogue non supporté. Veuillez utiliser NGC, M ou IC.")
            return False
        result = Simbad.query_object(objName)
        if result is None:
            logging.warning("object unknown in Simbad")
            return False
        return True

    def generateOverview(self, objName, fovDegree, nbPixels):
        """
        retrouve une image de l'objet
        """
        logging.info("generateOverview")
        hdu = None
        res = SkyView.get_images(objName, survey=['DSS'], pixels=np.int64(np.round(nbPixels/2.)), radius=fovDegree*u.deg)
        if len(res) > 0:
            hdu = res[0][0]
        else:
            logging.warning("Overview is not found!")
        return hdu
