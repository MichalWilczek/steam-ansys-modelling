
from source.geometry.geometric_functions import GeometricFunctions

class Insulation(GeometricFunctions):

    @staticmethod
    def calculate_cross_sectional_insulation_area(area_strand, area_winding):
        """
        :param area_strand: as float
        :param area_winding: as float
        :return: as float
        """
        return area_winding - area_strand

    @staticmethod
    def calculate_eff_insulation_length(cross_sectional_insulation_area, average_insulation_perimeter):
        """
        :param cross_sectional_insulation_area: as float
        :param average_insulation_perimeter: as float
        :return: as float
        """
        return cross_sectional_insulation_area / average_insulation_perimeter

    @staticmethod
    def calculate_winding_perimeter(winding_side1, winding_side2):
        """
        :param winding_side1: as float
        :param winding_side2: as float
        :return: as float
        """
        return GeometricFunctions.calculate_rectangular_perimeter(winding_side1, winding_side2)

    @staticmethod
    def calculate_insulation_volume(cross_sectional_insulation_area, insulation_length):
        """
        :param cross_sectional_insulation_area: as float
        :param insulation_length: as float
        :return: as float
        """
        return cross_sectional_insulation_area * insulation_length
