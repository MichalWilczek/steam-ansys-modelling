
import math

class CuNISTMaterialProperties(object):

    density = 8960.0         # [kg/m3]
    density_fake = 1.0       # [kg/m3] - necessary for equivalent heat capacity definition

    @staticmethod
    def electrical_resistivity(magnetic_field, temperature, rrr):
        """
        Calculates electrical resistivity of copper according to NIST standards
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :param rrr: residual resistivity ratio as float
        :return: electrical resistivity as float
        """
        c0 = 1.553 * 10.0 ** (-8.0)  # (for RRR = 100 = R_273 / R_4)
        p1 = 1.171 * 10.0 ** (-17.0)
        p2 = 4.49
        p3 = 3.841 * 10.0 ** 10.0
        p4 = 1.14
        p5 = 50.0
        p6 = 6.428
        p7 = 0.4531
        a0 = -2.662
        a1 = 0.3168
        a2 = 0.6229
        a3 = -0.1839
        a4 = 0.01827

        rho_0 = c0 / rrr
        rho_i = p1 * temperature ** p2 / (1.0 + p1 * p3 * temperature ** (p2 - p4) *
                                          math.e ** (-(p5 / temperature) ** p6))
        rho_i0 = p7 * rho_i * rho_0 / (rho_i + rho_0)
        rho_n = rho_0 + rho_i + rho_i0

        if magnetic_field > 0.01:
            x = c0 * magnetic_field / rho_n
            log_x = math.log10(x)
            f_exp = a0 + a1 * log_x + a2 * log_x ** 2.0 + a3 * log_x ** 3.0 + a4 * log_x ** 4.0
            corr = 10.0 ** f_exp
        else:
            corr = 0.0
        resistivity = rho_n * (1 + corr)
        return resistivity

    # @staticmethod
    # def thermal_conductivity(magnetic_field, temperature, rrr):
    #     """
    #     Calculates thermal conductivity of copper according to NIST standards
    #     :param magnetic_field: magnetic field as float
    #     :param temperature: temperature as float
    #     :param rrr: residual resistivity ratio as float
    #     :return: thermal conductivity as float
    #     """
    #     beta = 0.634 / rrr
    #     beta_r = beta / (3.0 * 10.0 ** (-4.0))
    #     p1 = 1.754 * 10.0 ** (-8.0)
    #     p2 = 2.763
    #     p3 = 1102.0
    #     p4 = -0.165
    #     p5 = 70.0
    #     p6 = 1.756
    #     p7 = 0.838 / (beta_r ** 0.1661)
    #     w_0 = beta / temperature
    #     w_i = p1 * temperature ** p2 / (1.0 + p1 * p3 * temperature ** (p2 + p4) * math.e **
    #                                     (-(p5 / temperature) ** p6))
    #     w_i0 = p7 * (w_i * w_0) / (w_i + w_0)
    #     k_n = 1.0 / (w_0 + w_i + w_i0)
    #     thermal_conductivity = k_n * \
    #         (CuNISTMaterialProperties.electrical_resistivity(magnetic_field=0.0, temperature=temperature, rrr=rrr) /
    #          CuNISTMaterialProperties.electrical_resistivity(magnetic_field=magnetic_field, temperature=temperature,
    #                                                          rrr=rrr))
    #     return thermal_conductivity
    @staticmethod
    def thermal_conductivity(magnetic_field, temperature, rrr):
        """
        Calculates thermal conductivity of copper according to Wiedermann formula
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :param rrr: residual resistivity ratio as float
        :return: thermal conductivity as float
        """
        electrical_resistivity = CuNISTMaterialProperties.electrical_resistivity(magnetic_field, temperature, rrr)
        thermal_conductivity = 2.45 * 10.0**(-8.0) * temperature/electrical_resistivity
        return thermal_conductivity

    @staticmethod
    def volumetric_heat_capacity(temperature):
        """
        Calculates volumetric heat capacity of copper according to NIST standards
        :param temperature: temperature as float
        :return: volumetric heat capacity as float
        """
        a = -1.91844
        b = -0.15973
        c = 8.61013
        d = -18.996
        e = 21.9661
        f = -12.7328
        g = 3.54322
        h = -0.3797
        log_t = math.log10(temperature)
        f_exp = a + b * log_t ** 1.0 + c * log_t ** 2.0 + d * log_t ** 3.0 + e * log_t ** 4.0 + \
            f * log_t ** 5.0 + g * log_t ** 6.0 + h * log_t ** 7.0
        cp = 10.0 ** f_exp
        return cp * CuNISTMaterialProperties.density
