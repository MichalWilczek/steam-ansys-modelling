
import math

class GeometricFunctions(object):

    @staticmethod
    def calculate_circle_area(diameter):
        """
        Calculates area of a circle
        :param diameter: as float
        :return: area as float
        """
        if diameter < 0.0:
            raise ValueError("ERROR - the diameter should be positive")
        return math.pi/4.0 * (diameter**2.0)

    @staticmethod
    def calculate_diameter_from_circle_area(area):
        """
        Calculates diameter from circle area
        :param area: as float
        :return: diameter as float
        """
        if area < 0.0:
            raise ValueError("ERROR - the area should be positive")
        return math.sqrt(4.0*area / math.pi)

    @staticmethod
    def calculate_circle_perimeter(diameter):
        """
        Calculates circle circumference
        :param diameter: as float
        :return: as float
        """
        if diameter < 0.0:
            raise ValueError("ERROR - the diameter should be positive")
        return math.pi * diameter

    @staticmethod
    def calculate_rectangular_area(side1, side2):
        """
        Calculates area of a rectangle
        :param side1: as float
        :param side2: as float
        :return: as float
        """
        if side1 < 0.0 or side2 < 0.0:
            raise ValueError("ERROR - each input values should be positive")
        return side1 * side2

    @staticmethod
    def calculate_rectangular_perimeter(side1, side2):
        """
        Calculates circumference of a rectangle
        :param side1: as float
        :param side2: as float
        :return: as float
        """
        if side1 < 0.0 or side2 < 0.0:
            raise ValueError("ERROR - each input values should be positive")
        return 2.0 * (side1 + side2)

    @staticmethod
    def subtract_area_from_area(small_area, large_area):
        """
        :param small_area: as float
        :param large_area: as float
        :return: as float
        """
        if small_area > large_area:
            raise Exception("ERROR - small area should be smaller than the large area")
        elif small_area < 0.0 or large_area < 0.0:
            raise ValueError("ERROR - each input values should be positive")
        return large_area - small_area

    @staticmethod
    def calculate_volume_from_area_and_height(area, height):
        """
        :param area: as float
        :param height: as float
        :return: as float
        """
        if area < 0.0 or height < 0.0:
            raise ValueError("ERROR - each input values should be positive")
        return area * height
