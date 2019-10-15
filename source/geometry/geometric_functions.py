
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

    @staticmethod
    def calculate_circle_perimeter(diameter):
        """
        Calculates circle circumference
        :param diameter: as float
        :return: as float
        """
        return math.pi * diameter

    @staticmethod
    def calculate_rectangular_area(side1, side2):
        """
        Calculates area of a rectangle
        :param side1: as float
        :param side2: as float
        :return: as float
        """
        return side1 * side2

    @staticmethod
    def calculate_rectangular_perimeter(side1, side2):
        """
        Calculates circumference of a rectangle
        :param side1: as float
        :param side2: as float
        :return: as float
        """
        return 2.0 * (side1 + side2)


