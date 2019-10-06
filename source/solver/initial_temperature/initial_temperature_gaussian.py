
from source.solver.initial_temperature.initial_temperature import InitialTemperature
import numpy as np
import math

class InitialTemperatureGaussian(InitialTemperature):

    def __init__(self, ansys_commands, class_geometry, input_data, mat_props):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, input_data, mat_props)
        self.initial_temperature_profile = None

    def create_ic_temperature_profile(self):
        self.initial_temperature_profile = self.geometry.define_gaussian_temperature_distribution_array(
            self.geometry.coil_geometry, magnetic_field=self.factory.magnetic_field_initially_quenched_winding)
        return self.initial_temperature_profile

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(temperature=self.factory.temperature_init)
        gaussian_array = InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(
            self.initial_temperature_profile, ambient_temperature=self.factory.temperature_init)
        self.ansys_commands.set_gaussian_initial_temperature_distribution(gaussian_array)

        self.calculate_energy_initially_deposited_inside_the_coil(
            node_down=gaussian_array[0, 0], node_up=gaussian_array[len(gaussian_array)-1, 0],
            magnetic_field_value=self.factory.constant_magnetic_field_value, temperature_init_distr=gaussian_array)

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
        temp_quench = self.material_properties.calculate_critical_temperature(magnetic_field=magnetic_field)
        temp_peak = self.factory.temperature_max_init_quenched_zone
        temp_operating = self.factory.temperature_init
        directional_quench_init_length = self.factory.quench_init_length/2.0

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
        temp_peak = self.factory.temperature_max_init_quenched_zone
        temp_operating = self.factory.temperature_init
        quench_init_pos = self.factory.quench_init_position
        node_temp = temp_operating + (temp_peak-temp_operating)*math.e**(-((position-quench_init_pos)/alpha)**2.0)
        return node_temp

    def define_gaussian_temperature_distribution_array(self, imaginary_1d_geometry, magnetic_field):
        """
        Defines imaginary IC gaussian distribution temeperature for imaginary 1D coil geometry
        :param imaginary_1d_geometry: 2-column numpy array; 1-imaginary node number, 2-node position in meters
        """
        gaussian_distribution_array = np.zeros((len(imaginary_1d_geometry[:, 0]), 2))
        for i in range(len(imaginary_1d_geometry[:, 0])):
            position = imaginary_1d_geometry[i, 1]
            temp = self.calculate_node_gaussian_temperature(position=position, magnetic_field=magnetic_field)
            gaussian_distribution_array[i, 0] = imaginary_1d_geometry[i, 0]
            gaussian_distribution_array[i, 1] = temp
        self.plot_and_save_temperature(self.directory, self.geometry.coil_geometry, self.initial_temperature_profile,
                                       iteration=0, time_step=0.0)
        return gaussian_distribution_array
