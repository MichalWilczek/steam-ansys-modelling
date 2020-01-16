
import math

class G10NISTMaterialProperties(object):

    # Values taken from 'Review of ROXIE's Material Properties Database for Quench Simulation'
    density = 1948.0    # [kg/m3]
    density_fake = 1.0  # [kg/m3]

    @staticmethod
    def thermal_conductivity(temperature):
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
    def volumetric_heat_capacity(temperature):
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
        g10_cp = 10.0**f_exp
        return g10_cp * G10NISTMaterialProperties.density
