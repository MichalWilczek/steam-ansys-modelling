
import math
import numpy as np

class G10NonlinearMaterials(object):

    density = 1948.0        # [kg/m3]
    density_fake = 1.0      # [kg/m3]

    def __init__(self, temperature_profile):
        self.temperature_profile = temperature_profile

    def calculate_thermal_conductivity(self):
        """
        Returns G10 thermal conductivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        g10_thermal_conductivity_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            g10_thermal_conductivity_array[i, 0] = self.temperature_profile[i]
            g10_thermal_conductivity_array[i, 1] = self.thermal_conductivity_nist(temperature=self.temperature_profile[i])
        return g10_thermal_conductivity_array

    def calculate_cv(self):
        """
        Returns G10 volumetric heat capacity array
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        g10_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            g10_cv_array[i, 0] = self.temperature_profile[i]
            g10_cv_array[i, 1] = self.cv_nist(temperature=self.temperature_profile[i])
        return g10_cv_array

    def calculate_thermal_diffusivity(self):
        """
        Returns G10 thermal diffusivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        g10_thermal_conductivity = self.calculate_thermal_conductivity()
        g10_cv = self.calculate_cv()
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = g10_thermal_conductivity[:, 1] / g10_cv[:, 1]
        return diffusivity_array

    @staticmethod
    def thermal_conductivity_nist(temperature):
        """
        Calculates thermal conductivity of G10 according to NIST standards
        :param temperature: temperature as float
        :return: thermal conductivity as float
        """
        a0 = -4.1236
        a1 = 13.788
        a2 = -26.068
        a3 = 26.272
        a4 = -14.663
        a5 = 4.4954
        a6 = -0.6905
        a7 = 0.0397
        log_t = math.log10(temperature)
        f_exp = a0 + a1*log_t + a2*log_t**2.0 + a3*log_t**3.0 + a4*log_t**4.0 + \
            a5*log_t**5.0 + a6*log_t**6.0 + a7*log_t**7
        g10_thermal_conductivity = 10.0**f_exp
        return g10_thermal_conductivity

    @staticmethod
    def cv_nist(temperature):
        """
        Calculates volumetric heat capacity of G10 according to NIST standards
        :param temperature: temperature as float
        :return: volumetric heat capacity as float
        """
        a = -2.4083
        b = 7.6006
        c = -8.2982
        d = 7.3301
        e = -4.2386
        f = 1.4294
        g = -0.24396
        h = 0.015236
        i = 0.0
        log_t = math.log10(temperature)
        f_exp = a + b*log_t + c*log_t**2.0 + d*log_t**3.0 + e*log_t**4.0 + f*log_t**5.0 + g*log_t**6.0 + \
            h*log_t**7.0 + i*log_t**8.0
        g10_cv = 10.0**f_exp
        return g10_cv
