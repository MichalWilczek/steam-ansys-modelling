
from source.common_functions.general_functions import GeneralFunctions
from source.materials.material_properties_plotter import MaterialPropertiesPlotter
from source.materials.cu_nist_material_properties import CuNISTMaterialProperties
from source.materials.material_properties_units import MaterialPropertiesUnits
import numpy as np


class CuMaterialProperties(MaterialPropertiesPlotter, CuNISTMaterialProperties):

    def __init__(self, temperature_profile, rrr,
                 txt_output=False, png_output=False, output_directory=None, magnetic_field_list=None):
        self.temperature_profile = temperature_profile
        self.rrr = rrr
        self.output_directory = output_directory
        if txt_output or png_output:
            if output_directory is None:
                raise TypeError("Please, specify the output directory.")
            if type(magnetic_field_list) is not list or len(magnetic_field_list) == 0:
                raise TypeError("Please, specify list of magnetic fields to compute.")
            self.cv = None
            self.resistivity = []
            self.k = []
            self.diffusivity = []
            self.calculate_stored_material_properties(magnetic_field_list)
            if txt_output:
                self.extract_txt_data(magnetic_field_list)
            if png_output:
                self.extract_png_data(magnetic_field_list)

    def calculate_electrical_resistivity(self, magnetic_field):
        """
        Returns copper electrical resistivity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: electrical resistivity as float
        """
        cu_resistivity_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            cu_resistivity_array[i, 0] = self.temperature_profile[i]
            cu_resistivity_array[i, 1] = self.electrical_resistivity(
                magnetic_field, temperature=self.temperature_profile[i], rrr=self.rrr)
        return cu_resistivity_array

    def calculate_thermal_conductivity(self, magnetic_field):
        """
        Returns copper thermal conductivity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        cu_thermal_conductivity_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            cu_thermal_conductivity_array[i, 0] = self.temperature_profile[i]
            cu_thermal_conductivity_array[i, 1] = self.thermal_conductivity(
                magnetic_field=magnetic_field, temperature=self.temperature_profile[i], rrr=self.rrr)
        return cu_thermal_conductivity_array

    def calculate_volumetric_heat_capacity(self):
        """
        Returns copper volumetric heat capacity array
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        cu_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            cu_cv_array[i, 0] = self.temperature_profile[i]
            cu_cv_array[i, 1] = self.volumetric_heat_capacity(temperature=self.temperature_profile[i])
        return cu_cv_array

    def calculate_thermal_diffusivity(self, magnetic_field):
        """
        Returns copper thermal diffusivity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        cu_thermal_conductivity = self.calculate_thermal_conductivity(magnetic_field=magnetic_field)
        cu_cv = self.calculate_volumetric_heat_capacity()
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = cu_thermal_conductivity[:, 1] / cu_cv[:, 1]
        return diffusivity_array

    def calculate_stored_material_properties(self, magnetic_field_list):
        """
        Returns to internal Class memory the material properties arrays
        :param magnetic_field_list: list of values of magnetic field strength as floats
        :return: material properties numpy arrays in Class 'self' memory
        """
        self.cv = self.calculate_volumetric_heat_capacity()
        for magnetic_field in magnetic_field_list:
            self.k.append(self.calculate_thermal_conductivity(magnetic_field))
            self.resistivity.append(self.calculate_electrical_resistivity(magnetic_field))
            self.diffusivity.append(self.calculate_thermal_diffusivity(magnetic_field))

    def extract_txt_data(self, magnetic_field_list):
        """
        Saves txt files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        GeneralFunctions.save_array(self.output_directory, "Cu_cv.txt", self.cv)
        for i in range(len(magnetic_field_list)):
            GeneralFunctions.save_array(
                self.output_directory, "Cu_k_magnetic_field_{}.txt".format(magnetic_field_list[i]), self.k[i])
            GeneralFunctions.save_array(
                self.output_directory,
                "Cu_resistivity_magnetic_field_{}.txt".format(magnetic_field_list[i]), self.resistivity[i])
            GeneralFunctions.save_array(
                self.output_directory,
                "Cu_diffusivity_magnetic_field_{}.txt".format(magnetic_field_list[i]), self.diffusivity[i])

    def extract_png_data(self, magnetic_field_list):
        """
        Saves png files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="Cu_cv.png",
            array=self.cv, y_axis_name="volumetric heat capacity - Cu, " +
                                       MaterialPropertiesUnits.volumetric_heat_capacity_unit)

        for i in range(len(magnetic_field_list)):
            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory, filename="Cu_k_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.k[i], y_axis_name="thermal conductivity - Cu, " +
                                             MaterialPropertiesUnits.thermal_conductivity_unit)

            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory,
                filename="Cu_resistivity_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.resistivity[i], y_axis_name="resistivity - Cu, " +
                                                       MaterialPropertiesUnits.electrical_resistivity_unit)

            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory,
                filename="Cu_diffusivity_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.diffusivity[i], y_axis_name="thermal diffusivity - Cu, " +
                                                       MaterialPropertiesUnits.thermal_diffusivity_unit)
