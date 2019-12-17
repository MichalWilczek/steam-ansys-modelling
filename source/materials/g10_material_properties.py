
import numpy as np
from source.common_functions.general_functions import GeneralFunctions
from source.materials.material_properties_plotter import MaterialPropertiesPlotter
from source.materials.g10_nist_material_properties import G10NISTMaterialProperties
from source.materials.material_properties_units import MaterialPropertiesUnits

class G10MaterialProperties(G10NISTMaterialProperties):

    def __init__(self, temperature_profile, txt_output=False, png_output=False, output_directory=None):
        self.temperature_profile = temperature_profile
        self.output_directory = output_directory
        if txt_output or png_output:
            if output_directory is None:
                raise TypeError("Please, specify the output directory.")
            self.cv = None
            self.k = None
            self.diffusivity = None
            self.calculate_stored_material_properties()
            if txt_output:
                self.extract_txt_data()
            if png_output:
                self.extract_png_data()

    def calculate_thermal_conductivity(self):
        """
        Returns G10 thermal conductivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        g10_thermal_conductivity_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            g10_thermal_conductivity_array[i, 0] = self.temperature_profile[i]
            g10_thermal_conductivity_array[i, 1] = self.thermal_conductivity(temperature=self.temperature_profile[i])
        return g10_thermal_conductivity_array

    def calculate_volumetric_heat_capacity(self):
        """
        Returns G10 volumetric heat capacity array
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        g10_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            g10_cv_array[i, 0] = self.temperature_profile[i]
            g10_cv_array[i, 1] = self.volumetric_heat_capacity(temperature=self.temperature_profile[i])
        return g10_cv_array

    def calculate_thermal_diffusivity(self):
        """
        Returns G10 thermal diffusivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        g10_thermal_conductivity = self.calculate_thermal_conductivity()
        g10_cv = self.calculate_volumetric_heat_capacity()
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = g10_thermal_conductivity[:, 1] / g10_cv[:, 1]
        return diffusivity_array

    def calculate_stored_material_properties(self):
        """
        Returns to internal Class memory the material properties arrays
        :return: material properties numpy arrays in Class 'self' memory
        """
        self.cv = self.calculate_volumetric_heat_capacity()
        self.k = self.calculate_thermal_conductivity()
        self.diffusivity = self.calculate_thermal_diffusivity()

    def extract_txt_data(self):
        """
        Saves txt files with material properties arrays in Class directory
        """
        GeneralFunctions.save_array(self.output_directory, "G10_cv.txt", self.cv)
        GeneralFunctions.save_array(self.output_directory, "G10_k.txt", self.k)
        GeneralFunctions.save_array(self.output_directory, "G10_diffusivity.txt", self.diffusivity)

    def extract_png_data(self):
        """
        Saves png files with material properties arrays in Class directory
        """
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="G10_cv.png",
            array=self.cv, y_axis_name="volumetric heat capacity - G10, " +
                                       MaterialPropertiesUnits.volumetric_heat_capacity_unit)
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="G10_k.png",
            array=self.k, y_axis_name="thermal conductivity - G10, " +
                                      MaterialPropertiesUnits.thermal_conductivity_unit)
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="G10_diffusivity.png",
            array=self.diffusivity, y_axis_name="thermal diffusivity - G10, " +
                                                MaterialPropertiesUnits.thermal_diffusivity_unit)
