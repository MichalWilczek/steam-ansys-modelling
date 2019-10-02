
from source.initial_temperature.initial_temperature import InitialTemperature

class InitialTemperatureGaussian(InitialTemperature):

    def __init__(self, ansys_commands, class_geometry, input_data):
        super.__init__(ansys_commands, class_geometry, input_data)

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(temperature=self.factory.temperature_init)
        gaussian_initial_temperature = self.geometry.define_gaussian_temperature_distribution_array(
            self.geometry.coil_geometry, magnetic_field=self.factory.magnetic_field_initially_quenched_winding)

        self.ansys_commands.set_gaussian_initial_temperature_distribution(gaussian_initial_temperature)


