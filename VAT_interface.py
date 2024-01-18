import logging
from astroquery.simbad import Simbad

class VAT_interface:
    """
    interface d'acces VAT_Class, AstroQuery
    """

    def __init__(self):
        logging.debug("init VAT_interface")

    def checkObjName(self, objName):
        """
        Verifier si le nom de l'objet est connu
        """
        logging.debug("checkObjName")
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

    def generateOverview(self, objName):
        logging.debug("generateOverview")
