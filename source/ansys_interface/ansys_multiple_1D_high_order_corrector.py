
from source.ansys_interface.ansys_multiple_1D import AnsysMultiple1D
from source.common_functions.unit_conversion import UnitConversion
from source.geometry.insulation.insulation import Insulation
from source.common_functions.general_functions import GeneralFunctions
import time

class AnsysMultiple1DHighOrderCorrector(AnsysMultiple1D):

    def __init__(self, factory, ansys_input_directory):
        AnsysMultiple1D.__init__(self, factory, ansys_input_directory)
        self.point_mass_is_applied = self.check_if_point_mass_is_applied()

    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.directory)
        self.create_first_lines_of_input_parameter_file_for_ansys(data)
        data.write_text('number_of_windings =' + str(self.input_data.geometry_settings.type_input.n_windings))
        data.write_text('number_of_windings_in_reel =' + str(
            self.input_data.geometry_settings.type_input.n_turns_in_layer))
        data.write_text('trans_dimension_winding =' + str(
            self.input_data.geometry_settings.type_input.trans_dimension_winding * UnitConversion.milimeters_to_meters))
        data.write_text('division_long_side =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.n_divisions_e_coil))
        data.write_text('division_short_side =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.n_divisions_d_coil))
        data.write_text('division_radius =' + str(
            self.input_data.geometry_settings.type_input.type_mesh_settings.n_divisions_rad))

        data.write_text('long_side =' + str(
            self.input_data.geometry_settings.type_input.e_coil * UnitConversion.milimeters_to_meters))
        data.write_text('short_side =' + str(
            self.input_data.geometry_settings.type_input.d_coil * UnitConversion.milimeters_to_meters))
        data.write_text('radius =' + str(self.calculate_initial_radius()))

        if self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis:
            data.write_text('trans_division_insulation =' + str(
                self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis_input.
                n_divisions_ins))
            data.write_text('eq_trans_dimension_insulation =' + str(self.calculate_insulation_length()))
            data.write_text('create_point_thermal_capacity =' + str(
                GeneralFunctions.change_boolean_into_integer(self.point_mass_is_applied)))
            if self.point_mass_is_applied:
                data.write_text('point_mass_volume =' + str(self.calculate_point_mass_volume()))

        self.create_apdl_commands_for_python_waiting_process(data)
        time.sleep(2)

    def upload_apdl_geometry_input_file(self, filename='1D_1D_1D_Geometry_High_Order_Corrector'):
        """
        Inputs prepared file with geometry to ANSYS environment
        :param filename: geometry file name as string
        """
        self.input_file(filename=filename, extension='inp', directory=self.ansys_input_directory)

    def calculate_initial_radius(self):
        winding_radius_step = self.input_data.geometry_settings.type_input.a_strand * \
                              UnitConversion.milimeters_to_meters
        initial_radius = self.input_data.geometry_settings.type_input.rad_coil * \
            UnitConversion.milimeters_to_meters

        layer_to_count = self.input_data.geometry_settings.type_input.which_layer_first_in_analysis
        final_radius = initial_radius + (float(layer_to_count) - 1.0) * winding_radius_step
        return final_radius

    def calculate_number_of_elements_per_winding(self):
        division_side1 = self.input_data.geometry_settings.type_input.type_mesh_settings.n_divisions_e_coil
        division_side2 = self.input_data.geometry_settings.type_input.type_mesh_settings.n_divisions_d_coil
        return float(2 * (division_side1 + division_side2) + 1)

    def calculate_total_winding_length(self):
        length_side1 = self.input_data.\
            geometry_settings.type_input.e_coil * UnitConversion.milimeters_to_meters
        length_side2 = self.input_data.\
            geometry_settings.type_input.d_coil * UnitConversion.milimeters_to_meters
        return 2.0 * (length_side1 + length_side2)

    def calculate_insulation_element_area(self):
        Insulation.check_input_of_correction_factor(self.input_data.geometry_settings.type_input.u_resin)
        return Insulation.return_insulation_single_element_area(
            diameter_strand=self.input_data.geometry_settings.type_input.d_strand * UnitConversion.milimeters_to_meters,
            diameter_strand_with_insulation=self.input_data.
                geometry_settings.type_input.d_ins * UnitConversion.milimeters_to_meters,
            total_winding_length=self.calculate_total_winding_length(),
            number_of_elements=self.calculate_number_of_elements_per_winding(),
            contact_correction_factor=self.input_data.geometry_settings.type_input.u_ins
        )

    def calculate_point_mass_volume(self):
        Insulation.check_input_of_correction_factor(self.input_data.geometry_settings.type_input.u_ins)
        Insulation.check_input_of_correction_factor(self.input_data.geometry_settings.type_input.u_resin)
        return Insulation.return_insulation_resin_single_element_volume(
            winding_side=self.input_data.geometry_settings.type_input.a_strand * UnitConversion.milimeters_to_meters,
            diameter_strand_with_insulation=self.input_data.
                geometry_settings.type_input.d_ins * UnitConversion.milimeters_to_meters,
            diameter_strand=self.input_data.geometry_settings.type_input.d_strand * UnitConversion.milimeters_to_meters,
            contact_correction_factor=self.input_data.geometry_settings.type_input.u_ins,
            total_winding_length=self.calculate_total_winding_length(),
            resin_filling_correction_factor=self.input_data.geometry_settings.type_input.u_resin,
            number_of_elements=self.calculate_number_of_elements_per_winding()
        )
