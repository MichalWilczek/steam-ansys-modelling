
class NbTiCUDIMaterialProperties(object):

    density = 6000.0          # [kg/m3]
    density_fake = 1.0        # [kg/m3] - necessary for equivalent heat capacity definition

    tc0 = 9.2                 # [K]
    bc20 = 14.5               # [T]

    def volumetric_heat_capacity(self, magnetic_field, temperature):
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
