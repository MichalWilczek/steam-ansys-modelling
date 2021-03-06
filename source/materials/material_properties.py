
import numpy as np
from source.common_functions.unit_conversion import UnitConversion
from source.common_functions.general_functions import GeneralFunctions
from source.materials.material_properties_plotter import MaterialPropertiesPlotter
from source.materials.material_properties_units import MaterialPropertiesUnits
from source.geometry.geometric_functions import GeometricFunctions

class MaterialProperties(MaterialPropertiesPlotter):

    def __init__(self, factory, output_directory_materials):

        self.input_data = factory.input_data
        self.output_directory = factory.output_directory
        self.output_directory_materials = output_directory_materials

        self.super_to_normal_ratio = self.input_data.material_settings.input.r_nc_sc
        self.f_superconductor = self.ratio_superconductor()
        self.f_non_superconductor = self.ratio_normal_conductor()

        self.temperature_profile = MaterialProperties.create_temperature_step(
            temp_min=self.input_data.material_settings.input.T_min_materials,
            temp_max=self.input_data.material_settings.input.T_max_materials)

        self.superconductor = factory.get_superconductor_class(self.temperature_profile,
                                                               self.output_directory_materials)
        self.normal_conductor = factory.get_normal_conductor_class(self.temperature_profile,
                                                                   self.output_directory_materials)
        self.insulation = factory.get_insulation_class(self.temperature_profile,
                                                       self.output_directory_materials)
        self.critical_current_density = factory.get_critical_current_density_class()

        magnetic_field_list = self.input_data.material_settings.input.materials_output_for_B_list
        self.strand_equivalent_cv = []
        self.strand_equivalent_diffusivity = []
        self.strand_equivalent_thermal_conductivity = []
        self.strand_equivalent_resistivity = []
        self.calculate_stored_material_properties(magnetic_field_list)
        if self.input_data.material_settings.input.txt_material_output:
            self.extract_txt_data(magnetic_field_list)
        if self.input_data.material_settings.input.png_material_output:
            self.extract_png_data(magnetic_field_list)

    def ratio_superconductor(self):
        """
        Returns superconductor proportion in the strand composite
        :return: as float
        """
        return 1.0/(1.0 + self.super_to_normal_ratio)

    def ratio_normal_conductor(self):
        """
        Returns normal conductor (filler) proportion in the strand composite
        :return: as float
        """
        return 1.0 - self.ratio_superconductor()

    @staticmethod
    def wire_area(wire_diameter):
        return GeometricFunctions.calculate_circle_area(wire_diameter)

    def reduced_wire_area(self, wire_diameter):
        """
        Calculates the normal conductor (filler) area in the strand composite
        :param wire_diameter: as float
        :return: as float
        """
        return GeometricFunctions.calculate_circle_area(wire_diameter) * self.f_non_superconductor

    def reduced_wire_diameter(self, wire_diameter):
        """
        Calculates the imaginary diameter of a strand if area of a normal conductor (filler) is only considered
        :param wire_diameter: real wire diameter as float
        :return: reduced diameter as float
        """
        reduced_wire_area = self.reduced_wire_area(wire_diameter)
        return GeometricFunctions.calculate_diameter_from_circle_area(reduced_wire_area)

    @staticmethod
    def create_temperature_step(temp_min, temp_max, number_temp_points=100):
        """
        Creates temperature values to be input in all material properties functions
        :param temp_min: minimum temperature as float
        :param temp_max: maximum temperature as float
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
            resistivity_elem = self.normal_conductor.electrical_resistivity(
                magnetic_field=mag_field, rrr=self.normal_conductor.rrr, temperature=t_elem)
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
            elem_area = self.wire_area(wire_diameter*UnitConversion.milimeters_to_meters)
            elem_volume = elem_area*elem_length
            elem_energy = elem_volume * cv_elem * (t_elem-ref_temperature)
            qf_energy += elem_energy
        return qf_energy

    def calculate_winding_thermal_diffusivity(self, magnetic_field):
        """
        Returns equivalent strand thermal diffusivity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        eq_thermal_conductivity = self.calculate_winding_eq_thermal_conductivity(magnetic_field=magnetic_field)
        winding_cv = self.calculate_winding_eq_cv(magnetic_field=magnetic_field)
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = eq_thermal_conductivity[:, 1] / winding_cv[:, 1]
        return diffusivity_array

    def calculate_winding_eq_cv(self, magnetic_field, kappa_cv=1):
        """
        Returns strand equivalent volumetric heat capacity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        winding_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            winding_cv_array[i, 0] = self.temperature_profile[i]
            winding_cv_array[i, 1] = kappa_cv*self.winding_eq_cv(magnetic_field, temperature=self.temperature_profile[i])
        return winding_cv_array

    def winding_eq_cv(self, magnetic_field, temperature):
        """
        Calculates strand equivalent volumetric heat capacity
        :param magnetic_field: magnetic field as float
        :param temperature: temperature as float
        :return: volumetric heat capacity as float
        """
        normal_conductor_cv = self.normal_conductor.volumetric_heat_capacity(temperature)
        superconductor_cv = self.superconductor.volumetric_heat_capacity(magnetic_field, temperature)
        winding_eq_cv = self.f_non_superconductor*normal_conductor_cv + self.f_superconductor*superconductor_cv
        return winding_eq_cv

    def calculate_winding_eq_thermal_conductivity(self, magnetic_field):
        winding_k_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            winding_k_array[i, 0] = self.temperature_profile[i]
            winding_k_array[i, 1] = self.winding_eq_thermal_conductivity(magnetic_field,
                                                                         temperature=self.temperature_profile[i])
        return winding_k_array

    def winding_eq_thermal_conductivity(self, magnetic_field, temperature, kappa_cond=1):
        return kappa_cond*self.normal_conductor.thermal_conductivity(magnetic_field, temperature, self.normal_conductor.rrr) * \
               self.f_non_superconductor

    def calculate_winding_eq_resistivity(self, magnetic_field, kappa_res=1):
        winding_rho_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            winding_rho_array[i, 0] = self.temperature_profile[i]
            winding_rho_array[i, 1] = kappa_res*self.winding_eq_resistivity(magnetic_field,
                                                                  temperature=self.temperature_profile[i])
        return winding_rho_array

    def winding_eq_resistivity(self, magnetic_field, temperature):
        return self.normal_conductor.electrical_resistivity(magnetic_field, temperature, self.normal_conductor.rrr) / \
               self.f_non_superconductor

    def create_joule_heating_density_profile(self, magnetic_field, wire_diameter, current):
        """
        Returns initial Joule heating density profile as numpy array
        :param magnetic_field: magnetic field as float
        :param wire_diameter: wire diameter as float
        :param current: current as float
        :return: numpy array; 1st column temperature as float, 2nd column: Joule heating density as float
        """
        wire_area = self.wire_area(wire_diameter*UnitConversion.milimeters_to_meters)

        temperature_profile = MaterialProperties.create_temperature_step(
            temp_min=self.input_data.material_settings.input.T_min_materials,
            temp_max=self.input_data.material_settings.input.T_max_materials,
            number_temp_points=(self.input_data.material_settings.input.T_max_materials -
                                self.input_data.material_settings.input.T_min_materials)*500)
        heat_gen_array = np.zeros((len(temperature_profile), 2))
        for i in range(len(temperature_profile)):
            eq_electrical_resistivity = self.winding_eq_resistivity(magnetic_field, temperature_profile[i])
            power_density = self.critical_current_density.calculate_joule_heating(
                magnetic_field, current, temperature=temperature_profile[i], wire_area=wire_area,
                normal_conductor_resistivity=eq_electrical_resistivity,
                superconductor_proportion=self.f_superconductor)
            heat_gen_array[i, 0] = temperature_profile[i]
            heat_gen_array[i, 1] = power_density
        self.extract_joule_heating_density_profile(heat_gen_array)
        return heat_gen_array

    def extract_joule_heating_density_profile(self, joule_heating_density_array):
        """
        Saves txt and png files with Joule heating initial profile
        :param joule_heating_density_array: numpy array;
        1st column temperature as float, 2nd column: joule heating density as float
        """
        GeneralFunctions.save_array(self.output_directory_materials, "joule_heating_density_profile.txt",
                                    joule_heating_density_array)
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory_materials,
            filename="joule_heating_density_profile.png",
            array=joule_heating_density_array,
            y_axis_name="Joule Heating Density, " + MaterialPropertiesUnits.power_density_unit)

    def calculate_stored_material_properties(self, magnetic_field_list):
        """
        Returns to internal Class memory the material properties arrays
        :param magnetic_field_list: list of values of magnetic field strength as floats
        :return: material properties numpy arrays in Class 'self' memory
        """
        for magnetic_field in magnetic_field_list:
            self.strand_equivalent_cv.append(self.calculate_winding_eq_cv(magnetic_field))
            self.strand_equivalent_diffusivity.append(self.calculate_winding_thermal_diffusivity(magnetic_field))
            self.strand_equivalent_thermal_conductivity.append(
                self.calculate_winding_eq_thermal_conductivity(magnetic_field))
            self.strand_equivalent_resistivity.append(self.calculate_winding_eq_resistivity(magnetic_field))

    def extract_txt_data(self, magnetic_field_list):
        """
        Saves txt files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        for i in range(len(magnetic_field_list)):
            GeneralFunctions.save_array(
                self.output_directory_materials,
                "Strand_eq_cv_magnetic_field_{}.txt".format(magnetic_field_list[i]),
                self.strand_equivalent_cv[i])
            GeneralFunctions.save_array(
                self.output_directory_materials,
                "Strand_eq_diffusivity_magnetic_field_{}.txt".format(magnetic_field_list[i]),
                self.strand_equivalent_diffusivity[i])
            GeneralFunctions.save_array(
                self.output_directory_materials,
                "Strand_eq_thermal_conductivity_magnetic_field_{}.txt".format(magnetic_field_list[i]),
                self.strand_equivalent_thermal_conductivity[i])
            GeneralFunctions.save_array(
                self.output_directory_materials,
                "Strand_eq_resistivity_magnetic_field_{}.txt".format(magnetic_field_list[i]),
                self.strand_equivalent_resistivity[i])

    def extract_png_data(self, magnetic_field_list):
        """
        Saves png files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        for i in range(len(magnetic_field_list)):
            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory_materials,
                filename="Strand_equivalent_cv_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.strand_equivalent_cv[i],
                y_axis_name="volumetric heat capacity - Strand, " +
                            MaterialPropertiesUnits.volumetric_heat_capacity_unit)

            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory_materials,
                filename="Strand_equivalent_diffusivity_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.strand_equivalent_diffusivity[i],
                y_axis_name="thermal diffusivity - Strand, " + MaterialPropertiesUnits.thermal_diffusivity_unit)

            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory_materials,
                filename="Strand_equivalent_thermal_conductivity_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.strand_equivalent_thermal_conductivity[i],
                y_axis_name="thermal conductivity - Strand, " + MaterialPropertiesUnits.thermal_conductivity_unit)

            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory_materials,
                filename="Strand_equivalent_resistivity_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.strand_equivalent_resistivity[i],
                y_axis_name="electrical resistivity - Strand, " + MaterialPropertiesUnits.electrical_resistivity_unit)
