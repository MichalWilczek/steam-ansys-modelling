
from source.physics.initial_temperature.initial_temperature import InitialTemperature
from source.common_functions.general_functions import GeneralFunctions
import numpy as np
import math

class InitialTemperatureGaussian(InitialTemperature):

    def __init__(self, ansys_commands, class_geometry, mat_props, factory):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, mat_props, factory)
        self.initial_temperature_profile = None

    def create_ic_temperature_profile(self):
        self.initial_temperature_profile = self.define_gaussian_temperature_distribution_array(
            self.geometry.coil_geometry,
            magnetic_field=self.input_data.temperature_settings.input.B_initially_quenched_winding)
        GeneralFunctions.save_array(self.plots.output_directory_temperature,
                        "temperature_profile_0.txt", self.initial_temperature_profile)
        return self.initial_temperature_profile

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(
            temperature=self.input_data.temperature_settings.input.T_bath)
        gaussian_array = InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(
            self.initial_temperature_profile,
            ambient_temperature=self.input_data.temperature_settings.input.T_bath)
        refined_gaussian_array = InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(
            gaussian_array, ambient_temperature=self.input_data.temperature_settings.input.T_bath)
        for i in range(len(refined_gaussian_array[:, 0])):
            nodes_temp_list = self.geometry.retrieve_node_set_from_imaginary_node_number(
                self.geometry.coil_data, self.geometry.dict_windings_planes, imaginary_node=gaussian_array[i, 0])
            ansys_nodes_temp_list = self.geometry.prepare_ansys_nodes_selection_list(nodes_temp_list)
            self.ansys_commands.select_nodes_list(ansys_nodes_temp_list)
            self.ansys_commands.set_initial_temperature(temperature=gaussian_array[i, 1], allsel=False)

        self.calculate_energy_initially_deposited_inside_the_coil(
            magnetic_field_value=self.input_data.temperature_settings.input.B_initially_quenched_winding,
            temperature_init_distr=gaussian_array)

    @staticmethod
    def refine_gaussian_array_input_above_t_critical(gaussian_distribution_array, ambient_temperature):
        refined_array = gaussian_distribution_array[np.where(gaussian_distribution_array[:, 1] > ambient_temperature)]
        return refined_array

    def calculate_alpha(self, magnetic_field):
        """
        Calculates gaussian distribution function coefficient as a function of magnetic field
        :param magnetic_field: magnetic field as float
        :return: coefficient as float
        """
        temp_quench = self.material_properties.critical_current_density.critical_temperature(
            magnetic_field=magnetic_field)
        temp_peak = self.input_data.temperature_settings.input.T_max
        temp_operating = self.input_data.temperature_settings.input.T_bath
        directional_quench_init_length = self.input_data.analysis_settings.L_quench_init / 2.0

        log_n = math.log((temp_quench-temp_operating)/(temp_peak-temp_operating), math.e)
        denominator = math.sqrt(-log_n)**0.5
        alpha = directional_quench_init_length/denominator
        return alpha

    def calculate_node_gaussian_temperature(self, position, magnetic_field):
        """
        Calculates nodal initial temperature corresponding to gaussian distribution
        :param position: position in metres as float
        :param magnetic_field: magnetic field value at given node as float
        :return: temperature at node as float
        """

        alpha = self.calculate_alpha(magnetic_field)
        temp_peak = self.input_data.temperature_settings.input.T_max
        temp_operating = self.input_data.temperature_settings.input.T_bath
        quench_init_pos = self.input_data.analysis_settings.x_quench_init
        node_temp = temp_operating + (temp_peak-temp_operating)*math.e**(-((position-quench_init_pos)/alpha)**2.0)
        return node_temp

    def define_gaussian_temperature_distribution_array(self, imaginary_1d_geometry, magnetic_field):
        """
        Defines imaginary IC gaussian distribution temperature for imaginary 1D coil geometry
        :param imaginary_1d_geometry: 2-column numpy array; 1-imaginary node number, 2-node position in meters
        :param magnetic_field:
        """
        gaussian_distribution_array = np.zeros((len(imaginary_1d_geometry[:, 0]), 2))
        for i in range(len(imaginary_1d_geometry[:, 0])):
            position = imaginary_1d_geometry[i, 1]
            temp = self.calculate_node_gaussian_temperature(position=position, magnetic_field=magnetic_field)
            gaussian_distribution_array[i, 0] = imaginary_1d_geometry[i, 0]
            gaussian_distribution_array[i, 1] = temp
        self.plots.plot_and_save_temperature(self.output_directory, self.geometry.coil_geometry,
                                             gaussian_distribution_array, iteration=0, time_step=0.0)
        return gaussian_distribution_array
