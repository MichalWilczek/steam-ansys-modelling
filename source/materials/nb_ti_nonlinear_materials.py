
import numpy as np

class NbTiNonlinearMaterials(object):

    a0 = 1.7
    a1 = 2.33 * 10.0 ** 9.0
    a2 = 9.57 * 10 ** 5.0
    a3 = 163.0
    tc0 = 9.2
    bc20 = 14.5

    # - current sharing parameters
    c1 = 3449.0
    c2 = -257.0

    density = 6000.0          # [kg/m3]
    density_fake = 1.0        # [kg/m3] - necessary for equivalent heat capacity definition

    def __init__(self, temperature_profile):
        self.temperature_profile = temperature_profile

    def calculate_cv(self, magnetic_field):
        """
        Returns Nb-Ti volumetric heat capacity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        nbti_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            nbti_cv_array[i, 0] = self.temperature_profile[i]
            nbti_cv_array[i, 1] = self.cv_cudi(magnetic_field, temperature=self.temperature_profile[i])
        return nbti_cv_array

    def calculate_critical_temperature(self, magnetic_field):
        """
        Calculates Nb-Ti critical temperature
        :param magnetic_field: magnetic field as float
        :return: critical temperature as float
        """
        critical_temperature_0 = self.tc0              # [K]
        critical_magnetic_field_0 = self.bc20          # [T]
        critical_temperature = critical_temperature_0*(1.0-magnetic_field/critical_magnetic_field_0)**0.59
        return critical_temperature

    def calculate_current_sharing_temperature(self, critical_temperature, current, magnetic_field):
        """
        Calculates current sharing temperature
        :param critical_temperature: as float
        :param current: as float
        :param magnetic_field: as float
        :return: current sharing temperature as float
        """
        return critical_temperature*(1.0-current/(self.c1+self.c2*magnetic_field))

    def cv_cudi(self, magnetic_field, temperature):
        """
        Calculates volumetric heat capacity of Nb-Ti according to CUDI repository
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :return: volumetric heat capacity as float
        """
        tc = self.tc0*(1.0-magnetic_field/self.bc20)**0.59
        if temperature < tc:
            a0 = 0.0
            a1 = 64.0*magnetic_field
            a2 = 0.0
            a3 = 49.1
            a4 = 0.0
        elif tc <= temperature < 28.358:
            a0 = 0
            a1 = 928.0
            a2 = 0.0
            a3 = 16.24
            a4 = 0.0
        elif 28.358 <= temperature < 50.99:
            a0 = 41383.0
            a1 = -7846.1
            a2 = 553.71
            a3 = 11.9838
            a4 = -0.2177
        elif 50.99 <= temperature < 165.8:
            a0 = -1.53*10.0**6.0
            a1 = 83022.0
            a2 = -716.3
            a3 = 2.976
            a4 = -0.00482
        elif 165.8 <= temperature < 496.54:
            a0 = 1.24*10.0**6.0
            a1 = 13706.0
            a2 = -51.66
            a3 = 0.09296
            a4 = -6.29*10.0**(-5.0)
        else:
            a0 = 2.45*10.0**6.0
            a1 = 955.5
            a2 = -0.257
            a3 = 0.0
            a4 = 0.0
        cv = a0 + a1*temperature + a2*temperature**2.0 + a3*temperature**3.0 + a4*temperature**4.0
        return cv
