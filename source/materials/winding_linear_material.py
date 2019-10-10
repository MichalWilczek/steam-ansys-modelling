
import numpy as np

class WindingLinearMaterial(object):

    density = 6000.0          # [kg/m3]
    density_fake = 1.0        # [kg/m3]

    critical_temperature = 5  # [K]

    def __init__(self, temperature_profile):
        self.temperature_profile = temperature_profile

    def calculate_cv(self, *args, **kwargs):
        """
        Returns volumetric heat capacity array
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        cv_array = np.zeros((len(self.temperature_profile), 2))
        cv_array[:, 0] = self.temperature_profile[:, 0]
        cv_array[:, 1] = self.cv()
        return cv_array

    def calculate_thermal_diffusivity(self):
        """
        Returns thermal diffusivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        thermal_conductivity = self.calculate_thermal_conductivity()
        cv = self.calculate_cv()
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = thermal_conductivity[:, 1] / cv[:, 1]
        return diffusivity_array

    def calculate_thermal_conductivity(self):
        """
        Returns thermal conductivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        thermal_conductivity_array = np.zeros((len(self.temperature_profile), 2))
        thermal_conductivity_array[:, 0] = self.temperature_profile[:, 0]
        thermal_conductivity_array[:, 1] = self.thermal_conductivity()
        return thermal_conductivity_array

    def calculate_critical_temperature(self, *args, **kwargs):
        """
        Calculates critical temperature
        """
        return self.critical_temperature

    def calculate_current_sharing_temperature(self, *args, **kwargs):
        """
        Calculates current sharing temperature
        """
        return self.critical_temperature

    @staticmethod
    def resistivity():
        resistivity = 0.00000000025
        return resistivity

    @staticmethod
    def thermal_conductivity():
        thermal_conductivity = 1.0
        return thermal_conductivity

    @staticmethod
    def cv():
        cv = 5.0
        return cv
