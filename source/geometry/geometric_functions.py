
import math

class GeometricFunctions(object):

    @staticmethod
    def calculate_circle_area(diameter):
        """
        Calculates area of a circle
        :param diameter: as float
        :return: area as float
        """
        return math.pi/4.0 * (diameter**2.0)

    @staticmethod
    def calculate_diameter_from_circle_area(area):
        """
        Calculates diameter from circle area
        :param area: as float
        :return: diameter as float
        """
        return math.sqrt(4.0*area / math.pi)
