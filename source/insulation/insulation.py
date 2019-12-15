
from source.geometry.geometric_functions import GeometricFunctions

class Insulation(GeometricFunctions):

    @staticmethod
    def return_insulation_single_element_area(diameter_strand, diameter_strand_with_insulation, total_winding_length,
                                              number_of_elements, contact_correction_factor):
        """
        Returns area of a single 1D insulation element for ANSYS geometry
        :param diameter_strand: as float
        :param diameter_strand_with_insulation:
        :param total_winding_length: length of a single winding as float
        :param number_of_elements: number of insulation elements in one winding as float
        :param contact_correction_factor:
        :return: as float
        """
        area_strand = GeometricFunctions.calculate_circle_area(diameter_strand)
        area_strand_with_insulation = GeometricFunctions.calculate_circle_area(diameter_strand_with_insulation)
        area_insulation = GeometricFunctions.subtract_area_from_area(area_strand, area_strand_with_insulation)
        volume_insulation = Insulation.calculate_volume_from_area_and_height(area_insulation,
                                                                             height=total_winding_length)
        element_area = 0.25 * contact_correction_factor * volume_insulation / Insulation.\
            get_insulation_side(diameter_strand, diameter_strand_with_insulation)
        return element_area / number_of_elements

    @staticmethod
    def return_insulation_resin_single_element_volume(winding_side, diameter_strand_with_insulation,
                                                      diameter_strand, contact_correction_factor, total_winding_length,
                                                      resin_filling_correction_factor, number_of_elements):
        area_winding = GeometricFunctions.calculate_rectangular_area(winding_side, winding_side)
        area_strand_with_insulation = GeometricFunctions.calculate_circle_area(diameter_strand_with_insulation)
        area_strand = GeometricFunctions.calculate_circle_area(diameter_strand)
        area_resin = GeometricFunctions.subtract_area_from_area(area_strand_with_insulation, area_winding)
        volume_resin_winding = GeometricFunctions.calculate_volume_from_area_and_height(area_resin,
                                                                                        total_winding_length)
        area_insulation = GeometricFunctions.subtract_area_from_area(area_strand, area_strand_with_insulation)
        volume_insulation = GeometricFunctions.calculate_volume_from_area_and_height(area_insulation,
                                                                                     total_winding_length)
        volume_resin_winding_corrected = volume_resin_winding * resin_filling_correction_factor
        volume_insulation_corrected = volume_insulation * (1.0 - contact_correction_factor)
        final_volume = (volume_insulation_corrected + volume_resin_winding_corrected) / number_of_elements
        return final_volume

    @staticmethod
    def calculate_average_insulation_perimeter(winding_side1, winding_side2, strand_diameter):
        winding_perimeter = GeometricFunctions.calculate_rectangular_perimeter(winding_side1, winding_side2)
        strand_perimeter = GeometricFunctions.calculate_circle_perimeter(strand_diameter)
        return (winding_perimeter + strand_perimeter) / 2.0

    @staticmethod
    def calculate_eff_insulation_length(cross_sectional_insulation_area, average_insulation_perimeter):
        """
        :param cross_sectional_insulation_area: as float
        :param average_insulation_perimeter: as float
        :return: as float
        """
        return cross_sectional_insulation_area / average_insulation_perimeter

    @staticmethod
    def get_insulation_side(small_circle, large_circle):
        """
        Returns effective insulation element length for ANSYS geometry
        :param small_circle: as float
        :param large_circle: as float
        :return: as float
        """
        if small_circle > large_circle:
            raise ValueError("ERROR - small circle cannot be larger than the large circle")
        elif small_circle < 0.0 or large_circle < 0.0:
            raise ValueError("ERROR - each input values should be positive")
        return (large_circle - small_circle) / 2.0

    @staticmethod
    def check_input_of_correction_factor(correction_factor):
        if correction_factor > 1.0 or correction_factor < 0.0:
            raise ValueError("Correction factor should be between 0.0 and 1.0")
        elif not isinstance(correction_factor, float):
            raise TypeError("Correction factor should be a float")
