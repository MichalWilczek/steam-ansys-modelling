
import numpy as np
from source.common_functions.general_functions import GeneralFunctions
from source.materials.material_properties_plotter import MaterialPropertiesPlotter
from source.materials.nb_ti_cudi_material_properties import NbTiCUDIMaterialProperties
from source.materials.material_properties_units import MaterialPropertiesUnits


class NbTiMaterialProperties(NbTiCUDIMaterialProperties):

    a0 = 1.7
    a1 = 2.33 * 10.0 ** 9.0
    a2 = 9.57 * 10 ** 5.0
    a3 = 163.0

    def __init__(self, temperature_profile,
                 txt_output=False, png_output=False, output_directory=None, magnetic_field_list=None):
        self.temperature_profile = temperature_profile
        self.output_directory = output_directory
        if txt_output or png_output:
            if output_directory is None:
                raise TypeError("Please, specify the output directory.")
            if type(magnetic_field_list) is not list or len(magnetic_field_list) == 0:
                raise TypeError("Please, specify list of magnetic fields to compute.")
            self.cv = []
            self.calculate_stored_material_properties(magnetic_field_list)
            if txt_output:
                self.extract_txt_data(magnetic_field_list)
            if png_output:
                self.extract_png_data(magnetic_field_list)

    def calculate_volumetric_heat_capacity(self, magnetic_field):
        """
        Returns Nb-Ti volumetric heat capacity array
        :param magnetic_field: magnetic field as float
        :return: numpy array; 1st column temperature as float, 2nd column: volumetric heat capacity as float
        """
        nbti_cv_array = np.zeros((len(self.temperature_profile), 2))
        for i in range(len(self.temperature_profile)):
            nbti_cv_array[i, 0] = self.temperature_profile[i]
            nbti_cv_array[i, 1] = self.volumetric_heat_capacity(magnetic_field, temperature=self.temperature_profile[i])
        return nbti_cv_array

    def calculate_stored_material_properties(self, magnetic_field_list):
        """
        Returns to internal Class memory the material properties arrays
        :param magnetic_field_list: list of values of magnetic field strength as floats
        :return: material properties numpy arrays in Class 'self' memory
        """
        for magnetic_field in magnetic_field_list:
            self.cv.append(self.calculate_volumetric_heat_capacity(magnetic_field))

    def extract_txt_data(self, magnetic_field_list):
        """
        Saves txt files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        for i in range(len(magnetic_field_list)):
            GeneralFunctions.save_array(
                self.output_directory, "Nb_Ti_cv_magnetic_field_{}.txt".format(magnetic_field_list[i]), self.cv[i])

    def extract_png_data(self, magnetic_field_list):
        """
        Saves png files with material properties arrays in Class directory
        :param magnetic_field_list: list of values of magnetic field strength as floats
        """
        for i in range(len(magnetic_field_list)):
            MaterialPropertiesPlotter.plot_material_properties(
                directory=self.output_directory,
                filename="Nb_Ti_cv_magnetic_field_{}.png".format(magnetic_field_list[i]),
                array=self.cv[i], y_axis_name="volumetric heat capacity - Nb-Ti, " +
                                              MaterialPropertiesUnits.volumetric_heat_capacity_unit)
