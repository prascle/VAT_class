import logging

import numpy as np

from astroquery.simbad import Simbad
from astroquery.skyview import SkyView

from astropy.coordinates import SkyCoord
from astropy.coordinates import position_angle
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

    def calculateTilesNumber(self, fovDegree, cover, resolution, nbPixels):
        """
        number of tiles along an axis
        """
        tileFov = resolution/3600. * nbPixels
        tilesNumber = np.int64(np.ceil(fovDegree / tileFov - cover/100.) * 1./(1. - cover/100.))
        logging.info("calculateTilesNumber: %d, %f"%(tilesNumber, tileFov))
        return tilesNumber, tileFov

    def tilesCoordinates(self, objName, tilesNumber, tileFov, cover):
        """
        """
        logging.info("tilesCoordinates")
        center_coords = SkyCoord.from_name(objName)
        offset_value = (tileFov*(1-cover/100.) )* u.deg
        # Direction de référence pour le décalage suivant les
        # déclinaisons positives, on a pris pi/4 arbitrairement. Il fallait logiquement une valeur entre 0. et pi/2.
        # Le même raisonnement est appliquée pour chaque direction de décalage. Seul le signe change et les coordonnées du 2nd
        # point, on inverse simplement longitude et latitude.
        position_angle_DECplus  = position_angle(0., 0.,       0., np.pi/4.)
        position_angle_DECmoins = position_angle(0., 0.,       0.,-np.pi/4.)
        position_angle_RAplus   = position_angle(0., 0., np.pi/4.,       0.)
        position_angle_RAmoins  = position_angle(0., 0.,-np.pi/4.,       0.)
        # Translation du point de départ à partir des corrdonnées du centre de l'objet ciblé
        coord_starting_point1 =         center_coords.directional_offset_by(position_angle_RAmoins,  offset_value/2.*float(tilesNumber))
        coord_starting_point  = coord_starting_point1.directional_offset_by(position_angle_DECmoins, offset_value/2.*float(tilesNumber))
        # On applique ensuite le décalage pour déterminer l'emplacement de chaque tuile à partir de cette nouvelle origine
        tile_coordinates_center = []
        for i in range(tilesNumber):
            for j in range(tilesNumber):
                coord_tile_step1 = coord_starting_point.directional_offset_by(position_angle_RAplus,  offset_value*float(i))
                coord_tile_final =     coord_tile_step1.directional_offset_by(position_angle_DECplus, offset_value*float(j))
                tile_coordinates_center.append(coord_tile_final)
                logging.info("Coordinates of tile (%s, %s): %s"%(i+1,j+1, coord_tile_final))
        return tile_coordinates_center

