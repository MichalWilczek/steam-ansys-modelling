
from source.solver.initial_temperature.initial_temperature import InitialTemperature
import numpy as np

class InitialTemperatureGaussian(InitialTemperature):

    def __init__(self, ansys_commands, class_geometry, input_data, mat_props):
        InitialTemperature.__init__(self, ansys_commands, class_geometry, input_data, mat_props)

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(temperature=self.factory.temperature_init)

        gaussian_initial_temperature = self.geometry.define_gaussian_temperature_distribution_array(
            self.geometry.coil_geometry, magnetic_field=self.factory.magnetic_field_initially_quenched_winding)

        gaussian_array = InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(
            gaussian_initial_temperature, ambient_temperature=self.factory.temperature_init)
        self.ansys_commands.set_gaussian_initial_temperature_distribution(gaussian_array)

        self.calculate_energy_initially_deposited_inside_the_coil(
            node_down=gaussian_array[0, 0], node_up=gaussian_array[len(gaussian_array)-1, 0],
            magnetic_field_value=self.factory.constant_magnetic_field_value, temperature_init_distr=gaussian_array)

    @staticmethod
    def refine_gaussian_array_input_above_t_critical(gaussian_distribution_array, ambient_temperature):
        refined_array = gaussian_distribution_array[np.where(gaussian_distribution_array[:, 1] > ambient_temperature)]
        return refined_array



