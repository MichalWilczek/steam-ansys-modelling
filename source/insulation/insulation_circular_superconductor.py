
from source.insulation.insulation import Insulation
from source.geometry.geometric_functions import GeometricFunctions

class InsulationCircularSuperconductor(Insulation, GeometricFunctions):

    @staticmethod
    def return_eff_insulation_length(winding_side1, winding_side2, strand_diameter):
        """
        Returns effective insulation element length for ANSYS geometry
        :param winding_side1: as float
        :param winding_side2: as float
        :param strand_diameter: as float
        :return: as float
        """
        perimeter = InsulationCircularSuperconductor.calculate_average_insulation_perimeter(
            winding_side1, winding_side2, strand_diameter)
        area_strand = GeometricFunctions.calculate_circle_area(strand_diameter)
        area_winding = GeometricFunctions.calculate_rectangular_area(winding_side2, winding_side1)
        area = Insulation.calculate_cross_sectional_insulation_area(area_strand=area_strand, area_winding=area_winding)
        insulation_length = Insulation.calculate_eff_insulation_length(area, perimeter)
        return insulation_length

    @staticmethod
    def return_insulation_single_element_area(winding_side1, winding_side2, strand_diameter,
                                              total_winding_length, number_of_elements):
        """
        Returns area of a single 1D insulation element for ANSYS geometry
        :param winding_side1: as float
        :param winding_side2: as float
        :param strand_diameter: as float
        :param total_winding_length: length of a single winding as float
        :param number_of_elements: number of insulation elements in one winding as float
        :return: as float
        """
        all_elements_area = InsulationCircularSuperconductor.return_insulation_all_elements_area(
            winding_side1, winding_side2, strand_diameter, total_winding_length)
        return all_elements_area / number_of_elements

    @staticmethod
    def return_insulation_all_elements_area(winding_side1, winding_side2, strand_diameter, total_winding_length):
        """
        Returns area of a quarter of insulation length along one winding
        :param winding_side1: as float
        :param winding_side2: as float
        :param strand_diameter: as float
        :param total_winding_length: length of a single winding as float
        :return: as float
        """
        area_strand = GeometricFunctions.calculate_circle_area(strand_diameter)
        area_winding = GeometricFunctions.calculate_rectangular_area(winding_side2, winding_side1)
        area = Insulation.calculate_cross_sectional_insulation_area(area_strand=area_strand, area_winding=area_winding)

        volume = Insulation.calculate_insulation_volume(area, insulation_length=total_winding_length)
        element_area = 0.25 * volume / InsulationCircularSuperconductor.return_eff_insulation_length(
            winding_side1, winding_side2, strand_diameter)
        return element_area

    @staticmethod
    def calculate_strand_perimeter(strand_diameter):
        return GeometricFunctions.calculate_circle_perimeter(strand_diameter)

    @staticmethod
    def calculate_average_insulation_perimeter(winding_side1, winding_side2, strand_diameter):
        winding_perimeter = Insulation.calculate_winding_perimeter(winding_side1, winding_side2)
        strand_perimeter = InsulationCircularSuperconductor.calculate_strand_perimeter(strand_diameter)
        return (winding_perimeter + strand_perimeter) / 2.0

