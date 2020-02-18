
import math
from source.materials.nb_ti_cudi_material_properties import NbTiCUDIMaterialProperties

class NbTiJcLowCurrent(NbTiCUDIMaterialProperties):

    @staticmethod
    def calculate_joule_heating(magnetic_field, current, temperature, wire_area, normal_conductor_resistivity,
                                superconductor_proportion):
        critical_current_density = NbTiJcLowCurrent.critical_current_density(magnetic_field, temperature,
                                                                             superconductor_proportion)
        current_density = NbTiJcLowCurrent.current_density(current, wire_area)
        resistivity = normal_conductor_resistivity*NbTiJcLowCurrent.check_if_domain_is_normal(
            critical_current_density, current_density)
        return resistivity * current_density**2.0

    @staticmethod
    def check_if_domain_is_normal(critical_current_density, current_density):
        return max(1.0 - critical_current_density / (abs(current_density) + 10.0**(-3.0)), 0.0)

    @staticmethod
    def critical_current_density(magnetic_field, temperature, superconductor_proportion):
        """
        Calculates critical current density value for Niobium Titanium according to Matthias' formulae
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :param superconductor_proportion:
        :return: critical current density as float
        """
        critical_temperature = NbTiJcLowCurrent.critical_temperature(magnetic_field)
        critical_current_density = max(0.0, (1.004*10.0**10.0 - 7.619*10.0**8.0 * magnetic_field +
                                             2.797*10.0**10.0 * math.exp(-1.4 * magnetic_field) + 1.112*10.0**11.0 *
                                             math.exp(-12 * magnetic_field)) * (1.0 - temperature /
                                                                                critical_temperature))
        return critical_current_density * superconductor_proportion

    @staticmethod
    def current_density(current, wire_area):
        return current / wire_area

    @staticmethod
    def critical_temperature(magnetic_field, critical_temperature_0=NbTiCUDIMaterialProperties.tc0,
                             critical_magnetic_field_0=NbTiCUDIMaterialProperties.bc20):
        """
        Calculates critical temperature according to Matthias' formula
        :param critical_temperature_0: critical temperature for B=0 T as float
        :param critical_magnetic_field_0: critical magnetic field for T=0 K as float
        :param magnetic_field: magnetic field as float
        :return: critical temperature as float
        """
        critical_temperature = critical_temperature_0 * (1 - max(min(magnetic_field, 14.499), 0.0) /
                                                         critical_magnetic_field_0)**0.59
        return critical_temperature
