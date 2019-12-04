
from source.ansys.ansys_multiple_1D import AnsysMultiple1D
from source.factory.unit_conversion import UnitConversion
from source.insulation.insulation_circular_superconductor import InsulationCircularSuperconductor
from source.magnetic_field.winding_remap_search import WindingRemapSearch
import time

class AnsysMultiple1DSkewQuad(AnsysMultiple1D, UnitConversion, InsulationCircularSuperconductor):

    def __init__(self, factory, ansys_input_directory):
        AnsysMultiple1D.__init__(self, factory, ansys_input_directory)

    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.directory)
        self.variable_file_invariable_input(data)
        data.write_text('number_of_windings =' + str(self.input_data.geometry_settings.type_input.number_of_windings))
        data.write_text('number_of_windings_in_reel =' + str(
            self.input_data.geometry_settings.type_input.number_turns_in_layer))
        data.write_text('trans_dimension_winding =' + str(
            self.input_data.geometry_settings.type_input.winding_side * UnitConversion.milimeters_to_meters))
        data.write_text('division_long_side =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.division_long_side))
        data.write_text('division_short_side =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.division_short_side))
        data.write_text('division_radius =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.division_radius))

        data.write_text('long_side =' + str(
            self.input_data.geometry_settings.type_input.length_long_side * UnitConversion.milimeters_to_meters))
        data.write_text('short_side =' + str(
            self.input_data.geometry_settings.type_input.length_short_side * UnitConversion.milimeters_to_meters))
        data.write_text('radius =' + str(self.calculate_initial_radius()))

        if self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis:
            data.write_text('trans_division_insulation =' + str(
                self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis_input.
                transverse_division_insulation))
            data.write_text('eq_trans_dimension_insulation =' + str(self.calculate_insulation_length()))

        self.create_apdl_commands_for_python_waiting_process(data)
        time.sleep(2)

    def input_geometry(self, filename='1D_1D_1D_Geometry_quadrupole'):
        """
        Inputs prepared file with geometry to ANSYS environment
        :param filename: geometry file name as string
        """
        self.input_file(filename=filename, extension='inp', directory=self.ansys_input_directory, waiting_time=10)

    def calculate_initial_radius(self):
        winding_radius_step = self.input_data.geometry_settings.type_input.winding_side * \
                              UnitConversion.milimeters_to_meters
        initial_radius = self.input_data.geometry_settings.type_input.geometry_radius_first_layer * \
            UnitConversion.milimeters_to_meters

        layers = self.input_data.geometry_settings.type_input.number_layers
        turns_in_layer = self.input_data.geometry_settings.type_input.number_turns_in_layer
        first_turn_in_analysis = self.input_data.geometry_settings.type_input.winding_number_first_in_analysis

        layer_winding_search = WindingRemapSearch(number_of_layers=layers, number_of_windings_in_layer=turns_in_layer)
        layer_to_count = layer_winding_search.in_which_layer_is_winding(first_turn_in_analysis)

        final_radius = initial_radius + (float(layer_to_count) - 1.0) * winding_radius_step
        return final_radius

    def calculate_number_of_elements_per_winding(self):
        division_side1 = self.input_data.geometry_settings.type_input.type_mesh_settings.division_long_side
        division_side2 = self.input_data.geometry_settings.type_input.type_mesh_settings.division_short_side
        return float(2 * (division_side1 + division_side2) + 1)

    def calculate_total_winding_length(self):
        length_side1 = self.input_data.geometry_settings.type_input.length_long_side * UnitConversion.milimeters_to_meters
        length_side2 = self.input_data.geometry_settings.type_input.length_short_side * UnitConversion.milimeters_to_meters
        return 2.0 * (length_side1 + length_side2)

    def calculate_insulation_element_area(self):
        winding_length = self.calculate_total_winding_length()
        strand_diameter = \
            self.input_data.geometry_settings.type_input.strand_diameter * UnitConversion.milimeters_to_meters
        winding_side = self.input_data.geometry_settings.type_input.winding_side * UnitConversion.milimeters_to_meters

        element_area = InsulationCircularSuperconductor.return_insulation_single_element_area(
            winding_side1=winding_side, winding_side2=winding_side,
            strand_diameter=strand_diameter,
            total_winding_length=winding_length,
            number_of_elements=self.calculate_number_of_elements_per_winding())
        return element_area
