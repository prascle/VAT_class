import os
import logging
import json
import shutil

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
        res = SkyView.get_images(objName, survey=['DSS'], pixels=nbPixels, radius=fovDegree*u.deg)
        if len(res) > 0:
            hdu = res[0][0]
        else:
            logging.warning("Overview is not found!")
        return hdu

    def calculateNbTiles(self, fovDegree, cover, resolution, nbPixels):
        """
        number of tiles along an axis
        """
        tileFov = resolution/3600. * nbPixels
        nbTiles = np.int64(np.ceil((fovDegree / tileFov - cover/100.) * 1./(1. - cover/100.)))
        cover = 100*(nbTiles*tileFov - fovDegree)/(tileFov*(nbTiles -1))
        logging.info("calculateNbTiles: %d  tileFov: %f cover: %f"%(nbTiles, tileFov, cover))
        return nbTiles, tileFov, cover

    def tilesCoordinates(self, objName, nbTiles, tileFov, cover):
        """
        generer la liste des coordonnées des centres des tuiles
        """
        logging.info("tilesCoordinates")
        center_coords = SkyCoord.from_name(objName)
        offset_value =  tileFov*(1. - cover/100.)*u.deg
        # --- Direction de référence pour le décalage suivant les déclinaisons positives.
        #     on a pris pi/4 (radian) arbitrairement. Il fallait logiquement une valeur entre 0. et pi/2.
        #     angle = position_angle(lon1, lat1, lon2, lat2) : Position Angle (East of North) between two points on a sphere.
        #     https://docs.astropy.org/en/stable/api/astropy.coordinates.position_angle.html#astropy.coordinates.position_angle
        alpha = np.pi/4.
        position_angle_DECplus  = position_angle(0., 0.,    0., alpha)
        position_angle_DECmoins = position_angle(0., 0.,    0.,-alpha)
        position_angle_RAplus   = position_angle(0., 0., alpha,    0.)
        position_angle_RAmoins  = position_angle(0., 0.,-alpha,    0.)
        # --- Translation du point de départ à partir des coordonnées du centre de l'objet ciblé
        coord_starting_point1 =         center_coords.directional_offset_by(position_angle_RAmoins,  (nbTiles-1)*offset_value/2.)
        coord_starting_point  = coord_starting_point1.directional_offset_by(position_angle_DECmoins, (nbTiles-1)*offset_value/2.)
        # --- On applique ensuite le décalage pour déterminer l'emplacement de chaque tuile à partir de cette nouvelle origine
        tile_coordinates_center = []
        for i in range(nbTiles):
            for j in range(nbTiles):
                coord_tile_step1 = coord_starting_point.directional_offset_by(position_angle_RAplus,  offset_value*float(i))
                coord_tile_final =     coord_tile_step1.directional_offset_by(position_angle_DECplus, offset_value*float(j))
                tile_coordinates_center.append(coord_tile_final)
                logging.info("Coordinates of tile (%s, %s): %s"%(i+1, j+1, coord_tile_final))
        return tile_coordinates_center

    def importFits(self, jsonSpecs, tileCoordinatesCenters, tileFov):
        logging.info("importFits")
        specs = json.loads(jsonSpecs)
        channels = [specs["cb_surveyChannel1"],
                    specs["cb_surveyChannel2"],
                    specs["cb_surveyChannel3"],
                    specs["cb_surveyChannel4"]]
        chanames = []
        for j in range(len(channels)):
            chanames.append(channels[j].replace(' ', '_'))
        dir = os.path.dirname(specs["targetSpecsFile"])
        print(tileFov)
        for i in range(len(tileCoordinatesCenters)):
            for j in range(len(channels)):
                if channels[j] == "none":
                    continue
                fileImage = os.path.splitext(specs["targetSpecsFile"])[0] + '_' + chanames[j] + '_tile_' + str(i) + '.fits'
                shortFile = os.path.basename(fileImage)
                if os.path.isfile(fileImage):
                    logging.info("file already existing: %s"%fileImage)
                    continue
                logging.info("download %s"%fileImage)
                image = SkyView.get_images(tileCoordinatesCenters[i], survey=channels[j], pixels=specs["sb_nbPixels"] , radius=tileFov*u.deg)[0][0]
                image.writeto(shortFile, overwrite=True, output_verify="ignore")
                shutil.move(shortFile, fileImage)
