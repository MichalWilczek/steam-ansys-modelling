
import numpy as np
from source.factory.general_functions import GeneralFunctions
from source.materials.material_properties_units import MaterialPropertiesUnits
from source.materials.material_properties_plotter import MaterialPropertiesPlotter

class InsulationLinearMaterialProperties(GeneralFunctions, MaterialPropertiesUnits, MaterialPropertiesPlotter):

    density = 1000.0    # [kg/m3]

    def __init__(self, temperature_profile, txt_output=False, png_output=False, output_directory=None):
        self.temperature_profile = temperature_profile
        self.output_directory = output_directory
        if txt_output or png_output:
            if output_directory is None :
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
        Returns thermal conductivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal conductivity as float
        """
        thermal_conductivity_array = np.zeros((len(self.temperature_profile), 2))
        thermal_conductivity_array[:, 0] = self.temperature_profile
        thermal_conductivity_array[:, 1] = self.thermal_conductivity()
        return thermal_conductivity_array

    def calculate_volumetric_heat_capacity(self):
        """
        Returns volumetric heat capacity array
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        cv_array = np.zeros((len(self.temperature_profile), 2))
        cv_array[:, 0] = self.temperature_profile
        cv_array[:, 1] = self.volumetric_heat_capacity()
        return cv_array

    def calculate_thermal_diffusivity(self):
        """
        Returns thermal diffusivity array
        :return: numpy array; 1st column temperature as float, 2nd column: thermal diffusivity as float
        """
        diffusivity_array = np.zeros((len(self.temperature_profile), 2))
        thermal_conductivity = self.calculate_thermal_conductivity()
        cv = self.calculate_volumetric_heat_capacity()
        diffusivity_array[:, 0] = self.temperature_profile
        diffusivity_array[:, 1] = thermal_conductivity[:, 1] / cv[:, 1]
        return diffusivity_array

    @staticmethod
    def thermal_conductivity():
        """
        Returns constant thermal conductivity
        :return: as float
        """
        thermal_conductivity = 1.0
        return thermal_conductivity

    @staticmethod
    def volumetric_heat_capacity():
        """
        Returns constant volumetric heat capacity
        :return: as float
        """
        volumetric_heat_capacity = 5.0
        return volumetric_heat_capacity

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
        GeneralFunctions.save_array(self.output_directory, "insulation_cv.txt", self.cv)
        GeneralFunctions.save_array(self.output_directory, "insulation_k.txt", self.k)
        GeneralFunctions.save_array(self.output_directory, "insulation_diffusivity.txt", self.diffusivity)

    def extract_png_data(self):
        """
        Saves png files with material properties arrays in Class directory
        """
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="insulation_cv.png",
            array=self.cv, y_axis_name="volumetric heat capacity - insulation, " +
                                       MaterialPropertiesUnits.volumetric_heat_capacity_unit)
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="insulation_k.png",
            array=self.k, y_axis_name="thermal conductivity - insulation, " +
                                      MaterialPropertiesUnits.thermal_conductivity_unit)
        MaterialPropertiesPlotter.plot_material_properties(
            directory=self.output_directory, filename="insulation_diffusivity.png",
            array=self.diffusivity, y_axis_name="thermal diffusivity - insulation, " +
                                                MaterialPropertiesUnits.thermal_diffusivity_unit)
