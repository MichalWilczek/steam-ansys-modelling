
import numpy as np
import os
import math
from source.factory.unit_conversion import UnitConversion
from source.factory.general_functions import GeneralFunctions

class Materials(GeneralFunctions):

    def __init__(self, factory):

        self.superconductor = factory.get_superconductor_class(factory)
        self.normal_conductor = factory.get_normal_conductor_class(factory)
        self.insulation = factory.get_insulation_class(factory)

        self.rrr = self.input_data.material_settings.input.rrr

        self.output_directory = factory.output_directory
        self.output_directory_materials = GeneralFunctions.create_folder_in_directory(self.output_directory,
                                                                                      "mat_props")
        self.input_data = factory.input_data
        self.super_to_normal_ratio = self.input_data.material_settings.input.nonsupercond_to_supercond_ratio

        self.f_superconductor = self.ratio_superconductor()
        self.f_non_superconductor = self.ratio_normal_conductor()

        self.temperature_profile = Materials.create_temperature_step(
            temp_min=self.input_data.material_settings.input.min_temperature_span,
            temp_max=self.input_data.material_settings.input.max_temperaute_span
        )

    def ratio_superconductor(self):
        return 1.0/(1.0 + self.super_to_normal_ratio)

    def ratio_normal_conductor(self):
        return 1.0 - self.ratio_superconductor()

    @staticmethod
    def wire_area(wire_diameter):
        return math.pi/4.0 * (wire_diameter**2.0)

    def reduced_wire_area(self, wire_diameter):
        return self.wire_area(wire_diameter) * self.f_non_superconductor

    def reduced_wire_diameter(self, wire_diameter):
        return (4.0*self.reduced_wire_area(wire_diameter)/math.pi)**0.5

    @staticmethod
    def create_temperature_step(temp_min, temp_max, number_temp_points=100):
        """
        Creates temperature values to be input in all material properties functions
        :param temp_min: minimum temperature as integer
        :param temp_max: maximum temperature as integer
        :param number_temp_points: number of temperature points to be defined as integer
        :return: list of temperature steps
        """
        temperature_span = temp_max - temp_min
        temperature_step = temperature_span/float(number_temp_points - 1)
        temperature_step_profile = np.arange(temp_min, temp_max+0.1, temperature_step)
        return temperature_step_profile

    def calculate_qf_resistance(self, qf_down, qf_up, im_temp_profile, im_coil_geom, mag_field, wire_diameter):
        """
        Calculates quench front resistance
        :param qf_down: node number of lower quench front limit as integer
        :param qf_up: node number of upper quench front limit as integer
        :param im_temp_profile: numpy array; 1st column: node number as integer, 2nd column: node temperature as float
        :param im_coil_geom: numpy array; 1st column: node number as integer, 2nd column: coil length as float
        :param mag_field: magnetic_field as float
        :param wire_diameter: wire diameter as float
        :return: total resistance of the quench front in Ohms as float
        """
        qf_resistance = 0.0
        for i in range(qf_down, qf_up):
            t_1 = im_temp_profile[i-1, 1]
            t_2 = im_temp_profile[i, 1]
            t_elem = (t_1+t_2)/2.0
            resistivity_elem = self.normal_conductor.resistivity_nist(
                magnetic_field=mag_field, rrr=self.rrr, temperature=t_elem)
            elem_length = abs(im_coil_geom[i, 1] - im_coil_geom[i-1, 1])
            elem_res = resistivity_elem*elem_length/self.reduced_wire_area(
                wire_diameter*UnitConversion.milimeters_to_meters)
            qf_resistance += elem_res
        return qf_resistance

    def calculate_energy(self, im_temp_profile, im_coil_geom, mag_field, wire_diameter, ref_temperature):
        """
        Calculates the initial energy input inside the coil
        :param im_temp_profile: numpy array; 1st column: node number as integer, 2nd column: node temperature as float
        :param im_coil_geom: numpy array; 1st column: node number as integer, 2nd column: coil length as float
        :param mag_field: magnetic_field as float
        :param wire_diameter: wire diameter as float
        :param ref_temperature: reference temperature as float
        :return: initial energy input in Joules as float
        """
        qf_energy = 0.0
        for i in range(len(im_temp_profile)-1):
            t_1 = im_temp_profile[i, 1]
            t_2 = im_temp_profile[i+1, 1]
            t_elem = (t_1+t_2)/2.0
            cv_elem = self.winding_eq_cv(magnetic_field=mag_field, temperature=t_elem)
            elem_length = abs(im_coil_geom[i, 1] - im_coil_geom[i-1, 1])
            elem_area = self.reduced_wire_area(wire_diameter*UnitConversion.milimeters_to_meters)
            elem_volume = elem_area*elem_length
            elem_energy = elem_volume * cv_elem * (t_elem-ref_temperature)
            qf_energy += elem_energy
        return qf_energy

    def calculate_strand_thermal_diffusivity(self, magnetic_field, rrr):
        """
        Returns equivalent strand thermal diffusivity array
        :param magnetic_field: magnetic field as float
        :param rrr: residual resistivity ratio as float
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        normal_conductor_thermal_conductivity = self.normal_conductor.calculate_thermal_cond(
            magnetic_field=magnetic_field, rrr=rrr)
        strand_cv = self.calculate_winding_eq_cv(magnetic_field=magnetic_field)
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = normal_conductor_thermal_conductivity[:, 1] / strand_cv[:, 1]
        return diffusivity_array

    def calculate_winding_eq_cv(self, magnetic_field):
        """
        Returns strand equivalent volumetric heat capacity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        winding_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            winding_cv_array[i, 0] = self.temperature_profile[i]
            winding_cv_array[i, 1] = self.winding_eq_cv(magnetic_field, temperature=self.temperature_profile[i])
        return winding_cv_array

    def winding_eq_cv(self, magnetic_field, temperature):
        """
        Calculates strand equivalent volumetric heat capacity
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :return: volumetric heat capacity as float
        """
        normal_conductor_cv = self.normal_conductor.cv_nist(temperature)
        superconductor_cv = self.superconductor.cv_cudi(magnetic_field, temperature)
        winding_eq_cv = self.f_non_superconductor*normal_conductor_cv + self.f_superconductor*superconductor_cv
        return winding_eq_cv

    def calculate_current_in_copper_matrix(self, temperature, magnetic_field, current):
        """
        Calculates current level in copper matrix at superconducting, transition and normal state
        :param temperature: reference temperature as float
        :param magnetic_field: magnetic field as float
        :param current: current as float
        :return: current in copper as float
        """
        temp_critic = self.superconductor.calculate_critical_temperature(magnetic_field)
        temp_cs = self.superconductor.calculate_current_sharing_temperature(temp_critic, current, magnetic_field)
        ic = self.calculate_critical_current_ic(current, temperature, temp_critic, temp_cs)
        if temperature < temp_cs:
            return 0.0
        elif temp_cs <= temperature < temp_critic:
            return current - ic
        else:
            return current

    @staticmethod
    def calculate_critical_current_ic(current, temperature, critical_temperature, current_sharing_temperature):
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

    def calculate_joule_heating(self, magnetic_field, wire_diameter, current, temperature):
        """
        Calculates Joule heating power density in W/m3
        :param magnetic_field: as float
        :param wire_diameter: as float
        :param current: as float
        :param temperature: as float
        :return: joule heating power density as float
        """
        temp_critic = self.superconductor.calculate_critical_temperature(magnetic_field)
        temp_cs = self.superconductor.calculate_current_sharing_temperature(temp_critic, current, magnetic_field)
        reduced_area = self.reduced_wire_area(wire_diameter)*UnitConversion.milimeters2_to_meters2
        ic = self.calculate_critical_current_ic(current, temperature, temp_critic, temp_cs)
        normal_conductor_resistivity = self.normal_conductor.resistivity_nist(magnetic_field, temperature, rrr=self.rrr)

        if temperature < temp_cs:
            return 0.0
        elif temp_cs <= temperature < temp_critic:
            return normal_conductor_resistivity*(current-ic)**2.0/(reduced_area**2.0)
        else:
            return normal_conductor_resistivity*current**2.0/(reduced_area**2.0)

    def create_heat_gen_profile(self, magnetic_field, wire_diameter, current):
        temperature_profile = Materials.create_temperature_step(
            temp_min=self.input_data.material_settings.input.min_temperature_span,
            temp_max=self.input_data.material_settings.input.max_temperature_span,
            number_temp_points=(self.input_data.material_settings.input.max_temperature_span -
                                self.input_data.material_settings.input.min_temperature_span)*10)
        heat_gen_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            heat_gen_array[i, 0] = temperature_profile[i]
            heat_gen_array[i, 1] = self.calculate_joule_heating(
                magnetic_field, wire_diameter, current, temperature=temperature_profile[i])
        GeneralFunctions.save_array(self.output_directory_materials, "heat_generation_profile.txt", heat_gen_array)
        fig = self.plot_properties(heat_gen_array, "Heat Generation, [W/m^3]")
        filename = "Heat_Generation_Curve_B_{}.png".format(magnetic_field)
        os.chdir(self.output_directory_materials)
        fig.savefig(filename, dpi=200)
        return heat_gen_array
