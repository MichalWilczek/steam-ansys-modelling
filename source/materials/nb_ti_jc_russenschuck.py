
from source.materials.nb_ti_cudi_material_properties import NbTiCUDIMaterialProperties

class NbTiJcRussenschuck(NbTiCUDIMaterialProperties):

    # - current sharing parameters
    c1 = 3449.0
    c2 = -257.0

    def calculate_joule_heating(self, magnetic_field, current, temperature, wire_area, normal_conductor_resistivity):
        temperature_c = NbTiJcRussenschuck.critical_temperature(magnetic_field)
        temperature_cs = self.current_sharing_temperature(temperature_c, current, magnetic_field)
        if temperature < temperature_cs:
            return 0.0
        elif temperature_cs <= temperature <= temperature_c:
            jc = self.critical_current_density(magnetic_field, current, temperature, wire_area)
            return normal_conductor_resistivity * jc**2.0
        else:
            j = current/wire_area
            return normal_conductor_resistivity * j**2.0

    def critical_current_density(self, magnetic_field, current, temperature, wire_area):
        """
        Calculates critical current density value for Niobium Titanium according to Russenschuck formulae
        :param magnetic_field: magnetic field as float
        :param current: current in the wire as float
        :param temperature: temperature as float
        :param wire_area: wire area as float
        :return: critical density as float
        """
        critical_temperature = NbTiJcRussenschuck.critical_temperature(
            critical_temperature_0=NbTiCUDIMaterialProperties.tc0,
            critical_magnetic_field_0=NbTiCUDIMaterialProperties.bc20,
            magnetic_field=magnetic_field)
        current_sharing_temperature = self.current_sharing_temperature(critical_temperature, current, magnetic_field)
        critical_current_density = NbTiJcRussenschuck.critical_current_ic(
            current, temperature, critical_temperature, current_sharing_temperature) / wire_area
        return critical_current_density

    @staticmethod
    def critical_temperature(magnetic_field, critical_temperature_0=NbTiCUDIMaterialProperties.tc0,
                             critical_magnetic_field_0=NbTiCUDIMaterialProperties.bc20):
        """
        Calculates Nb-Ti critical temperature
        :param critical_temperature_0: critical temperature for B=0 T as float
        :param critical_magnetic_field_0: critical magnetic field for T=0 K as float
        :param magnetic_field: magnetic field as float
        :return: critical temperature as float
        """
        critical_temperature = critical_temperature_0*(1.0-magnetic_field/critical_magnetic_field_0)**0.59
        return critical_temperature

    def current_sharing_temperature(self, critical_temperature, current, magnetic_field):
        """
        Calculates current sharing temperature
        :param critical_temperature: as float
        :param current: as float
        :param magnetic_field: as float
        :return: current sharing temperature as float
        """
        return critical_temperature*(1.0-current/(self.c1+self.c2*magnetic_field))

    @staticmethod
    def critical_current_ic(current, temperature, critical_temperature, current_sharing_temperature):
        """
        Calculates critical current
        :param current: as float
        :param temperature: reference temperature as float
        :param critical_temperature: as float
        :param current_sharing_temperature: as float
        :return: critical current as float
        """
        return current * (temperature - current_sharing_temperature) / (
                critical_temperature - current_sharing_temperature)
